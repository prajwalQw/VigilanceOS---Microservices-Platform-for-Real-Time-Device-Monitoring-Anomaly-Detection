#!/usr/bin/env python3
"""
Device Simulator for VigilanceOS
Simulates multiple IoT devices sending telemetry data
"""

import asyncio
import aiohttp
import json
import random
import time
from datetime import datetime
import argparse

class DeviceSimulator:
    def __init__(self, api_url="http://localhost:8000", num_devices=5):
        self.api_url = api_url
        self.num_devices = num_devices
        self.devices = []
        self.running = False
        
    def generate_devices(self):
        """Generate device configurations"""
        device_names = [
            "Sensor Alpha", "Sensor Beta", "Sensor Gamma", 
            "Sensor Delta", "Sensor Epsilon", "Sensor Zeta",
            "Monitor One", "Monitor Two", "Tracker X", "Tracker Y"
        ]
        
        for i in range(self.num_devices):
            device = {
                "device_id": f"SIM_DEVICE_{i+1:03d}",
                "name": device_names[i % len(device_names)] + f" {i+1}",
                "lat": round(random.uniform(25.0, 49.0), 6),  # US coordinates
                "lng": round(random.uniform(-125.0, -66.0), 6),
                "base_temp": random.uniform(20, 30),
                "base_battery": random.uniform(70, 100),
                "base_signal": random.uniform(-80, -50),
                "anomaly_chance": 0.05  # 5% chance of anomaly per reading
            }
            self.devices.append(device)
    
    def generate_telemetry(self, device):
        """Generate realistic telemetry data for a device"""
        # Base values with some random variation
        temp_variation = random.uniform(-5, 5)
        battery_drain = random.uniform(-0.1, 0.1)
        signal_variation = random.uniform(-10, 10)
        
        # Update base values
        device["base_battery"] = max(0, min(100, device["base_battery"] + battery_drain))
        
        # Generate telemetry
        telemetry = {
            "device_id": device["device_id"],
            "temperature": round(device["base_temp"] + temp_variation, 1),
            "battery": round(device["base_battery"], 1),
            "signal_strength": round(device["base_signal"] + signal_variation, 1),
            "cpu_usage": round(random.uniform(20, 80), 1),
            "memory_usage": round(random.uniform(30, 90), 1),
            "disk_usage": round(random.uniform(20, 70), 1)
        }
        
        # Occasionally generate anomalies
        if random.random() < device["anomaly_chance"]:
            anomaly_type = random.choice(["temperature", "battery", "signal"])
            if anomaly_type == "temperature":
                telemetry["temperature"] = random.uniform(85, 120)
            elif anomaly_type == "battery":
                telemetry["battery"] = random.uniform(0, 15)
            elif anomaly_type == "signal":
                telemetry["signal_strength"] = random.uniform(-120, -100)
        
        return telemetry
    
    async def register_device(self, session, device):
        """Register a device with the API"""
        device_data = {
            "name": device["name"],
            "device_id": device["device_id"],
            "lat": device["lat"],
            "lng": device["lng"],
            "threshold_config": {
                "temperature": {"min": 0, "max": 85},
                "battery": {"min": 20},
                "signal_strength": {"min": -80}
            }
        }
        
        try:
            async with session.post(f"{self.api_url}/devices/", json=device_data) as response:
                if response.status in [200, 201]:
                    print(f"✓ Registered device: {device['device_id']}")
                elif response.status == 400:
                    print(f"⚠ Device already exists: {device['device_id']}")
                else:
                    print(f"✗ Failed to register device: {device['device_id']} (Status: {response.status})")
        except Exception as e:
            print(f"✗ Error registering device {device['device_id']}: {e}")
    
    async def send_telemetry(self, session, device):
        """Send telemetry data for a device"""
        telemetry = self.generate_telemetry(device)
        
        try:
            async with session.post(f"{self.api_url}/telemetry/", json=telemetry) as response:
                if response.status in [200, 201]:
                    print(f"📊 {device['device_id']}: T={telemetry['temperature']}°C, "
                          f"B={telemetry['battery']}%, S={telemetry['signal_strength']}dBm")
                else:
                    print(f"✗ Failed to send telemetry for {device['device_id']} (Status: {response.status})")
        except Exception as e:
            print(f"✗ Error sending telemetry for {device['device_id']}: {e}")
    
    async def device_loop(self, session, device, interval):
        """Main loop for a single device"""
        while self.running:
            await self.send_telemetry(session, device)
            await asyncio.sleep(interval + random.uniform(-1, 1))  # Add some jitter
    
    async def run(self, interval=10, register_devices=True):
        """Run the device simulator"""
        print(f"🚀 Starting VigilanceOS Device Simulator")
        print(f"📡 API URL: {self.api_url}")
        print(f"🔢 Number of devices: {self.num_devices}")
        print(f"⏱️  Telemetry interval: {interval} seconds")
        print("-" * 50)
        
        self.generate_devices()
        self.running = True
        
        async with aiohttp.ClientSession() as session:
            # Register devices if requested
            if register_devices:
                print("📝 Registering devices...")
                for device in self.devices:
                    await self.register_device(session, device)
                print("-" * 50)
            
            # Start device loops
            print("📊 Starting telemetry simulation...")
            tasks = []
            for device in self.devices:
                task = asyncio.create_task(self.device_loop(session, device, interval))
                tasks.append(task)
            
            try:
                await asyncio.gather(*tasks)
            except KeyboardInterrupt:
                print("\n🛑 Stopping simulator...")
                self.running = False
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)

def main():
    parser = argparse.ArgumentParser(description="VigilanceOS Device Simulator")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                       help="API base URL (default: http://localhost:8000)")
    parser.add_argument("--devices", type=int, default=5,
                       help="Number of devices to simulate (default: 5)")
    parser.add_argument("--interval", type=int, default=10,
                       help="Telemetry interval in seconds (default: 10)")
    parser.add_argument("--no-register", action="store_true",
                       help="Skip device registration")
    
    args = parser.parse_args()
    
    simulator = DeviceSimulator(api_url=args.api_url, num_devices=args.devices)
    
    try:
        asyncio.run(simulator.run(
            interval=args.interval,
            register_devices=not args.no_register
        ))
    except KeyboardInterrupt:
        print("\n👋 Simulator stopped by user")

if __name__ == "__main__":
    main()