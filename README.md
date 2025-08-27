# VannaSQL Agent

A natural language to SQL converter using Vanna.AI with Ollama and ChromaDB for local database querying.
![Flowchart](./docs/architecture.svg)

## Overview

This project implements Vanna.AI to enable natural language querying of your MySQL database. It uses:
- **Ollama** for local LLM inference (Mistral model)
- **ChromaDB** for vector storage of training data
- **MySQL** as the target database

## Prerequisites

1. **Ollama** installed and running
   ```bash
   # Install Ollama from https://ollama.com
   # Pull the Mistral model
   ollama pull mistral
   ```

2. **MySQL database** accessible with connection details
3. **Python 3.12+**
4. **Microsoft Visual Studio Build Tools**

## Setup

### Online Installation

1. **Install dependencies:**
   ```bash
   pip install -e .
   # or with uv:
   uv sync
   ```

### Offline Installation

For offline environments without internet access, see our comprehensive guide:

📖 **[Offline Package Setup Guide](Docs/OFFLINE_PACKAGE_SETUP_GUIDE.md)**

This guide covers:
- Downloading all dependencies as wheel files
- Resolving dependency conflicts
- Converting source packages to wheels
- Step-by-step offline installation process

2. **Configure database connection:**
   Edit the connection details in the scripts:
   ```python
   vn.connect_to_mysql(
       host='localhost', 
       dbname='your_database', 
       user='your_user', 
       password='your_password', 
       port=3306
   )
   ```

## Usage

### 1. Train the Model (First Time Setup)

Run the training script to extract your database schema and train the model:

```bash
python hello.py
```

This will:
- ✅ Connect to your MySQL database
- 📊 Extract the database schema from `INFORMATION_SCHEMA`
- 📋 Create a training plan
- 🎓 Train the model with your schema
- 📚 Add example training data

**Note:** You only need to train once unless you want to add more training data.

### 2. Interactive Command Line Interface

For interactive querying via command line:

```bash
python example_usage.py
```

Example questions you can ask:
- "Show me all tables in the database"
- "How many records are in each table?"
- "What columns does the users table have?"
- "Find all users created today"

### 3. Web Interface

For a graphical web interface:

```bash
python web_interface.py
```

Then open your browser to: `http://localhost:5000`

The web interface provides:
- 🔍 Natural language query input
- 📊 Automatic SQL generation
- 📈 Query results with visualizations
- 📝 Query history

## Training Data Types

The system learns from multiple types of training data:

1. **Database Schema** (automatic)
   - Table structures from `INFORMATION_SCHEMA`
   - Column names, types, and relationships

2. **DDL Statements** (customizable)
   ```python
   vn.train(ddl="CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))")
   ```

3. **Documentation** (customizable)
   ```python
   vn.train(documentation="CFMS stands for Case File Management System")
   ```

4. **Example Queries** (customizable)
   ```python
   vn.train(sql="SELECT COUNT(*) FROM users WHERE active = 1")
   ```

## Customization

### Adding More Training Data

You can enhance the model by adding domain-specific training:

```python
# Business terminology
vn.train(documentation="Active users are those with status = 'active'")

# Common queries
vn.train(sql="SELECT u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id")

# Table definitions
vn.train(ddl="CREATE TABLE orders (id INT, user_id INT, total DECIMAL(10,2), created_at TIMESTAMP)")
```

### Using Different Models

To use a different Ollama model:

```python
vn = MyVanna(config={'model': 'llama2'})  # or 'codellama', 'phi4-mini:latest', etc.
```

### Managing Training Data

```python
# View all training data
training_data = vn.get_training_data()
print(training_data)

# Remove specific training data
vn.remove_training_data(id='1-ddl')
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │    │   Vanna Core    │    │     MySQL       │
│ (Natural Lang.) │───▶│   + ChromaDB    │───▶│   Database      │
│                 │    │   + Ollama      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Generated SQL  │
                       │   + Results     │
                       └─────────────────┘
```

1. **User** asks a question in natural language
2. **ChromaDB** finds relevant training data (schema, examples, docs)
3. **Ollama/Mistral** generates SQL using the training context
4. **Vanna** executes the SQL against **MySQL**
5. **Results** are returned to the user

## File Structure

```
VannaSQL-Agent/
├── hello.py                        # Training script (run first)
├── example_usage.py                # Interactive CLI interface
├── web_interface.py                # Web UI interface
├── pyproject.toml                  # Dependencies
├── Config.md                       # Package download configuration
├── OFFLINE_PACKAGE_SETUP_GUIDE.md  # Comprehensive offline installation guide
├── dep_pkg/                        # Local packages directory (after setup)
│   └── *.whl                       # Downloaded wheel files
└── README.md                       # This file
```

## Troubleshooting

### Common Issues

1. **"No training data found"**
   - Run `python hello.py` first to train the model

2. **Database connection errors**
   - Verify MySQL is running and credentials are correct
   - Check firewall/network connectivity

3. **Ollama model not found**
   - Make sure Ollama is running: `ollama serve`
   - Pull the model: `ollama pull mistral`

4. **Poor query quality**
   - Add more training data specific to your domain
   - Include example queries for common use cases
   - Add business terminology documentation

### Performance Tips

- **Model choice**: `mistral` is good for general use, `codellama` for complex SQL
- **Training data**: More domain-specific examples = better results
- **Hardware**: Ollama benefits from more RAM and GPU acceleration

## Security Considerations

- This setup runs locally with no external API calls
- Database credentials are stored in plain text (consider environment variables)
- The web interface has no authentication (suitable for development only)
- Generated SQL is executed directly (consider query validation for production)

## Contributing

Feel free to improve the training data, add new examples, or enhance the interface!
