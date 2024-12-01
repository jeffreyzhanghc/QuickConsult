import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/context/AuthContext';
import authService from '../../auth/services/authService';
import { PlusCircle, Loader2,ArrowLeft } from 'lucide-react';

export default function SessionList() {
  const [activeSessions, setActiveSessions] = useState([]);
  const [completedSessions, setCompletedSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const [activeRes, completedRes] = await Promise.all([
          authService.api.get('/sessions/my/active'),
          authService.api.get('/sessions/my/completed')
        ]);
        setActiveSessions(activeRes.data);
        setCompletedSessions(completedRes.data);
      } catch (error) {
        setError('Failed to load sessions');
        console.error('Error fetching sessions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  const createNewSession = async () => {
    try {
      const response = await authService.api.post('/sessions');
      navigate(`/sessions/${response.data.id}`);
    } catch (error) {
      setError('Failed to create new session');
      console.error('Error creating session:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="flex items-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading sessions...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-6">
    {/* Navigation */}
    <nav className="bg-white/80 backdrop-blur-md border-b border-neutral-200/50 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/')}
              className="px-3 py-1.5 text-sm rounded-md border border-neutral-200 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50 transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </nav>
      <div className="max-w-3xl mx-auto">
        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold">Sessions</h1>
          <button
            onClick={createNewSession}
            className="flex items-center gap-2 px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors"
          >
            <PlusCircle className="w-5 h-5" />
            New Session
          </button>
        </div>

        {activeSessions.length > 0 && (
          <>
            <h2 className="text-lg font-medium mb-3">Active Sessions</h2>
            <div className="grid gap-4 mb-8">
              {activeSessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => navigate(`/sessions/${session.id}`)}
                  className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200 cursor-pointer hover:border-rose-500 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">Chat Session</div>
                      <div className="text-sm text-neutral-600">
                        Started {new Date(session.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="text-sm text-neutral-600">
                      {session.messages?.length || 0} messages
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {completedSessions.length > 0 && (
          <>
            <h2 className="text-lg font-medium mb-3">Completed Sessions</h2>
            <div className="grid gap-4">
              {completedSessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => navigate(`/sessions/${session.id}`)}
                  className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200 cursor-pointer hover:border-rose-500 transition-colors opacity-75"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">Chat Session (Completed)</div>
                      <div className="text-sm text-neutral-600">
                        {new Date(session.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="text-sm text-neutral-600">
                      {session.messages?.length || 0} messages
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {activeSessions.length === 0 && completedSessions.length === 0 && (
          <div className="text-center py-12">
            <p className="text-neutral-600">No sessions yet. Start a new chat session!</p>
          </div>
        )}
      </div>
    </div>
  );
}