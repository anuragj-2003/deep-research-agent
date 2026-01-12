from states.state import AgentState
import smtplib, ssl
import os
from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

def ask_email(state: AgentState):
    """
    Interupts to ask the user for an email address, ONLY if not already present.
    """
    if state.email:
        return {} # Email already set, continue to send_email

    # Interrupt to ask for email
    user_email = interrupt("Please provide your email address to receive the report:")
    return {"email": user_email}

def send_email_node(state: AgentState):
    """
    Sends the generated report to the user's email.
    Uses smtplib for sending emails.
    """
    user_email = state.email
    topic = state.topic
    report_format = state.report_format
    
    if not user_email:
        return {"messages": [HumanMessage(content="Error: No email address provided.")]}
    
    # Construct filename
    filename = f"{topic.replace(' ', '_')}_report.{report_format}"
    filepath = os.path.join("reports", filename)
    
    if not os.path.exists(filepath):
        return {"messages": [HumanMessage(content=f"Error: Report file {filepath} not found.")]}

    # Configuration
    # Configuration
    from utils.config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
    
    sender_email = SMTP_USER
    password = SMTP_PASSWORD
    
    if not sender_email or not password:
         return {"messages": [HumanMessage(content="Error: SMTP credentials not set in environment variables.")]}

    # Create a secure SSL context
    context = ssl.create_default_context()

    subject = f"Research Report: {topic}"
    subject = f"Research Report: {topic}"
    # Body is now handled in MIMEMultipart construction
    
    # Simple email construction (Note: Ideally use email.message.EmailMessage for attachments)
    # For now, sending just text body as user requested "send that to email" implying the report or a notification.
    # To attach a file, we need MIMEText and MIMEMultipart.
    
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email import encoders

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject
    
    msg['Subject'] = subject
    
    # Simple HTML body without summary
    html_body = f"""
    <html>
      <body>
        <h2>Research Report: {topic}</h2>
        <p>Please find your requested research report attached.</p>
        <p>Best regards,<br>Autonomous Research Agent</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    with open(filepath, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    msg.attach(part)
    text = msg.as_string()

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, user_email, text)
        
        return {"messages": [HumanMessage(content=f"Report sent to {user_email}")]}
    except Exception as e:
        return {"messages": [HumanMessage(content=f"Failed to send email: {str(e)}")]}
