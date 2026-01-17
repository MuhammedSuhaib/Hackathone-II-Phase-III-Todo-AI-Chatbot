import { useState, useEffect } from 'react';
import { Task } from '@/types/Task';
import { apiClient } from '@/services/apiClient';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'task-completed' | 'task-created' | 'deadline-approaching' | 'task-overdue' | 'comment-added';
  timestamp: string;
  read: boolean;
}

const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get user ID from localStorage
      const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') : null;
      if (!userId) {
        setError('User not authenticated. Please log in to access notifications.');
        setLoading(false);
        return [];
      }

      // Fetch user's tasks
      const response = await apiClient.getAllTasks();

      if (response.success && response.data) {
        const tasks = response.data as Task[];
        const newNotifications: Notification[] = [];

        // Generate notifications based on tasks
        tasks.forEach((task: Task) => {
          // Task completed notification
          if (task.completed) {
            newNotifications.push({
              id: `completed-${task.id}`,
              title: 'Task Completed',
              message: `Your task "${task.title}" has been marked as complete`,
              type: 'task-completed',
              timestamp: task.updatedAt || task.createdAt,
              read: false
            });
          }

          // Deadline approaching notification (for high priority tasks)
          if (task.priority === 'high') {
            // In a real app, we'd check if the task has a deadline approaching
            newNotifications.push({
              id: `deadline-${task.id}`,
              title: 'High Priority Task',
              message: `Your high priority task "${task.title}" requires attention`,
              type: 'deadline-approaching',
              timestamp: task.createdAt,
              read: false
            });
          }
        });

        // Sort notifications by timestamp (newest first)
        newNotifications.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

        // Limit to the 5 most recent notifications
        setNotifications(newNotifications.slice(0, 5));
      } else {
        setError(response.message || 'Failed to fetch notifications');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Mark a notification as read
  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  // Mark all notifications as read
  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  };

  // Refresh notifications
  const refreshNotifications = () => {
    fetchNotifications();
  };

  // Fetch notifications when the hook is initialized
  useEffect(() => {
    fetchNotifications();

    // Refresh notifications every 5 minutes
    const interval = setInterval(fetchNotifications, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  // Count unread notifications
  const unreadCount = notifications.filter(n => !n.read).length;

  return {
    notifications,
    unreadCount,
    loading,
    error,
    fetchNotifications,
    markAsRead,
    markAllAsRead
  };
};

export default useNotifications;