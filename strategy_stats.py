import json
from pathlib import Path
from typing import Dict, List
import pandas as pd

class StrategyStats:
    def __init__(self):
        self.stats_file = Path("strategy_stats.json")
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                return self._initialize_stats()
        return self._initialize_stats()
    
    def _initialize_stats(self) -> Dict:
        return {
            'games_played': {},  # Number of games each strategy has played
            'total_score': {},   # Total normalized score for each strategy
        }
    
    def _save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f)
    
    def update_stats(self, strategy_name: str, score: float, num_rounds: int):
        """Update stats with normalized score (per 100 rounds)"""
        if strategy_name not in self.stats['games_played']:
            self.stats['games_played'][strategy_name] = 0
            self.stats['total_score'][strategy_name] = 0
        
        normalized_score = (score / num_rounds) * 100  # Normalize to 100 rounds
        self.stats['games_played'][strategy_name] += 1
        self.stats['total_score'][strategy_name] += normalized_score
        self._save_stats()
    
    def get_average_scores(self) -> Dict[str, float]:
        """Get average normalized scores for each strategy"""
        avg_scores = {}
        for strategy in self.stats['games_played']:
            if self.stats['games_played'][strategy] > 0:
                avg_scores[strategy] = (
                    self.stats['total_score'][strategy] / 
                    self.stats['games_played'][strategy]
                )
        return avg_scores
