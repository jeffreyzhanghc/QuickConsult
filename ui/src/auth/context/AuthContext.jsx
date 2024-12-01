import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Public paths that don't require authentication
  const publicPaths = ['/login', '/auth/error', '/auth/success'];

  const checkAuth = useCallback(async (force = false) => {
    // Skip auth check for public paths unless forced
    if (!force && publicPaths.includes(location.pathname)) {
      setLoading(false);
      return;
    }

    try {
      setError(null);
      const userData = await authService.validateSession();

      if (userData) {
        setUser(userData);
      } else if (!publicPaths.includes(location.pathname)) {
        // Clear user data if validation fails
        setUser(null);
        navigate('/login', { 
          state: { from: location.pathname },
          replace: true 
        });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setError('Authentication check failed');
      setUser(null);
      
      if (!publicPaths.includes(location.pathname)) {
        navigate('/login', { 
          state: { from: location.pathname },
          replace: true 
        });
      }
    } finally {
      setLoading(false);
    }
  }, [location.pathname, navigate]);

  // Initial auth check
  useEffect(() => {
    checkAuth();
  }, []);

  // Path change handler with debounce
  useEffect(() => {
    let timeoutId;
    
    const handlePathChange = () => {
      // Skip immediate check for public paths
      if (publicPaths.includes(location.pathname)) {
        setLoading(false);
        return;
      }

      setLoading(true);
      // Debounce the auth check to prevent multiple rapid checks
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        checkAuth();
      }, 100);
    };

    handlePathChange();

    return () => {
      clearTimeout(timeoutId);
    };
  }, [location.pathname, checkAuth]);

  const loginAsUser = () => {
    authService.loginAsUser();
  };

  const loginAsExpert = () => {
    authService.loginAsExpert();
  };

  const logout = async () => {
    try {
      setLoading(true);
      setError(null);
      await authService.logout();
      setUser(null);
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Logout failed:', error);
      setError('Logout failed');
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  const value = {
    user,
    loading,
    error,
    loginAsUser,
    loginAsExpert,
    logout,
    checkAuth,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {loading && !publicPaths.includes(location.pathname) ? (
        <div>Loading...</div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const RequireAuth = ({ children }) => {
  const { user, loading, checkAuth } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) {
      // Force an auth check when RequireAuth mounts
      checkAuth(true).catch(() => {
        navigate('/login', { 
          state: { from: location.pathname },
          replace: true 
        });
      });
    }
  }, [user, loading, checkAuth, navigate, location.pathname]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return user ? children : null;
};

export default AuthContext;