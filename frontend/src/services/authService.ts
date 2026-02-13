import { User, LoginCredentials, RegisterCredentials } from '@/types/User';

class AuthService {
  private user: User | null = null;
  private apiUrl: string = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://mahmedmumair-phase3.hf.space';

  constructor() {
    // Check if user is already logged in from previous session
    const storedUser = typeof window !== 'undefined' ? localStorage.getItem('user') : null;
    if (storedUser) {
      this.user = JSON.parse(storedUser);
    }
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.apiUrl}/api/v1${endpoint}`;

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

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `API request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Auth API request error:', error);
      throw error;
    }
  }

  async login(credentials: LoginCredentials): Promise<{ success: boolean; user?: User; message?: string }> {
    try {
      // Call backend login API
      const response = await this.request('/login', {
        method: 'POST',
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      });

      if (response.token) {
        // Create our User object from the response
        const user: User = {
          id: response.id,
          email: response.email,
          name: response.name,
          isLoggedIn: true,
          jwtToken: response.token,
          refreshToken: ''
        };

        // Store user and token in localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem('user', JSON.stringify(user));
          localStorage.setItem('user_id', user.id); // Store user ID for API calls
          localStorage.setItem('jwt_token', user.jwtToken || '');

          // Dispatch storage event to notify other tabs/components
          window.dispatchEvent(new StorageEvent('storage', {
            key: 'user',
            newValue: JSON.stringify(user),
            oldValue: null,
            url: window.location.href
          }));
        }

        this.user = user;

        return {
          success: true,
          user: user,
          message: 'Login successful'
        };
      } else {
        return {
          success: false,
          message: 'Login failed - no token received'
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Login failed. Please check your credentials.'
      };
    }
  }

  async register(credentials: RegisterCredentials): Promise<{ success: boolean; user?: User; message?: string }> {
    try {
      // Call backend register API
      const response = await this.request('/register', {
        method: 'POST',
        body: JSON.stringify({
          email: credentials.email,
          name: credentials.name,
          password: credentials.password,
          confirm_password: credentials.password, // Assuming same password for confirmation
        }),
      });

      if (response.token) {
        // Create our User object from the response
        const user: User = {
          id: response.id,
          email: response.email,
          name: response.name,
          isLoggedIn: true,
          jwtToken: response.token,
          refreshToken: ''
        };

        // Store user and token in localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem('user', JSON.stringify(user));
          localStorage.setItem('user_id', user.id); // Store user ID for API calls
          localStorage.setItem('jwt_token', user.jwtToken || '');

          // Dispatch storage event to notify other tabs/components
          window.dispatchEvent(new StorageEvent('storage', {
            key: 'user',
            newValue: JSON.stringify(user),
            oldValue: null,
            url: window.location.href
          }));
        }

        this.user = user;

        return {
          success: true,
          user: user,
          message: 'Registration successful'
        };
      } else {
        return {
          success: false,
          message: 'Registration failed - no token received'
        };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Registration failed. Please try again.'
      };
    }
  }

  async logout(): Promise<{ success: boolean; message?: string }> {
    try {
      // Clear user data from localStorage
      let oldUser = null;
      if (typeof window !== 'undefined') {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          oldUser = storedUser;
        }
        localStorage.removeItem('user');
        localStorage.removeItem('user_id');
        localStorage.removeItem('jwt_token');

        // Dispatch storage event to notify other tabs/components
        window.dispatchEvent(new StorageEvent('storage', {
          key: 'user',
          newValue: null,
          oldValue: oldUser || null,
          url: window.location.href
        }));
      }

      this.user = null;

      return {
        success: true,
        message: 'Logged out successfully'
      };
    } catch (error) {
      console.error('Logout error:', error);
      return {
        success: false,
        message: 'Logout failed'
      };
    }
  }

  getCurrentUser(): User | null {
    return this.user;
  }

  isAuthenticated(): boolean {
    return this.user?.isLoggedIn ?? false;
  }

  // Method to refresh token if needed
  async refreshToken(): Promise<boolean> {
    try {
      // For this implementation, we'll check if the token exists and is valid
      // In a real implementation, you might have a refresh endpoint
      const token = typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null;

      if (token) {
        // We could make a request to a refresh endpoint here
        // For now, just return true if token exists
        return true;
      }
      return false;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  }
}

export const authService = new AuthService();