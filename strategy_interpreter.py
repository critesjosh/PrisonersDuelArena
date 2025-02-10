"""
strategy_interpreter.py

This module provides AI-powered interpretation of natural language strategy descriptions
for the Prisoner's Dilemma game. It uses OpenAI's GPT model to convert human-readable
strategy descriptions into structured game logic.

Key features:
- Natural language processing of strategy descriptions
- Conversion to structured game patterns
- Strategy validation and error handling
- Caching of interpreted strategies for performance
- Fallback mechanisms for handling interpretation errors

The StrategyInterpreter class supports three types of patterns:
1. Sequence patterns (e.g., "cooperate 5 moves then defect 5 moves")
2. Conditional patterns (e.g., "copy opponent's last move")
3. Simple patterns (e.g., "always cooperate", "always defect", "random")
"""

import os
import json
from typing import Dict, Optional, Union, TypedDict, Literal
from openai import OpenAI  # Updated import for latest OpenAI package

class StrategyPattern(TypedDict):
    type: Literal["sequence", "conditional", "simple"]
    pattern: Dict[str, Union[str, int]]

class StrategyInterpreter:
    _instance: Optional['StrategyInterpreter'] = None
    _cache: Dict[str, StrategyPattern] = {}  # Class-level cache for interpreted strategies

    def __new__(cls) -> 'StrategyInterpreter':
        if cls._instance is None:
            cls._instance = super(StrategyInterpreter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.client = OpenAI()
            self.initialized = True
            self.system_prompt = """
            You are a Prisoner's Dilemma strategy interpreter. Your task is to convert strategy descriptions
            into actionable game logic. Focus on identifying key patterns and numerical sequences.

            IMPORTANT:
            - Numbers can be written as words (e.g., "ten" = 10)
            - Look for keywords: "moves", "rounds", "times", "then", "alternate", "copy"
            - Statistical strategies (e.g., "choose what opponent chose most often") should be converted to "copy opponent's last move"
            - If a strategy involves complex logic, default to a conditional pattern with "last_opponent_move"
            - For simple strategies, only use: "cooperate", "defect", or "random"

            Return a JSON object following one of these formats:

            1. For alternating/sequence patterns (e.g., "cooperate 5 moves then defect 5 moves"):
            {
                "type": "sequence",
                "pattern": {
                    "cooperate_count": 5,
                    "defect_count": 5
                }
            }

            2. For reactive patterns (e.g., "copy opponent's last move" or "cooperate 3 times then copy"):
            {
                "type": "conditional",
                "pattern": {
                    "condition": "last_opponent_move",
                    "initial_cooperation": 0  // Set this to the number of initial cooperation moves
                }
            }

            3. For basic patterns (e.g., "always cooperate", "always defect", "random"):
            {
                "type": "simple",
                "pattern": {
                    "action": "cooperate" | "defect" | "random"  // Only these three values are allowed
                }
            }
            """

    def get_cached_interpretation(self, strategy_text: str) -> Optional[StrategyPattern]:
        """Get cached interpretation if it exists."""
        return self._cache.get(strategy_text.lower().strip())

    def cache_interpretation(self, strategy_text: str, interpretation: StrategyPattern) -> None:
        """Cache the interpretation for future use."""
        self._cache[strategy_text.lower().strip()] = interpretation

    def interpret_strategy(self, strategy_text: str) -> StrategyPattern:
        """Interpret a natural language strategy description into a structured pattern.

        Args:
            strategy_text (str): The strategy description to interpret

        Returns:
            StrategyPattern: A structured representation of the strategy
        """
        try:
            # Check cache first
            cached = self.get_cached_interpretation(strategy_text)
            if cached:
                print(f"\n[Strategy Interpreter] Using cached interpretation for: '{strategy_text}'")
                return cached

            # Clean and standardize input
            strategy_text = strategy_text.lower().strip()

            print(f"\n[Strategy Interpreter] Analyzing strategy: '{strategy_text}'")
            print("[Strategy Interpreter] Preparing OpenAI request...")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Interpret this strategy: {strategy_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Lower temperature for more consistent results
            )

            print("\n[Strategy Interpreter] OpenAI Response:")
            print(f"  Response ID: {response.id}")
            print(f"  Model used: {response.model}")
            print(f"  Raw content: {response.choices[0].message.content}")

            interpreted_strategy = json.loads(response.choices[0].message.content)

            # Validate and clean up the interpretation
            if "type" not in interpreted_strategy or "pattern" not in interpreted_strategy:
                raise ValueError("Missing required fields in response")

            strategy_type = interpreted_strategy["type"]
            pattern = interpreted_strategy["pattern"]

            # Type validation and conversion
            if strategy_type == "sequence":
                pattern["cooperate_count"] = int(pattern["cooperate_count"])
                pattern["defect_count"] = int(pattern["defect_count"])
            elif strategy_type == "conditional":
                if pattern.get("condition") != "last_opponent_move":
                    raise ValueError("Unsupported conditional pattern")
                pattern["initial_cooperation"] = int(pattern.get("initial_cooperation", 0))
            elif strategy_type == "simple":
                if pattern.get("action") not in ["cooperate", "defect", "random"]:
                    return {
                        "type": "conditional",
                        "pattern": {
                            "condition": "last_opponent_move",
                            "initial_cooperation": 0
                        }
                    }

            # Cache the validated interpretation
            self.cache_interpretation(strategy_text, interpreted_strategy)
            return interpreted_strategy

        except Exception as e:
            print(f"\n[Strategy Interpreter] Error occurred: {type(e).__name__} - {str(e)}")
            # Fallback to basic cooperation
            return {"type": "simple", "pattern": {"action": "cooperate"}}