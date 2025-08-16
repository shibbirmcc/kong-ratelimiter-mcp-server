#!/bin/bash

VENV_DIR="venv"
PROJECT_NAME="kong-ratelimiter-mcp-server"

activate() {
    echo "🚀 Activating virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "📦 Creating virtual environment..."
        python -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    echo "✅ Virtual environment activated"
    
    # Install dependencies
    echo "📚 Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        # Use pyproject.toml with editable install for development
        pip install -e .[dev]
    fi
    
    echo "🎉 Setup complete! Virtual environment is ready."
    echo "💡 Run 'deactivate' to exit the virtual environment."
}

deactivate_venv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "🔄 Deactivating virtual environment..."
        deactivate
        echo "✅ Virtual environment deactivated"
    else
        echo "⚠️  No virtual environment is currently active"
    fi
}

# Check command line arguments
case "$1" in
    "activate"|"")
        activate
        ;;
    "deactivate")
        deactivate_venv
        ;;
    "clean")
        echo "🧹 Removing virtual environment..."
        if [ -d "$VENV_DIR" ]; then
            rm -rf "$VENV_DIR"
            echo "✅ Virtual environment removed"
        else
            echo "⚠️  No virtual environment found"
        fi
        ;;
    *)
        echo "Usage: $0 [activate|deactivate|clean]"
        echo ""
        echo "Commands:"
        echo "  activate    - Create/activate venv and install dependencies (default)"
        echo "  deactivate  - Deactivate current virtual environment"
        echo "  clean       - Remove virtual environment directory"
        echo ""
        echo "Examples:"
        echo "  $0           # Activate (default)"
        echo "  $0 activate  # Activate explicitly"
        echo "  $0 deactivate # Deactivate"
        echo "  $0 clean     # Remove venv"
        exit 1
        ;;
esac