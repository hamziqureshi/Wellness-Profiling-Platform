import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError


import common.constants as CONSTS
from api import websocket_routes


app = FastAPI(
    version="1.0.0",
    title="Healf-Task: Wellness Profiling Platform",
    summary="A platform for personalized wellness tracking and health profiling.",
    description=(
        "Healf-Task is a comprehensive wellness profiling platform designed to help users track, "
        "analyze, and improve their overall health. The platform offers personalized insights, "
        "data-driven recommendations, and tools to support a healthier lifestyle."
    ),
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


try:   
    app.include_router(websocket_routes.router)
except Exception as e:
    raise

    
@app.get('/')
def default():
    return JSONResponse(status_code=200, content="")


# Health check endpoints
@app.get("/healthz")
async def health_check():
    try:
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Health check failed")
    
logging.basicConfig(level=logging.DEBUG if CONSTS.IS_DEV else logging.INFO)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host=CONSTS.HOST,
        port=CONSTS.PORT,
        timeout_keep_alive=300,
        ws_ping_interval=None,     # <--- Disable low-level pinging
        ws_ping_timeout=None       # <--- Disable timeout on pong
    )