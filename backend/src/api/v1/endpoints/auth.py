from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ....models.user import UserCreate, UserResponse, UserLogin
from ....services.user_service import UserService
from ....database.session import get_session
from ....auth.jwt_handler import create_access_token
from ....config.settings import settings
from ....utils.logging_config import get_logger

router = APIRouter()
security = HTTPBearer()
logger = get_logger(__name__)

@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_session)
):
    """
    Register a new user.

    Args:
        user_data (UserCreate): User registration data
        db (Session): Database session

    Returns:
        UserResponse: Created user data with JWT token
    """
    logger.info(f"User registration attempt for email: {user_data.email}")

    try:
        # Check if user already exists
        existing_user = UserService.get_user_by_email(user_data.email, db)
        if existing_user:
            logger.warning(f"Registration failed: User with email {user_data.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Create the user
        user = UserService.create_user(user_data, db)
        logger.info(f"User created successfully with ID: {user.id}")

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": str(user.id)}  # Use user ID as subject
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )
        logger.debug(f"JWT token generated for user: {user.id}")

        # Return user data with token
        logger.info(f"User registration completed successfully for: {user.email}")
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            token=access_token
        )
    except HTTPException:
        logger.error(f"HTTP exception during registration for email: {user_data.email}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration for email {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=UserResponse)
def login_user(
    user_login: UserLogin,
    db: Session = Depends(get_session)
):
    """
    Authenticate user and return JWT token.

    Args:
        user_login (UserLogin): User login credentials
        db (Session): Database session

    Returns:
        UserResponse: User data with JWT token
    """
    logger.info(f"Login attempt for email: {user_login.email}")

    try:
        # Authenticate user
        user = UserService.authenticate_user(
            user_login.email,
            user_login.password,
            db
        )

        if not user:
            logger.warning(f"Login failed: Invalid credentials for email: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        logger.info(f"User authenticated successfully: {user.id}")

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": str(user.id)}  # Use user ID as subject
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )
        logger.debug(f"JWT token generated for user: {user.id}")

        # Return user data with token
        logger.info(f"Login completed successfully for: {user.email}")
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            token=access_token
        )
    except HTTPException:
        logger.error(f"HTTP exception during login for email: {user_login.email}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for email {user_login.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
def logout_user():
    """
    Logout user (client-side token removal is sufficient).

    Returns:
        dict: Success message
    """
    logger.info("User logout request received")
    return {"message": "Successfully logged out"}


@router.get("/profile", response_model=UserResponse)
def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session)
):
    """
    Get current user profile.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from Authorization header
        db (Session): Database session

    Returns:
        UserResponse: Current user data
    """
    logger.info("Profile access request")

    from ....auth.jwt_handler import verify_token

    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")

    if not user_id:
        logger.error("Invalid token: Could not extract user ID from token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    logger.debug(f"Token validated for user ID: {user_id}")

    user = UserService.get_user_by_id(user_id, db)
    if not user:
        logger.error(f"User not found for ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.info(f"Profile retrieved for user: {user.email}")

    # Create a new token for the response (though the user already has one)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        token=access_token
    )