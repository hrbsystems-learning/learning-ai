# Customer Prefect Flows

A collection of Prefect 3.x workflows for customer automation using CrewAI and LangChain with modern best practices.

## 🚀 Features

- **Prefect 3.x** orchestration with enhanced performance and event-driven capabilities
- **Transactional semantics** for reliable task execution and pipeline idempotency  
- **Event-driven workflows** with automations and external event integration
- **CrewAI** integration for multi-agent automation
- **LangChain** for LLM-powered processing with tracing support
- **Python 3.12** with modern async/await patterns
- **Type-safe** codebase with Pydantic v2 models
- **Rich CLI interface** with typer for easy management
- **Docker support** for containerized deployments
- **Comprehensive testing** with pytest
- **Production-ready** configuration management

## 📁 Project Structure

```
customer-prefect-flows/
├── src/customer_flows/          # Main source code
│   ├── flows/                   # Prefect 3.x flow definitions with transactions
│   ├── tasks/                   # Reusable Prefect 3.x tasks with enhanced features
│   ├── agents/                  # CrewAI agent definitions with monitoring
│   ├── chains/                  # LangChain chain implementations
│   ├── config/                  # Configuration management with Pydantic
│   ├── utils/                   # Utility functions and helpers
│   └── cli.py                   # Rich CLI interface
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── deployments/                 # Deployment configurations
│   ├── docker/                  # Docker configurations
│   ├── prefect_deployments.py   # Prefect 3.x deployment definitions
│   └── .env.example            # Environment configuration template
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
└── pyproject.toml              # Project configuration
```

## 🛠️ Installation

### Prerequisites

- Python 3.12+
- Git
- Docker (optional, for containerized deployment)

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/customer-prefect-flows.git
   cd customer-prefect-flows
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

4. **Configure environment:**
   ```bash
   cp deployments/.env.example .env
   # Edit .env with your configuration
   ```

5. **Validate configuration:**
   ```bash
   python -m src.customer_flows.cli validate-config
   ```

### Docker Setup (Alternative)

1. **Using Docker Compose:**
   ```bash
   cd deployments/docker
   cp ../.env.example .env
   # Edit .env with your configuration
   docker-compose up -d
   ```

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

- **Prefect**: API URL and key for Prefect Cloud/Server
- **OpenAI**: API key for LLM access
- **LangChain**: Tracing and monitoring settings
- **Customer**: Specific customer configuration
- **Database/Redis**: If your flows require persistence

## 🏃‍♂️ Usage

### CLI Commands

The project includes a rich CLI interface for easy management:

```bash
# Show system information
python -m src.customer_flows.cli info

# List available flows
python -m src.customer_flows.cli list-flows

# Run a flow
python -m src.customer_flows.cli run-flow --input "Your data here"

# Test CrewAI configuration
python -m src.customer_flows.cli test-crew

# Validate configuration
python -m src.customer_flows.cli validate-config

# Deploy flows
python -m src.customer_flows.cli deploy --env development
```

### Running Flows Directly

```bash
# Run a specific flow directly
python -m src.customer_flows.flows.example_flow

# Using Prefect CLI (after deployment)
prefect deployment run "example-analysis-development"
```

### Development Workflow

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting and formatting
ruff check src/
black src/

# Run type checking
mypy src/
```

## 📝 Creating New Flows

### 1. Create a Flow

```python
# src/customer_flows/flows/my_new_flow.py
from prefect import flow
from ..tasks.data_processing import process_data
from ..agents.analysis_crew import create_analysis_crew

@flow(name="my-new-flow")
def my_new_flow(input_data: str) -> dict:
    \"\"\"Process data using CrewAI and LangChain.\"\"\"
    
    # Process data
    processed = process_data(input_data)
    
    # Run CrewAI analysis
    crew = create_analysis_crew()
    analysis = crew.kickoff({"data": processed})
    
    return {"processed": processed, "analysis": analysis}

if __name__ == "__main__":
    my_new_flow("sample data")
```

### 2. Create Supporting Tasks

```python
# src/customer_flows/tasks/data_processing.py
from prefect import task
from typing import Any

@task
def process_data(raw_data: str) -> dict[str, Any]:
    \"\"\"Process raw data into structured format.\"\"\"
    # Your processing logic here
    return {"processed": raw_data.upper()}
```

### 3. Create CrewAI Agents

```python
# src/customer_flows/agents/analysis_crew.py
from crewai import Agent, Crew, Task
from langchain_openai import ChatOpenAI

def create_analysis_crew() -> Crew:
    \"\"\"Create a crew for data analysis.\"\"\"
    
    llm = ChatOpenAI(model="gpt-4")
    
    analyst = Agent(
        role="Data Analyst",
        goal="Analyze the provided data",
        backstory="Expert in data analysis and insights",
        llm=llm
    )
    
    task = Task(
        description="Analyze the data and provide insights",
        agent=analyst
    )
    
    return Crew(agents=[analyst], tasks=[task])
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_flows.py

# Run integration tests
pytest tests/integration/
```

## 🚀 Deployment

### Local Development with Docker

```bash
# Start Prefect server and worker
cd deployments/docker
docker-compose up -d

# Deploy flows
python ../prefect_deployments.py --environments development
```

### Manual Deployment

```bash
# Start Prefect server (local)
prefect server start

# Deploy using the deployment script
python deployments/prefect_deployments.py --environments development staging

