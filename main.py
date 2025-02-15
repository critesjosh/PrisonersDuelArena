"""
main.py

This is the main entry point for the Prisoner's Dilemma Simulator application.
It implements the Streamlit-based web interface and coordinates all the major
components of the system.

Key features:
- Web-based user interface using Streamlit
- Strategy creation and management
- Game simulation and visualization
- Tournament mode with multiple games
- Real-time statistics and analysis
- Strategy template browsing and usage
- Custom strategy creation with AI interpretation

The application allows users to:
1. Create and test custom strategies
2. Run single games or tournaments
3. Analyze game results with visualizations
4. Browse and use strategy templates
5. Track historical performance
"""

import streamlit as st
import pandas as pd
import random
from strategies import get_all_strategies, add_custom_strategy, remove_custom_strategy
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
    
    # Add strategy selection to sidebar
    st.sidebar.markdown("## 🎮 Active Strategies")
    st.sidebar.markdown("Select which strategies will participate in the simulation:")
    
    # Initialize session state for strategy selection if not exists
    if 'active_strategies' not in st.session_state:
        st.session_state.active_strategies = {s.name: True for s in strategies}
    
    # Create checkboxes for each strategy
    for strategy in strategies:
        st.session_state.active_strategies[strategy.name] = st.sidebar.checkbox(
            strategy.name,
            value=st.session_state.active_strategies.get(strategy.name, True),
            help=strategy.description
        )
    
    # Filter strategies based on selection
    active_strategies = [s for s in strategies if st.session_state.active_strategies[s.name]]
    if not active_strategies:
        st.sidebar.error("Please select at least one strategy!")
        active_strategies = strategies[:1]  # Select first strategy if none selected
    
    strategy_dict = {s.name: type(s) for s in active_strategies}

    stats_manager = StrategyStats()

    st.subheader("Select Your Strategy")
    selected_strategy = st.selectbox(
        "Choose your strategy",
        options=[s.name for s in active_strategies],
        help="Select the strategy you want to play with"
    )
    st.info([s for s in active_strategies if s.name == selected_strategy][0].description)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        single_game = st.button("Run Single Game")

    with col2:
        multi_game = st.button("Run 100 Games Against All Strategies")
        
    with col3:
        show_stats = st.button("Show Historical Tournament Results")
        
    with col4:
        if st.button("🗑️ Clear History", help="Delete all historical game results"):
            stats_manager.clear_all_stats()
            st.success("Historical data cleared successfully!")
            st.rerun()

    game = PrisonersDilemma()

    if single_game:
        player_strategy = strategy_dict[selected_strategy]()
        opponent = type(random.choice(active_strategies))()
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
                int(results['final_score1']),
                round(results['final_score1'] / results['total_rounds'], 2),
                round(results['cooperation_rate1'] * 100, 1)  # Store as numeric value
            ],
            'Opponent Strategy': [
                int(results['final_score2']),
                round(results['final_score2'] / results['total_rounds'], 2),
                round(results['cooperation_rate2'] * 100, 1)  # Store as numeric value
            ]
        })

        # Format the cooperation rate after DataFrame creation
        analysis_df['Your Strategy'] = analysis_df.apply(
            lambda x: f"{x['Your Strategy']}%" if x['Metric'] == 'Cooperation Rate' else x['Your Strategy'],
            axis=1
        )
        analysis_df['Opponent Strategy'] = analysis_df.apply(
            lambda x: f"{x['Opponent Strategy']}%" if x['Metric'] == 'Cooperation Rate' else x['Opponent Strategy'],
            axis=1
        )

        st.table(analysis_df)

    elif multi_game:
        st.subheader("Running Multiple Games")
        avg_scores = run_tournament(
            selected_strategy,
            strategy_dict,
            active_strategies,
            game,
            stats_manager
        )
        st.subheader("Updated Historical Performance")
        st.plotly_chart(
            create_historical_performance_plot(avg_scores),
            use_container_width=True
        )
    elif show_stats:
        st.subheader("Historical Tournament Results")
        
        # Show both the tournament matrix and historical performance plot
        fig_tournament = create_tournament_plots(active_strategies, stats_manager)
        st.plotly_chart(fig_tournament, use_container_width=True)
        
        avg_scores = stats_manager.get_average_scores()
        if avg_scores:  # Only show if there are recorded scores
            st.subheader("Average Strategy Performance")
            fig_performance = create_historical_performance_plot(avg_scores)
            st.plotly_chart(fig_performance, use_container_width=True)
        else:
            st.info("No historical performance data available yet. Run some games to see statistics!")

