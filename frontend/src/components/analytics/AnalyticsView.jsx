import React from 'react';
import { 
  ResponsiveContainer, AreaChart, Area, BarChart, Bar, XAxis, YAxis, 
  Tooltip, CartesianGrid, Cell 
} from 'recharts';
import { useSecurity } from '../../context/SecurityContext';

const COLORS = ['#10b981', '#06b6d4', '#f59e0b', '#f97316', '#ef4444'];

export const AnalyticsView = () => {
  const { analytics } = useSecurity();

  const timelineData = analytics?.protected_sessions_timeline || [
    { time: '00:00', safe_sessions: 8, suspicious_sessions: 0 },
    { time: '04:00', safe_sessions: 4, suspicious_sessions: 0 },
    { time: '08:00', safe_sessions: 22, suspicious_sessions: 1 },
    { time: '12:00', safe_sessions: 45, suspicious_sessions: 4 },
    { time: '16:00', safe_sessions: 56, suspicious_sessions: 3 },
    { time: '20:00', safe_sessions: 38, suspicious_sessions: 2 },
    { time: 'Now', safe_sessions: 28, suspicious_sessions: 2 },
  ];

  const patternData = analytics?.scam_pattern_frequencies || [
    { pattern_name: 'Screen Share + Instant Beneficiary', count: 14 },
    { pattern_name: 'Fake Refund Coached Flow', count: 8 },
    { pattern_name: 'Urgent KYC Verification Mirror', count: 5 },
    { pattern_name: 'Rapid Clipboard Anomaly', count: 3 },
  ];

  const riskDistData = analytics?.risk_distribution || [
    { range: '0-20 Safe', count: 38 },
    { range: '21-40 Normal', count: 19 },
    { range: '41-60 Caution', count: 8 },
    { range: '61-80 Elevated', count: 5 },
    { range: '81-100 Scam', count: 7 },
  ];

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto">
      {/* Header */}
      <div className="clean-card p-6">
        <h2 className="text-lg font-bold text-white">Security & Threat Analytics</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Aggregated behavioural telemetry and scam pattern distributions.
        </p>
      </div>

      {/* Grid of 3 Clean Essential Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* 1. Protected Sessions vs Suspicious Sessions */}
        <div className="clean-card p-5">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-1">
            Protected Sessions vs Suspicious Sessions
          </h3>
          <p className="text-[11px] text-slate-500 mb-4">24-hour timeline</p>
          
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timelineData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="safe_sessions" name="Protected Safe" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.2} strokeWidth={2} />
                <Area type="monotone" dataKey="suspicious_sessions" name="Suspicious Flagged" stroke="#ef4444" fill="#ef4444" fillOpacity={0.4} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Scam Pattern Frequency */}
        <div className="clean-card p-5">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-1">
            Scam Pattern Frequency
          </h3>
          <p className="text-[11px] text-slate-500 mb-4">Identified coached attack types</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={patternData} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="pattern_name" type="category" stroke="#64748b" fontSize={10} width={130} tickFormatter={(v) => v.length > 20 ? `${v.substring(0, 20)}...` : v} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" name="Incidents" fill="#f59e0b" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Risk Distribution (Spans across or 2nd row) */}
        <div className="clean-card p-5 lg:col-span-2">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-1">
            Risk Score Distribution
          </h3>
          <p className="text-[11px] text-slate-500 mb-4">Distribution across monitored sessions</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="range" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" name="Sessions Count" radius={[4, 4, 0, 0]}>
                  {riskDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AnalyticsView;
