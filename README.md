# 🎮 Prisoner's Dilemma Simulator

An advanced Prisoner's Dilemma simulation platform that leverages AI for dynamic strategy exploration, interpretation, and comparative analysis. This platform allows users to create, test, and analyze different strategies in the classic game theory scenario of the Prisoner's Dilemma.

## 🌟 Features

- **Interactive Strategy Creation**: Design custom strategies using natural language descriptions
- **AI-Powered Strategy Interpretation**: Automatic conversion of strategy descriptions into playable game logic
- **Multiple Game Modes**:
  - Single game simulation with detailed analysis
  - Tournament mode (100 games against all strategies)
- **Rich Visualization**:
  - Real-time score tracking
  - Cooperation rate analysis
  - Historical performance charts
- **Built-in Strategy Templates**:
  - Basic patterns (Always Cooperate, Always Defect, Random)
  - Intermediate patterns (Tit for Tat, Pattern Detection)
  - Advanced strategies (Learning Algorithms, Game Theory Optimal)

## 🛠️ Technology Stack

- Python-based simulation engine
- Streamlit for the web interface
- OpenAI GPT for strategy interpretation
- SQLAlchemy for data persistence
- Plotly for data visualization
- PostgreSQL for database storage

## 🎯 Game Rules

In the Prisoner's Dilemma:
- Two players must choose to either cooperate or defect
- If both cooperate, they each get 3 points
- If both defect, they each get 1 point
- If one defects while the other cooperates, the defector gets 5 points and the cooperator gets 0
- The game continues with a 0.3% chance of ending after each move

## 🚀 Getting Started

1. **Setup Environment**:
   ```bash
   # Install required packages
   pip install -r requirements.txt
   ```

2. **Configure Database**:
   - The application uses PostgreSQL for storing game results and strategy statistics
   - Database configuration is handled automatically through environment variables

3. **Run the Application**:
   ```bash
   streamlit run main.py
   ```

## 📝 Creating Custom Strategies

1. **Using Templates**:
   - Browse pre-defined strategy templates in the sidebar
   - Templates range from basic to advanced complexity levels
   - Click "Use This Template" to populate the strategy creation form

2. **Custom Strategy Creation**:
   - Provide a strategy name
   - Write a description of your strategy
   - Define the strategy logic in natural language
   - Examples:
     - "cooperate first 3 moves then copy opponent"
     - "alternate between cooperating and defecting"
     - "always defect if opponent defected twice in a row"

## 📊 Analysis Features

- **Per-Game Analysis**:
  - Final scores comparison
  - Round-by-round score progression
  - Cooperation rate tracking
  - Winner determination

- **Tournament Analysis**:
  - Average performance against all strategies
  - Historical performance tracking
  - Strategy effectiveness comparisons

## 🎛️ Advanced Features

- **Strategy Pattern Recognition**: AI-powered interpretation of strategy descriptions
- **Pattern Validation**: Prevents misinterpretation of strategy logic
- **Enhanced Logging**: Detailed strategy execution tracking
- **Flexible Game Configuration**: Customizable game parameters

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
