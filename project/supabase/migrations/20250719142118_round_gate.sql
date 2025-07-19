-- VigilanceOS Database Schema
-- PostgreSQL initialization script

-- Create database if not exists (handled by Docker)
-- CREATE DATABASE IF NOT EXISTS telemetry;

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'operator', 'viewer');
CREATE TYPE device_status AS ENUM ('online', 'offline', 'warning', 'error');

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'viewer',
    profile_pic VARCHAR(500),
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Devices table
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    lat FLOAT,
    lng FLOAT,
    status device_status DEFAULT 'offline',
    last_seen TIMESTAMPTZ,
    threshold_config JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Telemetry table
CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES devices(device_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    temperature FLOAT,
    battery FLOAT,
    signal_strength FLOAT,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_usage FLOAT
);

-- Anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES devices(device_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    anomaly_type VARCHAR(50) NOT NULL,
    reason VARCHAR(500),
    severity VARCHAR(20) DEFAULT 'medium',
    resolved VARCHAR(10) DEFAULT 'false'
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    target_id VARCHAR(50),
    details VARCHAR(500)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_telemetry_device_id ON telemetry(device_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_device_id ON anomalies(device_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_id ON audit_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);

-- Insert default admin user (password: admin123)
INSERT INTO admins (name, email, hashed_password, role) 
VALUES (
    'System Administrator',
    'admin@vigilance.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9w5KS', -- admin123
    'admin'
) ON CONFLICT (email) DO NOTHING;

-- Insert sample devices
INSERT INTO devices (name, device_id, lat, lng, status, threshold_config) VALUES
('Sensor Alpha', 'DEVICE_001', 37.7749, -122.4194, 'online', '{"temperature": {"min": 0, "max": 85}, "battery": {"min": 20}, "signal_strength": {"min": -80}}'),
('Sensor Beta', 'DEVICE_002', 40.7128, -74.0060, 'online', '{"temperature": {"min": -10, "max": 90}, "battery": {"min": 15}, "signal_strength": {"min": -85}}'),
('Sensor Gamma', 'DEVICE_003', 34.0522, -118.2437, 'warning', '{"temperature": {"min": 5, "max": 80}, "battery": {"min": 25}, "signal_strength": {"min": -75}}'),
('Sensor Delta', 'DEVICE_004', 41.8781, -87.6298, 'offline', '{"temperature": {"min": -5, "max": 75}, "battery": {"min": 30}, "signal_strength": {"min": -70}}'),
('Sensor Epsilon', 'DEVICE_005', 29.7604, -95.3698, 'online', '{"temperature": {"min": 10, "max": 95}, "battery": {"min": 20}, "signal_strength": {"min": -80}}')
ON CONFLICT (device_id) DO NOTHING;

-- Insert sample telemetry data
INSERT INTO telemetry (device_id, temperature, battery, signal_strength, cpu_usage, memory_usage, disk_usage) VALUES
('DEVICE_001', 23.5, 85.2, -65.0, 45.2, 62.1, 34.8),
('DEVICE_002', 21.8, 92.1, -58.5, 38.7, 55.3, 28.9),
('DEVICE_003', 89.2, 15.8, -78.2, 78.9, 89.4, 67.2),
('DEVICE_004', 19.4, 67.3, -72.1, 52.1, 71.8, 45.6),
('DEVICE_005', 26.7, 88.9, -61.3, 41.5, 58.7, 31.2);

-- Insert sample anomalies
INSERT INTO anomalies (device_id, anomaly_type, reason, severity, resolved) VALUES
('DEVICE_003', 'HIGH_TEMPERATURE', 'Temperature 89.2°C exceeds threshold 80°C', 'high', 'false'),
('DEVICE_003', 'LOW_BATTERY', 'Battery 15.8% below threshold 25%', 'medium', 'false'),
('DEVICE_004', 'WEAK_SIGNAL', 'Signal strength -72.1dBm below threshold -70dBm', 'medium', 'true');

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_admins_updated_at BEFORE UPDATE ON admins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();