# Set your OpenAI API key in the environment
   # This is required for strategy parsing functionality
   ```

2. **Running the Application**:
   ```bash
   streamlit run main.py --server.port 5000
   ```

   The application will be available at `http://localhost:5000`

## 🔧 Setup Requirements

- Python 3.8+
- PostgreSQL database (automatically configured through environment variables)
- OpenAI API access for strategy parsing

## ⚙️ Configuration

1. **Environment Setup**:
   - The application uses environment variables for configuration
   - Database configuration is handled automatically
   - OpenAI API key is required for strategy parsing (will be prompted during first run)

2. **Database Configuration**:
   - The application uses PostgreSQL for storing game results and strategy statistics
   - Database configuration is handled automatically through environment variables

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

## 📚 Documentation

The project uses Sphinx for documentation generation. You can build the documentation using:

```bash
cd docs
make html