import React from 'react';
import { Clock, Monitor, Smartphone, UserPlus, IndianRupee, Sparkles, AlertOctagon } from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';

export const SecurityTimeline = () => {
  const { session, events } = useSecurity();

  const displayEvents = events.length > 0 ? events : [
    {
      event_type: 'SCREEN_SHARING_STARTED',
      timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
      metadata: { tool_name: 'AnyDesk Remote', screen_sharing_active: true }
    },
    {
      event_type: 'BANKING_APP_FOREGROUNDED',
      timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
      metadata: { app_name: 'HDFC Mobile Banking', banking_app_active: true }
    },
    {
      event_type: 'NEW_BENEFICIARY_ADDED',
      timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
      metadata: { beneficiary_label: 'Fast_Refund_Desk', paste_detected: true }
    },
    {
      event_type: 'HIGH_VALUE_TRANSACTION_INITIATED',
      timestamp: new Date(Date.now() - 1000 * 60 * 1).toISOString(),
      metadata: { transaction_amount: 185000, currency: 'INR' }
    },
    {
      event_type: 'COACHED_BEHAVIOUR_TRIGGERED',
      timestamp: new Date().toISOString(),
      metadata: { coached_anomaly: true }
    }
  ];

  const getEventMeta = (eventType) => {
    switch (eventType) {
      case 'SCREEN_SHARING_STARTED':
        return { icon: Monitor, label: 'Screen sharing started', color: 'text-amber-400 bg-amber-500/10' };
      case 'BANKING_APP_FOREGROUNDED':
        return { icon: Smartphone, label: 'Banking app opened', color: 'text-cyan-400 bg-cyan-500/10' };
      case 'NEW_BENEFICIARY_ADDED':
        return { icon: UserPlus, label: 'New beneficiary added', color: 'text-purple-400 bg-purple-500/10' };
      case 'HIGH_VALUE_TRANSACTION_INITIATED':
        return { icon: IndianRupee, label: '₹1,85,000 transfer initiated', color: 'text-amber-400 bg-amber-500/10' };
      case 'COACHED_BEHAVIOUR_TRIGGERED':
        return { icon: Sparkles, label: 'Suspicious behaviour detected', color: 'text-red-400 bg-red-500/10' };
      case 'INTERVENTION_TRIGGERED':
        return { icon: AlertOctagon, label: 'Scam intervention triggered', color: 'text-red-500 bg-red-500/20' };
      default:
        return { icon: Clock, label: eventType.replace(/_/g, ' '), color: 'text-slate-400 bg-slate-800' };
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto">
      {/* Header */}
      <div className="clean-card p-6 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Security Timeline</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Chronological audit log for session: <span className="font-mono text-slate-300">{session?.session_id || 'demo-session-live'}</span>
          </p>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300">
          Status: {session?.final_outcome || 'ACTIVE'}
        </span>
      </div>

      {/* Timeline Stream */}
      <div className="clean-card p-6">
        <div className="relative pl-6 border-l-2 border-slate-800 space-y-6">
          {displayEvents.map((ev, idx) => {
            const meta = getEventMeta(ev.event_type);
            const Icon = meta.icon;
            const timeStr = new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            return (
              <div key={idx} className="relative">
                {/* Dot */}
                <div className={`absolute -left-[35px] top-1 w-6 h-6 rounded-full flex items-center justify-center border border-slate-700 ${meta.color}`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>

                {/* Content */}
                <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-cyan-400">{timeStr}</span>
                    <span className="text-[10px] text-slate-500 font-mono">#{idx + 1}</span>
                  </div>
                  <h4 className="text-sm font-bold text-white">{meta.label}</h4>
                  
                  {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5 pt-1.5 border-t border-slate-800/60">
                      {Object.entries(ev.metadata).map(([k, v]) => (
                        <span key={k} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-950 text-slate-400">
                          {k}: <strong className="text-slate-200">{String(v)}</strong>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SecurityTimeline;
