import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useUser } from '@/context/UserContext';
import Button from '../UI/Button';
import useNotifications from '../hooks/useNotifications';

const Header: React.FC = () => {
  const { user, logout } = useUser();
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  // Use notifications hook to get dynamic notifications
  const { notifications, unreadCount, loading, error, fetchNotifications, markAllAsRead } = useNotifications();

  const handleLogout = async () => {
    await logout();
    // Redirect to login page after logout
    router.push('/login');
    router.refresh(); // Refresh to update the UI after logout
    setDropdownOpen(false); // Close dropdown after logout
  };

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  return (
    <header className="bg-white shadow">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-3xl font-bold tracking-tight text-gray-900 hover:text-indigo-700 transition-colors">
            Todo App
          </Link>

          <div className="flex items-center space-x-4">
            {user ? (
              // User is logged in - show user menu and logout button
              <>
                <div className="relative">
                  <button
                    onClick={() => setNotificationsOpen(!notificationsOpen)}
                    className="rounded-full bg-gray-200 p-2 text-gray-700 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 relative"
                  >
                    <span className="sr-only">View notifications</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    {/* Notification badge - showing actual unread count */}
                    {unreadCount > 0 && (
                      <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
                        {unreadCount}
                      </span>
                    )}
                  </button>

                  {/* Notifications dropdown menu */}
                  {notificationsOpen && (
                    <div className="absolute right-0 mt-2 w-80 max-w-xs bg-white rounded-md shadow-lg py-1 z-10 ring-1 ring-black ring-opacity-5">
                      <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                        <p className="text-sm font-medium text-gray-900">Notifications</p>
                        {unreadCount > 0 && (
                          <button
                            onClick={markAllAsRead}
                            className="text-xs text-indigo-600 hover:text-indigo-900"
                          >
                            Mark all as read
                          </button>
                        )}
                      </div>
                      <div className="max-h-96 overflow-y-auto">
                        {loading ? (
                          <div className="px-4 py-6 text-center">
                            <svg className="animate-spin h-5 w-5 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <p className="mt-2 text-sm text-gray-500">Loading notifications...</p>
                          </div>
                        ) : error ? (
                          <div className="px-4 py-6 text-center">
                            <svg className="h-12 w-12 text-red-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <p className="mt-2 text-sm text-red-600">Error loading notifications</p>
                            <button
                              onClick={fetchNotifications}
                              className="mt-2 text-sm text-indigo-600 hover:text-indigo-900 font-medium"
                            >
                              Retry
                            </button>
                          </div>
                        ) : notifications.length === 0 ? (
                          <div className="px-4 py-6 text-center">
                            <svg className="h-12 w-12 text-gray-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                            </svg>
                            <p className="mt-2 text-sm text-gray-500">No new notifications</p>
                          </div>
                        ) : (
                          notifications.map((notification) => (
                            <a
                              key={notification.id}
                              href="#"
                              className={`block px-4 py-3 text-sm hover:bg-gray-50 ${!notification.read ? 'bg-blue-50' : 'bg-white'}`}
                            >
                              <div className="flex justify-between">
                                <p className={`font-medium ${!notification.read ? 'text-indigo-700' : 'text-gray-900'}`}>
                                  {notification.title}
                                </p>
                                {!notification.read && (
                                  <span className="inline-block w-2 h-2 rounded-full bg-indigo-500"></span>
                                )}
                              </div>
                              <p className="mt-1 text-gray-700 truncate">{notification.message}</p>
                              <p className="mt-1 text-xs text-gray-500">
                                {new Date(notification.timestamp).toLocaleString()}
                              </p>
                            </a>
                          ))
                        )}
                      </div>
                      <div className="px-4 py-2 border-t border-gray-200 text-center">
                        <a href="#" className="text-sm font-medium text-indigo-600 hover:text-indigo-900">
                          View all
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Click outside to close notifications dropdown */}
                  {notificationsOpen && (
                    <div
                      className="fixed inset-0 z-9 h-full w-full"
                      onClick={() => setNotificationsOpen(false)}
                    ></div>
                  )}
                </div>
                <div className="relative ml-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-700 hidden md:block">
                      {user.name || user.email}
                    </span>
                    <div className="relative">
                      <button
                        onClick={toggleDropdown}
                        className="flex rounded-full bg-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                      >
                        <span className="sr-only">Open user menu</span>
                        <div className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center">
                          <span className="text-white font-medium text-sm">
                            {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      </button>

                      {/* Dropdown menu - now controlled by state instead of hover */}
                      {dropdownOpen && (
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 ring-1 ring-black ring-opacity-5">
                          <div className="px-4 py-2 border-b border-gray-200">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {user.name || user.email}
                            </p>
                            <p className="text-xs text-gray-500 truncate">
                              {user.email}
                            </p>
                          </div>
                          <button
                            onClick={handleLogout}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            Sign out
                          </button>
                        </div>
                      )}

                      {/* Click outside to close dropdown */}
                      {dropdownOpen && (
                        <div
                          className="fixed inset-0 z-9 h-full w-full"
                          onClick={() => setDropdownOpen(false)}
                        ></div>
                      )}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              // User is not logged in - show login/signup buttons
              <div className="flex items-center space-x-3">
                <Link href="/login">
                  <Button variant="outline" className="px-4 py-2">
                    Sign In
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button variant="primary" className="px-4 py-2">
                    Sign Up
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;