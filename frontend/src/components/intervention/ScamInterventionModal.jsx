import React, { useState } from 'react';
import { 
  AlertTriangle, ShieldAlert, Check, X, ShieldX, 
  HelpCircle, PhoneCall, Info, Lock, ArrowRight, AlertCircle 
} from 'lucide-react';
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
    'A new beneficiary payee was added in rapid succession.',
    'A high-value fund transfer of ₹1,85,000 is queued to be sent.'
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

  const transferAmount = activeTelemetry.transaction.amount || 185000;
  const payeeLabel = activeTelemetry.transaction.beneficiary || activeTelemetry.beneficiary.label || 'Fast_Reversal_Desk_94';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md overflow-y-auto animate-fade-in">
      <div className="relative w-full max-w-xl bg-[#0d1424] border-2 border-red-500/80 rounded-2xl shadow-2xl shadow-red-950/80 p-6 md:p-8 text-white">
        
        {/* Top Alert Header */}
        <div className="flex items-start gap-4 border-b border-slate-800 pb-5 mb-5">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-red-600 to-rose-700 flex items-center justify-center shrink-0 shadow-lg shadow-red-950/60 ring-2 ring-red-400/40">
            <ShieldAlert className="w-8 h-8 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-black uppercase tracking-wider text-red-300 bg-red-950 px-2.5 py-0.5 rounded-full border border-red-700/60 font-mono">
                Urgent Security Interception
              </span>
              <span className="text-xs text-red-400 font-mono font-bold">
                Risk: {Math.round(riskEvaluation.risk_score || 94)}%
              </span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-white mt-1 tracking-tight">
              POSSIBLE SCAM DETECTED
            </h2>
          </div>
        </div>

        {/* Clear Primary Warning for Elderly / Non-Technical Users */}
        <div className="bg-red-950/40 border border-red-500/40 rounded-xl p-4 mb-5">
          <p className="text-base md:text-lg font-bold text-red-200 leading-snug">
            Someone may be remotely guiding you through this banking transaction.
          </p>
          <div className="mt-2 flex items-start gap-2 text-xs text-slate-300">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <p>
              Banks, police, electricity boards, and customer care will <strong>never</strong> ask you to install screen sharing tools (AnyDesk, TeamViewer) or send money to receive a refund or KYC update.
            </p>
          </div>
        </div>

        {/* Plain Language Detected Reasons */}
        <div className="mb-5">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5 font-mono">
            Why GuardianAI stopped this transfer:
          </h3>
          <ul className="space-y-2">
            {reasons.map((reason, idx) => (
              <li 
                key={idx} 
                className="flex items-start gap-3 text-xs md:text-sm bg-slate-900/90 p-3 rounded-xl border border-slate-800 text-slate-200"
              >
                <div className="w-5 h-5 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                  !
                </div>
                <span className="font-medium leading-snug">{reason}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Transaction Summary Box */}
        <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between mb-5">
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono">Pending Transfer</span>
            <p className="text-xl md:text-2xl font-black text-amber-400 font-mono">
              ₹{Number(transferAmount).toLocaleString('en-IN')}
            </p>
            <span className="text-[11px] text-slate-400">
              Recipient: <strong className="text-slate-200 font-mono">{payeeLabel}</strong>
            </span>
          </div>

          <div className="text-right">
            <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono">Status</span>
            <div className="px-2.5 py-1 rounded-full bg-red-500/20 border border-red-500/50 text-red-300 font-mono font-bold text-xs mt-1">
              PAUSED FOR SAFETY
            </div>
          </div>
        </div>

        {/* Double-confirmation warning if trust clicked */}
        {confirmOverride && (
          <div className="mb-5 p-4 rounded-xl bg-amber-950/60 border border-amber-500 text-amber-200 text-xs animate-fade-in">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-sm text-white">Do you personally know this person in real life?</p>
                <p className="text-slate-300 mt-1 leading-relaxed">
                  If they contacted you unexpectedly claiming to be bank support, refund agents, or government officials, this is a fraudulent scam. Proceeding will send non-refundable funds.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* High Impact Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Primary Cancel Button */}
          <button
            onClick={handleCancel}
            className="flex-1 py-4 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-green-500 text-white font-black text-base md:text-lg transition-all shadow-xl shadow-emerald-950/50 flex items-center justify-center gap-2.5"
          >
            <ShieldX className="w-6 h-6 shrink-0" />
            <span>Cancel Transaction</span>
            <span className="text-[10px] bg-emerald-950 text-emerald-200 px-2 py-0.5 rounded-full uppercase font-mono font-extrabold ml-1">
              Recommended
            </span>
          </button>

          {/* Secondary Trust Button */}
          <button
            onClick={handleTrust}
            className={`py-3.5 px-4 rounded-xl text-xs font-bold border transition-all ${
              confirmOverride
                ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-300 shadow-lg font-black'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
            }`}
          >
            {confirmOverride ? 'Confirm: I Take Full Risk & Trust Payee' : 'I Trust This Person'}
          </button>
        </div>

        {/* Reassurance text */}
        <div className="text-center mt-4">
          <p className="text-[11px] text-slate-400">
            Cancelling stops the transaction immediately. Your account balance remains completely safe.
          </p>
          <button
            onClick={() => {
              setIsInterventionModalOpen(false);
              setConfirmOverride(false);
            }}
            className="text-[11px] text-slate-500 hover:text-slate-300 underline mt-2 block mx-auto"
          >
            Close modal (demo preview)
          </button>
        </div>

      </div>
    </div>
  );
};

export default ScamInterventionModal;
