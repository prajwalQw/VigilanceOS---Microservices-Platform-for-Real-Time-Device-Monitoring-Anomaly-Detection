import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Smartphone, 
  AlertTriangle, 
  User, 
  FileText,
  Shield
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/devices', icon: Smartphone, label: 'Devices' },
    { to: '/anomalies', icon: AlertTriangle, label: 'Anomalies' },
    { to: '/audit-logs', icon: FileText, label: 'Audit Logs' },
    { to: '/profile', icon: User, label: 'Profile' },
  ];

  return (
    <div className="bg-gray-900 text-white w-64 min-h-screen p-4">
      <div className="flex items-center space-x-2 mb-8">
        <Shield className="h-8 w-8 text-blue-400" />
        <h1 className="text-xl font-bold">VigilanceOS</h1>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;