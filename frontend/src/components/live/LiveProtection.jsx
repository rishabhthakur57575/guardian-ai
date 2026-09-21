import React from 'react';
import { 
  Play, RefreshCw, AlertTriangle, ShieldCheck, 
  Monitor, Smartphone, UserPlus, IndianRupee, Sparkles, Activity, AlertOctagon, 
  Check, Lock, ArrowDown, ShieldAlert, Zap, HelpCircle, Layers, XCircle, ChevronRight, Info
} from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';
import RiskGauge from '../common/RiskGauge';

export const LiveProtection = () => {
  const { 
    sessionId,
    selectedScenarioId,
    switchScenario,
    availableScenarios,
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
      case 'SCREEN_SHARING_ENDED':
        return <Monitor className="w-4 h-4 text-amber-400" />;
      case 'BANKING_APP_FOREGROUNDED':
      case 'BANKING_APP_CLOSED':
        return <Smartphone className="w-4 h-4 text-cyan-400" />;
      case 'NEW_BENEFICIARY_ADDED':
        return <UserPlus className="w-4 h-4 text-purple-400" />;
      case 'HIGH_VALUE_TRANSACTION_INITIATED':
      case 'TRANSACTION_COMPLETED':
        return <IndianRupee className="w-4 h-4 text-emerald-400" />;
      case 'TRANSACTION_CANCELLED':
        return <XCircle className="w-4 h-4 text-emerald-400" />;
      case 'COACHED_BEHAVIOUR_TRIGGERED':
        return <Sparkles className="w-4 h-4 text-red-400" />;
      case 'INTERVENTION_TRIGGERED':
        return <AlertOctagon className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-slate-400" />;
    }
  };

  const defaultScenarioCatalog = [
    {
      id: 'family_assistance',
      name: '1. Family Remote Assistance',
      category: 'SAFE ASSISTANCE',
      description: 'Legitimate caregiver remote screen-share with verified family contact for routine utility bill payment.'
    },
    {
      id: 'legit_high_value',
      name: '2. Legitimate High-Value Transfer',
      category: 'SAFE UNCOACHED',
      description: 'Direct user transfer of ₹1,50,000 without screen sharing, hesitation, or external dictation.'
    },
    {
      id: 'coached_scam',
      name: '3. Coached Remote-Support Scam',
      category: 'CRITICAL THREAT',
      description: 'Unverified screen sharing, banking login under third-party view, rapid payee addition, and guided transfer.'
    },
    {
      id: 'rapid_banking',
      name: '4. Suspicious Rapid Banking',
      category: 'SUSPICIOUS MONITORING',
      description: 'Rapid app switching across SMS and banking, multiple back-navigation reversals, and clipboard payee paste.'
    },
    {
      id: 'scam_cancellation',
      name: '5. Scam Warning & Cancellation',
      category: 'SIMULATED INTERCEPTION',
      description: 'High-risk coached scam intercepted by GuardianAI warning; user halts and cancels the simulated transaction.'
    }
  ];

  const scenariosList = availableScenarios && availableScenarios.length > 0
    ? availableScenarios
    : defaultScenarioCatalog;

  const activeScenarioMeta = scenariosList.find((s) => s.id === selectedScenarioId) || scenariosList[0];

  // Dynamic steps from simulatorState or fallback to active catalog
  const stepsCatalog = (simulatorState.steps_catalog && simulatorState.steps_catalog.length > 0)
    ? simulatorState.steps_catalog.map((st, idx) => ({
        step: st.step_index || idx + 1,
        title: st.description || st.event_type.replace(/_/g, ' '),
        sub: st.event_type,
        riskDelta: st.event_type.includes('INTERVENTION') ? 'HALT' : (st.event_type.includes('CANCELLED') ? 'SAFE' : `Step ${idx + 1}`)
      }))
    : [];

  const currentStep = simulatorState.current_step || 0;
  const totalSteps = simulatorState.total_steps || stepsCatalog.length || 6;
  const isComplete = currentStep >= totalSteps;

  return (
    <div className="space-y-6 pb-16 max-w-6xl mx-auto">
      
      {/* 1. Header & Simulator Control Bar */}
      <div className="clean-card p-6 border border-slate-800/90 bg-gradient-to-r from-[#0b1122] via-[#0e162e] to-[#0b1122]">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <h2 className="text-xl font-bold text-white tracking-tight">Live Protection & Behavioral Simulator</h2>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Select and simulate end-to-end device telemetry scenarios through GuardianAI's risk engine and ML pipeline.
            </p>
          </div>

          {/* Interactive Control Buttons */}
          <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
            <button
              onClick={advanceSimulator}
              disabled={isComplete}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-40 text-white font-bold text-xs transition-all shadow-md shadow-cyan-950/40 flex items-center gap-2 shrink-0"
              title="Advance one event at a time"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>
                {isComplete ? 'Scenario Complete' : `Next Step (${currentStep + 1}/${totalSteps})`}
              </span>
            </button>

            <button
              onClick={() => setIsAutoSimulating(!isAutoSimulating)}
              className={`px-4 py-2.5 rounded-xl font-bold text-xs border transition-all flex items-center gap-2 shrink-0 ${
                isAutoSimulating
                  ? 'bg-red-600 text-white border-red-500 shadow-lg shadow-red-950/50 animate-pulse'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
              }`}
              title="Automatically execute scenario events in sequence"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>{isAutoSimulating ? 'Pause Auto Demo' : 'Auto-Play Demo'}</span>
            </button>

            <button
              onClick={resetSimulator}
              className="px-3.5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 text-xs font-semibold transition-colors flex items-center gap-1.5 shrink-0"
              title="Reset selected scenario to its initial clean state"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Scenario Selector Tabs */}
        <div className="mt-6 pt-5 border-t border-slate-800/80">
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>Select Test Scenario ({scenariosList.length} Available):</span>
            </span>
            <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/60 px-2.5 py-0.5 rounded-full">
              Active Session: <strong>{sessionId}</strong>
            </span>
          </div>

          {/* 5 Scenario Selector Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
            {scenariosList.map((sc) => {
              const isSelected = sc.id === selectedScenarioId;
              let categoryBadgeColor = 'bg-slate-800 text-slate-300 border-slate-700';
              if (sc.id.includes('family') || sc.id.includes('legit')) {
                categoryBadgeColor = 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60';
              } else if (sc.id.includes('rapid')) {
                categoryBadgeColor = 'bg-amber-950/80 text-amber-300 border-amber-800/60';
              } else if (sc.id.includes('scam')) {
                categoryBadgeColor = 'bg-red-950/80 text-red-300 border-red-800/60';
              }

              return (
                <button
                  key={sc.id}
                  onClick={() => switchScenario(sc.id)}
                  className={`p-3 rounded-xl border text-left transition-all relative flex flex-col justify-between ${
                    isSelected
                      ? 'bg-gradient-to-b from-[#131d3b] to-[#0c1326] border-cyan-500/80 shadow-lg shadow-cyan-950/50 ring-1 ring-cyan-500/30'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900 text-slate-400'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-1 mb-1.5">
                      <span className={`text-[9px] font-mono uppercase font-black px-1.5 py-0.5 rounded border ${categoryBadgeColor}`}>
                        {sc.category || 'SCENARIO'}
                      </span>
                      {isSelected && (
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                      )}
                    </div>
                    <h4 className={`text-xs font-bold leading-snug ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                      {sc.name}
                    </h4>
                    <p className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-tight">
                      {sc.description}
                    </p>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono text-slate-500">
                    <span>{sc.total_steps || 6} Steps</span>
                    <span className={isSelected ? 'text-cyan-400 font-bold' : 'text-slate-500'}>
                      {isSelected ? 'Active' : 'Select'}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Active Scenario Banner */}
          <div className="mt-3.5 p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between flex-wrap gap-2 text-xs">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-cyan-400 shrink-0" />
              <span className="text-slate-300">
                <strong className="text-white">{activeScenarioMeta.name}:</strong> {activeScenarioMeta.description}
              </span>
            </div>
            <div className="flex items-center gap-3 text-[11px] font-mono">
              <span className="text-slate-400">
                Pipeline Mode: <strong className="text-cyan-300">Active ML Telemetry</strong>
              </span>
              <span className="text-slate-400">
                Isolation: <strong className="text-emerald-300">Unique Session ID</strong>
              </span>
            </div>
          </div>

        </div>
      </div>

      {/* 2. Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Live Risk Gauge + Dynamic Progression Stepper + Explanations */}
        <div className="space-y-6">
          
          {/* Live Risk Gauge Card */}
          <div className="clean-card p-6 text-center">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                Pipeline Risk Score
              </span>
              <span className="text-[11px] font-mono text-cyan-400 font-bold">
                Step {currentStep}/{totalSteps}
              </span>
            </div>

            <RiskGauge score={riskEvaluation.risk_score} level={riskEvaluation.risk_level} size="large" />

            {riskEvaluation.risk_level === 'THREAT_DETECTED' && (
              <button
                onClick={() => setIsInterventionModalOpen(true)}
                className="w-full mt-5 py-2.5 px-4 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-xs transition-all shadow-lg shadow-red-950/50 flex items-center justify-center gap-2 animate-pulse"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>View Emergency Scam Warning</span>
              </button>
            )}
          </div>

          {/* Detected Signals from Real Pipeline Response */}
          <div className="clean-card p-5">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5 mb-3">
              <h3 className="text-xs font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-cyan-400" />
                <span>Pipeline Detected Signals</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-400">
                {(riskEvaluation.detected_signals || riskEvaluation.reasons || []).length} Flags
              </span>
            </div>

            <div className="space-y-2">
              {(riskEvaluation.detected_signals || riskEvaluation.reasons || ['Normal behavioral baseline maintained']).map((sig, sIdx) => (
                <div
                  key={sIdx}
                  className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs text-slate-200 flex items-start gap-2"
                >
                  <div className={`w-2 h-2 rounded-full shrink-0 mt-1.5 ${
                    riskEvaluation.risk_level === 'THREAT_DETECTED' ? 'bg-red-400' :
                    riskEvaluation.risk_level === 'MONITORING' ? 'bg-amber-400' : 'bg-emerald-400'
                  }`} />
                  <span className="leading-snug">{sig}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Model Plain-Language Explanation */}
          {riskEvaluation.human_explanation && (
            <div className="clean-card p-5">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5 mb-3">
                <h3 className="text-xs font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                  <span>Model Explanation</span>
                </h3>
                <span className="text-[10px] font-mono text-purple-400 bg-purple-950 px-2 py-0.5 rounded border border-purple-800/60">
                  {riskEvaluation.human_explanation.provider_type || 'EXPLAINABILITY'}
                </span>
              </div>

              <div className="space-y-2.5 text-xs">
                <p className="font-bold text-white text-sm">
                  {riskEvaluation.human_explanation.headline}
                </p>
                {riskEvaluation.human_explanation.recommended_action && (
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                    <span className="text-[10px] font-mono uppercase text-slate-500 block mb-0.5 font-bold">Recommended Guidance:</span>
                    <span>{riskEvaluation.human_explanation.recommended_action}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Dynamic Scenario Progression Stepper */}
          <div className="clean-card p-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
              <h3 className="text-xs font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span>Scenario Event Sequence</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-500 uppercase">
                {currentStep === 0 ? 'Baseline' : `Step ${currentStep} of ${totalSteps}`}
              </span>
            </div>

            <div className="space-y-1.5">
              {stepsCatalog.map((item, idx) => {
                const isPassed = idx < currentStep;
                const isCurrent = idx === currentStep - 1;

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
                          <span className="text-[10px] text-slate-400 block mt-0.5 leading-tight font-mono">
                            {item.sub}
                          </span>
                        </div>
                      </div>

                      <span className={`font-mono text-[10px] font-extrabold px-1.5 py-0.5 rounded shrink-0 ${
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
                          idx < currentStep - 1
                            ? 'text-cyan-400'
                            : idx === currentStep - 1
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
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4 flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
                <h3 className="text-sm font-bold text-white">Live Telemetry Ingestion Stream</h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono text-cyan-400 bg-slate-900 px-2.5 py-0.5 rounded border border-slate-800 font-bold">
                  {sessionId}
                </span>
                <span className="text-[11px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                  {events.length} Events
                </span>
              </div>
            </div>

            {events.length === 0 ? (
              <div className="py-24 text-center text-slate-500">
                <Activity className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                <h4 className="text-sm font-bold text-slate-300">Awaiting Scenario Telemetry</h4>
                <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                  Click <strong>"Next Step (1/{totalSteps})"</strong> or <strong>"Auto-Play Demo"</strong> above to ingest simulated events into the pipeline.
                </p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[640px] overflow-y-auto pr-1">
                {events.map((ev, idx) => {
                  const isCancelled = ev.event_type === 'TRANSACTION_CANCELLED';
                  const isThreat = ev.event_type.includes('COACHED') || ev.event_type.includes('INTERVENTION');
                  const isWarning = ev.event_type.includes('SCREEN') || ev.event_type.includes('TRANSACTION') || ev.event_type.includes('BENEFICIARY') || ev.event_type.includes('SWITCH');

                  return (
                    <div
                      key={ev.event_id || idx}
                      className={`p-4 rounded-xl border text-xs transition-all ${
                        isCancelled
                          ? 'bg-gradient-to-r from-emerald-950/30 via-slate-900 to-slate-900 border-emerald-500/50 shadow-md'
                          : isThreat
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

                            {/* Simulated Action Disclaimer */}
                            {isCancelled && (
                              <div className="mt-2 p-2 rounded bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-[11px] leading-snug">
                                <strong>Simulated Action:</strong> User cancelled transaction following emergency warning. No real banking transfer executed or blocked.
                              </div>
                            )}

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
              <span>Device-Side Behavioral Pipeline</span>
            </span>
            <span className="text-slate-400 font-mono">Zero PII • Isolated Session IDs</span>
          </div>
        </div>

      </div>

    </div>
  );
};

export default LiveProtection;
