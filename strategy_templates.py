from dataclasses import dataclass
from typing import List

@dataclass
class StrategyTemplate:
    name: str
    description: str
    logic: str
    category: str
    complexity: str  # "Basic", "Intermediate", "Advanced"
    example_usage: str

def get_basic_templates() -> List[StrategyTemplate]:
    return [
        StrategyTemplate(
            name="Alternating Pattern",
            description="Alternates between cooperation and defection in a fixed pattern",
            logic="cooperate 10 moves then defect 10 moves",
            category="Pattern-based",
            complexity="Basic",
            example_usage="Cooperates for 10 moves, then defects for 10 moves"
        ),
        StrategyTemplate(
            name="Gradual Trust Builder",
            description="Starts cooperative and gradually becomes more cautious",
            logic="cooperate first 3 moves then copy opponent",
            category="Adaptive",
            complexity="Basic",
            example_usage="Builds initial trust through cooperation"
        ),
        StrategyTemplate(
            name="Forgiveness Strategy",
            description="Copies opponent but occasionally forgives defection",
            logic="copy opponent but cooperate every 3rd move",
            category="Psychological",
            complexity="Basic",
            example_usage="Balance between retaliation and forgiveness"
        )
    ]

def get_intermediate_templates() -> List[StrategyTemplate]:
    return [
        StrategyTemplate(
            name="Majority Rule",
            description="Bases decisions on opponent's most common choice",
            logic="choose what opponent chose most often",
            category="Statistical",
            complexity="Intermediate",
            example_usage="Adapts to opponent's dominant strategy"
        ),
        StrategyTemplate(
            name="Pattern Detector",
            description="Tries to detect and exploit patterns in opponent's moves",
            logic="detect opponent pattern and counter",
            category="Analytical",
            complexity="Intermediate",
            example_usage="Good against predictable strategies"
        )
    ]

def get_advanced_templates() -> List[StrategyTemplate]:
    return [
        StrategyTemplate(
            name="Learning Algorithm",
            description="Adjusts strategy based on success of previous moves",
            logic="learn from past interactions and optimize",
            category="Machine Learning",
            complexity="Advanced",
            example_usage="Evolves strategy throughout the game"
        ),
        StrategyTemplate(
            name="Game Theory Optimal",
            description="Implements optimal strategy based on game theory principles",
            logic="calculate nash equilibrium and play accordingly",
            category="Theoretical",
            complexity="Advanced",
            example_usage="Maximizes expected value against rational opponents"
        )
    ]

def get_all_templates() -> List[StrategyTemplate]:
    return get_basic_templates() + get_intermediate_templates() + get_advanced_templates()

def get_template_by_name(name: str) -> StrategyTemplate:
    return next((t for t in get_all_templates() if t.name == name), None)