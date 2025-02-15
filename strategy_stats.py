# strategy_stats.py
#
# This module handles the statistics and performance tracking of strategies
# within a game environment. It provides functionality to update and retrieve
# strategy performance metrics, record game results, and manage database
# interactions.
#
# Dependencies:
# - models: Contains the Game and StrategyPerformance models.
# - datetime: For handling date and time operations.
# - typing: For type hinting and annotations.

from typing import Dict
from models import Game, StrategyPerformance, get_db, db_session
from datetime import datetime


class StrategyStats:
    def __init__(self):
        self._ensure_db_session()

    def _ensure_db_session(self):
        db = next(get_db())
        self.db = db

    def update_stats(self, strategy_name: str, score: float, num_rounds: int, cooperation_rate: float = 0.0):
        """Update stats with normalized score (per 100 rounds)"""
        normalized_score = (score / num_rounds) * 100  # Normalize to 100 rounds

        # Get or create strategy performance record
        performance = (
            self.db.query(StrategyPerformance)
            .filter(StrategyPerformance.strategy_name == strategy_name)
            .first()
        )

        if not performance:
            # Initialize a new performance record with default values
            performance = StrategyPerformance(
                strategy_name=strategy_name,
                total_games=0,
                total_score=0.0,
                avg_score_per_round=0.0,
                avg_cooperation_rate=0.0
            )
            self.db.add(performance)
            self.db.commit()  # Commit to ensure the record exists

        # Update performance metrics
        performance.total_games += 1
        performance.total_score += normalized_score
        performance.avg_score_per_round = performance.total_score / performance.total_games

        # Update cooperation rate as moving average
        if cooperation_rate is not None:
            current_total = performance.avg_cooperation_rate * (performance.total_games - 1)
            performance.avg_cooperation_rate = (current_total + cooperation_rate) / performance.total_games

        performance.last_updated = datetime.utcnow()
        self.db.commit()

    def get_average_scores(self) -> Dict[str, float]:
        """Get average normalized scores for each strategy"""
        performances = self.db.query(StrategyPerformance).all()
        return {p.strategy_name: p.avg_score_per_round for p in performances}

    def record_game(self, results: Dict, strategy1_name: str, strategy2_name: str):
        """Record a complete game in the database"""
        game = Game(
            strategy1_name=strategy1_name,
            strategy2_name=strategy2_name,
            score1=results['final_score1'],
            score2=results['final_score2'],
            total_rounds=results['total_rounds'],
            cooperation_rate1=results['cooperation_rate1'],
            cooperation_rate2=results['cooperation_rate2']
        )
        self.db.add(game)
        self.db.commit()

    def get_all_games(self) -> list:
        """
        Get all recorded games from the database.
        
        Returns:
            list: List of dictionaries containing game data with keys:
                - player1: Name of first player's strategy
                - player2: Name of second player's strategy
                - score1: First player's score
                - score2: Second player's score
                - cooperation_rate1: First player's cooperation rate
                - cooperation_rate2: Second player's cooperation rate
                - total_rounds: Number of rounds played
        """
        games = self.db.query(Game).all()
        return [{
            'player1': game.strategy1_name,
            'player2': game.strategy2_name,
            'score1': game.score1,
            'score2': game.score2,
            'cooperation_rate1': game.cooperation_rate1,
            'cooperation_rate2': game.cooperation_rate2,
            'total_rounds': game.total_rounds
        } for game in games]

    def clear_all_stats(self):
        """
        Clears all historical game data from the database.
        """
        with db_session() as session:
            session.query(Game).delete()
            session.query(StrategyPerformance).delete()
            session.commit()