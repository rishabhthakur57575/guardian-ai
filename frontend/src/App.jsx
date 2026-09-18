import React, { useState } from 'react';
import { SecurityProvider } from './context/SecurityContext';
import Navbar from './components/common/Navbar';
import HomeDashboard from './components/dashboard/HomeDashboard';
import LiveProtection from './components/live/LiveProtection';
import SecurityTimeline from './components/timeline/SecurityTimeline';
import AnalyticsView from './components/analytics/AnalyticsView';
import ScamInterventionModal from './components/intervention/ScamInterventionModal';
import ToastNotification from './components/common/ToastNotification';
import { Shield, Lock } from 'lucide-react';

function DashboardApp() {
  const [currentTab, setCurrentTab] = useState('dashboard');

  return (
    <div className="min-h-screen bg-[#060913] bg-grid-cyber text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Navigation */}
      <Navbar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 lg:px-8 pt-6">
        {currentTab === 'dashboard' && <HomeDashboard setCurrentTab={setCurrentTab} />}
        {currentTab === 'live' && <LiveProtection />}
        {currentTab === 'timeline' && <SecurityTimeline />}
        {currentTab === 'analytics' && <AnalyticsView />}
      </main>

      {/* Scam Intervention Modal (Triggered on Threat) */}
      <ScamInterventionModal />

      {/* Toast Notification Manager */}
      <ToastNotification />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#070b16]/90 py-6 px-4 text-xs text-slate-500 mt-auto backdrop-blur-sm">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-[10px] border border-cyan-500/30">
              G
            </div>
            <span className="font-semibold text-slate-400">GuardianAI</span>
            <span className="text-slate-600">•</span>
            <span>MUSA CodeX PS1 Cybersecurity Hackathon Prototype</span>
          </div>

          <div className="flex items-center gap-4 text-slate-400 text-[11px] font-mono">
            <span className="flex items-center gap-1">
              <Lock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Privacy-First Architecture</span>
            </span>
            <span>•</span>
            <span className="text-emerald-400">Zero PII Stored</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <SecurityProvider>
      <DashboardApp />
    </SecurityProvider>
  );
}
