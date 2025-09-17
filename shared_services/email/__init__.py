# Email service module for shared services
from .resend_service import ResendService
from .email_templates import EmailTemplates

__all__ = ['ResendService', 'EmailTemplates']