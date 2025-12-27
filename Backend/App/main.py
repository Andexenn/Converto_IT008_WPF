"""
Entry point for the server
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from Database.connection import get_db, r, init_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from Handlers import auth_handler, conversion_handler, compression_handler,\
      remove_background_handler, task_handler, user_handler

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
app.include_router(conversion_handler.router, prefix="/api", tags=["Service"] )
app.include_router(compression_handler.router, prefix="/api", tags=["Service"])
app.include_router(remove_background_handler.router, prefix="/api", tags=["Service"])
app.include_router(task_handler.router, prefix='/api', tags=["Data"])
app.include_router(user_handler.router, prefix='/api', tags=["Data"])

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
    Check if server is working well
    """
    return {"status": "healthy"}

@app.get("/connect_db")
def connect_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except OperationalError as e:
        print(f"Cannot connect to mysql db: {str(e)}")
        return {"status": "disconnect"}

    try:
        r.ping()
    except OperationalError as e:
        print(f"Cannot connect to redis db: {str(e)}")
        return {"status": "disconnect"}
    
    return {"status": "connected"}
