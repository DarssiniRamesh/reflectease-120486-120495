from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..routers.journal_router import router as journal_router

# FastAPI app configuration with OpenAPI documentation
app = FastAPI(
    title="Daily Journal API",
    description="A lightweight REST API for managing daily journal entries with mood tracking and filtering capabilities.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware configuration for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only include the journal router (auth endpoints deprecated/removed)
app.include_router(journal_router)

@app.get("/", tags=["health"])
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns a simple message indicating the service is healthy.
    """
    return {"message": "Daily Journal API is healthy", "version": "1.0.0"}
