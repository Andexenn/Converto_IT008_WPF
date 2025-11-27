"""
Entry point for the server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Database.connection import init_db
from Handlers import auth_handler, conversion_handler, conversion_history_handler, compression_handler, remove_background_handler

from config import settings

init_db()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="File Conversion and Compression API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_handler.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(conversion_handler.router, prefix="/api", tags=["Authentication"] )
app.include_router(conversion_history_handler.router, prefix="/api", tags=["Authentication"])
app.include_router(compression_handler.router, prefix="/api", tags=["Authentication"])
app.include_router(remove_background_handler.router, prefix="/api", tags=["Authentication"])

@app.get("/")
def root():
    """
    Define the root api endpoint
    """
    return {
        "message": f"{settings.APP_NAME} API is running",
        "version": "1.0.0",
        "docs":"/docs"
    }

@app.get("/health")
def health_check():
    """
    Check if api is work well
    """
    return {"status": "healthy"}
