import random
from typing import List, Tuple, Optional, Callable
import re

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
    instances = {}  # Class variable to store instance parameters

    def __init__(self, name: str = None, description: str = None, logic: str = None):
        # If parameters are not provided, try to get them from class storage
        if name is None and description is None and logic is None:
            instance_params = self.instances.get(self.__class__.__name__, {})
            name = instance_params.get('name', 'Custom Strategy')
            description = instance_params.get('description', 'A custom strategy')
            logic = instance_params.get('logic', 'always cooperate')

        super().__init__(name, description)
        self.logic = logic.lower()
        self.move_counter = 0

        # Parse numeric patterns like "10 then 10" or "cooperate 5 times then defect 5 times"
        pattern = r'(\d+)\s*(?:times?)?\s*(?:then|and|,)\s*(\d+)'
        matches = re.findall(pattern, self.logic)

        # Print debug information about pattern matching
        print(f"Logic string: {self.logic}")
        print(f"Pattern matches: {matches}")

        if matches:
            self.sequence_mode = True
            self.cooperate_count = int(matches[0][0])
            self.defect_count = int(matches[0][1])
            self.total_sequence = self.cooperate_count + self.defect_count
            print(f"Sequence mode activated: {self.cooperate_count} cooperate, {self.defect_count} defect")
        else:
            self.sequence_mode = False
            # Parse the logic string to determine the strategy
            self.always_cooperate = "always cooperate" in self.logic
            self.always_defect = "always defect" in self.logic
            self.copy_opponent = "copy" in self.logic or "mimic" in self.logic
            self.opposite = "opposite" in self.logic
            self.random = "random" in self.logic

    def make_choice(self) -> bool:
        if self.sequence_mode:
            position_in_sequence = self.move_counter % self.total_sequence
            choice = position_in_sequence < self.cooperate_count
            print(f"Move {self.move_counter}: position {position_in_sequence}, {'cooperate' if choice else 'defect'}")
            self.move_counter += 1
            return choice

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
    strategy_class = type(
        f"CustomStrategy_{len(_custom_strategies)}",
        (CustomStrategy,),
        {}
    )
    # Store the parameters in the class
    strategy_class.instances[strategy_class.__name__] = {
        'name': name,
        'description': description,
        'logic': logic
    }
    strategy = strategy_class()
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