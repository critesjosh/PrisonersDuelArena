import streamlit as st
import pandas as pd
import random
from strategies import get_all_strategies, add_custom_strategy
from game_logic import PrisonersDilemma
from visualizations import create_score_plot, create_cooperation_plot, create_historical_performance_plot
from strategy_stats import StrategyStats
from models import init_db

# Initialize database
init_db()

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

    # Add Custom Strategy Section
    st.sidebar.title("Create Custom Strategy")
    with st.sidebar:
        st.markdown("""
        ## Create Your Own Strategy
        Define how your strategy should behave. You can use keywords like:
        - "always cooperate"
        - "always defect"
        - "copy" or "mimic" (copies opponent's last move)
        - "opposite" (does opposite of opponent's last move)
        - "random"
        """)

        custom_name = st.text_input("Strategy Name", placeholder="My Custom Strategy")
        custom_description = st.text_area("Strategy Description", placeholder="Describe how your strategy works")
        custom_logic = st.text_area("Strategy Logic", placeholder="e.g., always cooperate first, then copy opponent")

        if st.button("Add Custom Strategy"):
            if custom_name and custom_description and custom_logic:
                add_custom_strategy(custom_name, custom_description, custom_logic)
                st.success(f"Added new strategy: {custom_name}")
            else:
                st.error("Please fill in all fields")

    # Get available strategies
    strategies = get_all_strategies()
    strategy_dict = {s.name: type(s) for s in strategies}

    # Initialize strategy stats
    stats_manager = StrategyStats()

    # Single column for player strategy selection
    st.subheader("Select Your Strategy")
    selected_strategy = st.selectbox(
        "Choose your strategy",
        options=[s.name for s in strategies],
        help="Select the strategy you want to play with"
    )
    # Get description from the strategy instance
    st.info([s for s in strategies if s.name == selected_strategy][0].description)

    # Create two columns for the simulation buttons
    col1, col2 = st.columns(2)

    with col1:
        single_game = st.button("Run Single Game")

    with col2:
        multi_game = st.button("Run 100 Games Against All Strategies")

    # Initialize game
    game = PrisonersDilemma()

    if single_game:
        # Initialize player strategy
        player_strategy = strategy_dict[selected_strategy]()

        # Randomly select opponent strategy (including the possibility of same strategy)
        opponent = type(random.choice(strategies))()

        # Run tournament
        results = game.run_tournament(player_strategy, opponent)

        # Update strategy stats and record game
        stats_manager.update_stats(
            selected_strategy, 
            results['final_score1'], 
            results['total_rounds'],
            results['cooperation_rate1']
        )
        stats_manager.update_stats(
            opponent.name, 
            results['final_score2'], 
            results['total_rounds'],
            results['cooperation_rate2']
        )
        stats_manager.record_game(results, selected_strategy, opponent.name)

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

    elif multi_game:
        st.subheader("Running Multiple Games")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Initialize player strategy
        player_strategy_class = strategy_dict[selected_strategy]
        total_strategies = len(strategies)

        for i, opponent_strategy in enumerate(strategies):
            status_text.text(f"Playing against {opponent_strategy.name}...")

            num_games = 100  # Reduced from 1000
            for game_num in range(num_games):
                if game_num % 10 == 0:  # Update status every 10 games
                    status_text.text(f"Playing against {opponent_strategy.name} - Game {game_num + 1}/{num_games}")
                
                player_strategy = player_strategy_class()
                opponent = type(opponent_strategy)()
                results = game.run_tournament(player_strategy, opponent)

                # Update stats and record game
                stats_manager.update_stats(
                    selected_strategy, 
                    results['final_score1'], 
                    results['total_rounds'],
                    results['cooperation_rate1']
                )
                stats_manager.update_stats(
                    opponent.name, 
                    results['final_score2'], 
                    results['total_rounds'],
                    results['cooperation_rate2']
                )
                stats_manager.record_game(results, selected_strategy, opponent.name)

            # Update progress
            progress_bar.progress((i + 1) / total_strategies)

        status_text.text("Finished running all games!")

        # Display updated historical performance
        st.subheader("Updated Historical Performance")
        avg_scores = stats_manager.get_average_scores()
        st.plotly_chart(
            create_historical_performance_plot(avg_scores),
            use_container_width=True
        )

if __name__ == "__main__":
    main()