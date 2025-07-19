import React, { useState, useEffect } from 'react';
import { 
  Smartphone, 
  Activity, 
  AlertTriangle, 
  TrendingUp,
  MapPin,
  Battery,
  Thermometer,
  Signal
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import api from '../services/api';
import { useWebSocket } from '../context/WebSocketContext';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentTelemetry, setRecentTelemetry] = useState([]);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const { lastMessage } = useWebSocket();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (lastMessage?.type === 'telemetry') {
      // Update real-time data
      setRecentTelemetry(prev => [lastMessage.data, ...prev.slice(0, 19)]);
    }
  }, [lastMessage]);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, telemetryRes, devicesRes] = await Promise.all([
        api.get('/admin/stats'),
        api.get('/telemetry?limit=20'),
        api.get('/devices?limit=10')
      ]);

      setStats(statsRes.data);
      setRecentTelemetry(telemetryRes.data);
      setDevices(devicesRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const chartData = recentTelemetry.slice(0, 10).reverse().map((item, index) => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    temperature: item.temperature || 0,
    battery: item.battery || 0,
    signal: Math.abs(item.signal_strength || -50)
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Smartphone className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Devices</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.devices?.total || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Online Devices</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.devices?.online || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Anomalies</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.unresolved_anomalies || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Data Points (24h)</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.telemetry_24h || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Real-time Telemetry</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="temperature" stroke="#ef4444" name="Temperature (°C)" />
              <Line type="monotone" dataKey="battery" stroke="#22c55e" name="Battery (%)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Device Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { name: 'Online', value: stats?.devices?.online || 0, fill: '#22c55e' },
              { name: 'Offline', value: stats?.devices?.offline || 0, fill: '#ef4444' },
              { name: 'Warning', value: stats?.devices?.warning || 0, fill: '#f59e0b' }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Devices */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Devices</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {devices.slice(0, 6).map((device) => (
              <div key={device.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{device.name}</h4>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    device.status === 'online' ? 'bg-green-100 text-green-800' :
                    device.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {device.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">ID: {device.device_id}</p>
                {device.lat && device.lng && (
                  <div className="flex items-center text-sm text-gray-500">
                    <MapPin className="h-4 w-4 mr-1" />
                    {device.lat.toFixed(4)}, {device.lng.toFixed(4)}
                  </div>
                )}
                {device.last_seen && (
                  <p className="text-xs text-gray-400 mt-2">
                    Last seen: {new Date(device.last_seen).toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;