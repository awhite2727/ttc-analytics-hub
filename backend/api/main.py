import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.db import db
from api.services.polling import update_vehicle_positions
from api.services.analytics import run_analytics_engine
from api.routers import static, realtime, metrics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print("Starting up... Connecting to DB.")
    db.connect()
    
    # Start the background tasks
    polling_task = asyncio.create_task(update_vehicle_positions())
    analytics_task = asyncio.create_task(run_analytics_engine())
    
    yield
    
    # --- SHUTDOWN ---
    print("Shutting down...")
    polling_task.cancel()
    analytics_task.cancel()
    db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ttc-analytics-hub.vercel.app/", "http://[::1]:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "TTC GTFS API"}

# Register the split routers
app.include_router(static.router, prefix="/api", tags=["Static Data"])
app.include_router(realtime.router, prefix="/api", tags=["Realtime Data"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])