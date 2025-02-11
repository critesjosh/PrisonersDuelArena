"""
game_logic.py

This module implements the core game mechanics for the Prisoner's Dilemma simulation.
It handles:
- Game rules and payoff matrix definition
- Round-by-round gameplay implementation
- Tournament execution and scoring
- Player interaction tracking and statistics collection

The PrisonersDilemma class provides methods for:
- Running individual game rounds
- Managing multi-round tournaments
- Calculating and tracking scores
- Recording player cooperation rates
"""

from typing import Tuple, List, Dict
import numpy as np
import random
from strategies import Strategy

class PrisonersDilemma:
    def __init__(self):
        # Payoff matrix: (row_player_payoff, col_player_payoff)
        self.payoff_matrix = {
            (True, True): (3, 3),    # Both cooperate
            (True, False): (0, 5),   # Row cooperates, Col defects
            (False, True): (5, 0),   # Row defects, Col cooperates
            (False, False): (1, 1)   # Both defect
        }
        self.MAX_ITERATIONS = 1000  # Safety limit

    def play_round(self, strategy1: Strategy, strategy2: Strategy) -> Tuple[int, int]:
        choice1 = strategy1.make_choice()
        choice2 = strategy2.make_choice()

        strategy1.update_history(choice1, choice2)
        strategy2.update_history(choice2, choice1)

        return self.payoff_matrix[(choice1, choice2)]

    def run_tournament(self, strategy1: Strategy, strategy2: Strategy) -> Dict:
        scores1 = []
        scores2 = []
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