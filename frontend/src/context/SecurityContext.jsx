import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import apiService from '../services/api';

const SecurityContext = createContext(null);

export const SecurityProvider = ({ children }) => {
  const [sessionId] = useState('demo-session-live');
  const [session, setSession] = useState(null);
  const [events, setEvents] = useState([]);
  const [riskEvaluation, setRiskEvaluation] = useState({
    risk_score: 0.0,
    risk_level: 'SAFE',
    reasons: ['Normal device behavioural baseline maintained.'],
    risk_factors: [],
    recommended_action: 'NONE'
  });
  const [analytics, setAnalytics] = useState(null);
  const [simulatorState, setSimulatorState] = useState({ current_step: 0, total_steps: 6 });
  const [isInterventionModalOpen, setIsInterventionModalOpen] = useState(false);
  const [isAutoSimulating, setIsAutoSimulating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [lastNotification, setLastNotification] = useState(null);
  const autoPlayTimerRef = useRef(null);

  // Fetch full live session state
  const refreshSessionData = useCallback(async () => {
    try {
      const sessData = await apiService.getSession(sessionId);
      setSession(sessData);
      setEvents(sessData.events || []);

      // Calculate or fetch risk
      const riskData = await apiService.getRiskScore(sessionId);
      setRiskEvaluation(riskData);

      // Check if threat detected and needs intervention
      if (riskData.risk_level === 'THREAT_DETECTED' && sessData.final_outcome !== 'INTERRUPTED' && sessData.final_outcome !== 'ALLOWED') {
        setIsInterventionModalOpen(true);
      }

      // Update simulator state
      const simState = await apiService.getSimulatorState(sessionId);
      setSimulatorState(simState);

      // Fetch analytics
      const analyticsData = await apiService.getAnalytics();
      setAnalytics(analyticsData);
    } catch (err) {
      console.error('Error refreshing session data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  // Initial load
  useEffect(() => {
    refreshSessionData();
  }, [refreshSessionData]);

  // Step simulator forward
  const advanceSimulator = async () => {
    try {
      const result = await apiService.simulatorStep(sessionId);
      if (result.status === 'STEP_ADVANCED') {
        setLastNotification(`Step ${result.current_step}/6: ${result.step_name}`);
        if (result.current_step === 6 || result.risk?.risk_level === 'THREAT_DETECTED') {
          setIsInterventionModalOpen(true);
          setIsAutoSimulating(false);
        }
      }
      await refreshSessionData();
      return result;
    } catch (err) {
      console.error('Error advancing simulator:', err);
    }
  };

  // Reset simulator
  const resetSimulator = async () => {
    try {
      setIsAutoSimulating(false);
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
      await apiService.simulatorReset(sessionId);
      setIsInterventionModalOpen(false);
      setLastNotification('Simulation reset to initial Safe Baseline.');
      await refreshSessionData();
    } catch (err) {
      console.error('Error resetting simulator:', err);
    }
  };

  // Auto-play simulation handler
  useEffect(() => {
    if (isAutoSimulating) {
      autoPlayTimerRef.current = setInterval(async () => {
        const simState = await apiService.getSimulatorState(sessionId);
        if (simState.current_step >= 6) {
          setIsAutoSimulating(false);
          clearInterval(autoPlayTimerRef.current);
        } else {
          await advanceSimulator();
        }
      }, 2400);
    } else {
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
    }
    return () => {
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
    };
  }, [isAutoSimulating, sessionId]);

  // Handle Intervention Action (Cancel vs Trust)
  const handleInterventionAction = async (actionType) => {
    try {
      await apiService.postIntervention({
        session_id: sessionId,
        risk_score: riskEvaluation.risk_score,
        action: 'TRANSACTION_HALTED',
        user_response: actionType, // 'CANCEL_TRANSACTION' or 'TRUST_USER'
      });

      setIsInterventionModalOpen(false);
      setLastNotification(
        actionType === 'CANCEL_TRANSACTION'
          ? '🛡️ Transaction Cancelled. High-risk transfer was successfully blocked.'
          : '⚠️ Override recorded: User confirmed trust.'
      );
      await refreshSessionData();
    } catch (err) {
      console.error('Error recording intervention:', err);
    }
  };

  // Derive active device telemetry
  const screenSharingEvent = events.find(
    (e) => e.event_type === 'SCREEN_SHARING_STARTED' || e.metadata?.screen_sharing_active
  );
  const bankingEvent = events.find(
    (e) => e.event_type === 'BANKING_APP_FOREGROUNDED' || e.metadata?.banking_app_active
  );
  const transactionEvent = events.find(
    (e) => e.event_type === 'HIGH_VALUE_TRANSACTION_INITIATED' || e.metadata?.transaction_amount
  );

  const activeTelemetry = {
    screenSharing: {
      active: !!screenSharingEvent,
      tool: screenSharingEvent?.metadata?.tool_name || (screenSharingEvent ? 'Active Screen Sharing' : 'None Detected'),
    },
    bankingApp: {
      active: !!bankingEvent,
      app: bankingEvent?.metadata?.app_name || (bankingEvent ? 'Active Banking App' : 'No Banking Session'),
    },
    transaction: {
      active: !!transactionEvent,
      amount: transactionEvent?.metadata?.transaction_amount || 0,
      beneficiary: transactionEvent?.metadata?.target_nickname || 'New Payee',
    }
  };

  return (
    <SecurityContext.Provider
      value={{
        sessionId,
        session,
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
        lastNotification,
        setLastNotification,
        advanceSimulator,
        resetSimulator,
        handleInterventionAction,
        refreshSessionData,
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
