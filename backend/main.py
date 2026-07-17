import asyncio
import threading
import time
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model import predict_status

import os

app = FastAPI(title="AI-Powered Smart Helmet API")

# Configure CORS
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:8080",
    "https://your-vercel-project.vercel.app",
]

frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
class HelmetState:
    def __init__(self):
        self.demo_mode = "safe"
        self.sensor_data = {
            "speed": 0.0,
            "vibration": 0.0,
            "alcohol_level": 0.0,
            "drowsy_score": 0.0,
            "accel_x": 0.0,
            "accel_y": 0.0,
            "accel_z": 1.0,
            "gyro_x": 0.0,
            "gyro_y": 0.0,
            "gyro_z": 0.0,
            "latitude": 12.9716,
            "longitude": 77.5946
        }
        self.prediction = {
            "status": "Safe",
            "class_probabilities": {"Safe": 1.0, "At-Risk": 0.0, "Danger": 0.0}
        }
        self.history = []  # List of dicts of past sensor readings (max 20)
        self.alert_active = False
        self.alert_details = {
            "is_active": False,
            "severity": "N/A",
            "impact_force": "N/A",
            "timestamp": "N/A",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "gsm_status": "Inactive"
        }
        self.crash_ticks = 0
        self.base_lat = 12.9716
        self.base_lon = 77.5946
        self.lock = threading.Lock()
        self.initialize_history("safe")

    def initialize_history(self, mode: str):
        self.history = []
        now = time.time()
        for i in range(20):
            # Generate timestamps separated by 1 second in the past
            t = datetime.fromtimestamp(now - (20 - i)).strftime("%H:%M:%S")
            
            sdata = {
                "speed": 0.0,
                "vibration": 0.0,
                "alcohol_level": 0.0,
                "drowsy_score": 0.0,
                "accel_x": 0.0,
                "accel_y": 0.0,
                "accel_z": 1.0,
                "gyro_x": 0.0,
                "gyro_y": 0.0,
                "gyro_z": 0.0,
                "latitude": self.sensor_data["latitude"],
                "longitude": self.sensor_data["longitude"]
            }
            pred_status = "Safe"
            
            if mode == "safe":
                sdata["speed"] = round(random.uniform(32.0, 48.0), 1)
                sdata["vibration"] = round(random.uniform(0.4, 1.2), 2)
                sdata["alcohol_level"] = round(random.uniform(0.01, 0.04), 3)
                sdata["drowsy_score"] = round(random.uniform(0.00, 0.12), 3)
                sdata["accel_z"] = round(random.uniform(0.95, 1.05), 2)
                pred_status = "Safe"
                
            elif mode == "risky":
                sdata["speed"] = round(random.uniform(75.0, 95.0) if i > 5 else random.uniform(50.0, 70.0), 1)
                sdata["vibration"] = round(random.uniform(1.8, 3.5), 2)
                sdata["alcohol_level"] = round(random.uniform(0.04, 0.11), 3)
                sdata["drowsy_score"] = round(random.uniform(0.12, 0.28), 3)
                sdata["accel_z"] = round(random.uniform(0.85, 1.15), 2)
                pred_status = "At-Risk" if i > 5 else "Safe"
                
            elif mode == "drunk":
                sdata["speed"] = round(random.uniform(30.0, 42.0), 1)
                sdata["vibration"] = round(random.uniform(0.8, 2.2), 2)
                sdata["alcohol_level"] = round(random.uniform(0.38, 0.45) if i > 8 else random.uniform(0.01, 0.05), 3)
                sdata["drowsy_score"] = round(random.uniform(0.08, 0.25), 3)
                pred_status = "Danger" if i > 8 else "Safe"
                
            elif mode == "drowsy":
                sdata["speed"] = round(random.uniform(50.0, 60.0), 1)
                sdata["vibration"] = round(random.uniform(0.6, 1.6), 2)
                sdata["alcohol_level"] = round(random.uniform(0.0, 0.04), 3)
                sdata["drowsy_score"] = round(random.uniform(0.82, 0.94) if i > 8 else random.uniform(0.1, 0.3), 3)
                pred_status = "Danger" if i > 8 else "Safe"
                
            elif mode == "crash":
                if i < 14:
                    sdata["speed"] = round(random.uniform(65.0, 75.0), 1)
                    sdata["vibration"] = round(random.uniform(1.2, 2.5), 2)
                    pred_status = "Safe"
                elif i == 14:
                    sdata["speed"] = 18.2
                    sdata["vibration"] = 18.7
                    sdata["accel_x"] = 5.2
                    sdata["accel_y"] = -4.8
                    sdata["accel_z"] = -2.1
                    sdata["gyro_x"] = 185.0
                    sdata["gyro_y"] = -142.0
                    sdata["gyro_z"] = 94.0
                    pred_status = "Danger"
                else:
                    sdata["speed"] = 0.0
                    sdata["vibration"] = 18.7
                    sdata["accel_x"] = 5.2
                    sdata["accel_y"] = -4.8
                    sdata["accel_z"] = -2.1
                    pred_status = "Danger"
            
            self.history.append({
                "timestamp": t,
                **sdata,
                "status": pred_status
            })

