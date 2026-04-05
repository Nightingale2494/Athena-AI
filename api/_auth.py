from firebase_admin import auth

def verify_token(authorization: str = None) -> dict:
    """Verify Firebase ID token from Authorization header."""
    if not authorization:
        raise Exception("Authorization header missing")
    
    if not authorization.startswith('Bearer '):
        raise Exception("Invalid authorization format")
    
    token = authorization.split('Bearer ')[1]
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise Exception("Invalid token")
    except auth.ExpiredIdTokenError:
        raise Exception("Token expired")
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")
