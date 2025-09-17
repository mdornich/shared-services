"""
Email Templates for all projects
Centralized HTML email templates for consistency
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class EmailTemplate:
    """Email template data"""
    subject: str
    html: str
    text: str

class EmailTemplates:
    """
    Centralized email templates for all projects.
    """
    
    @staticmethod
    def get_base_html(content: str, footer: Optional[str] = None) -> str:
        """
        Get base HTML template with consistent styling.
        
        Args:
            content: Main content HTML
            footer: Optional footer HTML
            
        Returns:
            Complete HTML email
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 0;
                }}
                .email-wrapper {{
                    background-color: #f5f5f5;
                    padding: 20px;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .email-header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px;
                    text-align: center;
                }}
                .email-header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 28px;
                }}
                .email-content {{
                    padding: 30px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 28px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .button:hover {{
                    opacity: 0.9;
                }}
                .email-footer {{
                    padding: 20px 30px;
                    background-color: #f9fafb;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                }}
                .divider {{
                    height: 1px;
                    background-color: #e5e7eb;
                    margin: 20px 0;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    background-color: #e0e7ff;
                    color: #3730a3;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 600;
                }}
                .success-badge {{
                    background-color: #d1fae5;
                    color: #065f46;
                }}
                .warning-badge {{
                    background-color: #fed7aa;
                    color: #92400e;
                }}
                .info-box {{
                    background-color: #f0f9ff;
                    border-left: 4px solid #3b82f6;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="email-container">
                    {content}
                    {f'<div class="email-footer">{footer}</div>' if footer else ''}
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def aiden_questionnaire_complete(
        name: str,
        questions_answered: int = 33,
        insights_url: Optional[str] = None
    ) -> EmailTemplate:
        """
        AIDEN 33-question questionnaire completion email.
        
        Args:
            name: User's name
            questions_answered: Number of questions completed
            insights_url: Optional URL to view insights
            
        Returns:
            EmailTemplate
        """
        content = f"""
        <div class="email-header">
            <h1>AIDEN Assessment Complete!</h1>
        </div>
        <div class="email-content">
            <h2>Congratulations, {name}! 🎊</h2>
            <p>You've successfully completed all <span class="success-badge">{questions_answered} questions</span> in your AIDEN Personal AI Assistant assessment.</p>
            
            <div class="info-box">
                <strong>Your AI Assistant Profile is Ready!</strong><br>
                Based on your responses, we've created a personalized AI assistant configuration tailored to your specific needs and preferences.
            </div>
            
            {"<center><a href='" + insights_url + "' class='button'>View Your AI Profile</a></center>" if insights_url else ""}
            
            <h3>What We've Learned About You:</h3>
            <ul>
                <li>Your work style and preferences</li>
                <li>Key areas where AI can assist you</li>
                <li>Optimal AI interaction patterns for your needs</li>
                <li>Custom recommendations for AI tool usage</li>
            </ul>
            
            <div class="divider"></div>
            
            <h3>Next Steps:</h3>
            <ol>
                <li><strong>Review Your Profile:</strong> Explore your personalized AI assistant recommendations</li>
                <li><strong>Activate Your Assistant:</strong> Start using your configured AI tools</li>
                <li><strong>Provide Feedback:</strong> Help us improve your AI experience</li>
            </ol>
            
            <p>Your journey to enhanced productivity with AI starts now!</p>
        </div>
        """
        
        footer = """
        <p><strong>Need Help?</strong> Our team is here to assist you in getting the most from your AI assistant.</p>
        <p style="font-size: 12px;">This assessment was powered by AIDEN - Your Personal AI Assistant Factory</p>
        """
        
        html = EmailTemplates.get_base_html(content, footer)
        
        text = f"""
        AIDEN Assessment Complete!
        
        Congratulations, {name}!
        
        You've successfully completed all {questions_answered} questions in your AIDEN Personal AI Assistant assessment.
        
        Your AI Assistant Profile is Ready!
        Based on your responses, we've created a personalized AI assistant configuration tailored to your specific needs and preferences.
        
        {"View Your AI Profile: " + insights_url if insights_url else ""}
        
        What We've Learned About You:
        - Your work style and preferences
        - Key areas where AI can assist you
        - Optimal AI interaction patterns for your needs
        - Custom recommendations for AI tool usage
        
        Next Steps:
        1. Review Your Profile: Explore your personalized AI assistant recommendations
        2. Activate Your Assistant: Start using your configured AI tools
        3. Provide Feedback: Help us improve your AI experience
        
        Your journey to enhanced productivity with AI starts now!
        
        Need Help? Our team is here to assist you in getting the most from your AI assistant.
        
        This assessment was powered by AIDEN - Your Personal AI Assistant Factory
        """
        
        return EmailTemplate(
            subject="🎉 Your AIDEN AI Assistant Profile is Ready!",
            html=html,
            text=text
        )
    
    @staticmethod
    def aiba_assessment_complete(
        name: str,
        company: Optional[str] = None,
        score: Optional[int] = None,
        report_url: Optional[str] = None
    ) -> EmailTemplate:
        """
        aiBA-1.2 AI assessment completion email.
        
        Args:
            name: User's name
            company: Optional company name
            score: Optional assessment score
            report_url: Optional URL to view report
            
        Returns:
            EmailTemplate
        """
        content = f"""
        <div class="email-header">
            <h1>AI Business Assessment Complete</h1>
        </div>
        <div class="email-content">
            <h2>Great job, {name}! 🏆</h2>
            {"<p>Your organization at <strong>" + company + "</strong> has completed the AI Business Assessment.</p>" if company else "<p>You've completed the AI Business Assessment.</p>"}
            
            {f'<div class="info-box"><strong>Your AI Readiness Score: {score}/100</strong><br>This score reflects your current position in the AI adoption journey.</div>' if score else ''}
            
            {"<center><a href='" + report_url + "' class='button'>Download Your Report</a></center>" if report_url else ""}
            
            <h3>Your Assessment Covers:</h3>
            <ul>
                <li>Current AI implementation status</li>
                <li>Organizational readiness for AI adoption</li>
                <li>Technical infrastructure assessment</li>
                <li>Strategic alignment with business goals</li>
                <li>Recommended next steps</li>
            </ul>
            
            <div class="divider"></div>
            
            <h3>What Happens Next?</h3>
            <p>Our AI consultants will review your assessment and may reach out with:</p>
            <ul>
                <li>Personalized recommendations for your AI journey</li>
                <li>Strategic guidance on implementation</li>
                <li>Resources and best practices</li>
            </ul>
        </div>
        """
        
        footer = """
        <p><strong>Questions?</strong> Reply to this email to connect with our AI consulting team.</p>
        <p style="font-size: 12px;">AI Business Assessment v1.2 - Confidential</p>
        """
        
        html = EmailTemplates.get_base_html(content, footer)
        
        text = f"""
        AI Business Assessment Complete
        
        Great job, {name}!
        
        {"Your organization at " + company + " has completed the AI Business Assessment." if company else "You've completed the AI Business Assessment."}
        
        {f'Your AI Readiness Score: {score}/100' if score else ''}
        
        {"Download Your Report: " + report_url if report_url else ""}
        
        Your Assessment Covers:
        - Current AI implementation status
        - Organizational readiness for AI adoption
        - Technical infrastructure assessment
        - Strategic alignment with business goals
        - Recommended next steps
        
        What Happens Next?
        Our AI consultants will review your assessment and may reach out with:
        - Personalized recommendations for your AI journey
        - Strategic guidance on implementation
        - Resources and best practices
        
        Questions? Reply to this email to connect with our AI consulting team.
        
        AI Business Assessment v1.2 - Confidential
        """
        
        return EmailTemplate(
            subject=f"Your AI Business Assessment Results {('- ' + company) if company else ''}",
            html=html,
            text=text
        )