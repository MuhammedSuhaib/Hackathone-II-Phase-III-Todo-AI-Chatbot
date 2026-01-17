from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ....models.user import UserCreate, UserResponse, UserLogin
from ....services.user_service import UserService
from ....database.session import get_session
from ....auth.jwt_handler import create_access_token
from ....config.settings import settings

router = APIRouter()
security = HTTPBearer()

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
    try:
        # Check if user already exists
        existing_user = UserService.get_user_by_email(user_data.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Create the user
        user = UserService.create_user(user_data, db)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": str(user.id)}  # Use user ID as subject
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        # Return user data with token
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            token=access_token
        )
    except HTTPException:
        raise
    except Exception as e:
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
    try:
        # Authenticate user
        user = UserService.authenticate_user(
            user_login.email,
            user_login.password,
            db
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": str(user.id)}  # Use user ID as subject
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        # Return user data with token
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            token=access_token
        )
    except HTTPException:
        raise
    except Exception as e:
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
    from ....auth.jwt_handler import verify_token

    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = UserService.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

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