import React from 'react';
import { Bell, LogOut, Wifi, WifiOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useWebSocket } from '../context/WebSocketContext';

const Header = () => {
  const { user, logout } = useAuth();
  const { isConnected } = useWebSocket();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-800">
            Welcome back, {user?.name}
          </h2>
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <div className="flex items-center space-x-1 text-green-600">
                <Wifi className="h-4 w-4" />
                <span className="text-sm">Connected</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1 text-red-600">
                <WifiOff className="h-4 w-4" />
                <span className="text-sm">Disconnected</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="h-5 w-5" />
            <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
          </button>

          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user?.name}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
            <div className="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {user?.name?.charAt(0).toUpperCase()}
              </span>
            </div>
          </div>

          <button
            onClick={logout}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;