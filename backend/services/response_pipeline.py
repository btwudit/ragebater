"""
RageBater Response Pipeline.

Orchestrates the analysis, Rage Engine, personality state,
and intensity controller into one deterministic response plan.

This module does not generate natural-language responses and
does not call an external AI service.
"""

from engine.intensity_controller import calculate_intensity
from engine.personality_state import PersonalityState
from engine.rage_engine import select_strategy
from services.analysis_service import analyze_message


class ResponsePipeline:
    """
    Coordinates all RageBater decision-making components.

    The pipeline is intentionally deterministic and keeps the
    response-generation layer separate for future LLM integration.
    """

    def __init__(self, personality_state=None):
        if personality_state is None:
            personality_state = PersonalityState()

        self.personality_state = personality_state

    def process(self, message: str) -> dict:
        """
        Process a user message through the complete RageBater pipeline.

        Returns a response plan containing:

        - analysis
        - strategy
        - personality state
        - final intensity
        """

        if not isinstance(message, str):
            raise TypeError("message must be a string")

        if not message.strip():
            raise ValueError("message cannot be empty")

        # Step 1: Analyze the user message.
        analysis = analyze_message(message)

        # Step 2: Select the RageBater strategy.
        strategy_result = select_strategy(analysis)

        # Step 3: Update personality based on the analysis.
        personality = self.personality_state.apply_analysis(
            analysis
        )

        # Step 4: Calculate final response intensity.
        final_intensity = calculate_intensity(
            base_intensity=strategy_result["intensity"],
            personality_state=personality,
            emotion=analysis["emotion"],
        )

        return {
            "analysis": analysis,
            "strategy": strategy_result["strategy"],
            "reason": strategy_result["reason"],
            "base_intensity": strategy_result["intensity"],
            "personality": personality,
            "intensity": final_intensity,
        }

    def reset_personality(self):
        """Reset the pipeline's personality state."""
        self.personality_state.reset()

        return self.personality_state.get_state()