from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models import User
from database import SessionLocal

# Configuration constants for JWT token generation and validation
SECRET_KEY = "your-secret-key"  # Should be stored securely in environment variables
ALGORITHM = "HS256"  # JWT encoding algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes

# Setup password hashing context and OAuth2 scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.
    
    Args:
        plain_password (str): The plain-text password to verify.
        hashed_password (str): The hashed password to compare against.
    
    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash using bcrypt.
    
    Args:
        password (str): The plain-text password to hash.
    
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Create a JWT access token.
    
    Args:
        data (dict): The data to encode in the token, typically includes user information.
    
    Returns:
        str: The encoded JWT token.
        
    Note:
        The token includes an expiration time based on ACCESS_TOKEN_EXPIRE_MINUTES.
        The token is signed using SECRET_KEY and ALGORITHM.
    """
    # Create a copy of the data to avoid modifying the original
    to_encode = data.copy()
    
    # Set token expiration time
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create and return the JWT token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """FastAPI dependency that validates JWT token and returns the current user.
    
    Args:
        token (str): The JWT token from the request header.
            Automatically extracted by FastAPI using oauth2_scheme.
    
    Returns:
        User: The authenticated user object.
        
    Raises:
        HTTPException: 
            - 401 if token is invalid
            - 401 if user not found in database
            
    Note:
        This function is typically used as a dependency in route handlers
        to ensure the request is authenticated and to get the current user.
    """
    # Create database session
    db = SessionLocal()
    
    try:
        # Decode and validate the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract username from token payload
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, 
                detail="Invalid credentials"
            )
            
    except JWTError:
        # Handle invalid or expired tokens
        raise HTTPException(
            status_code=401, 
            detail="Invalid credentials"
        )
    
    # Verify user exists in database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=401, 
            detail="Invalid credentials"
        )
        
    return user