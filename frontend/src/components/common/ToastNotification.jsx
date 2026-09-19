import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-react';
import { useSecurity } from '../../context/SecurityContext';

export const ToastNotification = () => {
  const { toast, clearToast } = useSecurity();

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => {
      clearToast();
    }, 4000);
    return () => clearTimeout(timer);
  }, [toast, clearToast]);

  if (!toast) return null;

  const getToastStyle = () => {
    switch (toast.type) {
      case 'success':
        return {
          bg: 'bg-emerald-950/90 border-emerald-500/50 text-emerald-200',
          icon: CheckCircle2,
          iconColor: 'text-emerald-400'
        };
      case 'warning':
        return {
          bg: 'bg-amber-950/90 border-amber-500/50 text-amber-200',
          icon: AlertTriangle,
          iconColor: 'text-amber-400'
        };
      case 'error':
        return {
          bg: 'bg-red-950/90 border-red-500/50 text-red-200',
          icon: AlertCircle,
          iconColor: 'text-red-400'
        };
      case 'info':
      default:
        return {
          bg: 'bg-slate-900/90 border-cyan-500/50 text-cyan-200',
          icon: Info,
          iconColor: 'text-cyan-400'
        };
    }
  };

  const style = getToastStyle();
  const Icon = style.icon;

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-fade-in max-w-md w-full px-4">
      <div className={`p-4 rounded-xl border backdrop-blur-md shadow-2xl flex items-center justify-between gap-3 ${style.bg}`}>
        <div className="flex items-center gap-3">
          <Icon className={`w-5 h-5 shrink-0 ${style.iconColor}`} />
          <p className="text-xs font-semibold leading-snug">{toast.message}</p>
        </div>
        <button
          onClick={clearToast}
          className="text-slate-400 hover:text-white p-1 rounded-lg transition-colors shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default ToastNotification;
