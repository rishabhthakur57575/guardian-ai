import React from 'react';
import { 
  ShieldCheck, ShieldAlert, AlertTriangle, Monitor, Smartphone, 
  ShieldX, ArrowRight, Activity, Zap, CheckCircle2, 
  IndianRupee, UserPlus, Eye, Lock, Sparkles, RefreshCw
} from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';
import RiskGauge from '../common/RiskGauge';

export const HomeDashboard = ({ setCurrentTab }) => {
  const { 
    riskEvaluation, 
    activeTelemetry, 
    analytics, 
    events,
    session,
    isLoading,
    isBackendOnline,
    refreshAllData,
    setIsInterventionModalOpen
  } = useSecurity();

  const metrics = analytics?.metrics || {
    today_protected_sessions: 48,
    threats_detected: 10,
    transactions_interrupted: 9,
    total_interrupted_amount_inr: 425000,
    average_risk_score: 24.5,
    system_status: 'ACTIVE_SHIELD_ONLINE'
  };

  const getStatusTheme = () => {
    switch (riskEvaluation?.risk_level) {
      case 'THREAT_DETECTED':
        return {
          cardBg: 'bg-gradient-to-r from-red-950/40 via-[#0b1122] to-red-950/20',
          border: 'border-red-500/60 shadow-xl shadow-red-950/30',
          title: 'SCAM THREAT DETECTED',
          headline: 'Suspicious Remote-Coached Activity Detected',
          desc: riskEvaluation.reasons?.[0] || 'Third party is viewing your screen while a financial transfer is being prepared.',
          icon: ShieldAlert,
          iconColor: 'text-red-400',
          iconBg: 'bg-red-500/20 border-red-500/40',
          badge: 'bg-red-500/20 text-red-300 border-red-500/50'
        };
      case 'MONITORING':
        return {
          cardBg: 'bg-gradient-to-r from-amber-950/30 via-[#0b1122] to-amber-950/15',
          border: 'border-amber-500/50 shadow-xl shadow-amber-950/20',
          title: 'ELEVATED MONITORING',
          headline: 'High-Sensitivity Behavioral Observation Active',
          desc: riskEvaluation.reasons?.[0] || 'Elevated device telemetry detected. Analyzing behavioral patterns.',
          icon: AlertTriangle,
          iconColor: 'text-amber-400',
          iconBg: 'bg-amber-500/20 border-amber-500/40',
          badge: 'bg-amber-500/20 text-amber-300 border-amber-500/50'
        };
      case 'SAFE':
      default:
        return {
          cardBg: 'bg-gradient-to-r from-emerald-950/25 via-[#0b1122] to-cyan-950/20',
          border: 'border-emerald-500/40 shadow-xl shadow-emerald-950/20',
          title: 'SHIELD ONLINE & SAFE',
          headline: 'All Devices Protected Against Remote Coached Scams',
          desc: riskEvaluation.reasons?.[0] || 'Device behavioral baseline is normal. No unauthorized screen viewing or coached exfiltration signals.',
          icon: ShieldCheck,
          iconColor: 'text-emerald-400',
          iconBg: 'bg-emerald-500/20 border-emerald-500/40',
          badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50'
        };
    }
  };

  const statusTheme = getStatusTheme();
  const StatusIcon = statusTheme.icon;

  if (isLoading && !session) {
    return (
      <div className="space-y-6 pb-12 animate-pulse">
        <div className="h-36 bg-slate-850 rounded-2xl border border-slate-800" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 bg-slate-850 rounded-xl border border-slate-800" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="h-64 bg-slate-850 rounded-2xl border border-slate-800" />
          <div className="h-64 lg:col-span-2 bg-slate-850 rounded-2xl border border-slate-800" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-16 max-w-6xl mx-auto">
      
      {/* 1. Hero Protection Banner */}
      <div className={`clean-card p-6 md:p-7 border ${statusTheme.border} ${statusTheme.cardBg} transition-all duration-300`}>
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-5">
          <div className="flex items-start gap-4">
            <div className={`p-3.5 rounded-2xl border shrink-0 ${statusTheme.iconBg} ${statusTheme.iconColor}`}>
              <StatusIcon className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold tracking-wider uppercase border font-mono ${statusTheme.badge}`}>
                  ● {statusTheme.title}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Session: <span className="text-slate-200">{session?.session_id || 'demo-session-live'}</span>
                </span>
              </div>
              <h2 className="text-xl md:text-2xl font-black text-white mt-1 tracking-tight">
                {statusTheme.headline}
              </h2>
              <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
                {statusTheme.desc}
              </p>
            </div>
          </div>

          {/* Banner Actions */}
          <div className="flex items-center gap-3 w-full lg:w-auto shrink-0 justify-end">
            {riskEvaluation.risk_level === 'THREAT_DETECTED' && (
              <button
                onClick={() => setIsInterventionModalOpen(true)}
                className="flex-1 lg:flex-none px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold transition-all shadow-lg shadow-red-950/50 flex items-center justify-center gap-1.5 animate-pulse"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>Open Scam Alert</span>
              </button>
            )}
            <button
              onClick={() => setCurrentTab('live')}
              className="flex-1 lg:flex-none px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold transition-all shadow-lg shadow-cyan-950/50 flex items-center justify-center gap-1.5"
            >
              <span>Live Protection & Simulator</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Key Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Metric 1 */}
        <div className="clean-card p-5 clean-card-hover flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Protected Sessions</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-black text-white font-mono">{metrics.today_protected_sessions}</p>
            <div className="flex items-center gap-1.5 mt-1 text-[11px] text-emerald-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Real-time device monitoring</span>
            </div>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="clean-card p-5 clean-card-hover flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Threats Flagged</span>
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-black text-amber-400 font-mono">{metrics.threats_detected}</p>
            <div className="flex items-center gap-1.5 mt-1 text-[11px] text-amber-400/90 font-medium">
              <span>Coached patterns intercepted</span>
            </div>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="clean-card p-5 clean-card-hover flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Transfers Blocked</span>
            <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
              <ShieldX className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-black text-red-400 font-mono">{metrics.transactions_interrupted}</p>
            <div className="flex items-center gap-1.5 mt-1 text-[11px] text-red-400/90 font-medium">
              <span>Zero victim fund loss</span>
            </div>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="clean-card p-5 clean-card-hover flex flex-col justify-between bg-gradient-to-br from-[#0b1122] to-cyan-950/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Capital Protected</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <IndianRupee className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-black text-cyan-400 font-mono">
              ₹{Number(metrics.total_interrupted_amount_inr || 425000).toLocaleString('en-IN')}
            </p>
            <div className="flex items-center gap-1.5 mt-1 text-[11px] text-cyan-300 font-medium font-mono">
              <span>Prevented exfiltration (INR)</span>
            </div>
          </div>
        </div>

      </div>

      {/* 3. Core Risk Evaluation & Granular Risk Factors */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left: Live Risk Assessment Gauge */}
        <div className="clean-card p-6 flex flex-col items-center justify-center text-center">
          <div className="flex items-center justify-between w-full border-b border-slate-800/80 pb-3 mb-4">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
              Live Threat Level
            </span>
            <span className="text-[11px] text-slate-500 font-mono">
              Heuristic Engine v1
            </span>
          </div>
          
          <div className="my-2">
            <RiskGauge score={riskEvaluation.risk_score} level={riskEvaluation.risk_level} size="large" />
          </div>

          <div className="w-full mt-4 pt-3 border-t border-slate-800/80 text-left space-y-1 text-xs">
            <div className="flex justify-between text-slate-400">
              <span>Action Recommendation:</span>
              <strong className={`font-mono font-bold ${
                riskEvaluation.recommended_action === 'INTERVENE' ? 'text-red-400' :
                riskEvaluation.recommended_action === 'MONITOR' ? 'text-amber-400' : 'text-emerald-400'
              }`}>
                {riskEvaluation.recommended_action || 'NONE'}
              </strong>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Last Evaluated:</span>
              <span className="font-mono text-slate-300">
                {new Date(riskEvaluation.evaluated_at || Date.now()).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Granular Risk Factors Breakdown */}
        <div className="clean-card p-6 lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Active Risk Factors & Signal Correlation</h3>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                {riskEvaluation.risk_factors?.length || 0} Flags Triggered
              </span>
            </div>

            {(!riskEvaluation.risk_factors || riskEvaluation.risk_factors.length === 0) ? (
              <div className="py-8 text-center text-slate-500">
                <CheckCircle2 className="w-9 h-9 mx-auto mb-2 text-emerald-500/60" />
                <p className="text-xs font-semibold text-slate-300">Baseline Behaviour Clean</p>
                <p className="text-[11px] text-slate-500 mt-1 max-w-sm mx-auto">
                  No risk triggers currently active. Launch the scam scenario in the Live Protection tab to see simulated risk factor escalation.
                </p>
              </div>
            ) : (
              <div className="space-y-2.5">
                {riskEvaluation.risk_factors.map((factor, idx) => {
                  const getSeverityStyle = (sev) => {
                    switch (sev) {
                      case 'CRITICAL':
                        return 'bg-red-500/20 text-red-300 border-red-500/50';
                      case 'HIGH':
                        return 'bg-rose-500/20 text-rose-300 border-rose-500/50';
                      case 'MEDIUM':
                        return 'bg-amber-500/20 text-amber-300 border-amber-500/50';
                      default:
                        return 'bg-blue-500/20 text-blue-300 border-blue-500/50';
                    }
                  };

                  return (
                    <div 
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start justify-between gap-3 text-xs"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold border font-mono uppercase ${getSeverityStyle(factor.severity)}`}>
                            {factor.severity}
                          </span>
                          <span className="font-bold text-slate-200">{factor.name}</span>
                        </div>
                        <p className="text-slate-400 text-[11px] mt-1 leading-snug">
                          {factor.description}
                        </p>
                      </div>
                      <div className="shrink-0 text-right font-mono">
                        <span className="text-xs font-bold text-cyan-400">+{factor.weight}%</span>
                        <span className="block text-[10px] text-slate-500">Weight</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Lock className="w-3 h-3 text-cyan-400" />
              <span>Behavioural Telemetry Guard</span>
            </span>
            <span className="text-slate-400">Strict Zero-PII Compliance</span>
          </div>
        </div>

      </div>

      {/* 4. Live Telemetry & Behavioural Signals (4 Cards) */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>Active Behavioural Signals</span>
          </h3>
          <span className="text-xs text-slate-400 font-mono">Device-Side Sensors</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Signal 1: Screen Sharing */}
          <div className={`clean-card p-5 flex flex-col justify-between border ${
            activeTelemetry.screenSharing.active ? 'border-red-500/50 bg-red-950/15' : 'border-slate-800'
          }`}>
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-semibold text-slate-400">Screen Sharing</span>
                <Monitor className={`w-4 h-4 ${activeTelemetry.screenSharing.active ? 'text-red-400' : 'text-slate-500'}`} />
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  activeTelemetry.screenSharing.active ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'
                }`} />
                <h4 className="text-sm font-bold text-white">
                  {activeTelemetry.screenSharing.active ? 'Active Mirroring' : 'No Screen Sharing'}
                </h4>
              </div>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Tool: <strong className="text-slate-200">{activeTelemetry.screenSharing.tool}</strong>
              </p>
              {activeTelemetry.screenSharing.active && (
                <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                  Host: {activeTelemetry.screenSharing.remoteHost}
                </p>
              )}
            </div>

            <div className="mt-4 pt-2.5 border-t border-slate-800/80 text-[11px] font-medium">
              {activeTelemetry.screenSharing.active ? (
                <span className="text-red-400">⚠️ Third party has live screen view</span>
              ) : (
                <span className="text-emerald-400">✓ Display strictly private</span>
              )}
            </div>
          </div>

          {/* Signal 2: Banking App Guard */}
          <div className={`clean-card p-5 flex flex-col justify-between border ${
            activeTelemetry.bankingApp.active ? 'border-cyan-500/50 bg-cyan-950/15' : 'border-slate-800'
          }`}>
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-semibold text-slate-400">Banking App Guard</span>
                <Smartphone className={`w-4 h-4 ${activeTelemetry.bankingApp.active ? 'text-cyan-400' : 'text-slate-500'}`} />
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  activeTelemetry.bankingApp.active ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'
                }`} />
                <h4 className="text-sm font-bold text-white">
                  {activeTelemetry.bankingApp.active ? 'Banking App Active' : 'No Banking Session'}
                </h4>
              </div>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Target: <strong className="text-slate-200">{activeTelemetry.bankingApp.app}</strong>
              </p>
              {activeTelemetry.bankingApp.active && (
                <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                  Auth: {activeTelemetry.bankingApp.authMethod}
                </p>
              )}
            </div>

            <div className="mt-4 pt-2.5 border-t border-slate-800/80 text-[11px] font-medium">
              {activeTelemetry.bankingApp.active && activeTelemetry.screenSharing.active ? (
                <span className="text-red-400 font-bold">⚠️ CRITICAL: Banking + Screen Share</span>
              ) : activeTelemetry.bankingApp.active ? (
                <span className="text-cyan-400">● Banking app in foreground</span>
              ) : (
                <span className="text-slate-500">✓ Inactive baseline</span>
              )}
            </div>
          </div>

          {/* Signal 3: Beneficiary & Payee Watch */}
          <div className={`clean-card p-5 flex flex-col justify-between border ${
            activeTelemetry.beneficiary.active || activeTelemetry.transaction.active
              ? 'border-purple-500/50 bg-purple-950/15' 
              : 'border-slate-800'
          }`}>
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-semibold text-slate-400">Payee & Transfer</span>
                <UserPlus className={`w-4 h-4 ${activeTelemetry.beneficiary.active ? 'text-purple-400' : 'text-slate-500'}`} />
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  activeTelemetry.beneficiary.active ? 'bg-purple-400 animate-pulse' : 'bg-slate-600'
                }`} />
                <h4 className="text-sm font-bold text-white">
                  {activeTelemetry.transaction.active ? `Transfer: ₹${Number(activeTelemetry.transaction.amount).toLocaleString('en-IN')}` :
                   activeTelemetry.beneficiary.active ? 'New Payee Added' : 'No Transfer Initiated'}
                </h4>
              </div>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Payee: <strong className="text-slate-200">{activeTelemetry.beneficiary.label || 'None'}</strong>
              </p>
              {activeTelemetry.beneficiary.pasteDetected && (
                <p className="text-[10px] text-purple-400 font-mono mt-0.5">
                  ⚡ Rapid clipboard paste ({activeTelemetry.beneficiary.creationSpeedMs}ms)
                </p>
              )}
            </div>

            <div className="mt-4 pt-2.5 border-t border-slate-800/80 text-[11px] font-medium">
              {activeTelemetry.transaction.active ? (
                <span className="text-purple-300 font-mono">{activeTelemetry.transaction.rail} High Value</span>
              ) : (
                <span className="text-slate-500">✓ No pending outbound funds</span>
              )}
            </div>
          </div>

          {/* Signal 4: Coached Cadence Sensor */}
          <div className={`clean-card p-5 flex flex-col justify-between border ${
            activeTelemetry.coachedCadence.active ? 'border-amber-500/50 bg-amber-950/15' : 'border-slate-800'
          }`}>
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-semibold text-slate-400">Coached Cadence</span>
                <Sparkles className={`w-4 h-4 ${activeTelemetry.coachedCadence.active ? 'text-amber-400' : 'text-slate-500'}`} />
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  activeTelemetry.coachedCadence.active ? 'bg-amber-400 animate-pulse' : 'bg-slate-600'
                }`} />
                <h4 className="text-sm font-bold text-white">
                  {activeTelemetry.coachedCadence.active ? 'Coached Anomaly' : 'Natural Touch Flow'}
                </h4>
              </div>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Variance: <strong className="text-slate-200">
                  {activeTelemetry.coachedCadence.active ? activeTelemetry.coachedCadence.varianceScore : 'Normal'}
                </strong>
              </p>
              {activeTelemetry.coachedCadence.rapidSwitch && (
                <p className="text-[10px] text-amber-400 font-mono mt-0.5">
                  ⚡ Rapid app switching correlation
                </p>
              )}
            </div>

            <div className="mt-4 pt-2.5 border-t border-slate-800/80 text-[11px] font-medium">
              {activeTelemetry.coachedCadence.active ? (
                <span className="text-amber-400 font-bold">⚠️ Remote guidance signature</span>
              ) : (
                <span className="text-emerald-400">✓ Natural interaction cadence</span>
              )}
            </div>
          </div>

        </div>
      </div>

      {/* 5. Recent Security Events */}
      <div className="clean-card p-6">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Recent Security Telemetry Events</h3>
          </div>
          <button
            onClick={() => setCurrentTab('timeline')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 transition-colors"
          >
            <span>View Security Timeline</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {events.length === 0 ? (
          <div className="py-8 text-center text-slate-500">
            <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-slate-600" />
            <p className="text-xs font-semibold">No recent security anomalies recorded.</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Switch to Live Protection to run the demo simulation scenario.</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {events.slice(0, 5).map((ev, idx) => {
              const isThreat = ev.event_type.includes('COACHED') || ev.event_type.includes('INTERVENTION');
              const isWarning = ev.event_type.includes('SCREEN') || ev.event_type.includes('TRANSACTION') || ev.event_type.includes('BENEFICIARY');

              return (
                <div
                  key={ev.event_id || idx}
                  className={`flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 rounded-xl border text-xs gap-2 transition-all ${
                    isThreat 
                      ? 'bg-red-950/20 border-red-500/40 text-red-200' 
                      : isWarning 
                      ? 'bg-amber-950/15 border-amber-500/30 text-amber-200'
                      : 'bg-slate-900/80 border-slate-800 text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                      isThreat ? 'bg-red-400 animate-pulse' : isWarning ? 'bg-amber-400' : 'bg-cyan-400'
                    }`} />
                    <div>
                      <span className="font-bold text-white">{ev.event_type.replace(/_/g, ' ')}</span>
                      {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {Object.entries(ev.metadata).slice(0, 3).map(([k, v]) => (
                            <span key={k} className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-950/80 text-slate-400 border border-slate-800">
                              {k}: <span className="text-slate-200">{String(v)}</span>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <span className="text-slate-500 font-mono text-[11px] shrink-0 self-end sm:self-center">
                    {new Date(ev.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
};

export default HomeDashboard;
