#!/usr/bin/env python3
"""
Example script to add rate limiting to the /healthz endpoint using Kong MCP Server tools.

This script demonstrates how to:
1. Create a route for the /healthz endpoint (if it doesn't exist)
2. Add rate limiting to that specific route
3. Monitor and manage the rate limiting configuration

Based on the request log provided:
- Endpoint: /healthz
- Method: GET
- Current status: 200 (working)
- Client IP: 127.0.0.1
- User Agent: PostmanRuntime/7.45.0
"""

import asyncio
import json
from typing import Dict, Any, Optional

# Import our Kong MCP server rate limiting tools
from src.kong_mcp_server.tools.kong_rate_limiting import (
    create_rate_limiting_plugin,
    get_rate_limiting_plugins,
    update_rate_limiting_plugin,
    delete_rate_limiting_plugin,
    get_plugins,
)
from src.kong_mcp_server.tools.kong_routes import (
    create_route,
    get_routes,
    update_route,
)
from src.kong_mcp_server.tools.kong_services import (
    create_service,
    get_services,
)


async def setup_healthz_rate_limiting():
    """Set up rate limiting for the /healthz endpoint."""
    
    print("🚀 Setting up rate limiting for /healthz endpoint...")
    
    try:
        # Step 1: Check if we have a service for health checks
        print("\n📋 Step 1: Checking for existing health check service...")
        services = await get_services()
        
        health_service = None
        for service in services:
            if service.get("name") == "health-service":
                health_service = service
                break
        
        if not health_service:
            print("   Creating health check service...")
            # Create a service for health checks (assuming your health endpoint is served by your app)
            health_service = await create_service(
                name="health-service",
                url="http://localhost:8080",  # Adjust this to your actual backend
                tags=["health", "monitoring"]
            )
            print(f"   ✅ Created health service: {health_service['id']}")
        else:
            print(f"   ✅ Found existing health service: {health_service['id']}")
        
        # Step 2: Check if we have a route for /healthz
        print("\n📋 Step 2: Checking for existing /healthz route...")
        routes = await get_routes()
        
        healthz_route = None
        for route in routes:
            if "/healthz" in route.get("paths", []):
                healthz_route = route
                break
        
        if not healthz_route:
            print("   Creating /healthz route...")
            healthz_route = await create_route(
                name="healthz-route",
                paths=["/healthz"],
                methods=["GET"],
                service_id=health_service["id"],
                tags=["health", "monitoring"]
            )
            print(f"   ✅ Created /healthz route: {healthz_route['id']}")
        else:
            print(f"   ✅ Found existing /healthz route: {healthz_route['id']}")
        
        # Step 3: Check for existing rate limiting on this route
        print("\n📋 Step 3: Checking for existing rate limiting...")
        existing_plugins = await get_plugins(route_id=healthz_route["id"])
        
        rate_limiting_plugin = None
        for plugin in existing_plugins:
            if plugin.get("name") == "rate-limiting":
                rate_limiting_plugin = plugin
                break
        
        if rate_limiting_plugin:
            print(f"   ⚠️  Rate limiting already exists: {rate_limiting_plugin['id']}")
            print(f"   Current config: {json.dumps(rate_limiting_plugin['config'], indent=2)}")
            
            # Ask if user wants to update
            response = input("\n   Do you want to update the existing rate limiting? (y/N): ")
            if response.lower() == 'y':
                updated_plugin = await update_rate_limiting_plugin(
                    plugin_id=rate_limiting_plugin["id"],
                    minute=60,  # Allow 60 requests per minute for health checks
                    hour=3600,  # Allow 3600 requests per hour
                    limit_by="ip",  # Limit by IP address
                    policy="local",  # Use local policy for simplicity
                    fault_tolerant=True,  # Continue serving if rate limiting fails
                    hide_client_headers=False,  # Show rate limiting headers to client
                    tags=["health", "monitoring", "updated"]
                )
                print(f"   ✅ Updated rate limiting plugin: {updated_plugin['id']}")
                return updated_plugin
            else:
                print("   Keeping existing rate limiting configuration.")
                return rate_limiting_plugin
        
        # Step 4: Create new rate limiting for /healthz
        print("\n📋 Step 4: Creating rate limiting for /healthz route...")
        
        # Configure rate limiting appropriate for health checks
        # Health checks are typically frequent but predictable
        rate_limiting_plugin = await create_rate_limiting_plugin(
            route_id=healthz_route["id"],
            minute=60,  # Allow 60 requests per minute (1 per second)
            hour=3600,  # Allow 3600 requests per hour
            day=86400,  # Allow 86400 requests per day (1 per second)
            limit_by="ip",  # Limit by IP address
            policy="local",  # Use local policy for simplicity
            fault_tolerant=True,  # Continue serving if rate limiting fails
            hide_client_headers=False,  # Show rate limiting headers to client
            tags=["health", "monitoring", "rate-limiting"]
        )
        
        print(f"   ✅ Created rate limiting plugin: {rate_limiting_plugin['id']}")
        print(f"   Configuration:")
        print(f"     - 60 requests per minute")
        print(f"     - 3600 requests per hour") 
        print(f"     - 86400 requests per day")
        print(f"     - Limited by IP address")
        print(f"     - Local policy")
        print(f"     - Fault tolerant")
        
        return rate_limiting_plugin
        
    except Exception as e:
        print(f"❌ Error setting up rate limiting: {e}")
        raise


