import streamlit as st
import pandas as pd
import random
from strategies import get_all_strategies
from game_logic import PrisonersDilemma
from visualizations import create_score_plot, create_cooperation_plot, create_historical_performance_plot
from strategy_stats import StrategyStats

st.set_page_config(
    page_title="Prisoner's Dilemma Simulator",
    page_icon="🎮",
    layout="wide"
)

def main():
    st.title("🎮 Prisoner's Dilemma Simulator")

    st.markdown("""
    ## Game Rules
    In the Prisoner's Dilemma, two players must choose to either cooperate or defect:
    - If both cooperate, they each get 3 points
    - If both defect, they each get 1 point
    - If one defects while the other cooperates, the defector gets 5 points and the cooperator gets 0

    The game continues with a 0.3% chance of ending after each move.
    """)

    # Get available strategies
    strategies = get_all_strategies()
    strategy_dict = {s.name: type(s) for s in strategies}

    # Initialize strategy stats
    stats_manager = StrategyStats()

    # Display historical performance
    st.subheader("Historical Strategy Performance")
    avg_scores = stats_manager.get_average_scores()
    if avg_scores:
        st.plotly_chart(
            create_historical_performance_plot(avg_scores),
            use_container_width=True
        )
    else:
        st.info("Play some games to see how different strategies perform over time!")

    # Single column for player strategy selection
    st.subheader("Select Your Strategy")
    selected_strategy = st.selectbox(
        "Choose your strategy",
        options=[s.name for s in strategies],
        help="Select the strategy you want to play with"
    )
    # Get description from the strategy instance
    st.info([s for s in strategies if s.name == selected_strategy][0].description)

    if st.button("Run Simulation"):
        # Initialize game and player strategy
        game = PrisonersDilemma()
        player_strategy = strategy_dict[selected_strategy]()

        # Randomly select opponent strategy (excluding player's strategy)
        available_opponents = [s for s in strategies if s.name != selected_strategy]
        opponent = type(random.choice(available_opponents))()

        # Run tournament
        results = game.run_tournament(player_strategy, opponent)

        # Update strategy stats
        stats_manager.update_stats(selected_strategy, results['final_score1'], results['total_rounds'])
        stats_manager.update_stats(opponent.name, results['final_score2'], results['total_rounds'])

        # Display opponent's strategy
        st.subheader("Opponent's Strategy")
        st.info(f"You played against: {opponent.name}\n\n{opponent.description}")

        # Display results
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Your Final Score", results['final_score1'])
        with col2:
            st.metric("Opponent's Final Score", results['final_score2'])
        with col3:
            winner = "Tie!" if results['final_score1'] == results['final_score2'] else \
                    "You Win!" if results['final_score1'] > results['final_score2'] else \
                    "Opponent Wins!"
            st.metric("Winner", winner)
        with col4:
            st.metric("Total Rounds", results['total_rounds'])

        # Visualizations
        st.plotly_chart(
            create_score_plot(results, selected_strategy, opponent.name),
            use_container_width=True
        )

        st.plotly_chart(
            create_cooperation_plot(results, selected_strategy, opponent.name),
            use_container_width=True
        )

        # Update and display historical performance
        avg_scores = stats_manager.get_average_scores()
        st.plotly_chart(
            create_historical_performance_plot(avg_scores),
            use_container_width=True
        )

        # Strategy Analysis
        st.subheader("Strategy Analysis")
        analysis_df = pd.DataFrame({
            'Metric': ['Total Score', 'Average Score per Round', 'Cooperation Rate'],
            'Your Strategy': [
                results['final_score1'],
                round(results['final_score1'] / results['total_rounds'], 2),
                f"{results['cooperation_rate1']:.1%}"
            ],
            'Opponent Strategy': [
                results['final_score2'],
                round(results['final_score2'] / results['total_rounds'], 2),
                f"{results['cooperation_rate2']:.1%}"
            ]
        })
        st.table(analysis_df)

if __name__ == "__main__":
    main()