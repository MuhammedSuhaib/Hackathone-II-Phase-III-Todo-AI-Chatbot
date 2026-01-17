'use client';

import React, { useState } from 'react';
import { Task } from '@/types/Task';
import Button from '../UI/Button';
import Modal from '../UI/Modal';

interface TaskCardProps {
  task: Task;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onToggleComplete, onDelete, onEdit }) => {
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const handleToggleComplete = () => {
    onToggleComplete(task.id);
  };

  const handleDeleteClick = () => {
    setShowConfirmDialog(true);
  };

  const handleConfirmDelete = () => {
    onDelete(task.id);
    setShowConfirmDialog(false);
  };

  const handleCancelDelete = () => {
    setShowConfirmDialog(false);
  };

  const handleEdit = () => {
    onEdit(task);
  };

  // Determine priority color
  const priorityColors = {
    low: 'border-l-green-500',
    medium: 'border-l-yellow-500',
    high: 'border-l-red-500',
  };

  return (
    <>
      <div
        className={`relative bg-white rounded-xl shadow-sm p-5 mb-4 border-l-4 ${priorityColors[task.priority || 'low']} transition-all duration-300 hover:shadow-md ${
          task.completed ? 'opacity-80 bg-gray-50' : 'opacity-100'
        }`}
      >
        <div className="flex items-start">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggleComplete}
            className="mt-1 h-6 w-6 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
            aria-label={`Mark task "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
          />
          <div className="ml-4 flex-1 min-w-0">
            <h3
              className={`text-lg font-semibold ${
                task.completed ? 'line-through text-gray-600' : 'text-gray-900'
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p className={`mt-2 text-base ${
                task.completed ? 'line-through text-gray-500' : 'text-gray-600'
              }`}>
                {task.description}
              </p>
            )}
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                task.priority === 'high'
                  ? 'bg-red-100 text-red-800'
                  : task.priority === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
              }`}>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
                </svg>
                {(task.priority ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) : 'No')} priority
              </span>
              <span className="inline-flex items-center text-sm text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {new Date(task.createdAt).toLocaleDateString()}
              </span>
              {task.completed && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Completed
                </span>
              )}
            </div>
          </div>
          <div className="ml-4 flex space-x-2">
            <Button
              variant="outline"
              size="md"
              onClick={handleEdit}
              aria-label={`Edit task "${task.title}"`}
              className="p-2.5 min-w-[36px]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </Button>
            <Button
              variant="outline-danger"
              size="md"
              onClick={handleDeleteClick}
              aria-label={`Delete task "${task.title}"`}
              className="p-2.5 min-w-[36px]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </Button>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <Modal
        isOpen={showConfirmDialog}
        onClose={handleCancelDelete}
        title="Confirm Deletion"
      >
        <div className="mt-2">
          <div className="flex items-center mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900">Are you sure?</h3>
          </div>
          <p className="text-gray-700 mb-1">
            Are you sure you want to delete the task <strong>"{task.title}"</strong>?
          </p>
          <p className="text-gray-500 text-sm">
            This action cannot be undone.
          </p>
        </div>

        <div className="mt-6 flex justify-end space-x-3">
          <Button
            variant="secondary"
            onClick={handleCancelDelete}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleConfirmDelete}
          >
            Delete Task
          </Button>
        </div>
      </Modal>
    </>
  );
};

export default TaskCard;