async def setup_aggressive_healthz_rate_limiting():
    """Set up more aggressive rate limiting for /healthz endpoint (for demonstration)."""
    
    print("🚀 Setting up AGGRESSIVE rate limiting for /healthz endpoint...")
    
    try:
        # Get the healthz route
        routes = await get_routes()
        healthz_route = None
        for route in routes:
            if "/healthz" in route.get("paths", []):
                healthz_route = route
                break
        
        if not healthz_route:
            print("❌ No /healthz route found. Please run setup_healthz_rate_limiting() first.")
            return
        
        # Create aggressive rate limiting
        rate_limiting_plugin = await create_rate_limiting_plugin(
            route_id=healthz_route["id"],
            minute=10,  # Only 10 requests per minute
            hour=100,   # Only 100 requests per hour
            limit_by="ip",
            policy="local",
            fault_tolerant=False,  # Strict enforcement
            hide_client_headers=False,
            tags=["health", "monitoring", "aggressive", "demo"]
        )
        
        print(f"   ✅ Created AGGRESSIVE rate limiting: {rate_limiting_plugin['id']}")
        print(f"   Configuration:")
        print(f"     - 10 requests per minute (very restrictive)")
        print(f"     - 100 requests per hour")
        print(f"     - Limited by IP address")
        print(f"     - Strict enforcement (not fault tolerant)")
        
        return rate_limiting_plugin
        
    except Exception as e:
        print(f"❌ Error setting up aggressive rate limiting: {e}")
        raise


async def monitor_healthz_rate_limiting():
    """Monitor rate limiting status for /healthz endpoint."""
    
    print("📊 Monitoring /healthz rate limiting...")
    
    try:
        # Get all rate limiting plugins
        rate_limiting_plugins = await get_rate_limiting_plugins()
        
        # Filter for healthz-related plugins
        healthz_plugins = []
        for plugin in rate_limiting_plugins:
            if plugin.get("route") and "healthz" in str(plugin.get("route", {})):
                healthz_plugins.append(plugin)
            elif "health" in plugin.get("tags", []):
                healthz_plugins.append(plugin)
        
        if not healthz_plugins:
            print("   ⚠️  No rate limiting found for /healthz endpoint")
            return
        
        print(f"   Found {len(healthz_plugins)} rate limiting plugin(s) for /healthz:")
        
        for i, plugin in enumerate(healthz_plugins, 1):
            print(f"\n   Plugin {i}:")
            print(f"     ID: {plugin['id']}")
            print(f"     Enabled: {plugin.get('enabled', 'unknown')}")
            print(f"     Config: {json.dumps(plugin.get('config', {}), indent=6)}")
            print(f"     Tags: {plugin.get('tags', [])}")
        
        return healthz_plugins
        
    except Exception as e:
        print(f"❌ Error monitoring rate limiting: {e}")
        raise


async def remove_healthz_rate_limiting():
    """Remove rate limiting from /healthz endpoint."""
    
    print("🗑️  Removing rate limiting from /healthz endpoint...")
    
    try:
        # Get rate limiting plugins for healthz
        plugins = await monitor_healthz_rate_limiting()
        
        if not plugins:
            print("   No rate limiting plugins found to remove.")
            return
        
        for plugin in plugins:
            print(f"   Removing plugin: {plugin['id']}")
            result = await delete_rate_limiting_plugin(plugin["id"])
            print(f"   ✅ {result.get('message', 'Deleted successfully')}")
        
        print("   All /healthz rate limiting plugins removed.")
        
    except Exception as e:
        print(f"❌ Error removing rate limiting: {e}")
        raise


async def main():
    """Main function to demonstrate rate limiting setup for /healthz endpoint."""
    
    print("=" * 60)
    print("Kong Rate Limiting Setup for /healthz Endpoint")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. Set up standard rate limiting for /healthz")
        print("2. Set up aggressive rate limiting for /healthz (demo)")
        print("3. Monitor current rate limiting status")
        print("4. Remove all rate limiting from /healthz")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        try:
            if choice == "1":
                await setup_healthz_rate_limiting()
            elif choice == "2":
                await setup_aggressive_healthz_rate_limiting()
            elif choice == "3":
                await monitor_healthz_rate_limiting()
            elif choice == "4":
                await remove_healthz_rate_limiting()
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except Exception as e:
            print(f"❌ Operation failed: {e}")
            print("Please check your Kong configuration and try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
