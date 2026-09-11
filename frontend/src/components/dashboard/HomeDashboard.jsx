import React from 'react';
import { 
  ShieldCheck, ShieldAlert, AlertTriangle, Monitor, Smartphone, 
  ShieldX, CheckCircle, ArrowRight 
} from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';
import RiskGauge from '../common/RiskGauge';

export const HomeDashboard = ({ setCurrentTab }) => {
  const { 
    riskEvaluation, 
    activeTelemetry, 
    analytics, 
    events 
  } = useSecurity();

  const metrics = analytics?.metrics || {
    today_protected_sessions: 48,
    threats_detected: 9,
    transactions_interrupted: 7,
    total_interrupted_amount_inr: 425000,
  };

  const getStatusCardTheme = () => {
    switch (riskEvaluation.risk_level) {
      case 'THREAT_DETECTED':
        return {
          border: 'border-red-500/50 bg-red-950/20',
          title: 'THREAT DETECTED',
          desc: 'Possible remote-coached scam sequence detected. Intervention required.',
          icon: ShieldAlert,
          iconColor: 'text-red-400',
        };
      case 'MONITORING':
        return {
          border: 'border-amber-500/50 bg-amber-950/20',
          title: 'MONITORING',
          desc: 'Elevated device telemetry detected. Analyzing behavioural patterns.',
          icon: AlertTriangle,
          iconColor: 'text-amber-400',
        };
      case 'SAFE':
      default:
        return {
          border: 'border-emerald-500/40 bg-emerald-950/15',
          title: 'SAFE',
          desc: 'Device behavioural baseline is normal. No suspicious remote actions detected.',
          icon: ShieldCheck,
          iconColor: 'text-emerald-400',
        };
    }
  };

  const statusTheme = getStatusCardTheme();
  const StatusIcon = statusTheme.icon;

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto">
      
      {/* 1. Protection Status Banner */}
      <div className={`clean-card p-6 border ${statusTheme.border}`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className={`p-3.5 rounded-xl bg-slate-900 border border-slate-800 ${statusTheme.iconColor}`}>
              <StatusIcon className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Protection Status
                </span>
                <span className={`text-xs font-bold ${statusTheme.iconColor}`}>
                  ● {statusTheme.title}
                </span>
              </div>
              <h2 className="text-xl font-bold text-white mt-0.5">
                {statusTheme.title === 'SAFE' && 'System is Protecting Your Device'}
                {statusTheme.title === 'MONITORING' && 'Elevated Activity Under Observation'}
                {statusTheme.title === 'THREAT DETECTED' && 'Scam Behaviour Identified'}
              </h2>
              <p className="text-xs text-slate-300 mt-1 max-w-xl">
                {riskEvaluation.reasons?.[0] || statusTheme.desc}
              </p>
            </div>
          </div>

          <button
            onClick={() => setCurrentTab('live')}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shrink-0"
          >
            <span>Live Protection & Simulator</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. Key Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="clean-card p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Today's Protected Sessions</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2 font-mono">{metrics.today_protected_sessions}</p>
          <span className="text-[11px] text-slate-500">Device monitoring active</span>
        </div>

        <div className="clean-card p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Threats Detected</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400 mt-2 font-mono">{metrics.threats_detected}</p>
          <span className="text-[11px] text-slate-500">Suspicious combinations flagged</span>
        </div>

        <div className="clean-card p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Transactions Interrupted</span>
            <ShieldX className="w-4 h-4 text-red-400" />
          </div>
          <p className="text-2xl font-bold text-red-400 mt-2 font-mono">{metrics.transactions_interrupted}</p>
          <span className="text-[11px] text-slate-500">Saved: ₹{metrics.total_interrupted_amount_inr.toLocaleString('en-IN')}</span>
        </div>
      </div>

      {/* 3. Device Telemetry & Risk Score Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* Risk Score */}
        <div className="clean-card p-5 flex flex-col items-center justify-center text-center">
          <span className="text-xs font-medium text-slate-400 mb-2">Current Risk Assessment</span>
          <RiskGauge score={riskEvaluation.risk_score} level={riskEvaluation.risk_level} />
        </div>

        {/* Active Screen Sharing Status */}
        <div className="clean-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
              <span className="text-xs font-medium text-slate-400">Screen-Sharing Status</span>
              <Monitor className={`w-4 h-4 ${activeTelemetry.screenSharing.active ? 'text-red-400' : 'text-slate-500'}`} />
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className={`w-2.5 h-2.5 rounded-full ${activeTelemetry.screenSharing.active ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'}`} />
              <h3 className="text-base font-bold text-white">
                {activeTelemetry.screenSharing.active ? 'Screen Sharing Detected' : 'No Screen Sharing'}
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Tool: <span className="text-slate-200">{activeTelemetry.screenSharing.tool}</span>
            </p>
          </div>

          <div className="mt-4 pt-2 border-t border-slate-800/80 text-[11px] text-slate-500">
            {activeTelemetry.screenSharing.active ? '⚠️ Third party has display visibility' : '✓ Local display secure'}
          </div>
        </div>

        {/* Banking App Status */}
        <div className="clean-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
              <span className="text-xs font-medium text-slate-400">Banking App Status</span>
              <Smartphone className={`w-4 h-4 ${activeTelemetry.bankingApp.active ? 'text-amber-400' : 'text-slate-500'}`} />
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className={`w-2.5 h-2.5 rounded-full ${activeTelemetry.bankingApp.active ? 'bg-amber-400' : 'bg-slate-600'}`} />
              <h3 className="text-base font-bold text-white">
                {activeTelemetry.bankingApp.active ? 'Banking App Open' : 'No Active Banking App'}
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              App: <span className="text-slate-200">{activeTelemetry.bankingApp.app}</span>
            </p>
          </div>

          <div className="mt-4 pt-2 border-t border-slate-800/80 text-[11px] text-slate-500">
            {activeTelemetry.bankingApp.active && activeTelemetry.screenSharing.active
              ? '⚠️ High risk: Screen share + Banking concurrent'
              : '✓ Isolated application environment'}
          </div>
        </div>

      </div>

      {/* 4. Recent Security Events */}
      <div className="clean-card p-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <h3 className="text-sm font-bold text-white">Recent Security Events</h3>
          <button
            onClick={() => setCurrentTab('timeline')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
          >
            View Full Timeline &rarr;
          </button>
        </div>

        {events.length === 0 ? (
          <div className="py-8 text-center text-slate-500">
            <CheckCircle className="w-8 h-8 mx-auto mb-1 text-slate-600" />
            <p className="text-xs font-medium">No recent security anomalies recorded.</p>
            <p className="text-[11px] text-slate-600 mt-0.5">Switch to Live Protection to run the demo simulation.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {events.slice(0, 4).map((ev, idx) => (
              <div
                key={ev.event_id || idx}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs"
              >
                <div className="flex items-center gap-2.5">
                  <span className={`w-2 h-2 rounded-full ${
                    ev.event_type.includes('COACHED') || ev.event_type.includes('INTERVENTION')
                      ? 'bg-red-400'
                      : ev.event_type.includes('SCREEN') || ev.event_type.includes('TRANSACTION')
                      ? 'bg-amber-400'
                      : 'bg-cyan-400'
                  }`} />
                  <span className="font-semibold text-slate-200">{ev.event_type.replace(/_/g, ' ')}</span>
                </div>
                <span className="text-slate-500 font-mono text-[11px]">
                  {new Date(ev.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};

export default HomeDashboard;
