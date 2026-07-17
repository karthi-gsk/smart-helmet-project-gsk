import React, { useState } from 'react';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Modules from './pages/Modules';
import { Home as HomeIcon, ShieldAlert, Cpu, HardHat } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('home');

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <Home setActiveTab={setActiveTab} />;
      case 'dashboard':
        return <Dashboard />;
      case 'modules':
        return <Modules />;
      default:
        return <Home setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <HardHat className="brand-icon pulse" />
          <span className="brand-text">Smart Helmet</span>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            <HomeIcon size={20} />
            <span>Home</span>
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <ShieldAlert size={20} />
            <span>Live Dashboard</span>
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'modules' ? 'active' : ''}`}
            onClick={() => setActiveTab('modules')}
          >
            <Cpu size={20} />
            <span>Project Modules</span>
          </button>
        </nav>
        
        <div className="sidebar-footer">
          <p className="college-text">College Mini Project</p>
          <p className="version-text">AI & IoT Prototype v1.0</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="main-header">
          <div className="header-info">
            <h1>AI-Powered Smart Helmet</h1>
            <p className="header-subtitle">Accident Prediction & Emergency Alert System</p>
          </div>
          <div className="header-badge">
            <span className="badge-dot animate-ping"></span>
            <span className="badge-text">System Live</span>
          </div>
        </header>
        
        <div className="page-wrapper">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
