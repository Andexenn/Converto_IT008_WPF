from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from Database.connection import init_db
from Handlers.UserHandlers import auth_handler
from Handlers.ConvertHandlers import image_converter_handlers
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
app.include_router(image_converter_handlers.router, prefix="/api/convert/image", tags=["Authentication"] )

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} API is running",
        "version": "1.0.0",
        "docs":"/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}


