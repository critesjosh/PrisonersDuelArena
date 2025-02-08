from typing import Dict
from models import Game, StrategyPerformance, get_db
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
            performance = StrategyPerformance(strategy_name=strategy_name)
            self.db.add(performance)

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