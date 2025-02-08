import os
import json
from openai import OpenAI
from typing import Dict, Optional

class StrategyInterpreter:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """
        You are a Prisoner's Dilemma strategy interpreter. Your task is to analyze strategy descriptions
        and convert them into a structured format. Pay special attention to sequence patterns.

        Return a JSON object that strictly follows these formats:

        1. For sequence patterns:
        - Triggered by phrases like "X moves then Y moves", "cooperate X then defect Y"
        - Example: "cooperate 10 moves then defect 10 moves" should be interpreted as:
        {
            "type": "sequence",
            "pattern": {
                "cooperate_count": 10,
                "defect_count": 10
            }
        }

        2. For conditional patterns:
        - Triggered by phrases about responding to opponent's moves
        {
            "type": "conditional",
            "pattern": {
                "condition": "last_opponent_move"
            }
        }

        3. For simple patterns:
        {
            "type": "simple",
            "pattern": {
                "action": "cooperate" | "defect" | "random"
            }
        }

        IMPORTANT: 
        - Always check for numbers followed by "moves", "rounds", or similar terms
        - For alternating patterns, always use the sequence type
        - Numbers can be written as digits or words (e.g., "ten" = 10)
        - Default to sequence type if any alternation or counting is mentioned
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
            print(f"[Strategy Interpreter] Input text: '{strategy_text}'")
            print(f"[Strategy Interpreter] Interpreted as: {interpreted_strategy}")

            # Validate the response structure
            if interpreted_strategy["type"] == "sequence":
                if "cooperate_count" not in interpreted_strategy["pattern"] or \
                   "defect_count" not in interpreted_strategy["pattern"]:
                    raise ValueError("Invalid sequence pattern structure")

                # Ensure counts are integers
                interpreted_strategy["pattern"]["cooperate_count"] = int(interpreted_strategy["pattern"]["cooperate_count"])
                interpreted_strategy["pattern"]["defect_count"] = int(interpreted_strategy["pattern"]["defect_count"])

            return interpreted_strategy

        except Exception as e:
            print(f"Error interpreting strategy: {e}")
            # Fallback to basic cooperation
            return {"type": "simple", "pattern": {"action": "cooperate"}}