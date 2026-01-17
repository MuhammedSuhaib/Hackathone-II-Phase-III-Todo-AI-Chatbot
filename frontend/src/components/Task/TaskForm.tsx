'use client';

import React, { useState, useEffect } from 'react';
import { Task, TaskFormData } from '@/types/Task';
import { validateTask } from '../utils/validation';
import Input from '../UI/Input';
import Button from '../UI/Button';

interface TaskFormProps {
  initialData?: Partial<Task> | TaskFormData;
  onSubmit: (taskData: TaskFormData) => void;
  onCancel?: () => void;
  submitText?: string;
}

const TaskForm: React.FC<TaskFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  submitText = 'Add Task'
}) => {
  const getDefaultInitialData = (): TaskFormData => ({
    title: '',
    description: '',
    priority: 'medium',
    ...initialData
  });

  const [formData, setFormData] = useState<TaskFormData>(() => {
    return getDefaultInitialData();
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setFormData({
      title: initialData?.title || '',
      description: initialData?.description || '',
      priority: initialData?.priority || 'medium'
    });
    setErrors({});
  }, [initialData?.title, initialData?.description, initialData?.priority]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    const validationErrors = validateTask(formData.title, formData.description, formData.priority);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length === 0) {
      setIsSubmitting(true);
      try {
        await onSubmit(formData);
        // Reset form after successful submission
        if (!(initialData as any)?.id) { // Only reset for new tasks, not updates
          setFormData({ title: '', description: '', priority: 'medium' });
        }
      } catch (error) {
        console.error('Error submitting task:', error);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
          Task Title *
        </label>
        <Input
          id="title"
          name="title"
          label=""
          value={formData.title}
          onChange={handleChange}
          required
          error={errors.title}
          placeholder="Enter task title"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        />
        {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={4}
          className="block w-full px-4 py-3 rounded-lg border border-gray-300 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Enter task description (optional)"
        />
        {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-semibold text-gray-700 mb-2">
          Priority *
        </label>
        <select
          id="priority"
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className="block w-full px-4 py-3 rounded-lg border border-gray-300 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          required
        >
          <option value="low">Low Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="high">High Priority</option>
        </select>
        {errors.priority && <p className="mt-1 text-sm text-red-600">{errors.priority}</p>}
      </div>

      <div className="flex space-x-4 pt-2">
        <Button
          type="submit"
          isLoading={isSubmitting}
          disabled={isSubmitting}
          className="flex-1 py-3 px-4 text-base font-medium"
        >
          <span className="flex items-center justify-center">
            {isSubmitting ? (
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
            {submitText}
          </span>
        </Button>

        {onCancel && (
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isSubmitting}
            className="py-3 px-4 text-base font-medium"
          >
            <span className="flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Cancel
            </span>
          </Button>
        )}
      </div>
    </form>
  );
};

export default TaskForm;