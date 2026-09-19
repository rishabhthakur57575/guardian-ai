import React, { useState } from 'react';
import { 
  Clock, Monitor, Smartphone, UserPlus, IndianRupee, Sparkles, 
  AlertOctagon, CheckCircle2, ShieldCheck, ShieldAlert, ShieldX, 
  Filter, Search, Lock, RefreshCw, Calendar, ArrowRight, Activity
} from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';

export const SecurityTimeline = () => {
  const { 
    session, 
    events, 
    sessionsList, 
    selectedTimelineSessionId, 
    selectedTimelineSessionData, 
    selectTimelineSession,
    isLoading 
  } = useSecurity();

  const [activeFilter, setActiveFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Determine active session data
  const currentSessionData = selectedTimelineSessionId === session?.session_id
    ? session
    : selectedTimelineSessionData || session;

  const rawEvents = currentSessionData?.events && currentSessionData.events.length > 0
    ? currentSessionData.events
    : events;

  const getEventMeta = (eventType) => {
    switch (eventType) {
      case 'SCREEN_SHARING_STARTED':
        return { 
          icon: Monitor, 
          label: 'Screen sharing started', 
          desc: 'Remote desktop mirroring connection initiated by third party.',
          color: 'text-amber-400 bg-amber-500/15 border-amber-500/40',
          severity: 'HIGH_ALERT'
        };
      case 'BANKING_APP_FOREGROUNDED':
        return { 
          icon: Smartphone, 
          label: 'Banking app opened', 
          desc: 'Financial application foregrounded while screen visibility active.',
          color: 'text-cyan-400 bg-cyan-500/15 border-cyan-500/40',
          severity: 'MONITORING'
        };
      case 'NEW_BENEFICIARY_ADDED':
        return { 
          icon: UserPlus, 
          label: 'New beneficiary added', 
          desc: 'Rapid payee addition via clipboard paste in under 4 seconds.',
          color: 'text-purple-400 bg-purple-500/15 border-purple-500/40',
          severity: 'SUSPICIOUS'
        };
      case 'HIGH_VALUE_TRANSACTION_INITIATED':
        return { 
          icon: IndianRupee, 
          label: 'High-value transaction initiated', 
          desc: 'Instant IMPS outbound transfer exceeds typical baseline threshold.',
          color: 'text-amber-400 bg-amber-500/15 border-amber-500/40',
          severity: 'CRITICAL_RISK'
        };
      case 'COACHED_BEHAVIOUR_TRIGGERED':
        return { 
          icon: Sparkles, 
          label: 'Coached behaviour pattern detected', 
          desc: 'Sensor telemetry confirms voice coaching cadence & app switching.',
          color: 'text-red-400 bg-red-500/15 border-red-500/40',
          severity: 'SCAM_DETECTED'
        };
      case 'INTERVENTION_TRIGGERED':
        return { 
          icon: AlertOctagon, 
          label: 'Scam intervention triggered', 
          desc: 'Warning modal presented to user. Outbound transfer halted.',
          color: 'text-red-400 bg-red-500/20 border-red-500/50',
          severity: 'INTERVENTION'
        };
      default:
        return { 
          icon: Clock, 
          label: eventType.replace(/_/g, ' '), 
          desc: 'Device telemetry event recorded.',
          color: 'text-slate-400 bg-slate-800 border-slate-700',
          severity: 'INFO'
        };
    }
  };

  const getOutcomeBadge = (outcome, score) => {
    if (outcome === 'INTERRUPTED') {
      return (
        <span className="px-3 py-1 rounded-full bg-red-500/15 border border-red-500/40 text-red-300 font-bold text-xs flex items-center gap-1.5 font-mono">
          <ShieldX className="w-3.5 h-3.5 text-red-400" />
          <span>INTERRUPTED (SCAM BLOCKED)</span>
        </span>
      );
    } else if (outcome === 'ALLOWED') {
      return (
        <span className="px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 font-bold text-xs flex items-center gap-1.5 font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>ALLOWED (USER TRUSTED)</span>
        </span>
      );
    } else {
      return (
        <span className="px-3 py-1 rounded-full bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 font-bold text-xs flex items-center gap-1.5 font-mono">
          <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>ACTIVE MONITORING</span>
        </span>
      );
    }
  };

  // Filter events
  const filteredEvents = rawEvents.filter((ev) => {
    if (activeFilter === 'THREATS' && !(ev.event_type.includes('COACHED') || ev.event_type.includes('INTERVENTION') || ev.event_type.includes('TRANSACTION'))) {
      return false;
    }
    if (activeFilter === 'SCREEN' && !ev.event_type.includes('SCREEN')) {
      return false;
    }
    if (activeFilter === 'BANKING' && !ev.event_type.includes('BANKING')) {
      return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchType = ev.event_type.toLowerCase().includes(q);
      const matchMeta = JSON.stringify(ev.metadata || {}).toLowerCase().includes(q);
      return matchType || matchMeta;
    }
    return true;
  });

  return (
    <div className="space-y-6 pb-16 max-w-5xl mx-auto">
      
      {/* 1. Header & Session Selector */}
      <div className="clean-card p-6 border border-slate-800">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-cyan-400" />
              <h2 className="text-xl font-bold text-white tracking-tight">Security Audit Timeline</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Forensic behavioral telemetry and anomaly correlation log per monitored session.
            </p>
          </div>

          {/* Session Switcher */}
          <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto">
            <span className="text-xs text-slate-400 font-mono">Inspect Session:</span>
            <select
              value={selectedTimelineSessionId}
              onChange={(e) => selectTimelineSession(e.target.value)}
              className="bg-slate-900 text-slate-200 border border-slate-700 rounded-xl px-3 py-1.5 text-xs font-mono font-semibold focus:outline-none focus:border-cyan-500 cursor-pointer"
            >
              {sessionsList.map((s) => (
                <option key={s.session_id} value={s.session_id}>
                  {s.session_id} ({s.final_outcome || 'ACTIVE'} • Risk {Math.round(s.risk_score)}%)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected Session Metadata Banner */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <span className="text-[10px] text-slate-500 font-mono uppercase block">Session ID</span>
              <strong className="font-mono text-cyan-400">{currentSessionData?.session_id || selectedTimelineSessionId}</strong>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 font-mono uppercase block">Start Time</span>
              <span className="font-mono text-slate-300">
                {currentSessionData?.start_time ? new Date(currentSessionData.start_time).toLocaleString() : 'Active'}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 font-mono uppercase block">Recorded Events</span>
              <span className="font-mono text-slate-300 font-bold">{rawEvents.length}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 font-mono uppercase block">Assessed Risk</span>
              <span className="font-mono text-red-400 font-bold">
                {Math.round(currentSessionData?.risk_score || 0)}% ({currentSessionData?.risk_level || 'SAFE'})
              </span>
            </div>
          </div>

          {getOutcomeBadge(currentSessionData?.final_outcome, currentSessionData?.risk_score)}
        </div>
      </div>

      {/* 2. Filters & Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-1.5 bg-[#0b1122] p-1 rounded-xl border border-slate-800">
          {[
            { id: 'ALL', label: 'All Events' },
            { id: 'THREATS', label: 'Threats & High-Risk' },
            { id: 'SCREEN', label: 'Screen Share' },
            { id: 'BANKING', label: 'Banking Flow' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeFilter === tab.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search event telemetry..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full sm:w-64 bg-[#0b1122] border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>
      </div>

      {/* 3. Vertical Timeline Stream */}
      <div className="clean-card p-6 md:p-8">
        {filteredEvents.length === 0 ? (
          <div className="py-16 text-center text-slate-500">
            <CheckCircle2 className="w-10 h-10 mx-auto mb-2 text-slate-600" />
            <h4 className="text-sm font-bold text-slate-300">No Events Match Filter</h4>
            <p className="text-xs text-slate-500 mt-1">Try selecting a different filter or advance the simulator in Live Protection.</p>
          </div>
        ) : (
          <div className="relative pl-7 md:pl-9 border-l-2 border-slate-800 space-y-7">
            {filteredEvents.map((ev, idx) => {
              const meta = getEventMeta(ev.event_type);
              const Icon = meta.icon;
              const dateObj = new Date(ev.timestamp);
              const timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

              return (
                <div key={ev.event_id || idx} className="relative group animate-fade-in">
                  
                  {/* Timeline Node Dot */}
                  <div className={`absolute -left-[41px] md:-left-[49px] top-1.5 w-7 h-7 md:w-8 md:h-8 rounded-full flex items-center justify-center border shadow-md ${meta.color}`}>
                    <Icon className="w-3.5 h-3.5 md:w-4 md:h-4" />
                  </div>

                  {/* Event Content Card */}
                  <div className="p-4 md:p-5 rounded-2xl bg-slate-900/80 border border-slate-800 clean-card-hover text-xs">
                    
                    {/* Top Row: Timestamp + Severity Badge */}
                    <div className="flex items-center justify-between mb-1.5 flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-cyan-400 text-xs">
                          {timeStr}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          • Step #{idx + 1}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full uppercase font-bold bg-slate-950 text-slate-400 border border-slate-800">
                          {meta.severity}
                        </span>
                        <span className="text-[9px] font-mono text-slate-500">
                          {ev.event_id}
                        </span>
                      </div>
                    </div>

                    {/* Headline */}
                    <h4 className="text-sm md:text-base font-bold text-white mt-1">
                      {meta.label}
                    </h4>
                    <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">
                      {meta.desc}
                    </p>

                    {/* Metadata Parameter Chips */}
                    {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                        <span className="text-[10px] text-slate-400 font-mono uppercase block mb-1.5 font-bold">
                          Captured Telemetry Parameters:
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {Object.entries(ev.metadata).map(([k, v]) => (
                            <span
                              key={k}
                              className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-950 text-slate-300 border border-slate-800 flex items-center gap-1"
                            >
                              <span className="text-slate-500">{k}:</span>
                              <strong className="text-cyan-300">{String(v)}</strong>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Privacy Footer */}
                    <div className="mt-3 pt-2 border-t border-slate-800/50 flex items-center justify-between text-[10px] text-slate-500">
                      <span className="flex items-center gap-1">
                        <Lock className="w-3 h-3 text-cyan-400" />
                        <span>Device-Local Behavioural Signal</span>
                      </span>
                      <span>Verified Zero PII</span>
                    </div>

                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
};

export default SecurityTimeline;
