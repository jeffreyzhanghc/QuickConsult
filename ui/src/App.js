// src/App.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, RequireAuth } from './auth/context/AuthContext';
import LoginPage from './auth/components/LoginPage';
import AuthSuccess from './auth/components/AuthSuccess';
import Home from './components/home/home';
import QuestionAnalysis from './components/question/QuestionAnalysis';
import QuestionMatches from './components/question/QuestionMatches';
import ChatSession from './components/session/SessionChat';
import SessionList from './components/session/SessionList';

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/success" element={<AuthSuccess />} />

        {/* Protected routes */}
        <Route path="/" element={<RequireAuth><Navigate to="/home" replace /></RequireAuth>} />
        <Route path="/home" element={<RequireAuth><Home /></RequireAuth>} />
        
        {/* Question flow */}
        <Route path="/question/analyze" element={<RequireAuth><QuestionAnalysis /></RequireAuth>} />
        <Route path="/questions/matches" element={<RequireAuth><QuestionMatches /></RequireAuth>} />
        {/* Session routes */}
        <Route path="/sessions" element={<RequireAuth><SessionList /></RequireAuth>} />
        <Route path="/sessions/:sessionId" element={<RequireAuth><ChatSession /></RequireAuth>} />
      </Routes>
    </AuthProvider>
  );
}

export default App;