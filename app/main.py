from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI

from app import settings
from app.core.logger_setup import setup_logging
from app.service.api import auth_router


# tasks before app start and after
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
    # Clean up if it is nessesary


app = FastAPI(
    title=settings.project_name,
    openapi_url="/openapi.json",
    lifespan=lifespan,
    loglevel="debug",
)

# routers:
#api_router = APIRouter()
#api_router.include_router(auth_router)

app.include_router(auth_router)

if __name__ == "__main__":
    # TODO: migration mechanism?
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
