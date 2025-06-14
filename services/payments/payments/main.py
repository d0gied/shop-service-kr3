from contextlib import asynccontextmanager
from common.logging import get_logger, log_routes
from common.middleware import FastAPILoggingMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from payments.database import create_all_tables, get_engine
from payments.routers.account import router as account_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    This is used to set up and tear down resources, such as database connections.
    """
    logger.info("Starting Payments Service")
    log_routes(app, logger=logger)  # Log the routes for debugging purposes

    logger.info("Setting up database connections and other resources")
    await create_all_tables(get_engine())
    yield
    logger.info("Stopping Payments Service")


app = FastAPI(
    title="Payments Service",
    description="This is the payments service for the application.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity; adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
app.add_middleware(FastAPILoggingMiddleware)


app.include_router(account_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Payments Service!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
