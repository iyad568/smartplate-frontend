"""
Orders API routes for SmartPlate order management - matching PlaqueStandard.jsx form data.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderSearch,
    OrderList,
    OrderStats
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order from PlaqueStandard form",
    responses={
        201: {"description": "Order created successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
    },
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> OrderResponse:
    """Create a new order from PlaqueStandard form (Step 1: Create order)."""
    service = OrderService(db)
    order = await service.create_order(order_data, user.id)
    return order


@router.post(
    "/{order_id}/process",
    response_model=dict,
    summary="Process order and create car",
    responses={
        200: {"description": "Order processed successfully"},
        400: {"description": "Order cannot be processed"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"},
    },
)
async def process_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> dict:
    """Process order and create car (Step 2: Create car)."""
    service = OrderService(db)
    result = await service.process_order(order_id, user.id)
    return result


@router.get(
    "/my",
    response_model=List[OrderResponse],
    summary="Get current user's orders",
    responses={
        200: {"description": "Orders retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
)
async def get_user_orders(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[OrderResponse]:
    """Get all orders for the current user."""
    service = OrderService(db)
    orders = await service.get_user_orders(user.id)
    return orders


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    responses={
        200: {"description": "Order retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"},
    },
)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> OrderResponse:
    """Get an order by ID."""
    service = OrderService(db)
    order = await service.get_order(order_id, user.id)
    return order


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update order",
    responses={
        200: {"description": "Order updated successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"},
    },
)
async def update_order(
    order_id: str,
    update_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> OrderResponse:
    """Update an order."""
    service = OrderService(db)
    order = await service.update_order(order_id, update_data, user.id)
    return order


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel order",
    responses={
        200: {"description": "Order cancelled successfully"},
        400: {"description": "Order cannot be cancelled"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"},
    },
)
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> OrderResponse:
    """Cancel an order."""
    service = OrderService(db)
    order = await service.cancel_order(order_id, user.id)
    return order


@router.post(
    "/{order_id}/mark-paid",
    response_model=OrderResponse,
    summary="Mark order payment as paid",
    responses={
        200: {"description": "Payment marked as paid successfully"},
        400: {"description": "Payment is already paid"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"},
    },
)
async def mark_payment_paid(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)
) -> OrderResponse:
    """Mark order payment as paid (admin only)."""
    service = OrderService(db)
    order = await service.mark_payment_paid(order_id)
    return order


@router.get(
    "/stats",
    response_model=OrderStats,
    summary="Get order statistics",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"},
    },
)
async def get_order_stats(
    user_id: Optional[str] = Query(None, description="Filter stats by user ID (admin only)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> OrderStats:
    """Get order statistics."""
    # Only admin can filter by user_id
    if user_id and user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    service = OrderService(db)
    stats = await service.get_order_stats(user_id)
    
    return OrderStats(
        total_orders=stats['total_orders'],
        pending_orders=stats['pending_orders'],
        processing_orders=stats['processing_orders'],
        completed_orders=stats['completed_orders'],
        cancelled_orders=stats['cancelled_orders'],
        paid_orders=stats['paid_orders'],
        total_revenue=stats['total_revenue'],
        orders_by_plate_type=stats['orders_by_plate_type'],
        orders_by_status=stats['orders_by_status']
    )
