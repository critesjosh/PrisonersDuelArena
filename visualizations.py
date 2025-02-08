import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict

def create_score_plot(results: Dict, strategy1_name: str, strategy2_name: str):
    df = pd.DataFrame({
        'Iteration': range(1, len(results['scores1']) + 1),
        strategy1_name: results['scores1'],
        strategy2_name: results['scores2']
    })

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Iteration'],
        y=df[strategy1_name],
        name=strategy1_name,
        mode='lines'
    ))

    fig.add_trace(go.Scatter(
        x=df['Iteration'],
        y=df[strategy2_name],
        name=strategy2_name,
        mode='lines'
    ))

    fig.update_layout(
        title='Cumulative Scores Over Time',
        xaxis_title='Iteration',
        yaxis_title='Cumulative Score',
        hovermode='x unified'
    )

    return fig

def create_cooperation_plot(results: Dict, strategy1_name: str, strategy2_name: str):
    data = {
        'Strategy': [strategy1_name, strategy2_name],
        'Cooperation Rate': [results['cooperation_rate1'], results['cooperation_rate2']]
    }
    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        x='Strategy',
        y='Cooperation Rate',
        title='Cooperation Rates by Strategy',
        text=df['Cooperation Rate'].apply(lambda x: f'{x:.1%}')
    )

    fig.update_layout(
        yaxis_title='Cooperation Rate',
        yaxis_tickformat=',.0%'
    )

    return fig

def create_historical_performance_plot(avg_scores: Dict[str, float]):
    df = pd.DataFrame({
        'Strategy': list(avg_scores.keys()),
        'Average Score (per 100 rounds)': list(avg_scores.values())
    })

    fig = px.bar(
        df,
        x='Strategy',
        y='Average Score (per 100 rounds)',
        title='Historical Strategy Performance',
        text=df['Average Score (per 100 rounds)'].apply(lambda x: f'{x:.1f}')
    )

    fig.update_layout(
        yaxis_title='Average Score (per 100 rounds)'
    )

    return fig