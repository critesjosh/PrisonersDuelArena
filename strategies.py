import random
from typing import List, Tuple, Optional, Callable

class Strategy:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.history: List[bool] = []
        self.opponent_history: List[bool] = []

    def make_choice(self) -> bool:
        """Return True for cooperate, False for defect"""
        return True  # Default to cooperation as a safe default

    def update_history(self, my_choice: bool, opponent_choice: bool):
        self.history.append(my_choice)
        self.opponent_history.append(opponent_choice)

class CustomStrategy(Strategy):
    def __init__(self, name: str, description: str, logic: str):
        super().__init__(name, description)
        self.logic = logic
        # Parse the logic string to determine the strategy
        self.always_cooperate = "always cooperate" in logic.lower()
        self.always_defect = "always defect" in logic.lower()
        self.copy_opponent = "copy" in logic.lower() or "mimic" in logic.lower()
        self.opposite = "opposite" in logic.lower()
        self.random = "random" in logic.lower()

    def make_choice(self) -> bool:
        if self.always_cooperate:
            return True
        elif self.always_defect:
            return False
        elif self.copy_opponent and self.opponent_history:
            return self.opponent_history[-1]
        elif self.opposite and self.opponent_history:
            return not self.opponent_history[-1]
        elif self.random:
            return random.choice([True, False])
        return True  # Default to cooperation if no clear strategy is detected

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

_custom_strategies: List[CustomStrategy] = []

def add_custom_strategy(name: str, description: str, logic: str) -> CustomStrategy:
    strategy = CustomStrategy(name, description, logic)
    _custom_strategies.append(strategy)
    return strategy

def get_all_strategies() -> List[Strategy]:
    base_strategies = [
        TitForTat(),
        AlwaysCooperate(),
        AlwaysDefect(),
        RandomStrategy()
    ]
    return base_strategies + _custom_strategies