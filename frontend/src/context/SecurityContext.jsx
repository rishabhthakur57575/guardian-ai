import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import apiService from '../services/api';

const SecurityContext = createContext(null);

export const SecurityProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState('demo-session-live');
  const [selectedScenarioId, setSelectedScenarioId] = useState('coached_scam');
  const [availableScenarios, setAvailableScenarios] = useState([]);
  const [session, setSession] = useState(null);
  const [sessionsList, setSessionsList] = useState([]);
  const [selectedTimelineSessionId, setSelectedTimelineSessionId] = useState('demo-session-live');
  const [selectedTimelineSessionData, setSelectedTimelineSessionData] = useState(null);
  
  const [events, setEvents] = useState([]);
  const [riskEvaluation, setRiskEvaluation] = useState({
    session_id: 'demo-session-live',
    risk_score: 0.0,
    risk_level: 'SAFE',
    reasons: ['Normal device behavioural baseline maintained.'],
    risk_factors: [],
    recommended_action: 'NONE',
    evaluated_at: new Date().toISOString()
  });

  const [analytics, setAnalytics] = useState(null);
  const [simulatorState, setSimulatorState] = useState({ current_step: 0, total_steps: 6, steps_catalog: [] });
  const [isInterventionModalOpen, setIsInterventionModalOpen] = useState(false);
  const [isAutoSimulating, setIsAutoSimulating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isBackendOnline, setIsBackendOnline] = useState(true);
  const [backendHealth, setBackendHealth] = useState(null);
  const [error, setError] = useState(null);
  const [toast, setToastState] = useState(null);

  const autoPlayTimerRef = useRef(null);

  const showToast = useCallback((message, type = 'info') => {
    setToastState({ message, type, id: Date.now() });
  }, []);

  const clearToast = useCallback(() => {
    setToastState(null);
  }, []);

  // Fetch full live session state and backend data
  const refreshAllData = useCallback(async () => {
    try {
      setError(null);
      
      // 1. Health check
      try {
        const healthData = await apiService.getHealth();
        setBackendHealth(healthData);
        setIsBackendOnline(true);
      } catch (hErr) {
        console.warn('Backend health check failed:', hErr);
        setIsBackendOnline(false);
      }

      // 2. Live Session
      try {
        const sessData = await apiService.getSession(sessionId);
        setSession(sessData);
        setEvents(sessData.events || []);

        // 3. Risk scoring evaluation
        const riskData = await apiService.getRiskScore(sessionId);
        setRiskEvaluation(riskData);

        // Auto trigger modal if threat detected and not yet resolved
        if (
          riskData.risk_level === 'THREAT_DETECTED' &&
          sessData.final_outcome !== 'INTERRUPTED' &&
          sessData.final_outcome !== 'ALLOWED'
        ) {
          setIsInterventionModalOpen(true);
        }
      } catch (sessErr) {
        console.warn('Live session fetch warning:', sessErr);
      }

      // 4. Simulator state & Scenarios
      try {
        const simState = await apiService.getSimulatorState(sessionId, selectedScenarioId);
        setSimulatorState(simState);
        if (simState.scenarios) {
          setAvailableScenarios(simState.scenarios);
        }
      } catch (simErr) {
        console.warn('Simulator state fetch warning:', simErr);
      }

      // 5. Sessions List
      try {
        const listData = await apiService.getSessions();
        setSessionsList(listData || []);
      } catch (listErr) {
        console.warn('Sessions list fetch warning:', listErr);
      }

      // 6. Analytics
      try {
        const analyticsData = await apiService.getAnalytics();
        setAnalytics(analyticsData);
      } catch (analyticsErr) {
        console.warn('Analytics fetch warning:', analyticsErr);
      }

    } catch (err) {
      console.error('Critical error in refreshAllData:', err);
      setError('Unable to sync with GuardianAI telemetry engine. Ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, selectedScenarioId]);

  // Initial load & periodic background telemetry sync
  useEffect(() => {
    refreshAllData();
    const interval = setInterval(() => {
      if (!isAutoSimulating) {
        refreshAllData();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [refreshAllData, isAutoSimulating]);

  // Selected session in timeline
  const selectTimelineSession = useCallback(async (sessId) => {
    setSelectedTimelineSessionId(sessId);
    try {
      const data = await apiService.getSession(sessId);
      setSelectedTimelineSessionData(data);
    } catch (err) {
      console.error(`Error loading session ${sessId}:`, err);
    }
  }, []);

  // Update selected timeline session when selected ID changes or after refresh
  useEffect(() => {
    if (selectedTimelineSessionId) {
      selectTimelineSession(selectedTimelineSessionId);
    }
  }, [selectedTimelineSessionId, selectTimelineSession]);

  // Switch scenario handler with unique session ID isolation
  const switchScenario = useCallback(async (newScenarioId) => {
    setIsAutoSimulating(false);
    if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
    setSelectedScenarioId(newScenarioId);
    const randSuffix = Math.random().toString(36).substring(2, 7);
    const newSessionId = `sim-${newScenarioId}-${randSuffix}`;
    setSessionId(newSessionId);
    try {
      await apiService.simulatorReset(newSessionId, newScenarioId);
      setIsInterventionModalOpen(false);
      showToast(`Switched scenario to: ${newScenarioId.replace(/_/g, ' ')}`, 'info');
    } catch (err) {
      console.error('Error switching scenario:', err);
      showToast('Error switching scenario on backend.', 'error');
    }
  }, [showToast]);

  // Step simulator forward
  const advanceSimulator = async () => {
    try {
      const result = await apiService.simulatorStep(sessionId, selectedScenarioId);
      if (result.status === 'STEP_ADVANCED') {
        const isThreat = result.risk?.risk_level === 'THREAT_DETECTED';
        showToast(
          `Step ${result.current_step}/${result.total_steps}: ${result.step_name}`,
          isThreat ? 'warning' : 'info'
        );
        if (result.event_type === 'INTERVENTION_TRIGGERED' || (isThreat && result.event_type !== 'TRANSACTION_CANCELLED')) {
          setIsInterventionModalOpen(true);
          setIsAutoSimulating(false);
        }
      } else if (result.status === 'COMPLETED') {
        showToast(`Scenario '${result.scenario_name || selectedScenarioId}' complete.`, 'info');
        setIsAutoSimulating(false);
      }
      await refreshAllData();
      return result;
    } catch (err) {
      console.error('Error advancing simulator:', err);
      showToast('Error communicating with simulator engine.', 'error');
    }
  };

  // Reset simulator for the current scenario session
  const resetSimulator = async () => {
    try {
      setIsAutoSimulating(false);
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
      await apiService.simulatorReset(sessionId, selectedScenarioId);
      setIsInterventionModalOpen(false);
      showToast('Simulation reset to clean baseline (Risk: 0.0% SAFE).', 'success');
      await refreshAllData();
    } catch (err) {
      console.error('Error resetting simulator:', err);
      showToast('Failed to reset simulation.', 'error');
    }
  };

  // Auto-play simulation handler
  useEffect(() => {
    if (isAutoSimulating) {
      autoPlayTimerRef.current = setInterval(async () => {
        try {
          const simState = await apiService.getSimulatorState(sessionId, selectedScenarioId);
          if (simState.current_step >= simState.total_steps) {
            setIsAutoSimulating(false);
            clearInterval(autoPlayTimerRef.current);
          } else {
            await advanceSimulator();
          }
        } catch (e) {
          setIsAutoSimulating(false);
          clearInterval(autoPlayTimerRef.current);
        }
      }, 2400);
    } else {
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
    }
    return () => {
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
    };
  }, [isAutoSimulating, sessionId, selectedScenarioId]);

  // Handle Intervention Action (Cancel vs Trust)
  const handleInterventionAction = async (actionType) => {
    try {
      await apiService.postIntervention({
        session_id: sessionId,
        risk_score: riskEvaluation.risk_score || 94.0,
        action: 'TRANSACTION_HALTED',
        user_response: actionType, // 'CANCEL_TRANSACTION' or 'TRUST_USER'
      });

      setIsInterventionModalOpen(false);
      if (actionType === 'CANCEL_TRANSACTION') {
        // Record simulated transaction cancellation event
        try {
          await apiService.postEvent({
            session_id: sessionId,
            event_type: 'TRANSACTION_CANCELLED',
            metadata: {
              transaction_cancelled: true,
              simulated_action: true,
              reason: 'USER_CANCELLED_AFTER_SCAM_WARNING',
              transaction_amount: activeTelemetry.transaction.amount || 120000.0,
              disclaimer: 'Simulated action: User cancelled transfer upon warning. No real banking transfer executed or blocked.'
            }
          });
        } catch (evErr) {
          console.warn('Cancellation event persistence note:', evErr);
        }
        showToast('Simulated Action: Transaction cancelled by user. (Simulated test action — no real bank transfer executed or blocked)', 'success');
      } else {
        showToast('Manual Override Recorded: User confirmed trust for this transaction only. (Helper identity is not whitelisted)', 'warning');
      }
      await refreshAllData();
    } catch (err) {
      console.error('Error recording intervention:', err);
      showToast('Failed to record intervention action.', 'error');
    }
  };

  // Derive active device telemetry signals
  const screenSharingEvent = events.find(
    (e) => e.event_type === 'SCREEN_SHARING_STARTED' || e.metadata?.screen_sharing_active
  );
  const bankingEvent = events.find(
    (e) => e.event_type === 'BANKING_APP_FOREGROUNDED' || e.metadata?.banking_app_active
  );
  const beneficiaryEvent = events.find(
    (e) => e.event_type === 'NEW_BENEFICIARY_ADDED' || e.metadata?.new_beneficiary
  );
  const transactionEvent = events.find(
    (e) => e.event_type === 'HIGH_VALUE_TRANSACTION_INITIATED' || e.metadata?.transaction_amount
  );
  const coachedEvent = events.find(
    (e) => e.event_type === 'COACHED_BEHAVIOUR_TRIGGERED' || e.metadata?.coached_sequence_detected
  );

  const activeTelemetry = {
    screenSharing: {
      active: !!screenSharingEvent,
      tool: screenSharingEvent?.metadata?.tool_name || (screenSharingEvent ? 'AnyDesk Remote Support' : 'None Detected'),
      remoteHost: screenSharingEvent?.metadata?.remote_host || 'None',
      resolution: screenSharingEvent?.metadata?.display_resolution || '1080x2400',
    },
    bankingApp: {
      active: !!bankingEvent,
      app: bankingEvent?.metadata?.app_name || (bankingEvent ? 'HDFC Mobile Banking' : 'None'),
      packageName: bankingEvent?.metadata?.package_name || '',
      sessionTime: bankingEvent?.metadata?.session_time_seconds || 0,
      authMethod: bankingEvent?.metadata?.auth_method || 'Biometric',
    },
    beneficiary: {
      active: !!beneficiaryEvent,
      label: beneficiaryEvent?.metadata?.beneficiary_label || 'Fast_Reversal_Desk_94',
      creationSpeedMs: beneficiaryEvent?.metadata?.creation_speed_ms || 3200,
      pasteDetected: !!beneficiaryEvent?.metadata?.paste_event_detected,
    },
    transaction: {
      active: !!transactionEvent,
      amount: transactionEvent?.metadata?.transaction_amount || 0,
      currency: transactionEvent?.metadata?.currency || 'INR',
      rail: transactionEvent?.metadata?.payment_rail || 'IMPS_INSTANT',
      beneficiary: transactionEvent?.metadata?.target_nickname || beneficiaryEvent?.metadata?.beneficiary_label || 'New Payee',
    },
    coachedCadence: {
      active: !!coachedEvent,
      signature: coachedEvent?.metadata?.pattern_signature || 'REMOTE_COACHED_FINANCIAL_EXFILTRATION',
      varianceScore: coachedEvent?.metadata?.touch_cadence_variance_score || 0.88,
      rapidSwitch: !!coachedEvent?.metadata?.rapid_app_switch,
    }
  };

  return (
    <SecurityContext.Provider
      value={{
        sessionId,
        setSessionId,
        session,
        sessionsList,
        selectedTimelineSessionId,
        selectedTimelineSessionData,
        selectTimelineSession,
        events,
        riskEvaluation,
        analytics,
        simulatorState,
        activeTelemetry,
        isInterventionModalOpen,
        setIsInterventionModalOpen,
        isAutoSimulating,
        setIsAutoSimulating,
        isLoading,
        isBackendOnline,
        backendHealth,
        error,
        toast,
        showToast,
        clearToast,
        selectedScenarioId,
        switchScenario,
        availableScenarios,
        advanceSimulator,
        resetSimulator,
        handleInterventionAction,
        refreshAllData,
      }}
    >
      {children}
    </SecurityContext.Provider>
  );
};

export const useSecurity = () => {
  const context = useContext(SecurityContext);
  if (!context) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
};

export default SecurityContext;
