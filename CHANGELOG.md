# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-08-23

### Added
- MCP protocol compliance with proper tool execution framework
- Standard MCP protocol endpoints for FastMCP client compatibility
- Codecov integration with 80% coverage requirement configuration
- Kong HTTP client for Admin API communication
- Enhanced server management script with health checks and improved logging
- MCP Inspector testing documentation and commands
- Port configuration with FASTMCP_PORT environment variable support

### Changed
- Updated default server port from 8000 to 8080
- Enabled all Kong tools (routes and services management)
- Removed basic hello world tool in favor of Kong-specific functionality
- Improved README with comprehensive developer instructions
- Updated Docker configuration for better port management

### Fixed
- Resolved code formatting and linting issues across the codebase
- Fixed test failures and improved test coverage
- Corrected port configuration with proper fallback mechanisms
- Addressed type checking issues and code quality improvements

### Documentation
- Enhanced README with MCP Inspector testing section
- Added proper command examples and port configuration docs
- Restored comprehensive developer setup instructions

## [0.1.0] - 2025-08-17

### Added
- Initial project setup with Python structure
- FastMCP server with SSE Transport
- Hello World tool for testing MCP functionality
- Version management script
- Basic project documentation