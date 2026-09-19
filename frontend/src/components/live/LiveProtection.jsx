import React from 'react';
import { 
  Play, RefreshCw, AlertTriangle, ShieldCheck, 
  Monitor, Smartphone, UserPlus, IndianRupee, Sparkles, Activity, AlertOctagon, 
  Check, Lock, ArrowDown, ShieldAlert, Zap
} from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';
import RiskGauge from '../common/RiskGauge';

export const LiveProtection = () => {
  const { 
    events, 
    riskEvaluation, 
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

  const stepsCatalog = [
    {
      step: 1,
      title: 'Screen sharing started',
      sub: 'AnyDesk remote support session initiated',
      riskDelta: '+25%'
    },
    {
      step: 2,
      title: 'Banking app opened',
      sub: 'HDFC Mobile foregrounded under active screen share',
      riskDelta: '+25%'
    },
    {
      step: 3,
      title: 'New beneficiary added',
      sub: 'Payee created with rapid clipboard paste (3.2s)',
      riskDelta: '+20%'
    },
    {
      step: 4,
      title: 'Large transaction initiated',
      sub: '₹1,85,000 transfer queued via IMPS Instant',
      riskDelta: '+20%'
    },
    {
      step: 5,
      title: 'Coached behaviour detected',
      sub: 'Rapid cadence variance & voice coaching signature',
      riskDelta: '+10%'
    },
    {
      step: 6,
      title: 'Intervention triggered',
      sub: 'Critical scam warning displayed to halt transaction',
      riskDelta: 'HALT'
    }
  ];

  return (
    <div className="space-y-6 pb-16 max-w-6xl mx-auto">
      
      {/* 1. Header & Simulator Control Bar */}
      <div className="clean-card p-6 border border-slate-800/90 bg-gradient-to-r from-[#0b1122] via-[#0e162e] to-[#0b1122]">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <h2 className="text-xl font-bold text-white tracking-tight">Live Protection & Scam Simulator</h2>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Simulate device-side telemetry arriving in real time. Watch how GuardianAI correlates remote screen sharing, banking access, and payee addition to detect coached fraud.
            </p>
          </div>

          {/* Interactive Control Buttons */}
          <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
            <button
              onClick={advanceSimulator}
              disabled={simulatorState.current_step >= 6}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-40 text-white font-bold text-xs transition-all shadow-md shadow-cyan-950/40 flex items-center gap-2 shrink-0"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>
                {simulatorState.current_step >= 6 ? 'Scenario Complete' : `Next Step (${simulatorState.current_step + 1}/6)`}
              </span>
            </button>

            <button
              onClick={() => setIsAutoSimulating(!isAutoSimulating)}
              className={`px-4 py-2.5 rounded-xl font-bold text-xs border transition-all flex items-center gap-2 shrink-0 ${
                isAutoSimulating
                  ? 'bg-red-600 text-white border-red-500 shadow-lg shadow-red-950/50 animate-pulse'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>{isAutoSimulating ? 'Pause Auto Demo' : 'Auto-Play Demo'}</span>
            </button>

            <button
              onClick={resetSimulator}
              className="px-3.5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 text-xs font-semibold transition-colors flex items-center gap-1.5 shrink-0"
              title="Reset simulation to initial clean SAFE state"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Live Risk Gauge + 6-Stage Progress Stepper */}
        <div className="space-y-6">
          
          {/* Live Risk Gauge Card */}
          <div className="clean-card p-6 text-center">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                Real-Time Risk
              </span>
              <span className="text-[11px] font-mono text-cyan-400 font-bold">
                Step {simulatorState.current_step}/6
              </span>
            </div>

            <RiskGauge score={riskEvaluation.risk_score} level={riskEvaluation.risk_level} size="large" />

            {riskEvaluation.risk_level === 'THREAT_DETECTED' && (
              <button
                onClick={() => setIsInterventionModalOpen(true)}
                className="w-full mt-5 py-2.5 px-4 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-xs transition-all shadow-lg shadow-red-950/50 flex items-center justify-center gap-2 animate-pulse"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>View Scam Warning Modal</span>
              </button>
            )}
          </div>

          {/* 6-Stage Coached Scam Scenario Stepper */}
          <div className="clean-card p-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
              <h3 className="text-xs font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span>Attack Flow Progression</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-500 uppercase">
                {simulatorState.current_step === 0 ? 'Baseline' : `Phase ${simulatorState.current_step} of 6`}
              </span>
            </div>

            <div className="space-y-1.5">
              {stepsCatalog.map((item, idx) => {
                const isPassed = idx < simulatorState.current_step;
                const isCurrent = idx === simulatorState.current_step - 1;

                let cardStyle = 'bg-slate-900/40 border-slate-800/70 text-slate-500 opacity-60';
                if (isCurrent) {
                  cardStyle = 'bg-gradient-to-r from-red-950/50 to-slate-900 border-red-500/80 text-red-200 shadow-lg shadow-red-950/40 ring-1 ring-red-500/30';
                } else if (isPassed) {
                  cardStyle = 'bg-gradient-to-r from-cyan-950/30 to-slate-900 border-cyan-500/40 text-cyan-200';
                }

                return (
                  <React.Fragment key={item.step}>
                    <div
                      className={`p-3 rounded-xl border text-xs transition-all flex items-center justify-between gap-3 ${cardStyle}`}
                    >
                      <div className="flex items-start gap-2.5">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center font-mono font-bold text-[11px] shrink-0 mt-0.5 ${
                          isPassed 
                            ? 'bg-cyan-500 text-slate-950' 
                            : isCurrent 
                            ? 'bg-red-500 text-white animate-pulse' 
                            : 'bg-slate-800 text-slate-500'
                        }`}>
                          {isPassed ? <Check className="w-3 h-3 stroke-[3]" /> : item.step}
                        </div>
                        <div>
                          <span className={`font-bold block ${isCurrent ? 'text-white' : isPassed ? 'text-cyan-300' : 'text-slate-400'}`}>
                            {item.title}
                          </span>
                          <span className="text-[10px] text-slate-400 block mt-0.5 leading-tight">
                            {item.sub}
                          </span>
                        </div>
                      </div>

                      <span className={`font-mono text-[11px] font-extrabold px-1.5 py-0.5 rounded shrink-0 ${
                        isPassed ? 'bg-cyan-950 text-cyan-400 border border-cyan-800/60' :
                        isCurrent ? 'bg-red-950 text-red-400 border border-red-800/60' :
                        'text-slate-600'
                      }`}>
                        {item.riskDelta}
                      </span>
                    </div>

                    {/* Downward connector between stages */}
                    {idx < stepsCatalog.length - 1 && (
                      <div className="flex items-center justify-center py-0.5">
                        <div className={`flex items-center gap-1 text-[10px] font-mono transition-colors ${
                          idx < simulatorState.current_step - 1
                            ? 'text-cyan-400'
                            : idx === simulatorState.current_step - 1
                            ? 'text-red-400 animate-bounce'
                            : 'text-slate-700'
                        }`}>
                          <ArrowDown className="w-3 h-3" />
                        </div>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>

        </div>

        {/* Right Column: Real-Time Event Stream Feed */}
        <div className="lg:col-span-2 clean-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
                <h3 className="text-sm font-bold text-white">Live Telemetry Ingestion Stream</h3>
              </div>
              <span className="text-[11px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                {events.length} Events Logged
              </span>
            </div>

            {events.length === 0 ? (
              <div className="py-20 text-center text-slate-500">
                <Activity className="w-10 h-10 mx-auto mb-3 text-slate-600" />
                <h4 className="text-sm font-bold text-slate-300">Awaiting Telemetry Events</h4>
                <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                  Click <strong>"Next Step (1/6)"</strong> or <strong>"Auto-Play Demo"</strong> above to begin feeding simulated device telemetry into the GuardianAI risk correlation pipeline.
                </p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                {events.map((ev, idx) => {
                  const isThreat = ev.event_type.includes('COACHED') || ev.event_type.includes('INTERVENTION');
                  const isWarning = ev.event_type.includes('SCREEN') || ev.event_type.includes('TRANSACTION') || ev.event_type.includes('BENEFICIARY');

                  return (
                    <div
                      key={ev.event_id || idx}
                      className={`p-4 rounded-xl border text-xs transition-all ${
                        isThreat
                          ? 'bg-gradient-to-r from-red-950/30 via-slate-900 to-slate-900 border-red-500/50 shadow-md shadow-red-950/20'
                          : isWarning
                          ? 'bg-gradient-to-r from-amber-950/20 via-slate-900 to-slate-900 border-amber-500/40'
                          : 'bg-slate-900/70 border-slate-800'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 shrink-0 mt-0.5">
                            {getEventIcon(ev.event_type)}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-white text-sm">
                                {ev.event_type.replace(/_/g, ' ')}
                              </span>
                              <span className="text-[10px] font-mono text-slate-500">
                                #{events.length - idx}
                              </span>
                            </div>

                            {/* Metadata parameters */}
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {Object.entries(ev.metadata || {}).map(([k, v]) => (
                                <span
                                  key={k}
                                  className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-950 text-slate-400 border border-slate-800/80"
                                >
                                  {k}: <strong className="text-slate-200">{String(v)}</strong>
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="text-right shrink-0">
                          <span className="text-[11px] font-mono text-cyan-400 font-semibold block">
                            {new Date(ev.timestamp).toLocaleTimeString()}
                          </span>
                          <span className="text-[9px] font-mono text-slate-500">
                            {ev.event_id || `ev_${idx}`}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="mt-5 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Device-Side Privacy Architecture</span>
            </span>
            <span className="text-slate-400 font-mono">Zero PII • Strict Telemetry Mode</span>
          </div>
        </div>

      </div>

    </div>
  );
};

export default LiveProtection;
