#!/usr/bin/env python3
"""
Quick script to add rate limiting to the /healthz endpoint.

Based on your request log:
- Endpoint: /healthz
- Method: GET
- Client IP: 127.0.0.1
- User Agent: PostmanRuntime/7.45.0

This script will add appropriate rate limiting to prevent abuse while allowing normal health checks.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kong_mcp_server.tools.kong_rate_limiting import (
    create_rate_limiting_plugin,
    get_rate_limiting_plugins,
)
from kong_mcp_server.tools.kong_routes import get_routes


async def add_healthz_rate_limiting():
    """Add rate limiting to the /healthz endpoint."""
    
    print("🔍 Looking for /healthz route...")
    
    try:
        # Find the /healthz route
        routes = await get_routes()
        healthz_route = None
        
        for route in routes:
            paths = route.get("paths", [])
            if any("/healthz" in path for path in paths):
                healthz_route = route
                break
        
        if not healthz_route:
            print("❌ No /healthz route found in Kong.")
            print("   Please ensure your /healthz endpoint is configured as a Kong route first.")
            print("   You can check your routes with: curl http://localhost:8001/routes")
            return False
        
        print(f"✅ Found /healthz route: {healthz_route['id']}")
        print(f"   Paths: {healthz_route.get('paths', [])}")
        print(f"   Methods: {healthz_route.get('methods', [])}")
        
        # Check if rate limiting already exists
        print("\n🔍 Checking for existing rate limiting...")
        existing_plugins = await get_rate_limiting_plugins()
        
        for plugin in existing_plugins:
            if plugin.get("route", {}).get("id") == healthz_route["id"]:
                print(f"⚠️  Rate limiting already exists for /healthz: {plugin['id']}")
                print(f"   Current limits: {plugin.get('config', {})}")
                return plugin
        
        # Add rate limiting
        print("\n🚀 Adding rate limiting to /healthz...")
        
        # Configure reasonable limits for health checks
        # Health checks are usually automated and frequent, but we want to prevent abuse
        rate_limit_plugin = await create_rate_limiting_plugin(
            route_id=healthz_route["id"],
            minute=120,  # 120 requests per minute (2 per second) - generous for health checks
            hour=7200,   # 7200 requests per hour
            day=172800,  # 172800 requests per day
            limit_by="ip",  # Limit by IP address
            policy="local",  # Use local policy
            fault_tolerant=True,  # Don't break health checks if rate limiting fails
            hide_client_headers=False,  # Show rate limiting headers
            tags=["healthz", "rate-limiting", "monitoring"]
        )
        
        print("✅ Successfully added rate limiting to /healthz!")
        print(f"   Plugin ID: {rate_limit_plugin['id']}")
        print(f"   Limits:")
        print(f"     • 120 requests per minute (2 per second)")
        print(f"     • 7,200 requests per hour")
        print(f"     • 172,800 requests per day")
        print(f"   Limited by: IP address")
        print(f"   Policy: Local")
        print(f"   Fault tolerant: Yes")
        
        print(f"\n📊 Rate limiting headers will be included in responses:")
        print(f"   • X-RateLimit-Limit-Minute: 120")
        print(f"   • X-RateLimit-Remaining-Minute: (remaining requests)")
        print(f"   • X-RateLimit-Reset: (reset time)")
        
        print(f"\n🧪 Test the rate limiting:")
        print(f"   curl -i http://localhost/healthz")
        print(f"   (Look for X-RateLimit-* headers in the response)")
        
        return rate_limit_plugin
        
    except Exception as e:
        print(f"❌ Error adding rate limiting: {e}")
        print(f"   Make sure Kong is running and accessible.")
        print(f"   Check Kong Admin API: curl http://localhost:8001/status")
        return False


async def main():
    """Main function."""
    print("=" * 60)
    print("Adding Rate Limiting to /healthz Endpoint")
    print("=" * 60)
    
    result = await add_healthz_rate_limiting()
    
    if result:
        print(f"\n🎉 Success! Rate limiting has been added to your /healthz endpoint.")
        print(f"   The endpoint will now be protected against abuse while allowing")
        print(f"   normal health check traffic.")
    else:
        print(f"\n❌ Failed to add rate limiting. Please check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
