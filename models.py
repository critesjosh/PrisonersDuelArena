# models.py
#
# This module defines the database models used for storing game and strategy
# performance data. It includes models for games and strategy performance,
# and provides the necessary schema for database interactions.
#
# Dependencies:
# - SQLAlchemy: For ORM and database management.
# - other necessary modules for database configuration.

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Database connection with error handling
def get_database_url():
    database_url = create_engine(os.getenv('DATABASE_URL', 'sqlite:///game_data.db'))
    if not database_url:
        raise EnvironmentError("DATABASE_URL environment variable is not set")
    return database_url

try:
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    logger.info("Database connection established successfully")
except Exception as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    raise

def init_db():
    """Initialize the database, creating all tables."""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

def get_db():
    """Get database session with error handling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()