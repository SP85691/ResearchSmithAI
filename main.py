from fastapi import FastAPI
from app.db.SessionManager import Base, engine
from app.api.v1.auth import router as auth_router

# Initialize database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="ResearchSmithAI API", version="1.0")

# Register routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
