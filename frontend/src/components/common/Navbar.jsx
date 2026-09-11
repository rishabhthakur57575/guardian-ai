import React from 'react';
import { Shield, ShieldAlert, ShieldCheck, Activity } from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';

export const Navbar = ({ currentTab, setCurrentTab }) => {
  const { riskEvaluation } = useSecurity();

  const getStatusBadge = () => {
    switch (riskEvaluation.risk_level) {
      case 'THREAT_DETECTED':
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 font-semibold text-xs">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>THREAT DETECTED</span>
          </div>
        );
      case 'MONITORING':
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-semibold text-xs">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <Activity className="w-3.5 h-3.5" />
            <span>MONITORING</span>
          </div>
        );
      case 'SAFE':
      default:
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>SAFE</span>
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
    <header className="bg-[#0b1120] border-b border-slate-800/80 px-4 lg:px-8 py-3.5 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-cyan-600 flex items-center justify-center text-white shadow-sm">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white">
                Guardian<span className="text-cyan-400">AI</span>
              </h1>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                PS1 Prototype
              </span>
            </div>
          </div>
        </div>

        {/* Clean Nav Tabs */}
        <nav className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-800 text-cyan-400 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Status indicator */}
        <div className="flex items-center gap-3">
          {getStatusBadge()}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
