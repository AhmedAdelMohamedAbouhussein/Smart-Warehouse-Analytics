import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import DashboardPage from './pages/DashboardPage';
import MapPage from './pages/WarehouseMapPage';
import OrdersPage from './pages/OrdersPage';
import InventoryPage from './pages/InventoryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AlgorithmComparisonPage from './pages/AlgorithmComparisonPage';
import { useWebSocket } from './hooks/useWebSocket';

const App: React.FC = () => {
  // Initialize WebSocket connection
  useWebSocket();

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/algorithms" element={<AlgorithmComparisonPage />} />
          <Route path="/settings" element={<div className="glass-card p-12 text-center text-slate-400">Settings module coming soon</div>} />
          <Route path="*" element={<div className="glass-card p-12 text-center text-slate-400">Page not found</div>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
