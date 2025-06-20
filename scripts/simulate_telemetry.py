import requests
import random
import time
from datetime import datetime, timedelta
import os
import json
from typing import List, Dict

# Configuration
TELEMETRY_API_URL = os.getenv("TELEMETRY_API_URL", "http://localhost:8001")
AUTH_API_URL = os.getenv("AUTH_API_URL", "http://localhost:8000")

# Test user credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
}

# Test devices
TEST_DEVICES = [
    {"name": "Refrigerator", "device_type": "Refrigerator", "base_load": 100, "variance": 20},
    {"name": "Air Conditioner", "device_type": "Air Conditioner", "base_load": 1500, "variance": 500},
    {"name": "Washing Machine", "device_type": "Washing Machine", "base_load": 500, "variance": 200},
    {"name": "Dishwasher", "device_type": "Dishwasher", "base_load": 1200, "variance": 300},
    {"name": "Water Heater", "device_type": "Water Heater", "base_load": 4000, "variance": 1000},
]

def setup_test_user() -> str:
    """Create a test user and return the access token."""
    try:
        # Try to register the user
        response = requests.post(
            f"{AUTH_API_URL}/api/auth/register",
            json=TEST_USER
        )
    except:
        print("Failed to register user (user might already exist)")

    # Login and get token
    try:
        response = requests.post(
            f"{AUTH_API_URL}/api/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        return response.json()["access_token"]
    except Exception as e:
        print(f"Failed to login: {e}")
        raise

def setup_test_devices(token: str) -> List[Dict]:
    """Create test devices and return their IDs."""
    devices = []
    for device in TEST_DEVICES:
        try:
            response = requests.post(
                f"{TELEMETRY_API_URL}/api/devices",
                json={
                    "name": device["name"],
                    "device_type": device["device_type"]
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            device_data = response.json()
            devices.append({
                **device,
                "id": device_data["id"]
            })
        except Exception as e:
            print(f"Failed to create device {device['name']}: {e}")
    return devices

def generate_telemetry(device: Dict, timestamp: datetime) -> float:
    """Generate realistic energy consumption data for a device."""
    # Base load with random variance
    energy = device["base_load"] + random.uniform(-device["variance"], device["variance"])
    
    # Add time-based patterns
    hour = timestamp.hour
    
    # Night-time reduction for most devices
    if hour >= 23 or hour <= 5:
        energy *= 0.5
    
    # Peak hours for AC
    if device["device_type"] == "Air Conditioner" and (hour >= 12 and hour <= 18):
        energy *= 1.5
    
    # Washing machine and dishwasher typically used at specific times
    if device["device_type"] in ["Washing Machine", "Dishwasher"]:
        if hour in [7, 8, 19, 20]:  # Morning and evening usage
            energy *= 2
        else:
            energy *= 0.1  # Minimal standby power
    
    return max(0, energy)  # Ensure non-negative values

def main():
    print("Setting up test environment...")
    token = setup_test_user()
    devices = setup_test_devices(token)
    
    print(f"Created {len(devices)} test devices")
    
    # Generate 24 hours of data with 1-minute intervals
    start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    print("Generating telemetry data...")
    for minute in range(24 * 60):  # 24 hours * 60 minutes
        timestamp = start_time + timedelta(minutes=minute)
        
        for device in devices:
            try:
                energy = generate_telemetry(device, timestamp)
                
                payload = {
                    "device_id": device["id"],
                    "timestamp": timestamp.isoformat() + "Z",
                    "energy_watts": energy
                }
                
                response = requests.post(
                    f"{TELEMETRY_API_URL}/api/telemetry",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 200 and response.status_code != 201:
                    print(f"Failed to send telemetry for {device['name']}: {response.text}")
                
            except Exception as e:
                print(f"Error sending telemetry for {device['name']}: {e}")
        
        # Progress update
        if minute % 60 == 0:
            hour = minute // 60
            print(f"Generated data for hour {hour}")
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    print("Finished generating telemetry data")

if __name__ == "__main__":
    main() 