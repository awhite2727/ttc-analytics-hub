import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.db import db
from api.services.polling import update_vehicle_positions
from api.routers import static, realtime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print("Starting up... Connecting to DB and starting poller.")
    db.connect()
    
    # Start the background polling task
    polling_task = asyncio.create_task(update_vehicle_positions())
    
    yield
    
    # --- SHUTDOWN ---
    print("Shutting down...")
    polling_task.cancel()
    db.close()

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "TTC GTFS API"}

# Register the split routers
app.include_router(static.router, prefix="/api", tags=["Static Data"])
app.include_router(realtime.router, prefix="/api", tags=["Realtime Data"])