"""
Advanced Discord Tool Example

Demonstrates advanced features:
- Complex embed structures with author, footer, timestamp
- Template variables in content and embeds
- Multiple fields with inline formatting
- Error handling
- Integration with AI agents for automated notifications
"""

from peargent import create_agent
from peargent.tools import discord_tool
from peargent.models import gemini
from datetime import datetime, timezone


def main():
    print("=" * 60)
    print("Discord Tool - Advanced Example")
    print("=" * 60)
    
    # Example 1: Complex embed with all features
    print("\n1. Complex embed with all features:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "New GitHub activity:",
        "embed": {
            "title": "GitHub Pull Request",
            "description": "A new pull request has been opened",
            "url": "https://github.com/user/repo/pull/123",
            "color": 0x238636,  # GitHub green
            "author": {
                "name": "GitHub Bot",
                "url": "https://github.com",
                "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            },
            "fields": [
                {"name": "Repository", "value": "user/awesome-project", "inline": True},
                {"name": "Branch", "value": "feature/new-tool", "inline": True},
                {"name": "Author", "value": "developer123", "inline": True},
                {"name": "Status", "value": "✅ All checks passed", "inline": False},
                {"name": "Changes", "value": "+150 -20", "inline": True},
                {"name": "Files Changed", "value": "5", "inline": True}
            ],
            "footer": {
                "text": "GitHub Notifications",
                "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    
    if result["success"]:
        print("✓ Complex embed sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 2: Template variables in content and embed
    print("\n\n2. Template variables in content and embed:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "Deployment to {{ environment }} completed!",
        "template_vars": {
            "environment": "Production",
            "status": "Success",
            "version": "v2.3.0",
            "duration": "2m 45s",
            "deployer": "CI/CD Pipeline"
        },
        "embed": {
            "title": "Deployment Status: {{ status }}",
            "description": "Version {{ version }} deployed successfully",
            "color": 0x00FF00,  # Green for success
            "fields": [
                {"name": "Version", "value": "{{ version }}", "inline": True},
                {"name": "Duration", "value": "{{ duration }}", "inline": True},
                {"name": "Deployed By", "value": "{{ deployer }}", "inline": True}
            ]
        }
    })
    
    if result["success"]:
        print("✓ Templated message sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 3: Multi-line content with code blocks
    print("\n\n3. Message with code blocks:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": """**Error Report**

```python
def process_data(data):
    # Error occurred here
    result = data.transform()
    return result
```

**Error:** `AttributeError: 'NoneType' object has no attribute 'transform'`
**Line:** 3
**Time:** 2026-01-05 10:30:00 UTC""",
        "embed": {
            "title": "Stack Trace",
            "description": "Full error details",
            "color": 0xFF0000  # Red for error
        }
    })
    
    if result["success"]:
        print("✓ Code block message sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 4: Alert notification
    print("\n\n4. Alert notification:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "**URGENT: System Alert**",
        "embed": {
            "title": "⚠️ High CPU Usage Detected",
            "description": "Server CPU usage has exceeded 90% threshold",
            "color": 0xFFCC00,  # Yellow/amber for warning
            "fields": [
                {"name": "Server", "value": "prod-server-01", "inline": True},
                {"name": "Current Usage", "value": "94%", "inline": True},
                {"name": "Threshold", "value": "90%", "inline": True},
                {"name": "Recommendation", "value": "Scale up resources or investigate processes", "inline": False}
            ],
            "footer": {"text": "Monitoring System"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    
    if result["success"]:
        print("✓ Alert notification sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 5: Success notification with custom formatting
    print("\n\n5. Success notification:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "Build completed!",
        "embed": {
            "title": "✅ Build Successful",
            "description": "All tests passed and deployment completed",
            "color": 0x00FF00,  # Green
            "fields": [
                {"name": "Build #", "value": "1234", "inline": True},
                {"name": "Branch", "value": "main", "inline": True},
                {"name": "Commit", "value": "`abc123f`", "inline": True},
                {"name": "Tests", "value": "✅ 150 passed\n⏭️ 0 skipped\n❌ 0 failed", "inline": False},
                {"name": "Coverage", "value": "95%", "inline": True},
                {"name": "Build Time", "value": "3m 22s", "inline": True}
            ],
            "thumbnail": {"url": "https://example.com/success-icon.png"}
        }
    })
    
    if result["success"]:
        print("✓ Success notification sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 6: Using AI agent to create smart notifications
    print("\n\n6. AI agent creating smart notifications:")
    print("-" * 60)
    
    agent = create_agent(
        name="DevOpsNotifier",
        description="A DevOps notification assistant",
        persona="""You are a DevOps notification assistant. 
When asked to send notifications, create well-formatted Discord messages with:
- Appropriate colors based on severity (green=success, yellow=warning, red=error)
- Clear, structured information in embed fields
- Professional formatting
Use the discord_webhook tool.""",
        model=gemini("gemini-2.5-flash-lite"),
        tools=[discord_tool]
    )
    
    # Agent creates a formatted notification
    response = agent.run(
        "Send a Discord notification that the database backup completed successfully. "
        "Include details: database name 'prod-db', size '2.5 GB', duration '5 minutes', "
        "next backup scheduled for '2026-01-06 02:00 UTC'"
    )
    
    print(f"Agent response: {response}")
    
    # Example 7: Conditional messages using Jinja2
    print("\n\n7. Conditional messages with Jinja2:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "{% if severity == 'critical' %}🚨 CRITICAL: {% endif %}System {{ status }}",
        "template_vars": {
            "severity": "critical",
            "status": "down"
        },
        "embed": {
            "title": "System Status Alert",
            "color": 0xFF0000
        }
    })
    
    if result["success"]:
        print("✓ Conditional message sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 8: Loop through items in Jinja2 template
    print("\n\n8. Loop through items in template:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "Daily Report Summary",
        "embed": {
            "title": "Daily Report",
            "description": """**Completed Tasks:**
{% for task in tasks %}- {{ task.name }}: {{ task.status }}
{% endfor %}""",
            "color": 0x5865F2
        },
        "template_vars": {
            "tasks": [
                {"name": "Data backup", "status": "✅ Success"},
                {"name": "Log cleanup", "status": "✅ Success"},
                {"name": "Health check", "status": "✅ Success"}
            ]
        }
    })
    
    if result["success"]:
        print("✓ Looped template sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 9: Error handling demonstration
    print("\n\n9. Error handling:")
    print("-" * 60)
    
    # Try with invalid webhook URL
    result = discord_tool.run({
        "content": "Test message",
        "webhook_url": "invalid-url"
    })
    
    print(f"Expected error result: {result['error']}")
    
    # Try with empty message (no content or embeds)
    result = discord_tool.run({})
    
    print(f"Expected error for empty message: {result['error']}")
    
    print("\n" + "=" * 60)
    print("Advanced examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
