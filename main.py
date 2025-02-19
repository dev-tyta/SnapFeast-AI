# main.py
from fastapi import FastAPI
from typing import List
from users.routes import router as users_router
from auth.route import router as auth_router
from orders.routes import order_router, meal_router

app = FastAPI(
    title="SnapFeast API",
    description="SnapFeast API for managing users, meals, and orders.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(meal_router)
app.include_router(order_router)


@app.get("/", tags=["Home"])
def read_root():
    return {"message": "Welcome to SnapFeast API!"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

