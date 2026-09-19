import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export const RiskGauge = ({ score = 0, level = 'SAFE', size = 'normal' }) => {
  const safeScore = Math.min(Math.max(Number(score) || 0, 0), 100);

  let strokeColor = '#10b981'; // emerald
  let textColor = 'text-emerald-400';
  let glowColor = 'rgba(16, 185, 129, 0.25)';
  let badgeClass = 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40';
  let LevelIcon = ShieldCheck;
  let levelText = 'SAFE';

  if (level === 'THREAT_DETECTED' || safeScore >= 70) {
    strokeColor = '#ef4444'; // red
    textColor = 'text-red-400';
    glowColor = 'rgba(239, 68, 68, 0.35)';
    badgeClass = 'bg-red-500/20 text-red-300 border-red-500/50 shadow-lg shadow-red-950/60';
    LevelIcon = ShieldAlert;
    levelText = 'THREAT DETECTED';
  } else if (level === 'MONITORING' || safeScore >= 30) {
    strokeColor = '#f59e0b'; // amber
    textColor = 'text-amber-400';
    glowColor = 'rgba(245, 158, 11, 0.25)';
    badgeClass = 'bg-amber-500/15 text-amber-300 border-amber-500/40';
    LevelIcon = AlertTriangle;
    levelText = 'MONITORING';
  }

  const isLarge = size === 'large';
  const radius = isLarge ? 50 : 42;
  const strokeWidth = isLarge ? 8 : 7;
  const viewBoxSize = isLarge ? 130 : 110;
  const center = viewBoxSize / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (safeScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center">
        <svg 
          className={`${isLarge ? 'w-36 h-36' : 'w-28 h-28'} transform -rotate-90`}
          viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
        >
          <defs>
            <filter id={`gauge-glow-${safeScore}`} x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor={strokeColor} floodOpacity="0.6"/>
            </filter>
          </defs>
          
          {/* Background circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          
          {/* Progress circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            filter={`url(#gauge-glow-${safeScore})`}
            className="transition-all duration-700 ease-out"
            fill="transparent"
          />
        </svg>

        {/* Center content */}
        <div className="absolute flex flex-col items-center justify-center text-center select-none">
          <span className={`${isLarge ? 'text-3xl' : 'text-2xl'} font-extrabold font-mono tracking-tight ${textColor}`}>
            {Math.round(safeScore)}%
          </span>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold font-mono">
            Scam Risk
          </span>
        </div>
      </div>

      {/* Level badge */}
      <div className={`mt-2.5 px-3 py-1 rounded-full text-[11px] font-bold border flex items-center gap-1.5 uppercase tracking-wide ${badgeClass}`}>
        <LevelIcon className="w-3.5 h-3.5" />
        <span>{levelText}</span>
      </div>
    </div>
  );
};

export default RiskGauge;
