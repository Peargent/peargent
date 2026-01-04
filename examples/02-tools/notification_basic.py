"""
Basic Notification Tool Example

Demonstrates how to send email notifications using the NotificationTool.
Shows both SMTP and Resend providers.
"""

from peargent import create_agent
from peargent.tools import notification_tool
from peargent.models import gemini


def main():
    print("=" * 60)
    print("Notification Tool - Basic Example")
    print("=" * 60)
    
    # Example 1: Send basic email via SMTP
    print("\n1. Sending basic email via SMTP:")
    print("-" * 60)
    
    # Note: SMTP credentials must be set in .env file:
    # SMTP_HOST=smtp.gmail.com
    # SMTP_PORT=587
    # SMTP_USERNAME=your-email@gmail.com
    # SMTP_PASSWORD=your-app-password
    
    result = notification_tool.run({
        "to_email": "recipient@example.com",
        "subject": "Test Email from Peargent",
        "body": "This is a test email sent using the Notification Tool.",
        "from_email": "sender@example.com"
    })
    
    if result["success"]:
        print(f" Email sent successfully!")
        print(f"Provider: {result['provider']}")
        if result['message_id']:
            print(f"Message ID: {result['message_id']}")
    else:
        print(f" Error: {result['error']}")
    
    # Example 2: Send email with Jinja2 template variables
    print("\n\n2. Sending email with Jinja2 template variables:")
    print("-" * 60)
    
    result = notification_tool.run({
        "to_email": "user@example.com",
        "subject": "Welcome {{ user_name }}!",
        "body": """
Hello {{ user_name }},

Your account has been successfully created!

Username: {{ username }}
Email: {{ email }}

Thanks for joining us!

Best regards,
The Team
        """,
        "template_vars": {
            "user_name": "Alice Johnson",
            "username": "alice_j",
            "email": "alice@example.com"
        },
        "from_email": "noreply@example.com"
    })
    
    if result["success"]:
        print(f" Email sent successfully!")
    else:
        print(f" Error: {result['error']}")
    
    # Example 3: Send email without templating (as-is)
    print("\n\n3. Sending email without templating:")
    print("-" * 60)
    
    # When template_vars is not provided, the email is sent as-is
    result = notification_tool.run({
        "to_email": "dev@example.com",
        "subject": "System Report for {{ date }}",  # Sent literally
        "body": "Current status: {{ status }}",  # Sent literally
        "from_email": "system@example.com"
        # No template_vars - content sent as-is with literal {{ variable }} syntax
    })
    
    if result["success"]:
        print(f" Email sent successfully (no templating applied)!")
    else:
        print(f" Error: {result['error']}")
    
    # Example 4: Send HTML email
    print("\n\n4. Sending HTML email:")
    print("-" * 60)
    
    html_body = """
    <html>
        <body>
            <h2>System Alert</h2>
            <p>Your scheduled task has completed successfully.</p>
            <ul>
                <li><strong>Task:</strong> Data Backup</li>
                <li><strong>Status:</strong>  Completed</li>
                <li><strong>Duration:</strong> 5 minutes</li>
            </ul>
            <p>View details in your <a href="https://dashboard.example.com">dashboard</a>.</p>
        </body>
    </html>
    """
    
    result = notification_tool.run({
        "to_email": "admin@example.com",
        "subject": "Task Completed Successfully",
        "body": html_body,
        "from_email": "alerts@example.com"
    })
    
    if result["success"]:
        print(f" Email sent successfully!")
    else:
        print(f" Error: {result['error']}")
    
    # Example 5: Using Resend provider
    print("\n\n5. Sending email via Resend:")
    print("-" * 60)
    
    # Note: RESEND_API_KEY must be set in .env file
    
    result = notification_tool.run({
        "to_email": "recipient@example.com",
        "subject": "Hello from Resend",
        "body": "This email was sent using the Resend API!",
        "from_email": "test@resend.dev", # Use test@resend.dev for local testing; requires verified custom domain in production
        "provider": "resend"
    })
    
    if result["success"]:
        print(f" Email sent successfully!")
        print(f"Provider: {result['provider']}")
        if result['message_id']:
            print(f"Message ID: {result['message_id']}")
    else:
        print(f" Error: {result['error']}")
    
    # Example 6: Using notification tool with an agent
    print("\n\n6. Using notification tool with an agent:")
    print("-" * 60)
    
    try:
        agent = create_agent(
            name="NotificationAgent",
            description="An agent that can send email notifications",
            persona=(
                "You are a helpful assistant that can send email notifications. "
                "When asked to send an email, use the send_notification tool. "
                "Always use appropriate subject lines and clear, professional message bodies."
            ),
            model=gemini("gemini-2.5-flash-lite"),
            tools=[notification_tool]
        )
        
        response = agent.run(
            "Send a reminder email to john@example.com about the team meeting tomorrow at 2 PM. "
            "Use sender@company.com as the from address."
        )
        print(f"\nAgent Response:\n{response}")
    except Exception as e:
        print(f"\n Error: {e}")
        print(f"Error type: {type(e).__name__}")
    
    print("\n" + "=" * 60)
    print("Note: Make sure to configure SMTP or Resend credentials in .env file")
    print("=" * 60)


if __name__ == "__main__":
    main()
