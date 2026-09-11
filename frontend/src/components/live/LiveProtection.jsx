import React from 'react';
import { 
  Play, RefreshCw, AlertTriangle, ShieldCheck, 
  Monitor, Smartphone, UserPlus, IndianRupee, Sparkles, Activity, AlertOctagon, Check 
} from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';
import RiskGauge from '../common/RiskGauge';

export const LiveProtection = () => {
  const { 
    events, 
    riskEvaluation, 
    activeTelemetry, 
    simulatorState, 
    advanceSimulator, 
    resetSimulator, 
    isAutoSimulating, 
    setIsAutoSimulating, 
    setIsInterventionModalOpen 
  } = useSecurity();

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'SCREEN_SHARING_STARTED':
        return <Monitor className="w-4 h-4 text-amber-400" />;
      case 'BANKING_APP_FOREGROUNDED':
        return <Smartphone className="w-4 h-4 text-cyan-400" />;
      case 'NEW_BENEFICIARY_ADDED':
        return <UserPlus className="w-4 h-4 text-purple-400" />;
      case 'HIGH_VALUE_TRANSACTION_INITIATED':
        return <IndianRupee className="w-4 h-4 text-amber-400" />;
      case 'COACHED_BEHAVIOUR_TRIGGERED':
        return <Sparkles className="w-4 h-4 text-red-400" />;
      case 'INTERVENTION_TRIGGERED':
        return <AlertOctagon className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-slate-400" />;
    }
  };

  const stepsList = [
    '1. Screen sharing started (AnyDesk detected)',
    '2. Banking app opened (HDFC Mobile foregrounded)',
    '3. New beneficiary added (rapid paste event)',
    '4. Large transaction initiated (₹1,85,000 transfer)',
    '5. Suspicious behaviour detected (anomaly correlation)',
    '6. Scam intervention triggered (warning modal)'
  ];

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto">
      
      {/* Header & Simulator Bar */}
      <div className="clean-card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white">Live Event Stream & Simulator</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Test the 6-stage coached remote screen-sharing scam scenario.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={advanceSimulator}
            disabled={simulatorState.current_step >= 6}
            className="px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white font-semibold text-xs transition-colors flex items-center gap-1.5"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Advance Step ({simulatorState.current_step}/6)</span>
          </button>

          <button
            onClick={() => setIsAutoSimulating(!isAutoSimulating)}
            className={`px-3.5 py-2 rounded-lg font-semibold text-xs border transition-colors flex items-center gap-1.5 ${
              isAutoSimulating
                ? 'bg-red-600 text-white border-red-500'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{isAutoSimulating ? 'Pause Auto Demo' : 'Auto Play Demo'}</span>
          </button>

          <button
            onClick={resetSimulator}
            className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 text-xs font-medium transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Left Simulator Progress + Right Event Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Risk & Step Progress */}
        <div className="space-y-4">
          <div className="clean-card p-5 text-center">
            <span className="text-xs font-medium text-slate-400 block mb-2">Live Risk Level</span>
            <RiskGauge score={riskEvaluation.risk_score} level={riskEvaluation.risk_level} />

            {riskEvaluation.risk_level === 'THREAT_DETECTED' && (
              <button
                onClick={() => setIsInterventionModalOpen(true)}
                className="w-full mt-4 py-2 px-3 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold text-xs transition-colors"
              >
                View Scam Warning Modal
              </button>
            )}
          </div>

          {/* Scenario Stages Checklist */}
          <div className="clean-card p-5">
            <span className="text-xs font-bold text-white block mb-3">Simulation Sequence</span>
            <div className="space-y-2">
              {stepsList.map((step, idx) => {
                const isPassed = idx < simulatorState.current_step;
                const isCurrent = idx === simulatorState.current_step - 1;
                return (
                  <div
                    key={idx}
                    className={`p-2.5 rounded-lg text-xs border flex items-center justify-between ${
                      isPassed
                        ? 'bg-cyan-950/30 border-cyan-500/30 text-cyan-300 font-medium'
                        : isCurrent
                        ? 'bg-red-950/30 border-red-500/40 text-red-300 font-semibold'
                        : 'bg-slate-900/40 border-slate-800/80 text-slate-500'
                    }`}
                  >
                    <span>{step}</span>
                    {isPassed && <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Live Event Stream Feed */}
        <div className="lg:col-span-2 clean-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                <h3 className="text-sm font-bold text-white">Live Event Stream</h3>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                {events.length} Events Logged
              </span>
            </div>

            {events.length === 0 ? (
              <div className="py-16 text-center text-slate-500">
                <Activity className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <p className="text-xs font-semibold">No live events yet.</p>
                <p className="text-[11px] text-slate-600 mt-0.5">Click "Advance Step" above to start the scam scenario.</p>
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[480px] overflow-y-auto pr-1">
                {events.map((ev, idx) => {
                  const isThreat = ev.event_type.includes('COACHED') || ev.event_type.includes('INTERVENTION');
                  const isWarning = ev.event_type.includes('SCREEN') || ev.event_type.includes('TRANSACTION');

                  return (
                    <div
                      key={ev.event_id || idx}
                      className={`p-3.5 rounded-lg border text-xs transition-all ${
                        isThreat
                          ? 'bg-red-950/25 border-red-500/40'
                          : isWarning
                          ? 'bg-amber-950/20 border-amber-500/30'
                          : 'bg-slate-900/60 border-slate-800'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div className="p-1.5 rounded-md bg-slate-900 border border-slate-800 shrink-0 mt-0.5">
                            {getEventIcon(ev.event_type)}
                          </div>
                          <div>
                            <span className="font-bold text-slate-200">
                              {ev.event_type.replace(/_/g, ' ')}
                            </span>
                            <div className="mt-1 flex flex-wrap gap-1.5">
                              {Object.entries(ev.metadata || {}).map(([k, v]) => (
                                <span
                                  key={k}
                                  className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800"
                                >
                                  {k}: <strong className="text-slate-200">{String(v)}</strong>
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        <span className="text-[11px] font-mono text-slate-500 shrink-0">
                          {new Date(ev.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex justify-between">
            <span>Device Telemetry Pipe</span>
            <span className="text-slate-400">Privacy-First (No PII / No OTP)</span>
          </div>
        </div>

      </div>
    </div>
  );
};

export default LiveProtection;
