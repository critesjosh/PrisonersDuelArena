import streamlit as st
import pandas as pd
import random
from strategies import get_all_strategies, add_custom_strategy
from game_logic import PrisonersDilemma
from visualizations import create_score_plot, create_cooperation_plot, create_historical_performance_plot
from strategy_stats import StrategyStats
from models import init_db
from strategy_templates import get_all_templates, get_template_by_name

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

    st.sidebar.title("Strategy Creation")

    st.sidebar.markdown("## 📚 Strategy Templates")
    templates = get_all_templates()
    template_names = [t.name for t in templates]
    selected_template = st.sidebar.selectbox(
        "Browse Templates",
        options=template_names,
        help="Select a pre-defined strategy template"
    )

    if selected_template:
        template = get_template_by_name(selected_template)
        st.sidebar.markdown(f"**Category:** {template.category}")
        st.sidebar.markdown(f"**Complexity:** {template.complexity}")
        st.sidebar.markdown(f"**Description:** {template.description}")
        st.sidebar.markdown(f"**Example Usage:** {template.example_usage}")

        if st.sidebar.button("Use This Template"):
            st.session_state.custom_name = template.name
            st.session_state.custom_description = template.description
            st.session_state.custom_logic = template.logic

    st.sidebar.markdown("## ✨ Create Custom Strategy")
    custom_name = st.sidebar.text_input(
        "Strategy Name",
        value=st.session_state.get('custom_name', ''),
        placeholder="My Custom Strategy"
    )
    custom_description = st.sidebar.text_area(
        "Strategy Description",
        value=st.session_state.get('custom_description', ''),
        placeholder="Describe how your strategy works"
    )
    custom_logic = st.sidebar.text_area(
        "Strategy Logic",
        value=st.session_state.get('custom_logic', ''),
        placeholder="e.g., always cooperate first, then copy opponent"
    )

    if st.sidebar.button("Add Custom Strategy"):
        if custom_name and custom_description and custom_logic:
            add_custom_strategy(custom_name, custom_description, custom_logic)
            st.sidebar.success(f"Added new strategy: {custom_name}")
        else:
            st.sidebar.error("Please fill in all fields")

    strategies = get_all_strategies()
    strategy_dict = {s.name: type(s) for s in strategies}

    stats_manager = StrategyStats()

    st.subheader("Select Your Strategy")
    selected_strategy = st.selectbox(
        "Choose your strategy",
        options=[s.name for s in strategies],
        help="Select the strategy you want to play with"
    )
    st.info([s for s in strategies if s.name == selected_strategy][0].description)

    col1, col2 = st.columns(2)

    with col1:
        single_game = st.button("Run Single Game")

    with col2:
        multi_game = st.button("Run 100 Games Against All Strategies")

    game = PrisonersDilemma()

    if single_game:
        player_strategy = strategy_dict[selected_strategy]()
        opponent = type(random.choice(strategies))()
        results = game.run_tournament(player_strategy, opponent)
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
        st.subheader("Opponent's Strategy")
        st.info(f"You played against: {opponent.name}\n\n{opponent.description}")
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
        st.plotly_chart(
            create_score_plot(results, selected_strategy, opponent.name),
            use_container_width=True
        )
        st.plotly_chart(
            create_cooperation_plot(results, selected_strategy, opponent.name),
            use_container_width=True
        )
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
        player_strategy_class = strategy_dict[selected_strategy]
        total_strategies = len(strategies)

        for i, opponent_strategy in enumerate(strategies):
            status_text.text(f"Playing against {opponent_strategy.name}...")
            num_games = 100
            for game_num in range(num_games):
                if game_num % 10 == 0:
                    status_text.text(f"Playing against {opponent_strategy.name} - Game {game_num + 1}/{num_games}")
                player_strategy = player_strategy_class()
                opponent = type(opponent_strategy)()
                results = game.run_tournament(player_strategy, opponent)
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
            progress_bar.progress((i + 1) / total_strategies)

        status_text.text("Finished running all games!")
        st.subheader("Updated Historical Performance")
        avg_scores = stats_manager.get_average_scores()
        st.plotly_chart(
            create_historical_performance_plot(avg_scores),
            use_container_width=True
        )

if __name__ == "__main__":
    if 'custom_name' not in st.session_state:
        st.session_state.custom_name = ''
    if 'custom_description' not in st.session_state:
        st.session_state.custom_description = ''
    if 'custom_logic' not in st.session_state:
        st.session_state.custom_logic = ''

    main()