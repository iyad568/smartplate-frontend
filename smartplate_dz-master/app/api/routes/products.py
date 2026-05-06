"""
Products API routes for SmartPlate product management.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductList,
    ProductSearch,
    StockUpdate,
    BulkStockUpdate,
    ProductStats
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])



@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    responses={
        201: {"description": "Product created successfully"},
        409: {"description": "Product with SKU/barcode already exists"},
        422: {"description": "Validation error"},
    },
)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)
) -> ProductResponse:
    """Create a new product."""
    service = ProductService(db)
    product = await service.create_product(product_data)
    return ProductResponse.model_validate(product)


@router.get(
    "/",
    response_model=ProductList,
    summary="Get all products with pagination and filters",
    responses={
        200: {"description": "Products retrieved successfully"},
    },
)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search query"),
    min_price: float = Query(None, ge=0, description="Minimum price filter"),
    max_price: float = Query(None, ge=0, description="Maximum price filter"),
    is_active: bool = Query(None, description="Filter by active status"),
    in_stock: bool = Query(None, description="Filter by stock availability"),
    low_stock: bool = Query(None, description="Filter by low stock items"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> ProductList:
    """Get products with filtering and pagination."""
    service = ProductService(db)
    
    products, total = await service.get_products(
        page=page,
        size=size,
        search=search,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        in_stock=in_stock,
        low_stock=low_stock
    )
    
    pages = (total + size - 1) // size if total > 0 else 0
    
    return ProductList(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get a product by ID",
    responses={
        200: {"description": "Product retrieved successfully"},
        404: {"description": "Product not found"},
    },
)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> ProductResponse:
    """Get a product by ID."""
    service = ProductService(db)
    product = await service.get_product(product_id)
    return ProductResponse.model_validate(product)




@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product",
    responses={
        200: {"description": "Product updated successfully"},
        404: {"description": "Product not found"},
        422: {"description": "Validation error"},
    },
)
async def update_product(
    product_id: UUID,
    update_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)
) -> ProductResponse:
    """Update a product."""
    service = ProductService(db)
    product = await service.update_product(product_id, update_data)
    return ProductResponse.model_validate(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    responses={
        204: {"description": "Product deleted successfully"},
        404: {"description": "Product not found"},
    },
)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)
) -> None:
    """Delete a product."""
    service = ProductService(db)
    await service.delete_product(product_id)


# ─── Search ──────────────────────────────────────────────────────────────

@router.post(
    "/search",
    response_model=ProductList,
    summary="Search products with advanced filters",
    responses={
        200: {"description": "Products retrieved successfully"},
    },
)
async def search_products(
    search_params: ProductSearch,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> ProductList:
    """Search products with advanced filters."""
    service = ProductService(db)
    
    products, total = await service.search_products(search_params)
    
    # Apply pagination
    skip = (page - 1) * size
    paginated_products = products[skip:skip + size]
    
    pages = (total + size - 1) // size if total > 0 else 0
    
    return ProductList(
        products=[ProductResponse.model_validate(p) for p in paginated_products],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


# ─── Stock Management ─────────────────────────────────────────────────────

@router.put(
    "/{product_id}/stock",
    response_model=ProductResponse,
    summary="Update product stock",
    responses={
        200: {"description": "Stock updated successfully"},
        404: {"description": "Product not found"},
        400: {"description": "Invalid stock quantity"},
    },
)
async def update_stock(
    product_id: UUID,
    stock_update: StockUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)
) -> ProductResponse:
    """Update product stock quantity."""
    service = ProductService(db)
    product = await service.update_stock(product_id, stock_update)
    return ProductResponse.model_validate(product)


@router.put(
    "/stock/bulk",
    response_model=List[ProductResponse],
    summary="Bulk update stock for multiple products",
    responses={
        200: {"description": "Stock updated successfully"},
        400: {"description": "Invalid update data"},
    },
)
async def bulk_update_stock(
    bulk_update: BulkStockUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)
) -> List[ProductResponse]:
    """Update stock for multiple products."""
    service = ProductService(db)
    products = await service.bulk_update_stock(bulk_update)
    return [ProductResponse.model_validate(p) for p in products]


# ─── Reports & Analytics ───────────────────────────────────────────────────

@router.get(
    "/reports/low-stock",
    response_model=List[ProductResponse],
    summary="Get products with low stock",
    responses={
        200: {"description": "Low stock products retrieved successfully"},
    },
)
async def get_low_stock_products(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[ProductResponse]:
    """Get products with low stock."""
    service = ProductService(db)
    products = await service.get_low_stock_products(limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.get(
    "/reports/out-of-stock",
    response_model=List[ProductResponse],
    summary="Get products that are out of stock",
    responses={
        200: {"description": "Out of stock products retrieved successfully"},
    },
)
async def get_out_of_stock_products(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[ProductResponse]:
    """Get products that are out of stock."""
    service = ProductService(db)
    products = await service.get_out_of_stock_products(limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.get(
    "/reports/stats",
    response_model=ProductStats,
    summary="Get product statistics",
    responses={
        200: {"description": "Product statistics retrieved successfully"},
    },
)
async def get_product_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> ProductStats:
    """Get comprehensive product statistics."""
    service = ProductService(db)
    return await service.get_stats()




