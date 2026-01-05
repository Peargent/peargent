"""
Advanced Email Tool Example

Demonstrates advanced features:
- Multiple providers (SMTP, Resend)
- Template variable substitution (simple + Jinja when available)
- Error handling and validation
- Integration with agents for automated notifications
"""

import os
from peargent import create_agent
from peargent.tools import email_tool
from peargent.models import gemini


def example_smtp_configuration():
    """Show different SMTP provider configurations."""
    print("=" * 60)
    print("SMTP Provider Configurations")
    print("=" * 60)
    
    # Gmail example
    print("\n1. Gmail SMTP:")
    print("-" * 60)
    print("Configuration in .env:")
    print("SMTP_HOST=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SMTP_USERNAME=your-email@gmail.com")
    print("SMTP_PASSWORD=your-app-password  # Use App Password, not regular password")
    print()
    result = email_tool.run({
        "to_email": "recipient@example.com",
        "subject": "Test from Gmail SMTP",
        "body": "This email was sent via Gmail SMTP.",
        "from_email": "your-email@gmail.com"
    })
    print(f"Result: {result['success']} - {result.get('error', 'Success')}")
    
    # Outlook/Office365 example
    print("\n2. Outlook/Office365 SMTP:")
    print("-" * 60)
    print("Configuration example (set in .env):")
    print("SMTP_HOST=smtp-mail.outlook.com")
    print("SMTP_PORT=587")
    print("SMTP_USERNAME=your-email@outlook.com")
    print("SMTP_PASSWORD=your-password")
    
    # Custom SMTP server example
    print("\n3. Custom SMTP Server:")
    print("-" * 60)
    print("Configuration example (set in .env):")
    print("SMTP_HOST=mail.yourdomain.com")
    print("SMTP_PORT=465  # or 587 for TLS")
    print("SMTP_USERNAME=noreply@yourdomain.com")
    print("SMTP_PASSWORD=your-password")


def example_template_systems():
    """Demonstrate template variable substitution (simple + Jinja when available)."""
    print("\n" + "=" * 60)
    print("Template Variable Substitution")
    print("=" * 60)
    
    # Example 1: User welcome email
    print("\n1. User Welcome Email Template:")
    print("-" * 60)
    
    user_data = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "username": "alice_j",
        "email": "alice@example.com",
        "company": "Tech Corp",
        "activation_link": "https://app.example.com/activate/abc123",
        "support_email": "support@example.com"
    }
    
    result = email_tool.run({
        "to_email": user_data["email"],
        "subject": "Welcome to {{ company }}, {{ first_name }}!",
        "body": """
<html>
<body>
    <h2>Welcome {{ first_name }} {{ last_name }}!</h2>
    
    <p>Your account has been successfully created.</p>
    
    <h3>Account Details:</h3>
    <ul>
        <li><strong>Username:</strong> {{ username }}</li>
        <li><strong>Email:</strong> {{ email }}</li>
        <li><strong>Company:</strong> {{ company }}</li>
    </ul>
    
    <p>
        <a href="{{ activation_link }}" style="background-color: #4CAF50; color: white; 
           padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Activate Your Account
        </a>
    </p>
    
    <p>If you have any questions, contact us at {{ support_email }}</p>
    
    <p>Best regards,<br>The {{ company }} Team</p>
</body>
</html>
        """,
        "template_vars": user_data,
        "from_email": "noreply@techcorp.com"
    })
    
    if result["success"]:
        print(f" Welcome email sent successfully")
    else:
        print(f" Error: {result['error']}")
    
    # Example 2: Alert email with metrics
    print("\n2. System Alert Email Template:")
    print("-" * 60)
    
    alert_data = {
        "alert_type": "High CPU Usage",
        "server_name": "web-server-01",
        "cpu_percent": "95",
        "memory_percent": "78",
        "timestamp": "2026-01-03 14:30:00",
        "threshold": "80",
        "dashboard_url": "https://monitoring.example.com/servers/web-01"
    }
    
    result = email_tool.run({
        "to_email": "devops@example.com",
        "subject": " Alert: {{ alert_type }} on {{ server_name }}",
        "body": """
Alert Type: {{ alert_type }}
Server: {{ server_name }}
Time: {{ timestamp }}

Current Metrics:
- CPU Usage: {{ cpu_percent }}% (Threshold: {{ threshold }}%)
- Memory Usage: {{ memory_percent }}%

Action Required: Please investigate immediately.

View dashboard: {{ dashboard_url }}

This is an automated alert from the monitoring system.
        """,
        "template_vars": alert_data,
        "from_email": "alerts@example.com"
    })
    
    if result["success"]:
        print(f" Alert email sent successfully")
    else:
        print(f" Error: {result['error']}")
    
    # Example 3: Invoice/Receipt template
    print("\n3. Invoice Email Template:")
    print("-" * 60)
    
    invoice_data = {
        "customer_name": "John Doe",
        "invoice_number": "INV-2026-001",
        "invoice_date": "January 3, 2026",
        "amount": "$149.99",
        "payment_method": "Credit Card (****1234)",
        "items": "Premium Plan - Annual Subscription",
        "next_billing_date": "January 3, 2027",
        "invoice_url": "https://billing.example.com/invoices/001"
    }
    
    result = email_tool.run({
        "to_email": "john@example.com",
        "subject": "Invoice {{ invoice_number }} - Payment Received",
        "body": """
<html>
<body>
    <h2>Thank you for your payment!</h2>
    
    <p>Dear {{ customer_name }},</p>
    
    <p>We have received your payment of <strong>{{ amount }}</strong>.</p>
    
    <h3>Invoice Details:</h3>
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Invoice Number:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ invoice_number }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Date:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ invoice_date }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Amount:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ amount }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Payment Method:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ payment_method }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Items:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ items }}</td>
        </tr>
    </table>
    
    <p>Next billing date: {{ next_billing_date }}</p>
    
    <p><a href="{{ invoice_url }}">Download Invoice PDF</a></p>
    
    <p>Thank you for your business!</p>
</body>
</html>
        """,
        "template_vars": invoice_data,
        "from_email": "billing@example.com"
    })
    
    if result["success"]:
        print(f" Invoice email sent successfully")
    else:
        print(f" Error: {result['error']}")


