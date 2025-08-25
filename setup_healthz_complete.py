#!/usr/bin/env python3
"""
Complete setup script for /healthz endpoint with rate limiting.

This script will:
1. Create a service for your health check endpoint
2. Create a route for /healthz
3. Add appropriate rate limiting
4. Test the setup

Based on your request log:
- Endpoint: /healthz
- Method: GET
- Client IP: 127.0.0.1
- User Agent: PostmanRuntime/7.45.0
"""

import asyncio
import sys
import os
import json

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kong_mcp_server.tools.kong_rate_limiting import (
    create_rate_limiting_plugin,
    get_rate_limiting_plugins,
)
from kong_mcp_server.tools.kong_routes import (
    create_route,
    get_routes,
)
from kong_mcp_server.tools.kong_services import (
    create_service,
    get_services,
)


async def setup_healthz_complete():
    """Complete setup for /healthz endpoint with rate limiting."""
    
    print("🚀 Setting up complete /healthz endpoint with rate limiting...")
    
    try:
        # Step 1: Create or find the health service
        print("\n📋 Step 1: Setting up health check service...")
        
        services = await get_services()
        health_service = None
        
        # Look for existing health service
        for service in services:
            if service.get("name") == "health-service":
                health_service = service
                break
        
        if health_service:
            print(f"✅ Found existing health service: {health_service['id']}")
            print(f"   URL: {health_service.get('url', 'N/A')}")
        else:
            print("   Creating new health service...")
            
            # You can modify this URL to point to your actual backend
            # Common options:
            # - http://localhost:8080 (if your app runs on port 8080)
            # - http://host.docker.internal:8080 (if Kong is in Docker)
            # - http://your-app-service:8080 (if using Kubernetes)
            backend_url = input("   Enter your backend URL (default: http://localhost:8080): ").strip()
            if not backend_url:
                backend_url = "http://localhost:8080"
            
            health_service = await create_service(
                name="health-service",
                url=backend_url,
                tags=["health", "monitoring", "system"]
            )
            print(f"✅ Created health service: {health_service['id']}")
            print(f"   URL: {health_service['url']}")
        
        # Step 2: Create or find the /healthz route
        print("\n📋 Step 2: Setting up /healthz route...")
        
        routes = await get_routes()
        healthz_route = None
        
        # Look for existing /healthz route
        for route in routes:
            paths = route.get("paths", [])
            if any("/healthz" in path for path in paths):
                healthz_route = route
                break
        
        if healthz_route:
            print(f"✅ Found existing /healthz route: {healthz_route['id']}")
            print(f"   Paths: {healthz_route.get('paths', [])}")
            print(f"   Methods: {healthz_route.get('methods', [])}")
        else:
            print("   Creating /healthz route...")
            
            healthz_route = await create_route(
                name="healthz-route",
                paths=["/healthz"],
                methods=["GET", "HEAD"],  # HEAD is common for health checks
                service_id=health_service["id"],
                strip_path=False,  # Keep the /healthz path when forwarding
                tags=["health", "monitoring", "system"]
            )
            print(f"✅ Created /healthz route: {healthz_route['id']}")
            print(f"   Paths: {healthz_route['paths']}")
            print(f"   Methods: {healthz_route['methods']}")
        
        # Step 3: Check for existing rate limiting
        print("\n📋 Step 3: Setting up rate limiting...")
        
        existing_plugins = await get_rate_limiting_plugins()
        existing_rate_limit = None
        
        for plugin in existing_plugins:
            if plugin.get("route", {}).get("id") == healthz_route["id"]:
                existing_rate_limit = plugin
                break
        
        if existing_rate_limit:
            print(f"⚠️  Rate limiting already exists: {existing_rate_limit['id']}")
            print(f"   Current config: {json.dumps(existing_rate_limit.get('config', {}), indent=4)}")
            
            update_choice = input("\n   Do you want to keep the existing rate limiting? (Y/n): ").strip().lower()
            if update_choice == 'n':
                print("   You can manually update or delete the existing plugin if needed.")
            
            rate_limit_plugin = existing_rate_limit
        else:
            print("   Creating rate limiting for /healthz...")
            
            # Ask user for rate limiting preferences
            print("\n   Choose rate limiting level:")
            print("   1. Generous (300/min, 18000/hour) - Good for frequent health checks")
            print("   2. Standard (120/min, 7200/hour) - Balanced protection")
            print("   3. Strict (60/min, 3600/hour) - Strong protection")
            print("   4. Custom - Enter your own limits")
            
            choice = input("   Enter choice (1-4, default: 2): ").strip()
            
            if choice == "1":
                minute_limit, hour_limit = 300, 18000
                level = "generous"
            elif choice == "3":
                minute_limit, hour_limit = 60, 3600
                level = "strict"
            elif choice == "4":
                try:
                    minute_limit = int(input("   Requests per minute: "))
                    hour_limit = int(input("   Requests per hour: "))
                    level = "custom"
                except ValueError:
                    print("   Invalid input, using standard limits")
                    minute_limit, hour_limit = 120, 7200
                    level = "standard"
            else:  # Default to standard
                minute_limit, hour_limit = 120, 7200
                level = "standard"
            
            rate_limit_plugin = await create_rate_limiting_plugin(
                route_id=healthz_route["id"],
                minute=minute_limit,
                hour=hour_limit,
                day=hour_limit * 24,  # 24 hours worth
                limit_by="ip",
                policy="local",
                fault_tolerant=True,  # Don't break health checks if rate limiting fails
                hide_client_headers=False,  # Show rate limiting headers
                tags=["healthz", "rate-limiting", "monitoring", level]
            )
            
            print(f"✅ Created rate limiting plugin: {rate_limit_plugin['id']}")
            print(f"   Level: {level}")
            print(f"   Limits: {minute_limit}/min, {hour_limit}/hour, {hour_limit * 24}/day")
        
        # Step 4: Summary and testing instructions
        print(f"\n🎉 Setup Complete!")
        print(f"=" * 50)
        print(f"Service ID: {health_service['id']}")
        print(f"Route ID: {healthz_route['id']}")
        print(f"Rate Limit Plugin ID: {rate_limit_plugin['id']}")
        
        print(f"\n📊 Configuration Summary:")
        print(f"• Backend URL: {health_service.get('url')}")
        print(f"• Route Path: /healthz")
        print(f"• Methods: {healthz_route.get('methods', [])}")
        print(f"• Rate Limits: {rate_limit_plugin.get('config', {})}")
        
        print(f"\n🧪 Test Your Setup:")
        print(f"1. Test the endpoint:")
        print(f"   curl -i http://localhost/healthz")
        print(f"")
        print(f"2. Check rate limiting headers:")
        print(f"   Look for X-RateLimit-* headers in the response")
        print(f"")
        print(f"3. Test rate limiting:")
        print(f"   for i in {{1..10}}; do curl -s -o /dev/null -w '%{{http_code}}\\n' http://localhost/healthz; done")
        print(f"")
        print(f"4. Monitor Kong logs:")
        print(f"   Check your Kong logs for rate limiting events")
        
        print(f"\n📋 Kong Admin API Commands:")
        print(f"• Check service: curl http://localhost:8001/services/{health_service['id']}")
        print(f"• Check route: curl http://localhost:8001/routes/{healthz_route['id']}")
        print(f"• Check plugin: curl http://localhost:8001/plugins/{rate_limit_plugin['id']}")
        
        return {
            "service": health_service,
            "route": healthz_route,
            "rate_limit_plugin": rate_limit_plugin
        }
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        print(f"   Make sure Kong is running and accessible.")
        print(f"   Check Kong Admin API: curl http://localhost:8001/status")
        raise


async def main():
    """Main function."""
    print("=" * 60)
    print("Complete /healthz Endpoint Setup with Rate Limiting")
    print("=" * 60)
    print("This script will set up everything needed for your /healthz endpoint:")
    print("• Health check service")
    print("• /healthz route")
    print("• Rate limiting protection")
    print("=" * 60)
    
    try:
        result = await setup_healthz_complete()
        
        print(f"\n✅ All done! Your /healthz endpoint is now set up with rate limiting.")
        print(f"   You can now make requests to http://localhost/healthz")
        print(f"   Rate limiting will protect against abuse while allowing normal health checks.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
