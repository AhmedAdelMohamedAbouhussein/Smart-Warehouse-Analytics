import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-[#0f172a]">
      <Sidebar />
      <main className="pl-64 flex flex-col h-screen overflow-hidden">
        <Header />
        <div className="flex-1 p-6 relative overflow-y-auto scrollbar-thin bg-[#0f172a]">
          <div className="max-w-[1600px] mx-auto h-full flex flex-col">
            {children}
          </div>
        </div>
      </main>
      
      {/* Global Background Glows */}
      <div className="fixed top-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-900/10 blur-[120px] rounded-full -z-10" />
      <div className="fixed bottom-[-10%] left-[20%] w-[30%] h-[30%] bg-blue-900/10 blur-[100px] rounded-full -z-10" />
    </div>
  );
};

export default Layout;
