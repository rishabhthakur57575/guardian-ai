import React from 'react';

export const RiskGauge = ({ score = 0, level = 'SAFE' }) => {
  let strokeColor = '#10b981'; // emerald
  let textColor = 'text-emerald-400';
  let badgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';

  if (level === 'THREAT_DETECTED' || score >= 70) {
    strokeColor = '#ef4444'; // red
    textColor = 'text-red-400';
    badgeClass = 'bg-red-500/10 text-red-400 border-red-500/30';
  } else if (level === 'MONITORING' || score >= 30) {
    strokeColor = '#f59e0b'; // amber
    textColor = 'text-amber-400';
    badgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  }

  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center">
        <svg className="w-28 h-28 transform -rotate-90">
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke="#1e293b"
            strokeWidth="6"
            fill="transparent"
          />
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke={strokeColor}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
            fill="transparent"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className={`text-2xl font-bold font-mono ${textColor}`}>
            {Math.round(score)}%
          </span>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-medium">
            Risk Score
          </span>
        </div>
      </div>
      <div className={`mt-2 px-2.5 py-0.5 rounded-md text-[11px] font-semibold border uppercase tracking-wide ${badgeClass}`}>
        {level.replace('_', ' ')}
      </div>
    </div>
  );
};

export default RiskGauge;
