"""
Entry point for the server
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from Database.connection import init_db, get_db
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
def health_check(db:Session = Depends(get_db)):
    """
    Check if server is working well
    """
    try:
        db.execute(text("SELECT 1"))
    except OperationalError as e:
        print(f"Can not connect to the database {str(e)}") 
    return {"status": "healthy"}
