#!/bin/bash

# Kong MCP Server Management Script
# Manages the Kong Rate Limiter MCP Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="/tmp/kong_mcp_server.pid"
LOG_FILE="/tmp/kong_mcp_server.log"
SERVER_MODULE="kong_mcp_server.server"
DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT="8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if server is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is not running
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Get server PID if running
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    fi
}

# Start the server
start_server() {
    print_status "Starting Kong MCP Server..."
    
    if is_running; then
        print_warning "Server is already running (PID: $(get_pid))"
        return 0
    fi
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Check if virtual environment exists and activate it
    if [ -d "venv" ]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
    else
        print_warning "Virtual environment not found. Make sure dependencies are installed."
    fi
    
    # Start server in background
    print_status "Launching server module: $SERVER_MODULE"
    nohup python -m "$SERVER_MODULE" > "$LOG_FILE" 2>&1 &
    local server_pid=$!
    
    # Save PID
    echo "$server_pid" > "$PID_FILE"
    
    # Wait a moment and check if server started successfully
    sleep 2
    if is_running; then
        print_success "Server started successfully (PID: $server_pid)"
        print_status "Server logs: $LOG_FILE"
        print_status "Default endpoint: http://${DEFAULT_HOST}:${DEFAULT_PORT}/sse/"
    else
        print_error "Failed to start server"
        if [ -f "$LOG_FILE" ]; then
            print_error "Check logs: $LOG_FILE"
            tail -n 10 "$LOG_FILE"
        fi
        return 1
    fi
}

# Stop the server
stop_server() {
    print_status "Stopping Kong MCP Server..."
    
    if ! is_running; then
        print_warning "Server is not running"
        return 0
    fi
    
    local pid=$(get_pid)
    print_status "Terminating process (PID: $pid)"
    
    # Try graceful shutdown first
    kill "$pid" 2>/dev/null
    
    # Wait up to 10 seconds for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && is_running; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if is_running; then
        print_warning "Graceful shutdown failed, forcing termination"
        kill -9 "$pid" 2>/dev/null
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ! is_running; then
        print_success "Server stopped successfully"
    else
        print_error "Failed to stop server"
        return 1
    fi
}

# Restart the server
restart_server() {
    print_status "Restarting Kong MCP Server..."
    stop_server
    sleep 1
    start_server
}

# Show server status
show_status() {
    if is_running; then
        local pid=$(get_pid)
        print_success "Server is running (PID: $pid)"
        
        # Show process info
        echo
        print_status "Process information:"
        ps -p "$pid" -o pid,ppid,cmd,etime 2>/dev/null || true
        
        # Show recent logs if available
        if [ -f "$LOG_FILE" ]; then
            echo
            print_status "Recent logs (last 10 lines):"
            tail -n 10 "$LOG_FILE"
        fi
    else
        print_warning "Server is not running"
    fi
}

# Show server logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Server logs:"
        echo "----------------------------------------"
        cat "$LOG_FILE"
    else
        print_warning "No log file found at $LOG_FILE"
    fi
}

# Follow server logs
follow_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Following server logs (Ctrl+C to stop):"
        echo "----------------------------------------"
        tail -f "$LOG_FILE"
    else
        print_warning "No log file found at $LOG_FILE"
        if is_running; then
            print_status "Server is running but no log file exists yet. Waiting..."
            while [ ! -f "$LOG_FILE" ] && is_running; do
                sleep 1
            done
            if [ -f "$LOG_FILE" ]; then
                tail -f "$LOG_FILE"
            fi
        fi
    fi
}

# Show help
show_help() {
    echo "Kong MCP Server Management Script"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|follow|help}"
    echo
    echo "Commands:"
    echo "  start    - Start the Kong MCP Server"
    echo "  stop     - Stop the Kong MCP Server"
    echo "  restart  - Restart the Kong MCP Server"
    echo "  status   - Show server status and recent logs"
    echo "  logs     - Show all server logs"
    echo "  follow   - Follow server logs in real-time"
    echo "  help     - Show this help message"
    echo
    echo "Files:"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
    echo "  Project:  $PROJECT_DIR"
    echo
    echo "Environment Variables:"
    echo "  HOST     - Server host (default: $DEFAULT_HOST)"
    echo "  PORT     - Server port (default: $DEFAULT_PORT)"
    echo
    echo "Examples:"
    echo "  $0 start         # Start the server"
    echo "  $0 status        # Check if running"
    echo "  $0 follow        # Watch logs in real-time"
    echo "  $0 restart       # Restart server"
}

# Main command processing
case "${1:-}" in
    "start")
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        restart_server
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "follow")
        follow_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        print_error "No command specified"
        echo
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac