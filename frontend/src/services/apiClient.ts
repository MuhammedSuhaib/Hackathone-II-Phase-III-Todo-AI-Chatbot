import { Task, TaskFormData } from '@/types/Task';
import { ApiResponse, ErrorResponse } from '@/types/ApiResponse';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://mahmedmumair-phase3.hf.space';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    // Add JWT token if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null;
    if (token && config.headers) {
      (config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        // Handle different status codes appropriately
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `API request failed with status ${response.status}`);
      }

      // Handle different response types based on status code
      let data;
      if (response.status === 204) {
        // No content for DELETE requests
        data = null;
      } else {
        data = await response.json();

        // Transform snake_case to camelCase for task objects
        if (data && typeof data === 'object') {
          // Handle single task object
          if (data.hasOwnProperty('created_at') || data.hasOwnProperty('updated_at')) {
            data = this.transformTaskResponse(data);
          }
          // Handle array of tasks
          else if (Array.isArray(data) && data.length > 0 && data[0].hasOwnProperty('created_at')) {
            data = data.map(task => this.transformTaskResponse(task));
          }
        }
      }

      return {
        success: true,
        data,
        message: data?.message,
      };
    } catch (error) {
      console.error('API request error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  async getAllTasks(): Promise<ApiResponse<Task[]>> {
    // Get user ID from localStorage or session
    const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
    if (!userId) {
      return {
        success: false,
        message: 'User not authenticated'
      };
    }
    return this.request<Task[]>(`/api/v1/users/${userId}/tasks`, { method: 'GET' });
  }

  async createTask(taskData: TaskFormData): Promise<ApiResponse<Task>> {
    const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
    if (!userId) {
      return {
        success: false,
        message: 'User not authenticated'
      };
    }
    return this.request<Task>(`/api/v1/users/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify({
        title: taskData.title,
        description: taskData.description,
        completed: taskData.completed || false,
        priority: taskData.priority
      }),
    });
  }

  async updateTask(id: string, taskData: Partial<Task>): Promise<ApiResponse<Task>> {
    const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
    if (!userId) {
      return {
        success: false,
        message: 'User not authenticated'
      };
    }

    // Prepare task data for API request
    const taskApiData: any = {
      title: taskData.title,
      description: taskData.description,
      completed: taskData.completed,
      priority: taskData.priority
    };

    // Only include fields that have values
    Object.keys(taskApiData).forEach(key => {
      if (taskApiData[key] === undefined) {
        delete taskApiData[key];
      }
    });

    return this.request<Task>(`/api/v1/users/${userId}/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(taskApiData),
    });
  }

  async toggleTaskCompletion(id: string): Promise<ApiResponse<{ id: string; completed: boolean }>> {
    const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
    if (!userId) {
      return {
        success: false,
        message: 'User not authenticated'
      };
    }
    return this.request<{ id: string; completed: boolean }>(`/api/v1/users/${userId}/tasks/${id}/toggle`, {
      method: 'PATCH',
    });
  }

  async deleteTask(id: string): Promise<ApiResponse<void>> {
    const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
    if (!userId) {
      return {
        success: false,
        message: 'User not authenticated'
      };
    }
    return this.request<void>(`/api/v1/users/${userId}/tasks/${id}`, { method: 'DELETE' });
  }

  async filterTasks(
    status?: 'all' | 'active' | 'completed',
    priority?: 'all' | 'low' | 'medium' | 'high',
    search?: string
  ): Promise<ApiResponse<Task[]>> {
    const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
    if (!userId) {
      return {
        success: false,
        message: 'User not authenticated'
      };
    }

    // Build query parameters
    const queryParams = new URLSearchParams();
    if (status && status !== 'all') queryParams.append('status', status);
    if (priority && priority !== 'all') queryParams.append('priority', priority);
    if (search) queryParams.append('search', search);

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/api/v1/users/${userId}/tasks?${queryString}` : `/api/v1/users/${userId}/tasks`;

    return this.request<Task[]>(endpoint, { method: 'GET' });
  }

  private transformTaskResponse(task: any): Task {
    return {
      id: task.id,
      title: task.title,
      description: task.description,
      completed: task.completed,
      priority: task.priority || 'low', // Provide default priority if not present
      createdAt: task.created_at,
      updatedAt: task.updated_at
    };
  }
}

export const apiClient = new ApiClient();