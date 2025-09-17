"""
Magic Link Authentication Service
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class MagicLinkService:
    """Service for handling magic link authentication with Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError("Missing Supabase environment variables")
        
        # Create Supabase client
        self.client: Client = create_client(self.supabase_url, self.supabase_anon_key)
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.redirect_url = f"{self.frontend_url}/auth/callback"
    
    async def send_magic_link(
        self, 
        email: str, 
        redirect_to: Optional[str] = None, 
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a magic link to the user's email."""
        try:
            # Parse full name
            first_name = ""
            last_name = ""
            if full_name:
                name_parts = full_name.strip().split(" ")
                first_name = name_parts[0] if name_parts else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Send magic link
            response = self.client.auth.sign_in_with_otp({
                "email": email,
                "options": {
                    "email_redirect_to": redirect_to or self.redirect_url,
                    "should_create_user": True,
                    "data": {
                        "source": "ai_assessment",
                        "first_name": first_name,
                        "last_name": last_name,
                        "full_name": full_name
                    }
                }
            })
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Magic link error: {response.error}")
                return {"success": False, "error": response.error.message}
            
            return {
                "success": True,
                "data": response.data if hasattr(response, 'data') else None,
                "message": "Magic link sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending magic link: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_magic_link(self, token: str, type: str = "magiclink") -> Dict[str, Any]:
        """Verify the magic link token."""
        try:
            response = self.client.auth.verify_otp({
                "token_hash": token,
                "type": type
            })
            
            if hasattr(response, 'error') and response.error:
                return {"success": False, "error": response.error.message}
            
            return {
                "success": True,
                "session": response.session if hasattr(response, 'session') else None,
                "user": response.user if hasattr(response, 'user') else None
            }
            
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return {"success": False, "error": str(e)}