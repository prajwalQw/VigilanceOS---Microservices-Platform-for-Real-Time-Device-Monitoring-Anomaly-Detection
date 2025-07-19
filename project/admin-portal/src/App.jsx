import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './pages/Dashboard';
import Devices from './pages/Devices';
import Anomalies from './pages/Anomalies';
import Profile from './pages/Profile';
import AuditLogs from './pages/AuditLogs';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { AuthProvider, useAuth } from './context/AuthContext';
import { WebSocketProvider } from './context/WebSocketContext';
import './App.css';

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <WebSocketProvider>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/devices" element={<Devices />} />
              <Route path="/anomalies" element={<Anomalies />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </WebSocketProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;