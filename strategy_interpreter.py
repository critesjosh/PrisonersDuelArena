import os
import json
from openai import OpenAI
from typing import Dict, Optional

class StrategyInterpreter:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """
        You are a Prisoner's Dilemma strategy interpreter. Your task is to convert strategy descriptions
        into actionable game logic. Focus on identifying key patterns and numerical sequences.

        IMPORTANT:
        - Numbers can be written as words (e.g., "ten" = 10)
        - Look for keywords: "moves", "rounds", "times", "then", "alternate"
        - Always validate that sequence patterns have clear numbers
        - Default to "simple" type only if no clear sequence or condition is found

        Return a JSON object following one of these formats:

        1. For alternating/sequence patterns (e.g., "cooperate 5 moves then defect 5 moves"):
        {
            "type": "sequence",
            "pattern": {
                "cooperate_count": 5,
                "defect_count": 5
            }
        }

        2. For reactive patterns (e.g., "copy opponent's last move"):
        {
            "type": "conditional",
            "pattern": {
                "condition": "last_opponent_move"
            }
        }

        3. For basic patterns (e.g., "always cooperate"):
        {
            "type": "simple",
            "pattern": {
                "action": "cooperate" | "defect" | "random"
            }
        }

        Examples:
        - Input: "cooperate 10 moves then defect 10 moves"
          Output: {"type": "sequence", "pattern": {"cooperate_count": 10, "defect_count": 10}}

        - Input: "alternate between cooperating 3 times and defecting twice"
          Output: {"type": "sequence", "pattern": {"cooperate_count": 3, "defect_count": 2}}

        - Input: "do what opponent did last"
          Output: {"type": "conditional", "pattern": {"condition": "last_opponent_move"}}
        """

    def interpret_strategy(self, strategy_text: str) -> Dict:
        try:
            # Clean and standardize input
            strategy_text = strategy_text.lower().strip()

            print(f"\n[Strategy Interpreter] Analyzing strategy: '{strategy_text}'")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Interpret this strategy: {strategy_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Lower temperature for more consistent results
            )

            interpreted_strategy = json.loads(response.choices[0].message.content)
            print(f"[Strategy Interpreter] Raw interpretation: {interpreted_strategy}")

            # Validate and clean up the interpretation
            if not isinstance(interpreted_strategy, dict):
                raise ValueError("Invalid response format")

            if "type" not in interpreted_strategy or "pattern" not in interpreted_strategy:
                raise ValueError("Missing required fields in response")

            strategy_type = interpreted_strategy["type"]
            pattern = interpreted_strategy["pattern"]

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
                print(f"[Strategy Interpreter] Validated conditional pattern")

            elif strategy_type == "simple":
                if pattern.get("action") not in ["cooperate", "defect", "random"]:
                    raise ValueError("Invalid simple action")
                print(f"[Strategy Interpreter] Validated simple pattern: {pattern['action']}")

            else:
                raise ValueError(f"Unsupported strategy type: {strategy_type}")

            return interpreted_strategy

        except Exception as e:
            print(f"[Strategy Interpreter] Error: {str(e)}")
            # Fallback to basic cooperation
            return {"type": "simple", "pattern": {"action": "cooperate"}}