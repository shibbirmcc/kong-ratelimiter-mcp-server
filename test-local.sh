#!/bin/bash

# Local CI Test Script
# This script runs all the commands that are executed in the CI pipeline
# Run this before committing to catch issues early

set -e  # Exit on any error

echo "🔍 Running local CI tests..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print step headers
print_step() {
    echo -e "\n${YELLOW}📋 $1${NC}"
    echo "------------------------"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a virtual environment and activate if needed
VENV_ACTIVATED=false
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  No virtual environment detected. Creating and activating one...${NC}"
    if [[ ! -d "venv" ]]; then
        echo "Creating virtual environment..."
        python -m venv venv
    fi
    echo "Activating virtual environment..."
    source venv/bin/activate
    VENV_ACTIVATED=true
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
    echo ""
fi

# Step 1: Install dependencies
print_step "Installing dependencies"
python -m pip install --upgrade pip
pip install -e .[dev]
print_success "Dependencies installed"

# Step 2: Run linting
print_step "Running linting checks"

echo "Running Black (code formatting)..."
if black --check src tests; then
    print_success "Black formatting check passed"
else
    print_error "Black formatting check failed"
    echo "Run 'black src tests' to fix formatting issues"
    exit 1
fi

echo "Running isort (import sorting)..."
if isort --check-only src tests; then
    print_success "isort check passed"
else
    print_error "isort check failed"
    echo "Run 'isort src tests' to fix import sorting issues"
    exit 1
fi

echo "Running flake8 (style guide enforcement)..."
if flake8 src tests; then
    print_success "flake8 check passed"
else
    print_error "flake8 check failed"
    exit 1
fi

# Step 3: Run type checking
print_step "Running type checking"
if mypy src; then
    print_success "Type checking passed"
else
    print_error "Type checking failed"
    exit 1
fi

# Step 4: Run tests
print_step "Running tests"
if pytest --cov=kong_mcp_server --cov-report=xml --cov-report=term-missing; then
    print_success "Tests passed"
    
    # Generate text coverage report
    coverage report > coverage.txt
    
    # Print coverage summary
    echo ""
    echo -e "${YELLOW}📊 Coverage Summary${NC}"
    echo "------------------------"
    if [ -f coverage.txt ]; then
        # Extract overall coverage percentage
        COVERAGE=$(grep -E "TOTAL.*[0-9]+%" coverage.txt | awk '{print $NF}')
        echo -e "${GREEN}Overall Coverage: $COVERAGE${NC}"
    else
        echo -e "${RED}Coverage file not found${NC}"
    fi
else
    print_error "Tests failed"
    exit 1
fi

# All checks passed
echo ""
echo "================================"
echo -e "${GREEN}🎉 All local CI checks passed!${NC}"
echo -e "${GREEN}✅ Your code is ready to commit${NC}"
echo "================================"

# Cleanup: Deactivate virtual environment if we activated it
if [[ "$VENV_ACTIVATED" == "true" ]]; then
    echo ""
    echo -e "${YELLOW}🧹 Deactivating virtual environment...${NC}"
    deactivate
    echo -e "${GREEN}✅ Virtual environment deactivated${NC}"
fi