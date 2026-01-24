"""
Basic Discord Tool Example

Demonstrates how to send messages to Discord channels using the DiscordTool.
Shows simple messages, templating, and embeds.
"""

from peargent import create_agent
from peargent.tools import discord_tool
from peargent.models import gemini


def main():
    print("=" * 60)
    print("Discord Tool - Basic Example")
    print("=" * 60)
    
    # Example 1: Send simple text message
    print("\n1. Sending simple text message:")
    print("-" * 60)
    
    # Note: DISCORD_WEBHOOK_URL must be set in .env file:
    # DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
    
    result = discord_tool.run({
        "content": "Hello from Peargent!"
    })
    
    if result["success"]:
        print("✓ Message sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 2: Send message with template variables
    print("\n\n2. Sending message with template variables:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "Hello {{ name }}! Your task **{{ task }}** is now complete.",
        "template_vars": {
            "name": "Team",
            "task": "Data Processing"
        }
    })
    
    if result["success"]:
        print("✓ Templated message sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 3: Send message with embed (as dict)
    print("\n\n3. Sending message with embed:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "System status update:",
        "embed": {
            "title": "System Alert",
            "description": "All systems are operational.",
            "color": 0x00FF00  # Green color
        }
    })
    
    if result["success"]:
        print("✓ Embed message sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 4: Send rich embed with fields
    print("\n\n4. Sending rich embed with fields:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "Server metrics:",
        "embed": {
            "title": "Server Status Report",
            "description": "Current system metrics",
            "color": 0x5865F2,  # Discord blurple
            "fields": [
                {"name": "CPU Usage", "value": "45%", "inline": True},
                {"name": "Memory", "value": "60%", "inline": True},
                {"name": "Disk Space", "value": "75%", "inline": True},
                {"name": "Uptime", "value": "99.9%", "inline": True}
            ],
            "footer": {"text": "Last updated: 2026-01-05"}
        }
    })
    
    if result["success"]:
        print("✓ Rich embed sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 5: Send message with custom username and avatar
    print("\n\n5. Sending message with custom username and avatar:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "Custom bot reporting for duty!",
        "username": "Peargent Bot",
        "avatar_url": "https://example.com/avatar.png"
    })
    
    if result["success"]:
        print("✓ Custom message sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 6: Send embed with image and thumbnail
    print("\n\n6. Sending embed with image:")
    print("-" * 60)
    
    result = discord_tool.run({
        "content": "Image showcase:",
        "embed": {
            "title": "Image Showcase",
            "description": "Check out this image!",
            "color": 0xFF5733,  # Orange
            "image": {"url": "https://example.com/image.png"},
            "thumbnail": {"url": "https://example.com/thumb.png"}
        }
    })
    
    if result["success"]:
        print("✓ Embed with image sent successfully!")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Example 7: Using Discord tool with an AI agent
    print("\n\n7. Using Discord tool with an AI agent:")
    print("-" * 60)
    
    # Create agent with Discord tool
    agent = create_agent(
        name="DiscordAssistant",
        description="A helpful assistant that can send Discord messages",
        persona="""You are a helpful assistant that can send messages to Discord.
When asked to notify someone on Discord, use the discord_webhook tool.""",
        model=gemini("gemini-2.5-flash-lite"),
        tools=[discord_tool]
    )
    
    # Agent will use the tool to send a message
    response = agent.run(
        "Send a Discord message saying 'Hello from AI agent!' with an embed titled 'AI Message'"
    )
    
    print(f"Agent response: {response}")


if __name__ == "__main__":
    main()
