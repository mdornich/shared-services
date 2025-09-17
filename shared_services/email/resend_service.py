"""
Resend Email Service
Handles transactional emails across all projects
"""
import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import resend

logger = logging.getLogger(__name__)

@dataclass
class EmailAttachment:
    """Email attachment data"""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"

@dataclass
class EmailResult:
    """Result of email send operation"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None

class ResendService:
    """
    Resend email service for transactional emails.
    
    Features:
    - HTML and plain text emails
    - Attachments support
    - Batch sending
    - Email tracking
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Resend service.
        
        Args:
            api_key: Resend API key (defaults to RESEND_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('RESEND_API_KEY')
        if not self.api_key:
            raise ValueError("Resend API key is required")
        
        resend.api_key = self.api_key
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'noreply@yourdomain.com')
        
    def send_email(
        self,
        to: str | List[str],
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[EmailAttachment]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> EmailResult:
        """
        Send an email using Resend.
        
        Args:
            to: Recipient email(s)
            subject: Email subject
            html: HTML content
            text: Plain text content
            from_email: Sender email (defaults to configured)
            reply_to: Reply-to email
            attachments: List of attachments
            tags: Email tags for tracking
            
        Returns:
            EmailResult with success status and message ID
        """
        try:
            # Ensure to is a list
            if isinstance(to, str):
                to = [to]
            
            # Build email params
            params = {
                "from": from_email or self.from_email,
                "to": to,
                "subject": subject,
            }
            
            # Add content (must have either HTML or text)
            if html:
                params["html"] = html
            if text:
                params["text"] = text
            if not html and not text:
                return EmailResult(
                    success=False,
                    error="Either HTML or text content is required"
                )
            
            # Add optional params
            if reply_to:
                params["reply_to"] = reply_to
            if tags:
                params["tags"] = tags
                
            # Add attachments
            if attachments:
                params["attachments"] = [
                    {
                        "filename": att.filename,
                        "content": att.content,
                        "content_type": att.content_type,
                    }
                    for att in attachments
                ]
            
            # Send email
            response = resend.Emails.send(params)
            
            return EmailResult(
                success=True,
                message_id=response.get("id"),
            )
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return EmailResult(
                success=False,
                error=str(e)
            )
    
    def send_batch(
        self,
        emails: List[Dict[str, Any]]
    ) -> List[EmailResult]:
        """
        Send multiple emails in batch.
        
        Args:
            emails: List of email parameters (same as send_email)
            
        Returns:
            List of EmailResult objects
        """
        results = []
        for email_params in emails:
            result = self.send_email(**email_params)
            results.append(result)
        return results
    
    def send_magic_link(
        self,
        to: str,
        name: str,
        magic_link: str,
        company: Optional[str] = None
    ) -> EmailResult:
        """
        Send a magic link authentication email.
        
        Args:
            to: Recipient email
            name: User's name
            magic_link: The magic link URL
            company: Optional company name
            
        Returns:
            EmailResult
        """
        subject = "Your secure login link"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ 
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #3b82f6;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                }}
                .footer {{ margin-top: 40px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Hello {name}!</h2>
                {"<p>Welcome to AIDEN from " + company + ".</p>" if company else "<p>Welcome to AIDEN.</p>"}
                <p>Click the button below to securely log in to your account:</p>
                <p style="margin: 30px 0;">
                    <a href="{magic_link}" class="button">Log In to AIDEN</a>
                </p>
                <p>Or copy and paste this link in your browser:</p>
                <p style="word-break: break-all; color: #3b82f6;">{magic_link}</p>
                <div class="footer">
                    <p>This link will expire in 15 minutes for security reasons.</p>
                    <p>If you didn't request this email, you can safely ignore it.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
        Hello {name}!
        
        {"Welcome to AIDEN from " + company + "." if company else "Welcome to AIDEN."}
        
        Click this link to securely log in to your account:
        {magic_link}
        
        This link will expire in 15 minutes for security reasons.
        If you didn't request this email, you can safely ignore it.
        """
        
        return self.send_email(
            to=to,
            subject=subject,
            html=html,
            text=text,
            tags={"type": "magic_link", "app": "aiden"}
        )
    
    def send_completion_email(
        self,
        to: str,
        name: str,
        completion_type: str,
        results_url: Optional[str] = None,
        attachment: Optional[EmailAttachment] = None
    ) -> EmailResult:
        """
        Send a completion email (assessment, questionnaire, etc).
        
        Args:
            to: Recipient email
            name: User's name  
            completion_type: Type of completion (e.g., "AI Assessment", "AIDEN Questionnaire")
            results_url: Optional URL to view results
            attachment: Optional PDF report attachment
            
        Returns:
            EmailResult
        """
        subject = f"Your {completion_type} Results"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ 
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #10b981;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                }}
                .success-badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    background-color: #d1fae5;
                    color: #065f46;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                .footer {{ margin-top: 40px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Congratulations, {name}! 🎉</h2>
                <p>You've successfully completed your <span class="success-badge">{completion_type}</span></p>
                
                {"<p>Your personalized results are ready. Click the button below to view them:</p><p style='margin: 30px 0;'><a href='" + results_url + "' class='button'>View Your Results</a></p>" if results_url else "<p>Your results report is attached to this email.</p>"}
                
                <h3>What's Next?</h3>
                <ul>
                    <li>Review your personalized insights</li>
                    <li>Share results with your team</li>
                    <li>Schedule a follow-up consultation</li>
                </ul>
                
                <div class="footer">
                    <p>Thank you for using our platform. If you have any questions, please don't hesitate to reach out.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
        Congratulations, {name}!
        
        You've successfully completed your {completion_type}.
        
        {"Your personalized results are ready. View them here: " + results_url if results_url else "Your results report is attached to this email."}
        
        What's Next?
        - Review your personalized insights
        - Share results with your team
        - Schedule a follow-up consultation
        
        Thank you for using our platform. If you have any questions, please don't hesitate to reach out.
        """
        
        attachments = [attachment] if attachment else None
        
        return self.send_email(
            to=to,
            subject=subject,
            html=html,
            text=text,
            attachments=attachments,
            tags={"type": "completion", "completion_type": completion_type}
        )