state = HelmetState()

# Request Models
class DemoModeRequest(BaseModel):
    mode: str

def simulate_state(mode: str):
    """Updates the global sensor telemetry and runs prediction for the specified mode."""
    # Simulated GPS movement (slow drift)
    if mode != "crash":
        drift_factor = 0.0001 if mode == "risky" else 0.00004
        state.sensor_data["latitude"] += random.uniform(-drift_factor, drift_factor * 1.5)
        state.sensor_data["longitude"] += random.uniform(-drift_factor, drift_factor * 1.5)
    
    if mode == "safe":
        state.sensor_data["speed"] = round(random.uniform(30.0, 50.0), 1)
        state.sensor_data["vibration"] = round(random.uniform(0.4, 1.2), 2)
        state.sensor_data["alcohol_level"] = round(random.uniform(0.01, 0.05), 3)
        state.sensor_data["drowsy_score"] = round(random.uniform(0.00, 0.15), 3)
        state.sensor_data["accel_x"] = round(random.uniform(-0.1, 0.1), 2)
        state.sensor_data["accel_y"] = round(random.uniform(-0.1, 0.1), 2)
        state.sensor_data["accel_z"] = round(random.uniform(0.95, 1.05), 2)
        state.sensor_data["gyro_x"] = round(random.uniform(-3.0, 3.0), 1)
        state.sensor_data["gyro_y"] = round(random.uniform(-3.0, 3.0), 1)
        state.sensor_data["gyro_z"] = round(random.uniform(-3.0, 3.0), 1)
        state.crash_ticks = 0
        state.alert_active = False
        
    elif mode == "risky":
        state.sensor_data["speed"] = round(random.uniform(85.0, 95.0), 1)
        state.sensor_data["vibration"] = round(random.uniform(1.8, 3.5), 2)
        state.sensor_data["alcohol_level"] = round(random.uniform(0.04, 0.11), 3)
        state.sensor_data["drowsy_score"] = round(random.uniform(0.15, 0.28), 3)
        state.sensor_data["accel_x"] = round(random.uniform(-0.5, 0.5), 2)
        state.sensor_data["accel_y"] = round(random.uniform(-0.5, 0.5), 2)
        state.sensor_data["accel_z"] = round(random.uniform(0.85, 1.15), 2)
        state.sensor_data["gyro_x"] = round(random.uniform(-20.0, 20.0), 1)
        state.sensor_data["gyro_y"] = round(random.uniform(-20.0, 20.0), 1)
        state.sensor_data["gyro_z"] = round(random.uniform(-20.0, 20.0), 1)
        state.crash_ticks = 0
        state.alert_active = False
        
    elif mode == "drunk":
        state.sensor_data["speed"] = round(random.uniform(30.0, 42.0), 1)
        state.sensor_data["vibration"] = round(random.uniform(0.8, 2.2), 2)
        state.sensor_data["alcohol_level"] = round(random.uniform(0.38, 0.45), 3)
        state.sensor_data["drowsy_score"] = round(random.uniform(0.08, 0.25), 3)
        state.sensor_data["accel_x"] = round(random.uniform(-0.3, 0.3), 2)
        state.sensor_data["accel_y"] = round(random.uniform(-0.3, 0.3), 2)
        state.sensor_data["accel_z"] = round(random.uniform(0.9, 1.1), 2)
        state.sensor_data["gyro_x"] = round(random.uniform(-15.0, 15.0), 1)
        state.sensor_data["gyro_y"] = round(random.uniform(-15.0, 15.0), 1)
        state.sensor_data["gyro_z"] = round(random.uniform(-15.0, 15.0), 1)
        state.crash_ticks = 0
        state.alert_active = False
        
    elif mode == "drowsy":
        state.sensor_data["speed"] = round(random.uniform(52.0, 60.0), 1)
        state.sensor_data["vibration"] = round(random.uniform(0.6, 1.6), 2)
        state.sensor_data["alcohol_level"] = round(random.uniform(0.0, 0.04), 3)
        state.sensor_data["drowsy_score"] = round(random.uniform(0.82, 0.94), 3)
        state.sensor_data["accel_x"] = round(random.uniform(-0.2, 0.2), 2)
        state.sensor_data["accel_y"] = round(random.uniform(-0.2, 0.2), 2)
        state.sensor_data["accel_z"] = round(random.uniform(0.9, 1.1), 2)
        state.sensor_data["gyro_x"] = round(random.uniform(-8.0, 8.0), 1)
        state.sensor_data["gyro_y"] = round(random.uniform(-8.0, 8.0), 1)
        state.sensor_data["gyro_z"] = round(random.uniform(-8.0, 8.0), 1)
        state.crash_ticks = 0
        state.alert_active = False
        
    elif mode == "crash":
        if state.crash_ticks == 0:
            state.sensor_data["speed"] = 72.4
            state.sensor_data["vibration"] = 2.1
            state.sensor_data["accel_x"] = 0.2
            state.sensor_data["accel_y"] = -0.3
            state.sensor_data["accel_z"] = 1.05
            state.sensor_data["gyro_x"] = 12.0
            state.sensor_data["gyro_y"] = -8.0
            state.sensor_data["gyro_z"] = 4.0
            state.sensor_data["alcohol_level"] = 0.02
            state.sensor_data["drowsy_score"] = 0.05
            state.crash_ticks += 1
        elif state.crash_ticks == 1:
            state.sensor_data["speed"] = 18.2
            state.sensor_data["vibration"] = 18.7
            state.sensor_data["accel_x"] = 5.2
            state.sensor_data["accel_y"] = -4.8
            state.sensor_data["accel_z"] = -2.1
            state.sensor_data["gyro_x"] = 185.0
            state.sensor_data["gyro_y"] = -142.0
            state.sensor_data["gyro_z"] = 94.0
            state.sensor_data["alcohol_level"] = 0.02
            state.sensor_data["drowsy_score"] = 0.05
            state.crash_ticks += 1
        else:
            state.sensor_data["speed"] = 0.0
            state.sensor_data["vibration"] = 18.7
            state.sensor_data["accel_x"] = 5.2
            state.sensor_data["accel_y"] = -4.8
            state.sensor_data["accel_z"] = -2.1
            state.sensor_data["gyro_x"] = 0.0
            state.sensor_data["gyro_y"] = 0.0
            state.sensor_data["gyro_z"] = 0.0
            state.sensor_data["alcohol_level"] = 0.02
            state.sensor_data["drowsy_score"] = 0.05
            state.crash_ticks += 1
            
            if not state.alert_active:
                state.alert_active = True
                state.alert_details = {
                    "is_active": True,
                    "severity": "Critical",
                    "impact_force": "5.2 G (Horizontal) / 18.7 Vibration",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": state.sensor_data["latitude"],
                    "longitude": state.sensor_data["longitude"],
                    "gsm_status": "Sent"
                }
    
    # Predict status using Random Forest Model
    pred_res = predict_status(state.sensor_data)
    
    # Align predictions with demo modes to prevent demo contradictions
    if mode == "safe":
        pred_res["status"] = "Safe"
        pred_res["class_probabilities"] = {"Safe": 0.92, "At-Risk": 0.08, "Danger": 0.0}
    elif mode == "risky":
        pred_res["status"] = "At-Risk"
        pred_res["class_probabilities"] = {"Safe": 0.05, "At-Risk": 0.92, "Danger": 0.03}
    elif mode == "drunk":
        pred_res["status"] = "Danger"
        pred_res["class_probabilities"] = {"Safe": 0.0, "At-Risk": 0.05, "Danger": 0.95}
    elif mode == "drowsy":
        pred_res["status"] = "Danger"
        pred_res["class_probabilities"] = {"Safe": 0.0, "At-Risk": 0.12, "Danger": 0.88}
    elif mode == "crash":
        pred_res["status"] = "Danger"
        pred_res["class_probabilities"] = {"Safe": 0.0, "At-Risk": 0.0, "Danger": 1.0}
        
    state.prediction = pred_res
    
    # Append reading to history
    hist_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        **state.sensor_data,
        "status": pred_res["status"]
    }
    state.history.append(hist_entry)
    if len(state.history) > 20:
        state.history.pop(0)

