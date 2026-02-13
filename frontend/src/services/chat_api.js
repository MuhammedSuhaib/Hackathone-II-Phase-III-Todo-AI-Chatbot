/**
 * API service for chat functionality
 */

class ChatAPIService {
  constructor(baseURL) {
    // Use the environment variable for API base URL, fallback to /api if not set
    this.baseURL = baseURL || process.env.NEXT_PUBLIC_API_BASE_URL + '/api' || 'https://mahmedmumair-phase3.hf.space/api';
  }

  /**
   * Send a message to the chat endpoint
   * @param {string} userId - The ID of the authenticated user
   * @param {string} message - The message content
   * @param {number} conversationId - Optional conversation ID for continuity
   * @returns {Promise<Object>} Response from the chat endpoint
   */
  async sendMessage(userId, message, conversationId = null) {
    const token = localStorage.getItem('jwt_token');

    if (!token) {
      throw new Error('Authentication token not found');
    }

    const requestBody = {
      message: message
    };

    if (conversationId) {
      requestBody.conversation_id = conversationId;
    }

    try {
      const response = await fetch(`${this.baseURL}/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Get conversation history
   * @param {string} userId - The ID of the authenticated user
   * @param {number} conversationId - The ID of the conversation to retrieve
   * @returns {Promise<Object>} Conversation data
   */
  async getConversation(userId, conversationId) {
    const token = localStorage.getItem('jwt_token');

    if (!token) {
      throw new Error('Authentication token not found');
    }

    try {
      const response = await fetch(`${this.baseURL}/${userId}/conversations/${conversationId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  }

  /**
   * Get all conversations for a user
   * @param {string} userId - The ID of the authenticated user
   * @returns {Promise<Array>} Array of conversation summaries
   */
  async getUserConversations(userId) {
    const token = localStorage.getItem('jwt_token');

    if (!token) {
      throw new Error('Authentication token not found');
    }

    try {
      const response = await fetch(`${this.baseURL}/${userId}/conversations`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting user conversations:', error);
      throw error;
    }
  }
}

// Export singleton instance
const chatAPI = new ChatAPIService();
export default chatAPI;