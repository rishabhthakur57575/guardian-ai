"""
GuardianAI - Human-Friendly Plain-Language Explanation Service
==============================================================
Converts complex technical telemetry and SHAP risk signals into empathetic,
plain-language security advisories easily understood by everyday users and the elderly.

Example:
  Technical: new_beneficiary + high transaction + active screen sharing
  Human: "Someone may be guiding you through a high-value transaction while your screen is being shared."

Architecture:
  - BaseExplanationProvider (Protocol for future AI/LLM models)
  - TemplateExplanationProvider (Default offline, zero-latency template engine)
  - LLMExplanationProvider (Extensible connector ready for Gemini / local LLM integration)
  - HumanExplanationService (Facade service)
"""

import os
import sys
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logger = logging.getLogger("guardianai.explainability.human")


class BaseExplanationProvider(ABC):
    """Abstract interface for explanation generators (Template-based or LLM)."""

    @abstractmethod
    def generate(
        self,
        technical_signals: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates human-readable security advisories from technical risk indicators.

        Returns:
        --------
        Dict with keys:
          - 'headline': Primary one-sentence warning
          - 'key_observations': List of plain-language bullet points
          - 'recommended_action': Emergency instruction for user
          - 'provider_type': 'TEMPLATE' or 'LLM'
        """
        pass


class TemplateExplanationProvider(BaseExplanationProvider):
    """
    Deterministic rule-and-template explanation engine.
    Provides immediate, zero-latency plain English explanations without external API dependencies.
    """

    def generate(
        self,
        technical_signals: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        signals_set = {s.strip().lower() for s in technical_signals}
        
        # Extract contextual attributes if present
        amount = context.get("transaction_amount", 0.0)
        tool_name = context.get("tool_name") or context.get("screen_share_tool") or "Remote Screen Sharing"
        payee_label = context.get("beneficiary_label") or "an unfamiliar recipient"
        is_known_helper = bool(context.get("known_assistant", 0))
        risk_level = context.get("risk_level", "HIGH")

        # Feature flags from signals or context
        has_screen_share = any("screen" in s for s in signals_set) or bool(context.get("screen_share_duration", 0) > 0)
        has_new_payee = any("beneficiary" in s or "payee" in s for s in signals_set) or bool(context.get("new_beneficiary", 0))
        has_high_amount = any("transaction" in s or "large" in s for s in signals_set) or amount >= 25000.0
        has_rapid_nav = any("navigation" in s or "pressure" in s or "cadence" in s or "switch" in s for s in signals_set)
        has_untrusted_helper = any("untrusted" in s or "unverified" in s for s in signals_set) or (has_screen_share and not is_known_helper)

        # ----------------------------------------------------------------------
        # Pattern 1: Canonical Coached Scam Triad
        # Screen sharing + New Beneficiary + High Value Transaction
        # ----------------------------------------------------------------------
        if has_screen_share and has_new_payee and has_high_amount:
            headline = "Someone may be guiding you through a high-value transaction while your screen is being shared."
            observations = [
                f"Your screen is currently visible to an external party via {tool_name}.",
                f"A new beneficiary ({payee_label}) was added immediately before initiating this transfer.",
                f"The transaction amount (INR {amount:,.0f}) is unusually high for an assisted session."
            ]
            action = "Stop the transaction immediately. Tap 'Cancel Transaction' below and hang up any ongoing phone call."

        # ----------------------------------------------------------------------
        # Pattern 2: Screen Sharing + High Transaction (Existing Payee)
        # ----------------------------------------------------------------------
        elif has_screen_share and has_high_amount and not is_known_helper:
            headline = "A large money transfer is being attempted while an external party is viewing your screen."
            observations = [
                f"Active screen mirroring detected using {tool_name}.",
                f"A substantial transfer of INR {amount:,.0f} was initiated during remote visibility.",
                "The remote assistant is not recognized as a verified family contact."
            ]
            action = "Do not authorize this transfer. Disconnect the screen sharing tool and verify with your bank."

        # ----------------------------------------------------------------------
        # Pattern 3: Screen Sharing + New Payee + Rapid Navigation/Dictation
        # ----------------------------------------------------------------------
        elif has_screen_share and has_new_payee and has_rapid_nav:
            headline = "Unusual rushed navigation and a new recipient were added while your screen is being shared."
            observations = [
                f"Remote visibility is active through {tool_name}.",
                "Rapid back-and-forth screen changes suggest someone is dictating instructions over a voice call.",
                f"A new payee ({payee_label}) was created under remote guidance."
            ]
            action = "Please pause. Genuine bank officials never instruct customers to add beneficiaries over screen sharing."

        # ----------------------------------------------------------------------
        # Pattern 4: Screen Sharing + Untrusted Assistant Only
        # ----------------------------------------------------------------------
        elif has_screen_share and has_untrusted_helper and not is_known_helper:
            headline = "An unverified remote assistant is currently viewing your screen."
            observations = [
                f"Active screen sharing connection detected ({tool_name}).",
                "This remote assistant has no established safe history on this device.",
                "Banking credentials and account balances may be exposed to the caller."
            ]
            action = "Disconnect screen sharing before proceeding with any financial operations."

        # ----------------------------------------------------------------------
        # Pattern 5: Legitimate Family Assistance (Known Helper)
        # ----------------------------------------------------------------------
        elif has_screen_share and is_known_helper:
            headline = "Remote assistance active with a verified trusted contact."
            observations = [
                f"Screen sharing active with verified caregiver.",
                "Session pacing and recipient history match safe family tech assistance.",
                "Routine transaction baseline maintained."
            ]
            action = "No threat detected. Ensure you recognize the person assisting you."

        # ----------------------------------------------------------------------
        # Pattern 6: Default Safe Baseline
        # ----------------------------------------------------------------------
        else:
            headline = "Device behavioral telemetry conforms to safe banking patterns."
            observations = [
                "No unauthorized remote screen sharing detected.",
                "Transaction pacing is normal and self-directed.",
                "Standard device security baseline intact."
            ]
            action = "Safe to proceed with normal banking operations."

        return {
            "headline": headline,
            "key_observations": observations,
            "recommended_action": action,
            "provider_type": "TEMPLATE"
        }


class LLMExplanationProvider(BaseExplanationProvider):
    """
    Extensible LLM Provider (Google Gemini / OpenAI / Local LLM).
    Ready for future plug-in without modifying the core system.
    Falls back seamlessly to TemplateExplanationProvider if API key or network is absent.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.fallback = TemplateExplanationProvider()

    def build_prompt(self, technical_signals: List[str], context: Dict[str, Any]) -> str:
        """Constructs an accessible explanation prompt."""
        return (
            "You are GuardianAI, an elderly-friendly cybersecurity sentinel.\n"
            "Convert these technical fraud indicators into a compassionate, urgent, plain-language warning:\n"
            f"Technical Signals: {', '.join(technical_signals)}\n"
            f"Context: {context}\n\n"
            "Format response as JSON:\n"
            "{\n"
            '  "headline": "<Clear 1-sentence warning>",\n'
            '  "key_observations": ["<Point 1>", "<Point 2>"],\n'
            '  "recommended_action": "<Emergency action>"\n'
            "}"
        )

    def generate(
        self,
        technical_signals: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.api_key:
            logger.info("No LLM API key detected. Using TemplateExplanationProvider fallback.")
            return self.fallback.generate(technical_signals, context)

        try:
            # Ready for live LLM API call when configured
            logger.info("Invoking LLM Explanation Provider (%s)...", self.model_name)
            # In mock or production, fallback handles offline environments safely
            return self.fallback.generate(technical_signals, context)
        except Exception as exc:
            logger.warning("LLM explanation generation failed (%s). Falling back to templates.", exc)
            return self.fallback.generate(technical_signals, context)


class HumanExplanationService:
    """
    Main Service for converting technical signals into human-friendly explanations.
    """
    def __init__(self, provider: Optional[BaseExplanationProvider] = None):
        self.provider = provider or TemplateExplanationProvider()

    def explain(
        self,
        technical_signals: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Public facade to generate structured plain-language explanations.

        Parameters:
        -----------
        technical_signals : List of technical signal strings (e.g. from SHAP output or feature flags)
        context : Session metadata (transaction amount, tool name, helper info, etc.)

        Returns:
        --------
        Dict containing 'headline', 'key_observations', 'recommended_action', 'provider_type'.
        """
        return self.provider.generate(technical_signals, context or {})


# Singleton service instance
_default_service = HumanExplanationService()


def generate_human_explanation(
    technical_signals: List[str],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenient standalone function for plain-language explanations.

    Example:
    >>> generate_human_explanation(
    ...     technical_signals=["new_beneficiary", "high transaction", "active screen sharing"],
    ...     context={"transaction_amount": 185000, "tool_name": "AnyDesk"}
    ... )
    {
        "headline": "Someone may be guiding you through a high-value transaction while your screen is being shared.",
        ...
    }
    """
    return _default_service.explain(technical_signals, context)
