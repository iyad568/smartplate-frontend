"""
Order service for SmartPlate order management - matching PlaqueStandard.jsx form data.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.order_repo import OrderRepository
from app.db.repositories.car_repo import CarRepository
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderSearch
from app.schemas.car import CarCreate
from app.models.order import Order


class OrderService:
    """Service for order management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.car_repo = CarRepository(db)
    
    async def create_order(self, order_data: OrderCreate, user_id: str) -> OrderResponse:
        """Create a new order and automatically create car (Step 1 + Step 2 combined)."""
        try:
            # Convert to dict for repository
            order_dict = order_data.dict()
            order_dict['user_id'] = user_id
            
            # Set default status and payment status
            order_dict['status'] = 'completed'
            order_dict['payment_status'] = 'paid'
            
            # Create order
            order = await self.order_repo.create(order_dict)
            
            # Check if car with this plate already exists
            existing_car = await self.car_repo.get_by_plate_number(order.plate)
            if existing_car:
                # Update existing car instead of creating new one
                car_update_data = {
                    'chassis_number': order.chassis if order.chassis else existing_car.chassis_number,
                    'vehicle_type': order.type if order.type else existing_car.vehicle_type,
                    'vehicle_brand': order.brand if order.brand else existing_car.vehicle_brand,
                    'power_type': order.power if order.power else existing_car.power_type,
                    'cni_number': order.cni if order.cni else existing_car.cni_number,
                    'owner_address': order.address if order.address else existing_car.owner_address,
                    'owner_name': order.name if order.name else existing_car.owner_name,
                    'owner_first_name': order.first if order.first else existing_car.owner_first_name,
                    'owner_phone': order.phone if order.phone else existing_car.owner_phone,
                    'owner_email': order.email if order.email else existing_car.owner_email,
                    'cart_grise_url': order.cart_grise_url if order.cart_grise_url else existing_car.cart_grise_url,
                }
                car = await self.car_repo.update(existing_car.id, car_update_data)
            else:
                # Create new car only if plate doesn't exist
                car_data_dict = {
                    'plate_number': order.plate if order.plate else '',
                    'chassis_number': order.chassis if order.chassis else None,
                    'vehicle_type': order.type if order.type else None,
                    'vehicle_brand': order.brand if order.brand else None,
                    'power_type': order.power if order.power else 'essence',
                    'cni_number': order.cni if order.cni else None,
                    'owner_address': order.address if order.address else None,
                    'owner_name': order.name if order.name else None,
                    'owner_first_name': order.first if order.first else None,
                    'owner_phone': order.phone if order.phone else None,
                    'owner_email': order.email if order.email else None,
                    'cart_grise_url': order.cart_grise_url if order.cart_grise_url else None,
                    'status': 'active',
                    'user_id': user_id
                }
                car = await self.car_repo.create(car_data_dict)
            
            return OrderResponse.model_validate(order)
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error in create_order: {str(e)}")
            # Re-raise as HTTPException for proper API response
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create order and car: {str(e)}"
            )
    
    async def process_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """Process order and create car (Step 2: Create car from order data)."""
        # Get order
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user owns the order
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if order is pending
        if order.status != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order cannot be processed. Current status: {order.status}"
            )
        
        # Check if payment is paid (you might want to add payment processing here)
        if order.payment_status != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment must be completed before processing order"
            )
        
        # Create car from order data using the get_car_data method
        car_data_dict = order.get_car_data()
        car_data = CarCreate(**car_data_dict)
        
        # Create car
        car = await self.car_repo.create({
            **car_data.dict(),
            'user_id': user_id
        })
        
        # Update order status to processing
        await self.order_repo.update(order_id, {
            'status': 'processing',
            'processed_at': datetime.utcnow()
        })
        
        # Update order status to completed
        await self.order_repo.update(order_id, {
            'status': 'completed',
            'completed_at': datetime.utcnow()
        })
        
        return {
            'order': OrderResponse.model_validate(order),
            'car': car,
            'message': 'Order processed successfully and car created'
        }
    
    async def get_order(self, order_id: str, user_id: Optional[str] = None) -> OrderResponse:
        """Get an order by ID."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user has access (if user_id is provided)
        if user_id and order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return OrderResponse.model_validate(order)
    
    async def get_user_orders(self, user_id: str) -> List[OrderResponse]:
        """Get all orders for a user."""
        orders = await self.order_repo.get_by_user_id(user_id)
        return [OrderResponse.model_validate(order) for order in orders]
    
    async def update_order(self, order_id: str, update_data: OrderUpdate, user_id: Optional[str] = None) -> OrderResponse:
        """Update an order."""
        # Get order first to check permissions
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user has access (if user_id is provided)
        if user_id and order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update order
        updated_order = await self.order_repo.update(order_id, update_data.dict(exclude_unset=True))
        if not updated_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return OrderResponse.model_validate(updated_order)
    
    async def cancel_order(self, order_id: str, user_id: str) -> OrderResponse:
        """Cancel an order."""
        # Get order
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user owns the order
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if order can be cancelled
        if order.status in ['completed', 'cancelled']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order cannot be cancelled. Current status: {order.status}"
            )
        
        # Update order status
        updated_order = await self.order_repo.update(order_id, {
            'status': 'cancelled'
        })
        
        return OrderResponse.model_validate(updated_order)
    
    async def mark_payment_paid(self, order_id: str) -> OrderResponse:
        """Mark order payment as paid."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.payment_status == 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is already marked as paid"
            )
        
        updated_order = await self.order_repo.update(order_id, {
            'payment_status': 'paid'
        })
        
        return OrderResponse.model_validate(updated_order)
    
    async def get_order_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get order statistics."""
        return await self.order_repo.get_stats(user_id)