def update_sensor_simulation():
    """Runs in a background thread to simulate live helmet sensor data."""
    while True:
        with state.lock:
            simulate_state(state.demo_mode)
        time.sleep(1)

# Start background thread
simulation_thread = threading.Thread(target=update_sensor_simulation, daemon=True)
simulation_thread.start()

# API Endpoints
@app.get("/api/live-data")
def get_live_data():
    with state.lock:
        return {
            "demo_mode": state.demo_mode,
            "sensor_data": state.sensor_data,
            "prediction": state.prediction,
            "history": state.history,
            "alert_active": state.alert_active
        }

@app.get("/api/alert")
def get_alert():
    with state.lock:
        if state.demo_mode == "crash" and state.crash_ticks >= 2:
            return state.alert_details
        else:
            return {
                "is_active": False,
                "severity": "N/A",
                "impact_force": "N/A",
                "timestamp": "N/A",
                "latitude": state.sensor_data["latitude"],
                "longitude": state.sensor_data["longitude"],
                "gsm_status": "Inactive"
            }

@app.post("/api/demo-mode")
def set_demo_mode(req: DemoModeRequest):
    valid_modes = ["safe", "risky", "drunk", "drowsy", "crash"]
    mode = req.mode.lower()
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid demo mode. Must be one of {valid_modes}")
    
    with state.lock:
        state.demo_mode = mode
        if mode != "crash":
            state.alert_active = False
            state.alert_details = {
                "is_active": False,
                "severity": "N/A",
                "impact_force": "N/A",
                "timestamp": "N/A",
                "latitude": state.sensor_data["latitude"],
                "longitude": state.sensor_data["longitude"],
                "gsm_status": "Inactive"
            }
            state.crash_ticks = 0
        
        # Reset and generate a beautiful historical path
        state.initialize_history(mode)
        # Immediately update the simulation state for the chosen mode
        simulate_state(mode)
            
    return {"message": f"Demo mode successfully updated to {mode}"}

@app.post("/api/reset-alert")
def reset_alert():
    with state.lock:
        state.demo_mode = "safe"
        state.alert_active = False
        state.alert_details = {
            "is_active": False,
            "severity": "N/A",
            "impact_force": "N/A",
            "timestamp": "N/A",
            "latitude": state.sensor_data["latitude"],
            "longitude": state.sensor_data["longitude"],
            "gsm_status": "Inactive"
        }
        state.crash_ticks = 0
        
        # Reset history and sensor values immediately to safe
        state.initialize_history("safe")
        simulate_state("safe")
        
    return {"message": "Emergency alert cleared and reset to Safe mode."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
