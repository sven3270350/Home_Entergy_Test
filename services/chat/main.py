from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import httpx
import os
from typing import List, Optional
import json

from app.database import get_db, init_db
from app.schemas import ChatQuery, ChatResponse
from app.auth import get_current_user, User
from app.llm import process_query, QueryResult

app = FastAPI(
    title="Smart Home Chat Service",
    description="Natural Language Query Service for Smart Home Energy Monitoring",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
TELEMETRY_SERVICE_URL = os.getenv("TELEMETRY_SERVICE_URL", "http://localhost:8001")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/api/chat/query", response_model=ChatResponse)
async def query_energy_data(
    query: ChatQuery,
    current_user: User = Depends(get_current_user)
):
    # Get user's devices from telemetry service
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TELEMETRY_SERVICE_URL}/api/devices",
            headers={"Authorization": f"Bearer {query.auth_token}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch devices"
            )
        
        devices = response.json()
    
    # Process the natural language query
    query_result = await process_query(
        query.text,
        devices,
        current_user,
        query.auth_token,
        TELEMETRY_SERVICE_URL
    )
    
    return ChatResponse(
        answer=query_result.answer,
        data=query_result.data,
        device_id=query_result.device_id,
        time_period=query_result.time_period
    )

@app.get("/health")
def health_check():
    try:
        # Check if OpenAI API key is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key not configured")
        return {"status": "healthy", "openai": "configured"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 