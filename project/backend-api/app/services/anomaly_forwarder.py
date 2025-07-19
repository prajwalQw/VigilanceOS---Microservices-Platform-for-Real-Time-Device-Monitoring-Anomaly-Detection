import asyncio
import aiohttp
import json
from sqlalchemy.orm import Session
from app.models.telemetry import Anomaly
from app.models.device import Device
from app.routes.websocket import broadcast_anomaly
import os

ANOMALY_DETECTOR_URL = os.getenv("ANOMALY_DETECTOR_URL", "http://localhost:8001")

async def check_anomaly(telemetry_data: dict, db: Session):
    """Forward telemetry data to anomaly detection service"""
    try:
        # Simple threshold-based anomaly detection (fallback)
        device = db.query(Device).filter(Device.device_id == telemetry_data["device_id"]).first()
        if not device or not device.threshold_config:
            return
        
        thresholds = device.threshold_config
        anomalies_detected = []
        
        # Check temperature
        if "temperature" in telemetry_data and "temperature" in thresholds:
            temp = telemetry_data["temperature"]
            if temp > thresholds["temperature"]["max"]:
                anomalies_detected.append({
                    "type": "HIGH_TEMPERATURE",
                    "reason": f"Temperature {temp}°C exceeds threshold {thresholds['temperature']['max']}°C",
                    "severity": "high"
                })
            elif temp < thresholds["temperature"]["min"]:
                anomalies_detected.append({
                    "type": "LOW_TEMPERATURE",
                    "reason": f"Temperature {temp}°C below threshold {thresholds['temperature']['min']}°C",
                    "severity": "medium"
                })
        
        # Check battery
        if "battery" in telemetry_data and "battery" in thresholds:
            battery = telemetry_data["battery"]
            if battery < thresholds["battery"]["min"]:
                anomalies_detected.append({
                    "type": "LOW_BATTERY",
                    "reason": f"Battery {battery}% below threshold {thresholds['battery']['min']}%",
                    "severity": "high" if battery < 10 else "medium"
                })
        
        # Check signal strength
        if "signal_strength" in telemetry_data and "signal_strength" in thresholds:
            signal = telemetry_data["signal_strength"]
            if signal < thresholds["signal_strength"]["min"]:
                anomalies_detected.append({
                    "type": "WEAK_SIGNAL",
                    "reason": f"Signal strength {signal}dBm below threshold {thresholds['signal_strength']['min']}dBm",
                    "severity": "medium"
                })
        
        # Save anomalies to database
        for anomaly_data in anomalies_detected:
            anomaly = Anomaly(
                device_id=telemetry_data["device_id"],
                anomaly_type=anomaly_data["type"],
                reason=anomaly_data["reason"],
                severity=anomaly_data["severity"],
                resolved="false"
            )
            db.add(anomaly)
            db.commit()
            
            # Broadcast anomaly to WebSocket clients
            await broadcast_anomaly({
                "device_id": telemetry_data["device_id"],
                "type": anomaly_data["type"],
                "reason": anomaly_data["reason"],
                "severity": anomaly_data["severity"],
                "timestamp": anomaly.timestamp.isoformat()
            })
    
    except Exception as e:
        print(f"Error in anomaly detection: {e}")

async def call_ml_anomaly_detector(telemetry_data: dict):
    """Call external ML anomaly detection service"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ANOMALY_DETECTOR_URL}/predict",
                json=telemetry_data,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("is_anomaly", False), result.get("confidence", 0.0)
    except Exception as e:
        print(f"ML anomaly detector unavailable: {e}")
    
    return False, 0.0