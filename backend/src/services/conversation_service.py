from typing import List, Optional
from sqlmodel import Session, select
from src.models.conversation import Conversation, ConversationCreate
from src.models.message import Message
from src.utils.logging_config import get_logger


class ConversationService:
    logger = get_logger(__name__)

    def create_conversation(self, conversation_data: ConversationCreate, db_session: Session) -> Conversation:
        """Create a new conversation."""
        self.logger.info(f"Creating conversation for user: {conversation_data.user_id}")
        conversation = Conversation(
            user_id=conversation_data.user_id,
            title=conversation_data.title
        )
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        self.logger.info(f"Conversation created successfully with ID: {conversation.id}")
        return conversation

    def get_conversation_by_id(self, conversation_id: int, db_session: Session) -> Optional[Conversation]:
        """Retrieve a conversation by its ID."""
        self.logger.debug(f"Retrieving conversation by ID: {conversation_id}")
        conversation = db_session.get(Conversation, conversation_id)
        if conversation:
            self.logger.debug(f"Conversation found with ID: {conversation_id}")
        else:
            self.logger.warning(f"Conversation not found with ID: {conversation_id}")
        return conversation

    def get_user_conversations(self, user_id: str, db_session: Session) -> List[Conversation]:
        """Retrieve all conversations for a specific user."""
        self.logger.info(f"Retrieving conversations for user: {user_id}")
        statement = select(Conversation).where(Conversation.user_id == user_id)
        results = db_session.exec(statement)
        conversations = results.all()
        self.logger.info(f"Retrieved {len(conversations)} conversations for user: {user_id}")
        return conversations

    def update_conversation_title(self, conversation_id: int, title: str, db_session: Session) -> Optional[Conversation]:
        """Update the title of a conversation."""
        self.logger.info(f"Updating conversation {conversation_id} title to: {title}")
        conversation = db_session.get(Conversation, conversation_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = conversation.updated_at  # Use current time
            db_session.add(conversation)
            db_session.commit()
            db_session.refresh(conversation)
            self.logger.info(f"Conversation {conversation_id} title updated successfully")
        else:
            self.logger.warning(f"Conversation not found for update: {conversation_id}")
        return conversation

    def add_message_to_conversation(self, conversation_id: int, message: Message, db_session: Session) -> Optional[Message]:
        """Add a message to a conversation."""
        self.logger.debug(f"Adding message to conversation: {conversation_id}")
        conversation = db_session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = conversation.updated_at  # Use current time
            db_session.add(message)
            db_session.commit()
            db_session.refresh(message)
            self.logger.debug(f"Message added to conversation: {conversation_id}")
            return message
        self.logger.warning(f"Conversation not found to add message: {conversation_id}")
        return None

    def get_conversation_messages(self, conversation_id: int, db_session: Session) -> List[Message]:
        """Retrieve all messages for a specific conversation."""
        self.logger.debug(f"Retrieving messages for conversation: {conversation_id}")
        conversation = db_session.get(Conversation, conversation_id)
        if conversation:
            messages = conversation.messages
            self.logger.debug(f"Retrieved {len(messages)} messages for conversation: {conversation_id}")
            return messages
        self.logger.warning(f"Conversation not found to retrieve messages: {conversation_id}")
        return []

    def delete_conversation(self, conversation_id: int, db_session: Session) -> bool:
        """Delete a conversation and its messages."""
        self.logger.info(f"Deleting conversation: {conversation_id}")
        conversation = db_session.get(Conversation, conversation_id)
        if conversation:
            db_session.delete(conversation)
            db_session.commit()
            self.logger.info(f"Conversation deleted successfully: {conversation_id}")
            return True
        self.logger.warning(f"Conversation not found for deletion: {conversation_id}")
        return False