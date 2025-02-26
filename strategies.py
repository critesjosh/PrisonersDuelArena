# strategies.py
#
# This module manages the implementation and execution of various strategies
# within the game environment. It provides functions to retrieve, add, and
# execute strategies, allowing for dynamic strategy management.
#
# Dependencies:
# - strategy_interpreter: For interpreting and executing strategies.
# - typing: For type hinting and annotations.
# - other necessary modules for strategy logic.

from typing import List, Tuple, Optional, Callable, Union
from strategy_interpreter import StrategyInterpreter
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
        # Get class-level attributes if they exist
        class_name = getattr(self, 'name', None)
        class_description = getattr(self, 'description', None)
        class_logic = getattr(self, 'logic', None)

        # Use class attributes first, then parameters, then defaults
        final_name = class_name or name or 'Custom Strategy'
        final_description = class_description or description or 'A custom strategy'
        final_logic = (class_logic or logic or 'always cooperate').lower()

        super().__init__(final_name, final_description)
        self.logic = final_logic
        self.move_counter = 0

        # Check if strategy interpretation is already cached
        cached_pattern = self.interpreter.get_cached_interpretation(self.logic)
        if cached_pattern:
            print(f"[{self.name}] Using cached strategy pattern")
            self.strategy_pattern = cached_pattern
        else:
            # Use AI to interpret the strategy and cache it
            print(f"[{self.name}] Interpreting new strategy: '{self.logic}'")
            self.strategy_pattern = self.interpreter.interpret_strategy(self.logic)

    def make_choice(self) -> bool:
        pattern_type = self.strategy_pattern['type']
        pattern = self.strategy_pattern['pattern']
        choice = True  # Default to cooperation

        print(f"\n[{self.name}] Making choice for move {self.move_counter + 1}")
        print(f"[{self.name}] Using pattern type: {pattern_type}")

        if pattern_type == "sequence":
            total_sequence = pattern['cooperate_count'] + pattern['defect_count']
            current_sequence_position = self.move_counter % total_sequence
            should_cooperate = current_sequence_position < pattern['cooperate_count']

            print(f"[{self.name}] Sequence details:")
            print(f"  - Total sequence length: {total_sequence}")
            print(f"  - Current position in sequence: {current_sequence_position}")
            print(f"  - Cooperate count: {pattern['cooperate_count']}")
            print(f"  - Should cooperate: {should_cooperate}")

            choice = should_cooperate

        elif pattern_type == "conditional":
            initial_cooperation = pattern.get('initial_cooperation', 0)

            if self.move_counter < initial_cooperation:
                choice = True
                print(f"[{self.name}] In initial cooperation phase: move {self.move_counter + 1} of {initial_cooperation}")
            else:
                if pattern['condition'] == "last_opponent_move":
                    choice = self.opponent_history[-1] if self.opponent_history else True
                    print(f"[{self.name}] Copying opponent's last move: {choice}")

        elif pattern_type == "simple":
            if pattern['action'] == "cooperate":
                choice = True
            elif pattern['action'] == "defect":
                choice = False
            elif pattern['action'] == "random":
                choice = random.choice([True, False])
            print(f"[{self.name}] Simple action '{pattern['action']}' resulted in: {choice}")

        self.move_counter += 1
        return choice

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
        {
            'name': name,
            'description': description,
            'logic': logic
        }
    )
    strategy = strategy_class(name=name, description=description, logic=logic)
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

def remove_custom_strategy(strategy_name):
    """
    Removes a custom strategy from the database.
    
    Args:
        strategy_name (str): Name of the strategy to remove
    """
    from models import CustomStrategy, db_session
    
    with db_session() as session:
        strategy = session.query(CustomStrategy).filter_by(name=strategy_name).first()
        if strategy:
            session.delete(strategy)
            session.commit()