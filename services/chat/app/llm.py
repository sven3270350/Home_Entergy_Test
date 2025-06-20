from datetime import datetime, timedelta
import httpx
import json
import os
from typing import List, Dict, Any, Optional
import openai
from dateutil import parser
import re

from .schemas import QueryResult

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

async def process_query(
    query: str,
    devices: List[Dict[str, Any]],
    user: Any,
    auth_token: str,
    telemetry_service_url: str
) -> QueryResult:
    # Extract intent and parameters from the query
    intent_data = await extract_intent(query, devices)
    
    # Fetch relevant data based on intent
    data = await fetch_telemetry_data(
        intent_data,
        auth_token,
        telemetry_service_url
    )
    
    # Generate natural language response
    response = await generate_response(intent_data, data)
    
    return QueryResult(
        answer=response["answer"],
        data=data,
        device_id=intent_data.get("device_id"),
        time_period=intent_data.get("time_period")
    )

async def extract_intent(query: str, devices: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Create a system prompt that includes device information
    devices_info = "\n".join([
        f"- {d['name']} (ID: {d['id']}, Type: {d['device_type']})"
        for d in devices
    ])
    
    system_prompt = f"""You are an AI assistant that helps users understand their smart home energy consumption data.
Available devices:
{devices_info}

Extract the following information from the user's query:
1. Device ID (if mentioned)
2. Time period (e.g., "yesterday", "last week", "today")
3. Type of information requested (e.g., consumption, comparison, peak usage)

Format your response as a JSON object."""

    # Call OpenAI API to extract intent
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    
    try:
        intent_data = json.loads(response.choices[0].message.content)
        
        # Convert time period to actual datetime range
        time_range = parse_time_period(intent_data.get("time_period", "24h"))
        intent_data["start_time"] = time_range["start"].isoformat()
        intent_data["end_time"] = time_range["end"].isoformat()
        
        return intent_data
    except Exception as e:
        return {
            "error": f"Failed to parse intent: {str(e)}",
            "time_period": "24h"  # Default to last 24 hours
        }

def parse_time_period(period: str) -> Dict[str, datetime]:
    now = datetime.utcnow()
    
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return {"start": start, "end": now}
    
    elif period == "yesterday":
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start = end - timedelta(days=1)
        return {"start": start, "end": end}
    
    elif period == "last week":
        start = now - timedelta(days=7)
        return {"start": start, "end": now}
    
    elif period == "last month":
        start = now - timedelta(days=30)
        return {"start": start, "end": now}
    
    else:  # Default to last 24 hours
        start = now - timedelta(hours=24)
        return {"start": start, "end": now}

async def fetch_telemetry_data(
    intent_data: Dict[str, Any],
    auth_token: str,
    telemetry_service_url: str
) -> Dict[str, Any]:
    device_id = intent_data.get("device_id")
    if not device_id:
        return {"error": "No device specified"}
    
    async with httpx.AsyncClient() as client:
        # Get device stats
        response = await client.get(
            f"{telemetry_service_url}/api/telemetry/{device_id}/stats",
            params={"period": intent_data.get("time_period", "24h")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if response.status_code != 200:
            return {"error": "Failed to fetch device statistics"}
        
        stats = response.json()
        
        # Get detailed telemetry data
        response = await client.get(
            f"{telemetry_service_url}/api/telemetry/{device_id}",
            params={
                "start_time": intent_data.get("start_time"),
                "end_time": intent_data.get("end_time")
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if response.status_code != 200:
            return {"error": "Failed to fetch telemetry data"}
        
        telemetry = response.json()
        
        return {
            "stats": stats,
            "telemetry": telemetry
        }

async def generate_response(
    intent_data: Dict[str, Any],
    data: Dict[str, Any]
) -> Dict[str, str]:
    if "error" in data:
        return {
            "answer": f"I encountered an error: {data['error']}",
            "data": data
        }
    
    stats = data.get("stats", {})
    
    # Create a natural language response based on the data
    system_prompt = """You are an AI assistant that helps users understand their smart home energy consumption data.
Generate a clear, concise response that answers the user's query about their energy usage.
Include relevant statistics and insights from the provided data."""

    context = f"""
Intent: {json.dumps(intent_data, indent=2)}
Data: {json.dumps(stats, indent=2)}
"""

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
    )
    
    return {
        "answer": response.choices[0].message.content,
        "data": data
    } 