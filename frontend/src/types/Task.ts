export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
}

export interface TaskFormData {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  completed?: boolean;
}

export interface FilterState {
  statusFilter: 'all' | 'active' | 'completed';
  priorityFilter: 'all' | 'low' | 'medium' | 'high';
  searchQuery: string;
}

export interface FormState {
  isSubmitting: boolean;
  errors: Record<string, string>;
}

export interface ToastState {
  show: boolean;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration: number;
}