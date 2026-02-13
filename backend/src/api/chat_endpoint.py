from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional
from src.database.session import get_session
from src.services.conversation_service import ConversationService
from src.services.ai_agent_service import AIAgentService
from src.models.message import Message, MessageCreate
from src.models.conversation import ConversationCreate
from src.auth.dependencies import get_current_user_id
from pydantic import BaseModel
import os
from src.utils.logging_config import get_logger


router = APIRouter(tags=["chat"])
logger = get_logger(__name__)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list = []
    tool_responses: list = []


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    db_session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Process a chat message and return AI response.

    Args:
        user_id: The authenticated user's ID (must match current_user)
        request: Contains the user's message and optional conversation_id

    Returns:
        ChatResponse with conversation_id, AI response, and any tool calls
    """
    logger.info(f"Chat endpoint called for user: {user_id}")

    # Verify that the user_id in the path matches the authenticated user
    if current_user_id != user_id:
        logger.warning(f"Unauthorized access attempt: path user_id={user_id}, authenticated user_id={current_user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: User ID mismatch")

    logger.debug(f"User authentication verified for user: {user_id}")

    # Initialize services
    conversation_service = ConversationService()
    ai_agent_service = AIAgentService(openrouter_api_key=os.getenv("OPEN_ROUTER_API_KEY"))
    ai_agent_service.initialize_agent_with_tools()  # Initialize with MCP tools
    logger.debug("AI agent service initialized with tools")

    # Get or create conversation
    conversation = None
    if request.conversation_id:
        logger.info(f"Retrieving existing conversation: {request.conversation_id}")
        conversation = conversation_service.get_conversation_by_id(request.conversation_id, db_session)
        if not conversation:
            logger.error(f"Conversation not found: {request.conversation_id}")
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.user_id != user_id:
            logger.warning(f"Access denied: Conversation {request.conversation_id} does not belong to user {user_id}")
            raise HTTPException(status_code=403, detail="Access denied: Conversation does not belong to user")
        logger.info(f"Found existing conversation: {conversation.id}")
    else:
        # Create new conversation
        logger.info(f"Creating new conversation for user: {user_id}")
        conversation_data = ConversationCreate(user_id=user_id)
        conversation = conversation_service.create_conversation(conversation_data, db_session)
        logger.info(f"New conversation created: {conversation.id}")

    # Create and save user message
    logger.debug(f"Saving user message to conversation: {conversation.id}")
    user_message = Message(
        conversation_id=conversation.id,
        sender='user',
        content=request.message,
        tool_calls=None,  # Explicitly set to None for user messages
        tool_responses=None  # Explicitly set to None for user messages
    )
    db_session.add(user_message)
    db_session.commit()
    logger.debug(f"User message saved to conversation: {conversation.id}")

    # Process the message with the AI agent
    logger.info(f"Processing AI request for user: {user_id}, conversation: {conversation.id}")
    result = await ai_agent_service.process_natural_language_request(
        user_input=request.message,
        user_id=user_id,
        conversation_id=conversation.id
    )
    logger.info(f"AI processing completed for user: {user_id}, conversation: {conversation.id}")

    # Create and save AI response message
    logger.debug(f"Saving AI response to conversation: {conversation.id}")
    ai_message = Message(
        conversation_id=conversation.id,
        sender='assistant',
        content=result["response"],
        tool_calls=result.get("tool_calls") if result.get("tool_calls") else None,
        tool_responses=result.get("tool_responses") if result.get("tool_responses") else None
    )
    db_session.add(ai_message)
    db_session.commit()
    logger.debug(f"AI response saved to conversation: {conversation.id}")

    logger.info(f"Chat endpoint completed for user: {user_id}, conversation: {conversation.id}")
    return ChatResponse(
        conversation_id=conversation.id,
        response=result["response"],
        tool_calls=result.get("tool_calls", []),
        tool_responses=result.get("tool_responses", [])
    )


# Endpoint to get conversation history
@router.get("/{user_id}/conversations/{conversation_id}")
def get_conversation(
    user_id: str,
    conversation_id: int,
    db_session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve a specific conversation with its messages.
    """
    logger.info(f"Retrieving conversation {conversation_id} for user: {user_id}")

    # Verify user authentication
    if current_user_id != user_id:
        logger.warning(f"Unauthorized access attempt: path user_id={user_id}, authenticated user_id={current_user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: User ID mismatch")

    conversation_service = ConversationService()
    conversation = conversation_service.get_conversation_by_id(conversation_id, db_session)

    if not conversation:
        logger.error(f"Conversation not found: {conversation_id}")
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_id:
        logger.warning(f"Access denied: Conversation {conversation_id} does not belong to user {user_id}")
        raise HTTPException(status_code=403, detail="Access denied: Conversation does not belong to user")

    logger.info(f"Conversation {conversation_id} retrieved successfully for user: {user_id}")
    return conversation