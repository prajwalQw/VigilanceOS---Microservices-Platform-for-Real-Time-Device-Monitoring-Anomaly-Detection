import React, { createContext, useContext, useEffect, useState } from 'react';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    const wsUrl = process.env.NODE_ENV === 'production' 
      ? `wss://${window.location.host}/ws/telemetry`
      : 'ws://localhost:8000/ws/telemetry';

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setSocket(null);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  // Send heartbeat every 30 seconds
  useEffect(() => {
    if (socket && isConnected) {
      const interval = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send('heartbeat');
        }
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [socket, isConnected]);

  const value = {
    socket,
    isConnected,
    lastMessage
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};