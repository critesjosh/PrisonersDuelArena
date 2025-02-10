# Set your OpenAI API key in the environment
   # This is required for strategy parsing functionality
   export OPENAI_API_KEY='your-api-key'
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
   - Required environment variables:
     - `OPENAI_API_KEY`: Your OpenAI API key for strategy parsing
     - `DATABASE_URL`: PostgreSQL connection string (automatically configured)
   - OpenAI API key will be prompted during first run if not set

2. **Database Configuration**:
   - The application uses PostgreSQL for storing:
     - Game results
     - Strategy statistics
     - Historical performance data
   - Database setup is handled automatically through the following process:
     - Tables are created on first run
     - Schemas are managed through SQLAlchemy migrations
     - No manual database setup required
   - Data stored includes:
     - Game outcomes
     - Strategy performance metrics
     - Tournament results
     - Player statistics

3. **Infrastructure Components**:
   - **Web Interface**: Streamlit-based dashboard
   - **Database**: PostgreSQL for data persistence
   - **AI Integration**: OpenAI GPT for strategy parsing
   - **Analysis Engine**: Python-based simulation core
   - **Visualization**: Plotly for interactive charts

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