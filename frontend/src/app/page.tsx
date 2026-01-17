'use client';

import React, { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/Layout/DashboardLayout';
import TaskList from '@/components/Task/TaskList';
import TaskForm from '@/components/Task/TaskForm';
import TaskFilters from '@/components/Task/TaskFilters';
import Button from '@/components/UI/Button';
import useTasks from '@/components/hooks/useTasks';
import Toast from '@/components/UI/Toast';
import { TaskFormData, FilterState } from '@/types/Task';
import { useUser } from '@/context/UserContext';

const Dashboard: React.FC = () => {
  const { tasks, loading, error, createTask, updateTask, toggleTaskCompletion, deleteTask, fetchTasks } = useTasks();
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<any>(null);
  const [filterState, setFilterState] = useState<FilterState>({
    statusFilter: 'all',
    priorityFilter: 'all',
    searchQuery: '',
  });
  const [toast, setToast] = useState({
    show: false,
    message: '',
    type: 'success' as 'success' | 'error' | 'info' | 'warning',
  });

  const handleCreateTask = async (taskData: TaskFormData) => {
    if (editingTask) {
      // Update existing task
      const result = await updateTask(editingTask.id, taskData);
      if (result) {
        setEditingTask(null);
        setShowForm(false);
        setToast({
          show: true,
          message: 'Task updated successfully!',
          type: 'success',
        });
      }
    } else {
      // Create new task
      const result = await createTask(taskData);
      if (result) {
        setShowForm(false);
        setToast({
          show: true,
          message: 'Task created successfully!',
          type: 'success',
        });
      }
    }
  };

  const handleToggleComplete = async (id: string) => {
    await toggleTaskCompletion(id);
  };

  const handleDeleteTask = async (id: string) => {
    await deleteTask(id);
  };

  const handleEditTask = (task: any) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleFilterChange = (filters: Partial<FilterState>) => {
    setFilterState(prev => ({
      ...prev,
      ...filters
    }));
  };

  const handleClearFilters = () => {
    setFilterState({
      statusFilter: 'all',
      priorityFilter: 'all',
      searchQuery: '',
    });
  };

  const handleToastClose = () => {
    setToast({ ...toast, show: false });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <Head>
        <title>Todo Dashboard</title>
        <meta name="description" content="Manage your tasks efficiently" />
      </Head>

      <DashboardLayout title="Task Dashboard">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
            <Button
              variant="primary"
              size="lg"
              onClick={() => setShowForm(!showForm)}
              className="px-6 py-3 text-base font-medium"
            >
              <span className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                {showForm ? 'Cancel' : 'Add New Task'}
              </span>
            </Button>
          </div>

          {showForm && (
            <div className="mb-8 bg-white p-8 rounded-xl shadow-lg border border-gray-200 transition-all duration-300">
              <div className="flex items-center mb-6 pb-4 border-b border-gray-200">
                <h3 className="text-2xl font-bold text-gray-800 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-3 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  {editingTask ? 'Edit Task' : 'Create New Task'}
                </h3>
              </div>
              <TaskForm
                initialData={editingTask}
                onSubmit={handleCreateTask}
                onCancel={() => {
                  setShowForm(false);
                  setEditingTask(null);
                }}
                submitText={editingTask ? 'Update Task' : 'Create Task'}
              />
            </div>
          )}

          <TaskFilters
            filterState={filterState}
            onFilterChange={handleFilterChange}
            onClearFilters={handleClearFilters}
          />

          <div className="bg-white shadow-lg rounded-xl p-6 border border-gray-200">
            <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
              <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-3 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Your Tasks
                <span className="ml-3 bg-indigo-100 text-indigo-800 text-sm font-medium px-3 py-1 rounded-full">
                  {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
                </span>
              </h2>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            )}

            <TaskList
              tasks={tasks}
              loading={loading}
              emptyMessage={
                <div className="text-center py-12">
                  <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
                  <p className="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
                  <div className="mt-6">
                    <Button
                      variant="primary"
                      onClick={() => setShowForm(true)}
                    >
                      Create New Task
                    </Button>
                  </div>
                </div>
              }
              statusFilter={filterState.statusFilter}
              priorityFilter={filterState.priorityFilter}
              searchQuery={filterState.searchQuery}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDeleteTask}
              onEdit={handleEditTask}
            />
          </div>
        </div>
      </DashboardLayout>

      <Toast
        show={toast.show}
        message={toast.message}
        type={toast.type}
        onClose={handleToastClose}
      />
    </div>
  );
};

export default Dashboard;