"""
game_logic.py

Core game mechanics for the Prisoner's Dilemma simulation. This module implements
the fundamental rules, scoring, and tournament logic for the game.

Key Features:
- Payoff matrix definition and management
- Game round execution and scoring
- Tournament management with multiple rounds
- Player interaction tracking
- Statistics collection and analysis
- Type-safe implementation with proper annotations

Classes:
    PrisonersDilemma: Main game engine that handles gameplay mechanics

Types:
    Choice: Type alias for True (cooperate) or False (defect)
    PayoffMatrix: Type alias for the game's scoring matrix

Example Usage:
    game = PrisonersDilemma()
    score1, score2 = game.play_round(strategy1, strategy2)
    tournament_results = game.run_tournament(strategy1, strategy2)
"""

from typing import Tuple, List, Dict, TypeVar, Literal
import numpy as np  # Will be used for future statistical analysis
import random
from strategies import Strategy

T = TypeVar('T')
Choice = Literal[True, False]
PayoffMatrix = Dict[Tuple[Choice, Choice], Tuple[int, int]]

class PrisonersDilemma:
    def __init__(self):
        # Payoff matrix: (row_player_payoff, col_player_payoff)
        self.payoff_matrix: PayoffMatrix = {
            (True, True): (3, 3),    # Both cooperate
            (True, False): (0, 5),   # Row cooperates, Col defects
            (False, True): (5, 0),   # Row defects, Col cooperates
            (False, False): (1, 1)   # Both defect
        }
        self.MAX_ITERATIONS = 1000  # Safety limit

    def play_round(self, strategy1: Strategy, strategy2: Strategy) -> Tuple[int, int]:
        """Play a single round of the Prisoner's Dilemma

        Args:
            strategy1 (Strategy): First player's strategy
            strategy2 (Strategy): Second player's strategy

        Returns:
            Tuple[int, int]: The scores for both players in this round
        """
        choice1 = strategy1.make_choice()
        choice2 = strategy2.make_choice()

        strategy1.update_history(choice1, choice2)
        strategy2.update_history(choice2, choice1)

        # Cast to Choice type to satisfy type checker
        key: Tuple[Choice, Choice] = (bool(choice1), bool(choice2))
        return self.payoff_matrix[key]

    def run_tournament(self, strategy1: Strategy, strategy2: Strategy) -> Dict:
        """Run a complete tournament between two strategies

        Args:
            strategy1 (Strategy): First player's strategy
            strategy2 (Strategy): Second player's strategy

        Returns:
            Dict: Tournament results including scores and statistics
        """
        scores1: List[int] = []
        scores2: List[int] = []
        cumulative1 = 0
        cumulative2 = 0
        iterations = 0

        # Continue until random end condition or max iterations
        while iterations < self.MAX_ITERATIONS:
            score1, score2 = self.play_round(strategy1, strategy2)
            cumulative1 += score1
            cumulative2 += score2
            scores1.append(cumulative1)
            scores2.append(cumulative2)
            iterations += 1

            # 0.3% chance of ending after each move
            if random.random() < 0.003:
                break

        return {
            'scores1': scores1,
            'scores2': scores2,
            'final_score1': cumulative1,
            'final_score2': cumulative2,
            'cooperation_rate1': sum(strategy1.history) / len(strategy1.history),
            'cooperation_rate2': sum(strategy2.history) / len(strategy2.history),
            'total_rounds': iterations
        }