def example_resend_provider():
    """Demonstrate Resend API features."""
    print("\n" + "=" * 60)
    print("Resend Provider Examples")
    print("=" * 60)
    
    print("\n1. Basic Resend Email:")
    print("-" * 60)
    
    result = email_tool.run({
        "to_email": "user@example.com",
        "subject": "Hello from Resend API",
        "body": "This is a test email sent via Resend.",
        "from_email": "test@resend.dev",  # Use test@resend.dev for local testing; requires verified custom domain in production
        "provider": "resend"
    })
    
    if result["success"]:
        print(f" Email sent successfully!")
        print(f"Message ID: {result.get('message_id', 'N/A')}")
    else:
        print(f" Error: {result['error']}")
    
    print("\n2. Resend with HTML Template:")
    print("-" * 60)
    
    result = email_tool.run({
        "to_email": "customer@example.com",
        "subject": "Your order has shipped!",
        "body": """
<html>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4CAF50;"> Your Order Has Shipped!</h2>
        <p>Great news! Your order is on its way.</p>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
            <p><strong>Order Number:</strong> #12345</p>
            <p><strong>Tracking Number:</strong> 1Z999AA10123456784</p>
            <p><strong>Estimated Delivery:</strong> January 5, 2026</p>
        </div>
        <p style="margin-top: 20px;">
            <a href="https://tracking.example.com/12345" 
               style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Track Your Package
            </a>
        </p>
    </div>
</body>
</html>
        """,
        "from_email": "test@resend.dev",  # Use test@resend.dev for local testing; requires verified custom domain in production
        "provider": "resend"
    })
    
    if result["success"]:
        print(f" Shipping notification sent successfully")
    else:
        print(f" Error: {result['error']}")


def example_agent_automation():
    """Demonstrate automated notifications with agents."""
    print("\n" + "=" * 60)
    print("Agent-Driven Automated Notifications")
    print("=" * 60)
    
    try:
        # Create an agent that can send intelligent notifications
        agent = create_agent(
            name="SmartNotifier",
            description="An intelligent agent that sends contextual email notifications",
            persona="""
You are a smart notification assistant. When asked to send notifications:
1. Craft professional, clear subject lines
2. Write concise, informative email bodies
3. Use appropriate formatting (HTML when beneficial)
4. Include relevant details and call-to-action
5. Use template variables when provided
Always use the send_notification tool to send emails.
            """,
            model=gemini("gemini-2.5-flash-lite"),
            tools=[email_tool]
        )
        
        print("\nScenario 1: Password Reset Request")
        print("-" * 60)
        response = agent.run(
            "A user named Sarah Martinez (sarah@example.com) requested a password reset. "
            "Send her an email with a reset link: https://app.example.com/reset/xyz789. "
            "The link expires in 1 hour. Use security@example.com as sender."
        )
        print(f"Agent: {response}")
        
        print("\n\nScenario 2: Daily Summary Report")
        print("-" * 60)
        response = agent.run(
            "Send a daily summary report to admin@example.com. "
            "Today's stats: 150 new users, 1,250 active sessions, $5,420 revenue. "
            "Use reports@example.com as sender."
        )
        print(f"Agent: {response}")
        
        print("\n\nScenario 3: Event Reminder")
        print("-" * 60)
        response = agent.run(
            "Send a reminder to team@example.com about tomorrow's product launch meeting "
            "at 10 AM EST. Include Zoom link: https://zoom.us/j/123456789. "
            "Use calendar@example.com as sender."
        )
        print(f"Agent: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all advanced examples."""
    
    # Check if environment is configured
    if not os.getenv("SMTP_HOST") and not os.getenv("RESEND_API_KEY"):
        print("   Warning: No SMTP or Resend credentials found in .env file")
        print("Set up credentials to run these examples:\n")
        print("For SMTP (e.g., Gmail):")
        print("  SMTP_HOST=smtp.gmail.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USERNAME=your-email@gmail.com")
        print("  SMTP_PASSWORD=your-app-password\n")
        print("For Resend:")
        print("  RESEND_API_KEY=your-resend-api-key\n")
        print("-" * 60)
    
    # Run examples
    example_smtp_configuration()
    example_template_systems()
    example_resend_provider()
    example_agent_automation()
    
    print("\n" + "=" * 60)
    print("Advanced Examples Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

