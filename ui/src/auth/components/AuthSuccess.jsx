// src/auth/components/AuthSuccess.jsx
import React, { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const AuthSuccess = () => {
  const { checkAuth } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const authenticate = async () => {
      try {
        await checkAuth();
        navigate('/home');
      } catch (error) {
        console.error('Authentication failed:', error);
        navigate('/login');
      }
    };
    authenticate();
  }, [checkAuth, navigate]);

  return <div>Authenticating...</div>;
};

export default AuthSuccess;
