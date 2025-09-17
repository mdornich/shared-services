"""
Magic Link Authentication Service
Ported from aiBA-1 magicLinkService.ts to Python
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from ..core.supabase_config import supabase_auth, supabase_admin, MAGIC_LINK_REDIRECT
from ..db.models import User
from ..db.session import SessionLocal

logger = logging.getLogger(__name__)


async def send_magic_link(
    email: str, 
    redirect_to: Optional[str] = None, 
    full_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a magic link to the user's email.
    
    Args:
        email: User's email address
        redirect_to: Optional custom redirect URL after authentication
        full_name: Optional user's full name for profile creation
    
    Returns:
        Dict with success status and message
    """
    try:
        # Parse full name into first and last
        first_name = ""
        last_name = ""
        if full_name:
            name_parts = full_name.strip().split(" ")
            first_name = name_parts[0] if name_parts else ""
            # Everything after the first word becomes the last name
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Send magic link via Supabase Auth
        # This will send "Confirm signup" email for new users,
        # and "Magic Link" email for existing users
        response = supabase_auth.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": redirect_to or MAGIC_LINK_REDIRECT,
                "should_create_user": True,  # Creates user if doesn't exist
                "data": {
                    "source": "ai_assessment",  # Track where users come from
                    "first_name": first_name,
                    "last_name": last_name,
                    "full_name": full_name
                }
            }
        })
        
        if response.error:
            logger.error(f"Magic link error: {response.error}")
            return {
                "success": False,
                "error": response.error.message
            }
        
        return {
            "success": True,
            "data": response.data,
            "message": "Magic link sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error sending magic link: {e}")
        return {
            "success": False,
            "error": "Failed to send magic link"
        }


async def verify_magic_link(token: str, type: str = "magiclink") -> Dict[str, Any]:
    """
    Verify the magic link token and create a session.
    
    Args:
        token: The token from the magic link
        type: Token type (magiclink, signup, recovery, etc.)
    
    Returns:
        Dict with success status, session, and user data
    """
    try:
        response = supabase_auth.auth.verify_otp({
            "token_hash": token,
            "type": type
        })
        
        if response.error:
            logger.error(f"Token verification error: {response.error}")
            return {
                "success": False,
                "error": response.error.message
            }
        
        return {
            "success": True,
            "session": response.session,
            "user": response.user
        }
        
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        return {
            "success": False,
            "error": "Failed to verify token"
        }


async def get_or_create_profile(
    user_id: str, 
    email: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get or create user profile in the users table.
    
    Args:
        user_id: Supabase auth user ID
        email: User's email address
        metadata: Optional metadata from auth (first_name, last_name, etc.)
    
    Returns:
        Dict with success status and user profile
    """
    db = SessionLocal()
    try:
        # Check if user exists in users table
        existing_user = db.query(User).filter(User.auth_user_id == user_id).first()
        
        if existing_user:
            return {
                "success": True,
                "profile": existing_user,
                "is_new": False
            }
        
        # Create new user if doesn't exist
        new_user = User(
            email=email,
            auth_user_id=user_id,
            first_name=metadata.get("first_name") if metadata else None,
            last_name=metadata.get("last_name") if metadata else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "success": True,
            "profile": new_user,
            "is_new": True
        }
        
    except Exception as e:
        logger.error(f"Error managing user profile: {e}")
        db.rollback()
        return {
            "success": False,
            "error": "Failed to manage user profile"
        }
    finally:
        db.close()


async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and return the user.
    
    Args:
        token: JWT token to verify
    
    Returns:
        User data if valid, None otherwise
    """
    try:
        response = supabase_auth.auth.get_user(token)
        
        if response.error or not response.user:
            logger.error(f"Token verification failed: {response.error}")
            return None
        
        return response.user
        
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None


async def get_profile(user_id: str) -> Optional[User]:
    """
    Get user profile by auth user ID.
    
    Args:
        user_id: Supabase auth user ID
    
    Returns:
        User profile if found, None otherwise
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.auth_user_id == user_id).first()
        return user
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None
    finally:
        db.close()


async def update_profile(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user profile with name and company.
    
    Args:
        user_id: Supabase auth user ID
        updates: Dict with name and/or company fields
    
    Returns:
        Dict with success status and updated profile
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.auth_user_id == user_id).first()
        
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Parse name into first_name and last_name if provided
        if "name" in updates:
            name_parts = updates["name"].strip().split(" ")
            user.first_name = name_parts[0] if name_parts else ""
            user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        if "company" in updates:
            # Note: The users table doesn't have a company field in the schema
            # This would need to be added or handled differently
            pass
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return {
            "success": True,
            "profile": user
        }
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        db.rollback()
        return {
            "success": False,
            "error": "Failed to update user"
        }
    finally:
        db.close()


async def is_profile_complete(user_id: str) -> bool:
    """
    Check if user has completed profile (has first_name and email).
    
    Args:
        user_id: Supabase auth user ID
    
    Returns:
        True if profile is complete, False otherwise
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.auth_user_id == user_id).first()
        
        if not user:
            return False
        
        # Profile is complete if they have first_name and email
        return bool(user.first_name and user.email)
        
    except Exception as e:
        logger.error(f"Error checking profile completion: {e}")
        return False
    finally:
        db.close()