def run_tournament(selected_strategy, strategy_dict, strategies, game, stats_manager):
    """
    Runs a tournament of 100 games between all possible combinations of strategies.
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize performance matrices
    strategy_names = [s.name for s in strategies]
    score_matrix = {s1: {s2: 0 for s2 in strategy_names} for s1 in strategy_names}
    coop_matrix = {s1: {s2: 0 for s2 in strategy_names} for s1 in strategy_names}
    
    total_combinations = len(strategies) * len(strategies)
    games_completed = 0
    
    # Run games between all possible strategy combinations
    for strategy1 in strategies:
        for strategy2 in strategies:
            status_text.text(f"Playing: {strategy1.name} vs {strategy2.name}...")
            
            total_score1 = 0
            total_score2 = 0
            total_coop1 = 0
            num_games = 100
            
            for game_num in range(num_games):
                if game_num % 10 == 0:
                    status_text.text(
                        f"Playing {strategy1.name} vs {strategy2.name} - Game {game_num + 1}/{num_games}"
                    )
                
                player1 = type(strategy1)()
                player2 = type(strategy2)()
                results = game.run_tournament(player1, player2)
                
                total_score1 += results['final_score1']
                total_score2 += results['final_score2']
                total_coop1 += results['cooperation_rate1']
                
                stats_manager.update_stats(
                    strategy1.name, 
                    results['final_score1'], 
                    results['total_rounds'],
                    results['cooperation_rate1']
                )
                stats_manager.update_stats(
                    strategy2.name, 
                    results['final_score2'], 
                    results['total_rounds'],
                    results['cooperation_rate2']
                )
                stats_manager.record_game(results, strategy1.name, strategy2.name)
            
            # Store average scores and cooperation rates in matrices
            score_matrix[strategy1.name][strategy2.name] = total_score1 / num_games
            coop_matrix[strategy1.name][strategy2.name] = (total_coop1 / num_games) * 100
            
            games_completed += 1
            progress_bar.progress(games_completed / total_combinations)

    status_text.text("Tournament completed! All strategy combinations tested.")
    
    # Create heatmaps using plotly
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np
    
    score_data = np.array([[score_matrix[s1][s2] for s2 in strategy_names] for s1 in strategy_names])
    coop_data = np.array([[coop_matrix[s1][s2] for s2 in strategy_names] for s1 in strategy_names])
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Average Scores', 'Cooperation Rates (%)'),
        horizontal_spacing=0.15
    )
    
    # Add score heatmap
    fig.add_trace(
        go.Heatmap(
            z=score_data,
            x=strategy_names,
            y=strategy_names,
            hoverongaps=False,
            text=np.round(score_data, 1),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorscale='RdYlGn',
            colorbar=dict(title='Score', x=0.45),
            name='Scores'
        ),
        row=1, col=1
    )
    
    # Add cooperation rate heatmap
    fig.add_trace(
        go.Heatmap(
            z=coop_data,
            x=strategy_names,
            y=strategy_names,
            hoverongaps=False,
            text=np.round(coop_data, 1),
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorscale='Blues',
            colorbar=dict(title='Cooperation %', x=1.0),
            name='Cooperation'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title='Strategy Performance Matrix',
        width=1200,
        height=600,
    )
    
    # Update axes for both subplots
    for i in [1, 2]:
        fig.update_xaxes(title='Opponent Strategy', side='bottom', tickangle=45, row=1, col=i)
        fig.update_yaxes(title='Player Strategy' if i == 1 else None, row=1, col=i)
    
    st.plotly_chart(fig, use_container_width=True)
    
    return stats_manager.get_average_scores()

def create_tournament_plots(strategies, stats_manager):
    """
    Creates tournament visualization plots using existing data from stats_manager.
    
    Args:
        strategies: List of available strategies
        stats_manager: StrategyStats instance containing historical game data
    """
    strategy_names = [s.name for s in strategies]
    score_matrix = {s1: {s2: 0 for s2 in strategy_names} for s1 in strategy_names}
    coop_matrix = {s1: {s2: 0 for s2 in strategy_names} for s1 in strategy_names}
    
    # Get existing data from stats_manager
    stats = stats_manager.get_all_games()
    game_counts = {s1: {s2: 0 for s2 in strategy_names} for s1 in strategy_names}
    
    # Aggregate existing data
    for game in stats:
        player1 = game['player1']
        player2 = game['player2']
        if player1 in strategy_names and player2 in strategy_names:
            score_matrix[player1][player2] += game['score1']
            coop_matrix[player1][player2] += game['cooperation_rate1'] * 100
            game_counts[player1][player2] += 1
    
    # Calculate averages
    for s1 in strategy_names:
        for s2 in strategy_names:
            count = game_counts[s1][s2]
            if count > 0:
                score_matrix[s1][s2] /= count
                coop_matrix[s1][s2] /= count
    
    # Create visualization
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np
    
    score_data = np.array([[score_matrix[s1][s2] for s2 in strategy_names] for s1 in strategy_names])
    coop_data = np.array([[coop_matrix[s1][s2] for s2 in strategy_names] for s1 in strategy_names])
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Average Scores', 'Cooperation Rates (%)'),
        horizontal_spacing=0.15
    )
    
    # Add score heatmap
    fig.add_trace(
        go.Heatmap(
            z=score_data,
            x=strategy_names,
            y=strategy_names,
            hoverongaps=False,
            text=np.round(score_data, 1),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorscale='RdYlGn',
            colorbar=dict(title='Score', x=0.45),
            name='Scores'
        ),
        row=1, col=1
    )
    
    # Add cooperation rate heatmap
    fig.add_trace(
        go.Heatmap(
            z=coop_data,
            x=strategy_names,
            y=strategy_names,
            hoverongaps=False,
            text=np.round(coop_data, 1),
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorscale='Blues',
            colorbar=dict(title='Cooperation %', x=1.0),
            name='Cooperation'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title='Historical Strategy Performance Matrix',
        width=1200,
        height=600,
    )
    
    # Update axes for both subplots
    for i in [1, 2]:
        fig.update_xaxes(title='Opponent Strategy', side='bottom', tickangle=45, row=1, col=i)
        fig.update_yaxes(title='Player Strategy' if i == 1 else None, row=1, col=i)
    
    return fig

if __name__ == "__main__":
    if 'custom_name' not in st.session_state:
        st.session_state.custom_name = ''
    if 'custom_description' not in st.session_state:
        st.session_state.custom_description = ''
    if 'custom_logic' not in st.session_state:
        st.session_state.custom_logic = ''

    main()