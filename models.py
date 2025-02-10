from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    strategy1_name = Column(String, nullable=False)
    strategy2_name = Column(String, nullable=False)
    score1 = Column(Float, nullable=False)
    score2 = Column(Float, nullable=False)
    total_rounds = Column(Integer, nullable=False)
    cooperation_rate1 = Column(Float, nullable=False)
    cooperation_rate2 = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class StrategyPerformance(Base):
    __tablename__ = 'strategy_performance'
    
    id = Column(Integer, primary_key=True)
    strategy_name = Column(String, nullable=False)
    total_games = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    avg_score_per_round = Column(Float, default=0.0)
    avg_cooperation_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Database connection
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///game_data.db'))
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
