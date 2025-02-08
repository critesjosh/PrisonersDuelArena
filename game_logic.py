from typing import Tuple, List, Dict
import numpy as np
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

    def play_round(self, strategy1: Strategy, strategy2: Strategy) -> Tuple[int, int]:
        choice1 = strategy1.make_choice()
        choice2 = strategy2.make_choice()
        
        strategy1.update_history(choice1, choice2)
        strategy2.update_history(choice2, choice1)
        
        return self.payoff_matrix[(choice1, choice2)]

    def run_tournament(self, strategy1: Strategy, strategy2: Strategy, iterations: int) -> Dict:
        scores1 = []
        scores2 = []
        cumulative1 = 0
        cumulative2 = 0

        for _ in range(iterations):
            score1, score2 = self.play_round(strategy1, strategy2)
            cumulative1 += score1
            cumulative2 += score2
            scores1.append(cumulative1)
            scores2.append(cumulative2)

        return {
            'scores1': scores1,
            'scores2': scores2,
            'final_score1': cumulative1,
            'final_score2': cumulative2,
            'cooperation_rate1': sum(strategy1.history) / len(strategy1.history),
            'cooperation_rate2': sum(strategy2.history) / len(strategy2.history)
        }
