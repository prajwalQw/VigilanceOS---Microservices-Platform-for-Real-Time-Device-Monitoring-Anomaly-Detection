import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  MapPin, 
  Activity, 
  AlertCircle,
  Edit,
  Trash2
} from 'lucide-react';
import api from '../services/api';

const Devices = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await api.get('/devices');
      setDevices(response.data);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredDevices = devices.filter(device => {
    const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         device.device_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || device.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'bg-green-100 text-green-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online': return <Activity className="h-4 w-4" />;
      case 'warning': return <AlertCircle className="h-4 w-4" />;
      case 'error': return <AlertCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Devices</h1>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Add Device</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search devices..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
        </div>
      </div>

      {/* Devices Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDevices.map((device) => (
          <div key={device.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{device.name}</h3>
                <div className="flex items-center space-x-2">
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-red-600">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status</span>
                  <span className={`px-2 py-1 text-xs rounded-full flex items-center space-x-1 ${getStatusColor(device.status)}`}>
                    {getStatusIcon(device.status)}
                    <span className="capitalize">{device.status}</span>
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Device ID</span>
                  <span className="text-sm font-mono text-gray-900">{device.device_id}</span>
                </div>

                {device.lat && device.lng && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Location</span>
                    <div className="flex items-center space-x-1 text-sm text-gray-900">
                      <MapPin className="h-3 w-3" />
                      <span>{device.lat.toFixed(4)}, {device.lng.toFixed(4)}</span>
                    </div>
                  </div>
                )}

                {device.last_seen && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Last Seen</span>
                    <span className="text-sm text-gray-900">
                      {new Date(device.last_seen).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <button className="w-full bg-gray-50 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium">
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredDevices.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Smartphone className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No devices found</h3>
          <p className="text-gray-600">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search or filter criteria.'
              : 'Get started by adding your first device.'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default Devices;