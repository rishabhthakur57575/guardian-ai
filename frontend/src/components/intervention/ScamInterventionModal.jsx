import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, Check, X, ShieldX } from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';

export const ScamInterventionModal = () => {
  const { 
    isInterventionModalOpen, 
    setIsInterventionModalOpen, 
    riskEvaluation, 
    activeTelemetry, 
    handleInterventionAction 
  } = useSecurity();

  const [confirmOverride, setConfirmOverride] = useState(false);

  if (!isInterventionModalOpen) return null;

  const defaultReasons = [
    'A remote person is currently viewing your screen (AnyDesk / TeamViewer).',
    'A banking application was opened while screen sharing is active.',
    'A new beneficiary was added quickly.',
    'A large money transfer of ₹1,85,000 is about to be sent.'
  ];

  const reasons = (riskEvaluation.reasons && riskEvaluation.reasons.length > 0)
    ? riskEvaluation.reasons
    : defaultReasons;

  const handleCancel = () => {
    handleInterventionAction('CANCEL_TRANSACTION');
    setConfirmOverride(false);
  };

  const handleTrust = () => {
    if (!confirmOverride) {
      setConfirmOverride(true);
    } else {
      handleInterventionAction('TRUST_USER');
      setConfirmOverride(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div className="relative w-full max-w-xl bg-[#111827] border-2 border-red-500 rounded-2xl shadow-2xl p-6 md:p-8 text-white">
        
        {/* Header */}
        <div className="flex items-center gap-4 border-b border-slate-800 pb-5 mb-5">
          <div className="w-14 h-14 rounded-xl bg-red-600 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-8 h-8 text-white" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-red-400 bg-red-950/80 px-2 py-0.5 rounded border border-red-800/60">
              High Risk Warning
            </span>
            <h2 className="text-2xl md:text-3xl font-bold text-white mt-1">
              POSSIBLE SCAM DETECTED
            </h2>
          </div>
        </div>

        {/* Plain Language Reassurance */}
        <div className="bg-red-950/30 border border-red-500/30 rounded-xl p-4 mb-5">
          <p className="text-base font-semibold text-red-200 leading-snug">
            Someone on a phone call may be watching your screen while you send money.
          </p>
          <p className="text-sm text-slate-300 mt-1.5">
            Banks, electricity departments, and police will <strong>never</strong> ask you to share your screen to send money or receive refunds.
          </p>
        </div>

        {/* Detected Reasons */}
        <div className="mb-5">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Why GuardianAI flagged this transaction:
          </h3>
          <ul className="space-y-2">
            {reasons.map((reason, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-sm bg-slate-900 p-3 rounded-lg border border-slate-800">
                <span className="w-5 h-5 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                  !
                </span>
                <span className="text-slate-200 font-medium">{reason}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Transaction Amount Box */}
        <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl flex items-center justify-between mb-5">
          <div>
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Amount to be Sent</span>
            <p className="text-xl font-bold text-amber-400">₹1,85,000</p>
          </div>
          <div className="text-right">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Risk Score</span>
            <p className="text-sm font-bold text-red-400 font-mono">
              {Math.round(riskEvaluation.risk_score || 94)}% (CRITICAL)
            </p>
          </div>
        </div>

        {/* Double-confirmation warning if trust clicked */}
        {confirmOverride && (
          <div className="mb-5 p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/50 text-amber-200 text-xs">
            <p className="font-bold">Are you sure you know this person in real life?</p>
            <p className="text-slate-300 mt-0.5">If they asked you to install AnyDesk or TeamViewer, this is almost certainly a scam.</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Primary Cancel Button */}
          <button
            onClick={handleCancel}
            className="flex-1 py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-base transition-colors flex items-center justify-center gap-2"
          >
            <ShieldX className="w-5 h-5" />
            <span>Cancel Transaction</span>
            <span className="text-[10px] bg-emerald-950 px-1.5 py-0.5 rounded text-emerald-200 uppercase font-semibold">
              Recommended
            </span>
          </button>

          {/* Secondary Trust Button */}
          <button
            onClick={handleTrust}
            className={`py-3 px-4 rounded-xl text-xs font-semibold border transition-colors ${
              confirmOverride
                ? 'bg-amber-600 hover:bg-amber-500 text-black border-amber-400 font-bold'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
            }`}
          >
            {confirmOverride ? 'Confirm & Trust Person' : 'I Trust This Person'}
          </button>
        </div>

        {/* Dismiss for demo */}
        <div className="text-center mt-3">
          <button
            onClick={() => {
              setIsInterventionModalOpen(false);
              setConfirmOverride(false);
            }}
            className="text-[11px] text-slate-500 hover:text-slate-300 underline"
          >
            Close warning modal (demo)
          </button>
        </div>

      </div>
    </div>
  );
};

export default ScamInterventionModal;