# Or using CLI
python -m src.customer_flows.cli deploy --env development
```

### Prefect Cloud Deployment

```bash
# Login to Prefect Cloud
prefect cloud login

# Deploy to cloud
python deployments/prefect_deployments.py --environments production
```

### Production Deployment

```bash
# Build and deploy with Docker
docker build -f deployments/docker/Dockerfile -t customer-flows:latest .
docker run -d --name customer-flows-worker customer-flows:latest

# Or use Kubernetes manifests (create as needed)
kubectl apply -f deployments/k8s/
```

## 📚 Documentation

- **Flows**: Detailed documentation in `docs/flows/`
- **Agents**: CrewAI agent configurations in `docs/agents/`
- **API Reference**: Auto-generated docs with `mkdocs serve`

## 🔧 Development Guidelines

### Code Style

- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking
- **Pre-commit** hooks for automated checks

### Naming Conventions

- **Flows**: `snake_case` with descriptive names
- **Tasks**: Action-oriented names (`process_data`, `send_email`)
- **Agents**: Role-based names (`DataAnalyst`, `ContentWriter`)

### Error Handling

- Use Prefect's retry mechanisms for transient failures
- Implement proper logging with `structlog`
- Create custom exceptions for business logic errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues for bug reports and feature requests
- **Documentation**: Check the `docs/` directory
- **Examples**: See `src/customer_flows/flows/` for example implementations   

---  

Yes, absolutely. This is one of the most powerful and important features of using conda as your primary environment manager.

You can and **should** use other package managers like `npm`, `npx`, `yarn`, and `uv` inside an active conda virtual environment. The conda environment acts as a foundational layer that isolates not just Python packages, but the entire toolchain, including the runtimes and package managers for other languages.

Here’s the fundamental principle of how this works and why it's so effective.

### The Core Principle: Conda Manages the `PATH`

When you create a conda environment, you are creating an isolated directory on your filesystem. The real magic happens when you run `conda activate my-env`:

1.  **`PATH` Modification:** Conda modifies your shell's `PATH` environment variable. The `PATH` is the list of directories your terminal searches to find executables.
2.  **Prioritization:** `conda activate` places your environment's `bin` directory (on Linux/macOS) or `Scripts` directory (on Windows) at the very **front** of the `PATH`.

This means that when you type a command like `npm` or `python`, the shell looks in your active environment's directory *first*. If it finds an `npm` executable there, it runs that one and stops searching. This effectively "shadows" any other versions of `npm` or `python` that might be installed globally on your system.

### How This Works for Each Package Manager:

Let's break it down for the examples you gave:

#### `npm`, `npx`, and `yarn` (Node.js Ecosystem)

To use these, you first need to install Node.js *into your conda environment*.

```bash
# 1. Create and activate an environment for a web project
conda create -n my-web-project
conda activate my-web-project

# 2. Install Node.js from the trusted conda-forge channel
conda install -c conda-forge nodejs yarn
```

**What just happened?**
*   Conda downloaded and placed the `node`, `npm`, `npx`, and `yarn` executables inside `.../envs/my-web-project/bin/`.
*   Now, when you run `npm install`, you are using the `npm` that is specific to this environment.
*   Any "global" installs with `npm install -g <package>` will be installed inside the `my-web-project` environment's directory, *not* your system's global Node.js directory. They are sandboxed.

#### `uv` (Modern Python Packager)

`uv` is a very fast Python package installer. You would typically install it into your environment using `pip` or `conda`.

```bash
# 1. Create and activate a Python environment
conda create -n my-fast-py-env python=3.11
conda activate my-fast-py-env

# 2. Install uv
pip install uv
```

**What just happened?**
*   The `uv` executable is now located in `.../envs/my-fast-py-env/bin/`.
*   When you run `uv pip install requests`, `uv` is smart enough to detect that it's running inside an active virtual environment and will install `requests` into that environment's `site-packages` directory, just like `pip` would.

### The Recommended Strategic Workflow

This leads to a clean, reproducible, and conflict-free workflow for any project:

1.  **Create:** For any new project, start with a dedicated conda environment.
    `conda create -n my-project-env`

2.  **Activate:** Always activate the environment before working on the project.
    `conda activate my-project-env`

3.  **Install Runtimes:** Use `conda` to install the foundational runtimes you need, like specific versions of Python and/or Node.js. This is generally more robust.
    `conda install python=3.11 nodejs=20`

4.  **Use Specific Package Managers:** Now, use the package managers appropriate for your project to install libraries.
    *   For Python dependencies: `pip install -r requirements.txt` or `uv pip sync`
    *   For JavaScript dependencies: `npm install` or `yarn add`

### Conclusion

Think of a conda environment not as a "Python-only" space, but as a **self-contained workshop**. You use `conda` to install the main power tools (the Python and Node.js runtimes). Then, inside that workshop, you use the more specialized hand tools (`pip`, `npm`, `uv`, `yarn`) to work on your specific project.

This strategy gives you the best of all worlds:
*   **Total Isolation:** Project A with Node.js 18 will never conflict with Project B with Node.js 20.
*   **Reproducibility:** Your `environment.yml` can define which version of Python and Node.js to use, ensuring anyone can perfectly recreate your setup.
*   **Cleanliness:** Your base operating system remains pristine and uncluttered by development packages.  

---  


