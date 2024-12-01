// src/auth/services/authService.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class AuthService {
  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    this.setupAuthInterceptor();
  }

  async validateSession() {
    try {
      const response = await this.api.get('/auth/session');
      return response.data;
    } catch (error) {
      // Don't attempt refresh on initial session validation
      return null;
    }
  }

  async refreshToken() {
    try {
      const response = await this.api.post('/auth/refresh');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async logout() {
    try {
      await this.api.post('/auth/logout');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      // Always redirect to login
      window.location.href = '/login';
    }
  }

  loginAsUser() {
    console.log('Redirecting to:', `${API_URL}/auth/user/google/url`)
    window.location.href = `${API_URL}/auth/user/google/url`;
  }

  loginAsExpert() {
    window.location.href = `${API_URL}/auth/expert/linkedin/url`;
  }

  setupAuthInterceptor() {
    let isRefreshing = false;
    let failedQueue = [];

    const processQueue = (error, token = null) => {
      failedQueue.forEach(prom => {
        if (error) {
          prom.reject(error);
        } else {
          prom.resolve(token);
        }
      });
      failedQueue = [];
    };

    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Only retry once and only for 401 errors
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            });
          }

          originalRequest._retry = true;
          isRefreshing = true;

          try {
            await this.refreshToken();
            processQueue(null);
            isRefreshing = false;
            // Retry the original request
            return this.api(originalRequest);
          } catch (refreshError) {
            processQueue(refreshError, null);
            isRefreshing = false;
            // If refresh fails, redirect to login
            await this.logout();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }
}

const authService = new AuthService();
export default authService;
