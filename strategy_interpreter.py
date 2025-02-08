import os
import json
from openai import OpenAI
from typing import Dict, Optional

class StrategyInterpreter:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """
        You are a Prisoner's Dilemma strategy interpreter. Analyze the given strategy description
        and return a JSON object that strictly follows this structure for the pattern types:

        For sequence patterns (e.g. "10 then 10", "cooperate 5 then defect 5"):
        {
            "type": "sequence",
            "pattern": {
                "cooperate_count": <number>,
                "defect_count": <number>
            }
        }

        For conditional patterns (e.g. "copy opponent's last move"):
        {
            "type": "conditional",
            "pattern": {
                "condition": "last_opponent_move"
            }
        }

        For simple patterns (e.g. "always cooperate", "always defect", "random"):
        {
            "type": "simple",
            "pattern": {
                "action": "cooperate" | "defect" | "random"
            }
        }

        Important: For patterns like "X then Y", always interpret as sequence type with cooperate_count=X and defect_count=Y
        """

    def interpret_strategy(self, strategy_text: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Interpret this strategy: {strategy_text}"}
                ],
                response_format={"type": "json_object"}
            )

            interpreted_strategy = json.loads(response.choices[0].message.content)
            print(f"AI interpreted strategy '{strategy_text}' as: {interpreted_strategy}")

            # Validate the response structure
            if interpreted_strategy["type"] == "sequence":
                if "cooperate_count" not in interpreted_strategy["pattern"] or \
                   "defect_count" not in interpreted_strategy["pattern"]:
                    raise ValueError("Invalid sequence pattern structure")

            return interpreted_strategy

        except Exception as e:
            print(f"Error interpreting strategy: {e}")
            # Fallback to basic cooperation
            return {"type": "simple", "pattern": {"action": "cooperate"}}