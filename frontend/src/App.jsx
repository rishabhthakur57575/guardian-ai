import React, { useState } from 'react';
import { SecurityProvider } from './context/SecurityContext';
import Navbar from './components/common/Navbar';
import HomeDashboard from './components/dashboard/HomeDashboard';
import LiveProtection from './components/live/LiveProtection';
import SecurityTimeline from './components/timeline/SecurityTimeline';
import AnalyticsView from './components/analytics/AnalyticsView';
import ScamInterventionModal from './components/intervention/ScamInterventionModal';

function DashboardApp() {
  const [currentTab, setCurrentTab] = useState('dashboard');

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
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

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#090d16] py-5 px-4 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <span>GuardianAI — MUSA CodeX PS1 Prototype</span>
          <span className="text-slate-400">Privacy-First Architecture • Zero PII Stored</span>
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
