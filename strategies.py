import random
from typing import List, Tuple, Optional, Callable
import re
from strategy_interpreter import StrategyInterpreter

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
    interpreter = StrategyInterpreter()

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

        # Use AI to interpret the strategy
        self.strategy_pattern = self.interpreter.interpret_strategy(self.logic)
        print(f"Interpreted strategy pattern: {self.strategy_pattern}")

    def make_choice(self) -> bool:
        pattern_type = self.strategy_pattern['type']
        pattern = self.strategy_pattern['pattern']

        if pattern_type == "sequence":
            total_sequence = pattern['cooperate_count'] + pattern['defect_count']
            position = self.move_counter % total_sequence
            self.move_counter += 1
            print(f"Sequence move {self.move_counter}: position {position}, pattern: {pattern}")
            return position < pattern['cooperate_count']

        elif pattern_type == "conditional":
            if pattern['condition'] == "last_opponent_move":
                return self.opponent_history[-1] if self.opponent_history else True

        elif pattern_type == "simple":
            if pattern['action'] == "cooperate":
                return True
            elif pattern['action'] == "defect":
                return False
            elif pattern['action'] == "random":
                return random.choice([True, False])

        return True  # Default to cooperation as fallback

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