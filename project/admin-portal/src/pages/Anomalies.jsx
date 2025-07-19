import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Filter,
  Search
} from 'lucide-react';
import api from '../services/api';

const Anomalies = () => {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [resolvedFilter, setResolvedFilter] = useState('all');

  useEffect(() => {
    fetchAnomalies();
  }, []);

  const fetchAnomalies = async () => {
    try {
      const response = await api.get('/telemetry/anomalies/');
      setAnomalies(response.data);
    } catch (error) {
      console.error('Failed to fetch anomalies:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveAnomaly = async (anomalyId) => {
    try {
      await api.put(`/telemetry/anomalies/${anomalyId}/resolve`);
      setAnomalies(prev => 
        prev.map(anomaly => 
          anomaly.id === anomalyId 
            ? { ...anomaly, resolved: 'true' }
            : anomaly
        )
      );
    } catch (error) {
      console.error('Failed to resolve anomaly:', error);
    }
  };

  const filteredAnomalies = anomalies.filter(anomaly => {
    const matchesSearch = anomaly.device_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         anomaly.anomaly_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === 'all' || anomaly.severity === severityFilter;
    const matchesResolved = resolvedFilter === 'all' || 
                           (resolvedFilter === 'resolved' && anomaly.resolved === 'true') ||
                           (resolvedFilter === 'unresolved' && anomaly.resolved === 'false');
    return matchesSearch && matchesSeverity && matchesResolved;
  });

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="h-4 w-4" />;
      case 'medium': return <Clock className="h-4 w-4" />;
      case 'low': return <AlertTriangle className="h-4 w-4" />;
      default: return <AlertTriangle className="h-4 w-4" />;
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
        <h1 className="text-2xl font-bold text-gray-900">Anomalies</h1>
        <div className="text-sm text-gray-500">
          {filteredAnomalies.filter(a => a.resolved === 'false').length} unresolved
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search anomalies..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Severity</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <select
              value={resolvedFilter}
              onChange={(e) => setResolvedFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="unresolved">Unresolved</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Anomalies List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="divide-y divide-gray-200">
          {filteredAnomalies.map((anomaly) => (
            <div key={anomaly.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`px-2 py-1 text-xs rounded-full flex items-center space-x-1 ${getSeverityColor(anomaly.severity)}`}>
                      {getSeverityIcon(anomaly.severity)}
                      <span className="capitalize">{anomaly.severity}</span>
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {anomaly.anomaly_type.replace(/_/g, ' ')}
                    </span>
                    {anomaly.resolved === 'true' && (
                      <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 flex items-center space-x-1">
                        <CheckCircle className="h-3 w-3" />
                        <span>Resolved</span>
                      </span>
                    )}
                  </div>
                  
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Device:</span> {anomaly.device_id}
                    </p>
                    {anomaly.reason && (
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Reason:</span> {anomaly.reason}
                      </p>
                    )}
                    <p className="text-xs text-gray-400">
                      {new Date(anomaly.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {anomaly.resolved === 'false' && (
                    <button
                      onClick={() => resolveAnomaly(anomaly.id)}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                    >
                      Resolve
                    </button>
                  )}
                  <button className="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200 transition-colors">
                    Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {filteredAnomalies.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <AlertTriangle className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No anomalies found</h3>
          <p className="text-gray-600">
            {searchTerm || severityFilter !== 'all' || resolvedFilter !== 'all'
              ? 'Try adjusting your search or filter criteria.'
              : 'No anomalies detected. Your devices are running smoothly!'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default Anomalies;