Here is the refined, production-grade guide to launching your Hermes AI Agent and Golang REST API architecture.

This updated workflow integrates OpenRouter's $0.00 / free model routing, SOLID clean-code patterns, graceful signal handling, and the hybrid Docker Named Volumes + Bind Mounts storage strategy.

📁 System Layout
Create a root project folder named hermes-iwcare-app with the following structure:  
```text
hermes-iwcare-app/
├── .env
├── docker-compose.yml
├── Dockerfile
├── main.go
├── go.mod
├── config.yaml              # Bind Mount: Enforces $0.00 free-model routing
├── hermes_skills/           # Bind Mount: Version-controlled skills
│   └── iwcare_consult.md
└── internal/
    ├── config/
    │   └── config.go        # Configuration loader
    ├── proxy/
    │   └── whitelist.go     # Whitelist security proxy
    └── hermes/
        └── client.go        # Hermes client caller  
```  
        
⚙️ Step 1: Configuration & Model Routing Setup:

1. .env (Free Model Credentials)
Set up your environment variables. Leave OPENAI_API_KEY and ANTHROPIC_API_KEY empty so Hermes routes solely through OpenRouter's free tier.
```
# Local Server Setup
SERVER_PORT=:8080
SHARED_WORKSPACE=/app/shared_workspace

# Hermes Auth Credentials
HERMES_GATEWAY_URL=http://hermes-agent:8642
HERMES_AUTH_USER=admin
HERMES_AUTH_PASS=supersecret_hermes_pass

# OpenRouter Free Models Key (Get a free key at openrouter.ai)
OPENROUTER_API_KEY=sk-or-v1-your-free-openrouter-key-here

# Leave blank to force Free-Tier routing
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Remote IWCare Java Backend
REMOTE_IWCARE_URL=https://api.iwhealthsystem.com
IWCARE_USER=dr_john_doe
IWCARE_PASSWORD=remote_java_password  

2. config.yaml (Free Model Delegation)
This file will be bind-mounted into Hermes. It forces the main agentic loop and all sub-tasks (vision, memory compression, title generation) to run on $0.00 free models.
```yaml
# Main Reasoning Model (Free 70B parameter model)
model:
  provider: openrouter
  default: meta-llama/llama-3.3-70b-instruct:free
  api_mode: chat_completions

# Auxiliary Sub-Task Routing
auxiliary:
  # Vision processing: Ingesting patient PDFs and images
  vision:
    provider: openrouter
    model: google/gemini-2.5-flash:free

  # Conversation Compression: Summarizing past medical chats into state.db
  compression:
    provider: openrouter
    model: qwen/qwen-2.5-72b-instruct:free

  # Session Labeling
  title_gen:
    provider: openrouter
    model: mistralai/mistral-7b-instruct:free

# Route Optimization Strategy
provider_routing:
  sort: "price"             # Always prefer $0.00 endpoints
  allow_fallbacks: true     # Auto-fallback if a free model hits rate-limits
```




