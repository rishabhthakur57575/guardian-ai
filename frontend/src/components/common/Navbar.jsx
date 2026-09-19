import React, { useState } from 'react';
import { 
  Shield, ShieldAlert, ShieldCheck, Activity, 
  Wifi, WifiOff, Menu, X, RefreshCw, Lock
} from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';

export const Navbar = ({ currentTab, setCurrentTab }) => {
  const { riskEvaluation, isBackendOnline, refreshAllData, isLoading } = useSecurity();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const getStatusBadge = () => {
    switch (riskEvaluation?.risk_level) {
      case 'THREAT_DETECTED':
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/15 border border-red-500/40 text-red-400 font-bold text-xs shadow-lg shadow-red-950/50">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>THREAT DETECTED</span>
          </div>
        );
      case 'MONITORING':
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-400 font-bold text-xs shadow-lg shadow-amber-950/50">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
            <Activity className="w-3.5 h-3.5" />
            <span>MONITORING</span>
          </div>
        );
      case 'SAFE':
      default:
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-400 font-bold text-xs shadow-lg shadow-emerald-950/50">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>PROTECTION ACTIVE</span>
          </div>
        );
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'live', label: 'Live Protection' },
    { id: 'timeline', label: 'Security Timeline' },
    { id: 'analytics', label: 'Analytics' },
  ];

  return (
    <header className="bg-[#070b16]/95 backdrop-blur-md border-b border-slate-800/90 px-4 lg:px-8 py-3.5 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
        
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-md shadow-cyan-500/20 ring-1 ring-cyan-400/30">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-extrabold tracking-tight text-white">
                Guardian<span className="text-cyan-400">AI</span>
              </h1>
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 font-mono">
                MUSA CodeX PS1
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-0.5">
              <Lock className="w-3 h-3 text-cyan-400" />
              <span>Zero PII Telemetry Interceptor</span>
            </div>
          </div>
        </div>

        {/* Center: Desktop Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-[#0b1122] p-1 rounded-xl border border-slate-800/80">
          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Right: Telemetry Engine Health & Status Badge */}
        <div className="hidden sm:flex items-center gap-3">
          {/* Health Indicator */}
          <button
            onClick={() => refreshAllData()}
            title={isBackendOnline ? 'API Connected (Click to refresh)' : 'API Disconnected (Click to retry)'}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono border transition-colors ${
              isBackendOnline
                ? 'bg-slate-900/80 text-slate-300 border-slate-800 hover:border-slate-700'
                : 'bg-red-950/80 text-red-400 border-red-800 hover:bg-red-900/60'
            }`}
          >
            {isBackendOnline ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>API ONLINE</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3 text-red-400" />
                <span>OFFLINE</span>
              </>
            )}
            <RefreshCw className={`w-3 h-3 text-slate-500 ml-1 ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          {getStatusBadge()}
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex md:hidden items-center gap-2">
          {getStatusBadge()}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg bg-slate-900 text-slate-300 border border-slate-800"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden mt-3 pt-3 border-t border-slate-800 space-y-1">
          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-semibold ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'text-slate-400 hover:bg-slate-800/40'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};

export default Navbar;
