import smtplib
from email.message import EmailMessage
import markdown
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
_port_raw = os.getenv("SMTP_PORT", "465")
# Clean up any potential garbage (like 587"465") by taking only the first digits
import re
_port_match = re.search(r'\d+', str(_port_raw))
SMTP_PORT = int(_port_match.group()) if _port_match else 465

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def send_research_report(to_email: str, subject: str, markdown_content: str, attachment_bytes=None, attachment_name="Report.docx"):
    """
    Sends a beautifully formatted HTML email containing the research report.
    """
    if not to_email:
        return
        
    print(f"[email] Sending premium report to {to_email}...")
    
    # Convert markdown to html
    html_body = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])
    
    # Wrap in a basic clean style wrapper
    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
          h1, h2, h3 {{ color: #111; }}
          a {{ color: #0366d6; text-decoration: none; }}
          a:hover {{ text-decoration: underline; }}
          blockquote {{ border-left: 4px solid #dfe2e5; margin: 0; padding-left: 16px; color: #6a737d; }}
          code {{ background-color: #f6f8fa; border-radius: 3px; padding: 0.2em 0.4em; font-size: 85%; }}
          pre {{ background-color: #f6f8fa; border-radius: 3px; padding: 16px; overflow: auto; }}
        </style>
      </head>
      <body>
        {html_body}
      </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = f"Deep Research Report: {subject}"
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    
    # Set the content to HTML
    msg.set_content("Please view this email in a client that supports HTML.")
    msg.add_alternative(html_content, subtype='html')

    # Add attachment if provided
    if attachment_bytes:
        msg.add_attachment(
            attachment_bytes.read(), 
            maintype='application', 
            subtype='vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=attachment_name
        )

    try:
        # Port 465 is usually for SMTP_SSL
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        else:
            # Port 587 and others usually use STARTTLS
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        print("[email] Sent successfully!")
    except Exception as e:
        print(f"[email] Error sending email: {e}")
