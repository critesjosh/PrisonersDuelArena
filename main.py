import streamlit as st
import pandas as pd
from strategies import get_all_strategies, TitForTat, AlwaysCooperate, AlwaysDefect, RandomStrategy
from game_logic import PrisonersDilemma
from visualizations import create_score_plot, create_cooperation_plot

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
    """)

    # Strategy selection
    strategy_classes = [TitForTat, AlwaysCooperate, AlwaysDefect, RandomStrategy]
    strategy_dict = {s().name: s for s in strategy_classes}
    strategies = get_all_strategies()  # For display purposes

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select Your Strategy")
        selected_strategy = st.selectbox(
            "Choose your strategy",
            options=[s.name for s in strategies],
            help="Select the strategy you want to play with"
        )
        st.info(strategy_dict[selected_strategy].description)

    with col2:
        st.subheader("Select Opponent Strategy")
        opponent_strategy = st.selectbox(
            "Choose opponent's strategy",
            options=[s.name for s in strategies],
            help="Select the strategy you want to play against"
        )
        st.info(strategy_dict[opponent_strategy].description)

    # Simulation parameters
    iterations = st.slider(
        "Number of iterations",
        min_value=10,
        max_value=1000,
        value=100,
        step=10,
        help="Choose how many rounds to simulate"
    )

    if st.button("Run Simulation"):
        # Initialize game and strategies
        game = PrisonersDilemma()
        player_strategy = strategy_dict[selected_strategy]()
        opponent = strategy_dict[opponent_strategy]()

        # Run tournament
        results = game.run_tournament(player_strategy, opponent, iterations)

        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your Final Score", results['final_score1'])
        with col2:
            st.metric("Opponent's Final Score", results['final_score2'])
        with col3:
            winner = "Tie!" if results['final_score1'] == results['final_score2'] else \
                    "You Win!" if results['final_score1'] > results['final_score2'] else \
                    "Opponent Wins!"
            st.metric("Winner", winner)

        # Visualizations
        st.plotly_chart(
            create_score_plot(results, selected_strategy, opponent_strategy),
            use_container_width=True
        )

        st.plotly_chart(
            create_cooperation_plot(results, selected_strategy, opponent_strategy),
            use_container_width=True
        )

        # Strategy Analysis
        st.subheader("Strategy Analysis")
        analysis_df = pd.DataFrame({
            'Metric': ['Total Score', 'Average Score per Round', 'Cooperation Rate'],
            'Your Strategy': [
                results['final_score1'],
                results['final_score1'] / iterations,
                f"{results['cooperation_rate1']:.2%}"
            ],
            'Opponent Strategy': [
                results['final_score2'],
                results['final_score2'] / iterations,
                f"{results['cooperation_rate2']:.2%}"
            ]
        })
        st.table(analysis_df)

if __name__ == "__main__":
    main()
