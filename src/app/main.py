from fastapi import FastAPI
from app.api.email_routes import router as email_router


def create_app() -> FastAPI:
    app = FastAPI(title="Trip Summary Email Service")
    app.include_router(email_router)
    return app


app = create_app()
