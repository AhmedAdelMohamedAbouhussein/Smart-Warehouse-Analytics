import { useEffect, useRef, useCallback } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { SimulationState } from '../types';

const getWsUrl = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.hostname;
  
  // If we're on Vite's default port, try to connect to the backend port 8000
  // otherwise use the current host (works for production or proxied setups)
  const port = window.location.port === '5173' ? '8000' : window.location.port;
  return `${protocol}//${host}${port ? `:${port}` : ''}/ws`;
};

const WS_URL = getWsUrl();

export const useWebSocket = () => {
  const socketRef = useRef<WebSocket | null>(null);
  const updateFromTick = useSimulationStore((state) => state.updateFromTick);
  const setInitialState = useSimulationStore((state) => state.setInitialState);

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    const socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      console.log('[WS] Connected to simulation server');
      const heartbeat = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
      (socket as any)._heartbeat = heartbeat;
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'system_init' && data.state) {
          setInitialState(data.state);
        } else if (data.tick !== undefined) {
          updateFromTick(data as SimulationState);
        }
      } catch (error) {
        console.error('[WS] Error parsing message:', error);
      }
    };

    socket.onclose = () => {
      console.log('[WS] Disconnected. Reconnecting in 3s...');
      if ((socket as any)._heartbeat) clearInterval((socket as any)._heartbeat);
      setTimeout(connect, 3000);
    };

    socket.onerror = (error) => {
      console.error('[WS] WebSocket error:', error);
      socket.close();
    };

    socketRef.current = socket;
  }, [updateFromTick, setInitialState]);

  useEffect(() => {
    connect();
    return () => {
      socketRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((message: any) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);

  return { sendMessage };
};
