# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a multi-agent nursing advisory system that uses AI agents to coordinate between patients, nursing staff, and management through Google Cloud Pub/Sub messaging. The system integrates multiple LLM providers (Anthropic Claude, OpenAI GPT, Google Gemini) and stores session data in MongoDB.

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run main application
python main.py

# Run test suite
python advisory_test_main.py

# Run single session test
python running_one_session.py
```

## Architecture

### Core Components
- **AdvisoryCenter** (`main_advisory_center.py`) - Central orchestrator managing active sessions and agent coordination
- **MainManagerAgent** (`agents/manager_agent.py`) - Primary AI-powered decision maker with LLM capabilities
- **ActiveSession** (`running_one_session.py`) - Per-user session management with MongoDB persistence

### Agent System
- **Manager Agent** - Uses LLM for intelligent routing and response generation
- **Staff Agent** - Represents nursing staff members 
- **User Agent** - Test implementation for patient interactions

### Infrastructure
- **PubSub Utils** (`pubsub_utils/`) - Google Cloud Pub/Sub messaging with topics: `from_users`, `from_staff`, `to_users`, `to_staff`
- **MongoDB** (`talk_to_mongo.py`) - Session data, messages, and decision storage
- **Secret Manager** (`services/secret_manager_service.py`) - Secure credential management
- **LLM Integration** (`llm_agents/`) - Multi-provider AI client supporting Anthropic, OpenAI, and Gemini

### Domain Data
- **Pediatric Specialties** (`domain_data/pediatrics_specialties.json`) - 20 medical specializations with Hebrew/English descriptions
- **Manager Agent Data** (`domain_data/llm_domain_data/manager_agent_data.py`) - LLM prompts and decision logic

## Environment Setup

Requires `.env` file with:
- Google Cloud credentials for Pub/Sub and Secret Manager
- MongoDB connection strings
- LLM provider API keys (managed through Secret Manager)

## Testing Patterns

- Async test framework with signal handling for graceful shutdown
- Background threading for concurrent message processing
- Mock session testing with real MongoDB and Pub/Sub connections
- Session lifecycle testing from creation to cleanup