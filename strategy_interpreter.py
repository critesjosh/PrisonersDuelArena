import os
import json
from openai import OpenAI
from typing import Dict, Optional

class StrategyInterpreter:
    _instance = None
    _cache = {}  # Class-level cache for interpreted strategies

    def __new__(cls):
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

            Examples:
            - Input: "cooperate first 3 moves then copy opponent"
              Output: {"type": "conditional", "pattern": {"condition": "last_opponent_move", "initial_cooperation": 3}}

            - Input: "cooperate 10 moves then defect 10 moves"
              Output: {"type": "sequence", "pattern": {"cooperate_count": 10, "defect_count": 10}}

            - Input: "do what opponent did last"
              Output: {"type": "conditional", "pattern": {"condition": "last_opponent_move", "initial_cooperation": 0}}

            - Input: "choose what opponent chose most often"
              Output: {"type": "conditional", "pattern": {"condition": "last_opponent_move", "initial_cooperation": 0}}

            - Input: "always cooperate"
              Output: {"type": "simple", "pattern": {"action": "cooperate"}}
            """

    def get_cached_interpretation(self, strategy_text: str) -> Optional[Dict]:
        """Get cached interpretation if it exists."""
        return self._cache.get(strategy_text.lower().strip())

    def cache_interpretation(self, strategy_text: str, interpretation: Dict):
        """Cache the interpretation for future use."""
        self._cache[strategy_text.lower().strip()] = interpretation

    def interpret_strategy(self, strategy_text: str) -> Dict:
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

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Interpret this strategy: {strategy_text}"}
            ]

            print("[Strategy Interpreter] OpenAI Request:")
            print(f"  Model: gpt-3.5-turbo")
            print(f"  Temperature: 0.1")
            print(f"  Messages:")
            for msg in messages:
                print(f"    - {msg['role']}: {msg['content'][:100]}...")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1  # Lower temperature for more consistent results
            )

            print("\n[Strategy Interpreter] OpenAI Response:")
            print(f"  Response ID: {response.id}")
            print(f"  Model used: {response.model}")
            print(f"  Raw content: {response.choices[0].message.content}")

            interpreted_strategy = json.loads(response.choices[0].message.content)
            print(f"\n[Strategy Interpreter] Parsed interpretation:")
            print(json.dumps(interpreted_strategy, indent=2))

            # Validate and clean up the interpretation
            if not isinstance(interpreted_strategy, dict):
                raise ValueError("Invalid response format")

            if "type" not in interpreted_strategy or "pattern" not in interpreted_strategy:
                raise ValueError("Missing required fields in response")

            strategy_type = interpreted_strategy["type"]
            pattern = interpreted_strategy["pattern"]

            print(f"\n[Strategy Interpreter] Validating {strategy_type} pattern...")

            if strategy_type == "sequence":
                if "cooperate_count" not in pattern or "defect_count" not in pattern:
                    raise ValueError("Invalid sequence pattern structure")

                # Convert to integers and validate
                pattern["cooperate_count"] = int(pattern["cooperate_count"])
                pattern["defect_count"] = int(pattern["defect_count"])

                if pattern["cooperate_count"] < 1 or pattern["defect_count"] < 1:
                    raise ValueError("Invalid sequence counts")

                print(f"[Strategy Interpreter] Validated sequence pattern:")
                print(f"  - Cooperate count: {pattern['cooperate_count']}")
                print(f"  - Defect count: {pattern['defect_count']}")

            elif strategy_type == "conditional":
                if pattern.get("condition") != "last_opponent_move":
                    raise ValueError("Unsupported conditional pattern")

                # Ensure initial_cooperation is present and valid
                if "initial_cooperation" not in pattern:
                    pattern["initial_cooperation"] = 0
                pattern["initial_cooperation"] = int(pattern["initial_cooperation"])

                print(f"[Strategy Interpreter] Validated conditional pattern:")
                print(f"  - Condition: {pattern['condition']}")
                print(f"  - Initial cooperation: {pattern['initial_cooperation']}")

            elif strategy_type == "simple":
                if pattern.get("action") not in ["cooperate", "defect", "random"]:
                    # Convert unsupported actions to conditional pattern
                    print(f"[Strategy Interpreter] Converting unsupported action to conditional pattern")
                    return {
                        "type": "conditional",
                        "pattern": {
                            "condition": "last_opponent_move",
                            "initial_cooperation": 0
                        }
                    }

                print(f"[Strategy Interpreter] Validated simple pattern: {pattern['action']}")

            else:
                raise ValueError(f"Unsupported strategy type: {strategy_type}")

            # Cache the validated interpretation
            self.cache_interpretation(strategy_text, interpreted_strategy)

            print("\n[Strategy Interpreter] Strategy interpretation completed successfully")
            return interpreted_strategy

        except Exception as e:
            print(f"\n[Strategy Interpreter] Error occurred:")
            print(f"  Type: {type(e).__name__}")
            print(f"  Message: {str(e)}")
            print("  Falling back to default cooperation strategy")
            # Fallback to basic cooperation
            return {"type": "simple", "pattern": {"action": "cooperate"}}