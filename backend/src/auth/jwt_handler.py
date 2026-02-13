from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status, Request
from ..config.settings import settings
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return decoded payload.

    Args:
        token (str): JWT token to verify

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    logger.debug("Verifying JWT token")

    try:
        # Decode the token using the secret key
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract user information from payload
        user_id = payload.get("sub")
        exp = payload.get("exp")

        if user_id is None:
            logger.error("Token verification failed: Missing user ID in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Missing user ID"
            )

        if exp is None:
            logger.error("Token verification failed: Missing expiration in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Missing expiration"
            )

        # Check if token is expired
        if datetime.fromtimestamp(exp) < datetime.now():
            logger.warning("Token verification failed: Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        logger.debug(f"Token verified successfully for user: {user_id}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        logger.error(f"Token verification failed: JWT error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception as e:
        logger.error(f"Token verification failed: Authentication error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )


async def get_current_user(request: Request) -> str:
    """
    Extract and verify user from JWT token in request headers.

    Args:
        request (Request): FastAPI request object containing Authorization header

    Returns:
        str: User ID extracted from token

    Raises:
        HTTPException: If no token provided or token is invalid
    """
    logger.debug("Extracting and verifying user from JWT token in request")

    # Get authorization header
    authorization = request.headers.get("Authorization")

    if not authorization:
        logger.warning("Authorization header missing in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    # Check if it's a Bearer token
    if not authorization.startswith("Bearer "):
        logger.warning("Invalid authorization header format in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )

    # Extract token
    token = authorization.split(" ")[1]

    # Verify token and get payload
    payload = verify_token(token)

    # Return user ID
    user_id = payload.get("sub")
    logger.debug(f"Current user extracted from token: {user_id}")
    return user_id


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token with the provided data.

    Args:
        data (dict): Data to encode in the token
        expires_delta (timedelta, optional): Token expiration time delta

    Returns:
        str: Encoded JWT token
    """
    logger.debug(f"Creating access token for data: {data}")
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire.timestamp()})
    logger.debug(f"Token will expire at: {expire}")

    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    logger.info(f"Access token created successfully")
    return encoded_jwt


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token without full verification (for logging/debugging).

    Args:
        token (str): JWT token to extract user ID from

    Returns:
        str: User ID if found, None otherwise
    """
    logger.debug("Extracting user ID from token without full verification")
    try:
        # Decode without verification to get user ID
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_signature": False, "verify_exp": False}
        )
        user_id = payload.get("sub")
        logger.debug(f"User ID extracted from token: {user_id}")
        return user_id
    except jwt.InvalidTokenError:
        logger.debug("Failed to extract user ID from token: Invalid token")
        return None