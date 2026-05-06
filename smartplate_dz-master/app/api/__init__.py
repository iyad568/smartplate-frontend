from fastapi import APIRouter

from app.api.routes import admin, auth, cars, dashboard, admin_dashboard, depannage, orders, products, services, sos, upload, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)
api_router.include_router(sos.router)
api_router.include_router(depannage.router)
api_router.include_router(cars.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin_dashboard.router)
api_router.include_router(orders.router)
api_router.include_router(products.router)
api_router.include_router(services.router)
api_router.include_router(upload.router)
