import random
from typing import List, Tuple

class Strategy:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.history: List[bool] = []
        self.opponent_history: List[bool] = []

    def make_choice(self) -> bool:
        """Return True for cooperate, False for defect"""
        pass

    def update_history(self, my_choice: bool, opponent_choice: bool):
        self.history.append(my_choice)
        self.opponent_history.append(opponent_choice)

class TitForTat(Strategy):
    def __init__(self):
        super().__init__(
            "Tit for Tat",
            "Cooperates on first move, then copies opponent's last move"
        )

    def make_choice(self) -> bool:
        if not self.opponent_history:
            return True
        return self.opponent_history[-1]

class AlwaysCooperate(Strategy):
    def __init__(self):
        super().__init__(
            "Always Cooperate",
            "Always chooses to cooperate"
        )

    def make_choice(self) -> bool:
        return True

class AlwaysDefect(Strategy):
    def __init__(self):
        super().__init__(
            "Always Defect",
            "Always chooses to defect"
        )

    def make_choice(self) -> bool:
        return False

class RandomStrategy(Strategy):
    def __init__(self):
        super().__init__(
            "Random",
            "Randomly chooses to cooperate or defect"
        )

    def make_choice(self) -> bool:
        return random.choice([True, False])

def get_all_strategies() -> List[Strategy]:
    return [
        TitForTat(),
        AlwaysCooperate(),
        AlwaysDefect(),
        RandomStrategy()
    ]
