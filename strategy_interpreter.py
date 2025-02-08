import os
import json
from openai import OpenAI
from typing import Dict, Optional

class StrategyInterpreter:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """
        You are a Prisoner's Dilemma strategy interpreter. Analyze the given strategy description
        and return a JSON object with the following structure:
        {
            "type": "sequence" | "conditional" | "simple",
            "pattern": {
                "cooperate_count": number,      // For sequence type
                "defect_count": number,         // For sequence type
                "condition": string,            // For conditional type
                "action": string               // For simple type
            }
        }
        Examples:
        1. "10 then 10" -> {"type": "sequence", "pattern": {"cooperate_count": 10, "defect_count": 10}}
        2. "always cooperate" -> {"type": "simple", "pattern": {"action": "cooperate"}}
        3. "copy opponent's last move" -> {"type": "conditional", "pattern": {"condition": "last_opponent_move"}}
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

            # Safely parse JSON instead of using eval()
            interpreted_strategy = json.loads(response.choices[0].message.content)
            print(f"AI interpreted strategy '{strategy_text}' as: {interpreted_strategy}")
            return interpreted_strategy

        except Exception as e:
            print(f"Error interpreting strategy: {e}")
            # Fallback to basic cooperation
            return {"type": "simple", "pattern": {"action": "cooperate"}}