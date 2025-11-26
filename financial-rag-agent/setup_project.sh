#!/bin/bash

# Financial RAG Agent - Setup Script
# This script initializes the project and builds the vector store

set -e  # Exit on error

echo "========================================================================"
echo "  Financial RAG Agent - Project Setup"
echo "========================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo ""
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -e ".[dev]"
echo "✓ Dependencies installed"

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo "✓ .env file already exists"
fi

# Build vector store
echo ""
echo "Building vector store..."
python3 -m financial_rag_agent.retrieval.vector_store
echo "✓ Vector store built"

# Run tests
echo ""
echo "Running tests..."
pytest tests/ -v --tb=short || echo "⚠️  Some tests may fail if API keys are not configured"

echo ""
echo "========================================================================"
echo "  Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys (OpenAI or Anthropic)"
echo "  2. Activate the virtual environment: source venv/bin/activate"
echo "  3. Run the demo: python notebooks/demo.py"
echo "  4. Start the API: uvicorn financial_rag_agent.api.main:app --reload"
echo "  5. Access docs at: http://localhost:8000/docs"
echo ""
echo "For more information, see README.md"
echo ""
