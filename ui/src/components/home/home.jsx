import React, { useState, useEffect } from 'react';
import { useAuth } from '../../auth/context/AuthContext';
import { Search, Brain, MessageSquare, Users, LogOut, Sparkles } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import authService from '../../auth/services/authService';

const Home = () => {
  const { user, logout } = useAuth();
  const [question, setQuestion] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const [recentSessions, setRecentSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchRecentSessions = async () => {
      try {
        const response = await authService.api.get('/sessions/my/active', {
          params: {
            limit: 3  // Get 3 most recent active sessions
          }
        });
        setRecentSessions(response.data);
      } catch (error) {
        console.error('Error fetching recent sessions:', error);
      } finally {
        setIsLoading(false);
      }
    };
  
    fetchRecentSessions();
  }, []);

  const recentQuestions = [
    { id: 1, title: "Sample Question Title 1", status: "In Progress", date: "2024-03-20" },
    { id: 2, title: "Sample Question Title 2", status: "In Progress", date: "2024-03-19" },
    { id: 3, title: "Sample Question Title 3", status: "Completed", date: "2024-03-18" },
  ];

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsSubmitting(true);
    try {
      // Navigate to analysis page with the question
      navigate('/question/analyze', {
        state: { question: question.trim() }
      });
    } catch (error) {
      console.error('Error submitting question:', error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-neutral-50 to-amber-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-neutral-200/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-neutral-800" />
              <span className="text-xl font-bold text-neutral-800">QuickConsult</span>
            </div>
            
            <div className="flex items-center space-x-6">
              {/* Main Nav Items 
              <button 
                className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
                onClick={() => window.location.href='/experts'}
              >
                <Users className="w-5 h-5" />
                <span>Expert Library</span>
              </button>
              <button 
                className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
                onClick={() => window.location.href='/history'}
              >
                <MessageSquare className="w-5 h-5" />
                <span>All Questions</span>
              </button>
              */}

              {/* User Section */}
              <div className="h-6 w-px bg-neutral-200"></div>
              <div className="flex items-center gap-4">
                <span className="text-neutral-600">
                  {user?.email}
                </span>
                <button
                  onClick={logout}
                  className="text-neutral-600 hover:text-neutral-900 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4">
        {/* Hero Section with Search */}
        <div className="text-center mt-32 mb-16">
          <h1 className="text-4xl font-bold text-neutral-900 mb-4">
            Ask Your Business Question
          </h1>
          <p className="text-neutral-600 text-lg mb-8">
            Get matched with verified experts using our AI-powered platform
          </p>
          
          {/* Question Form */}
          <form onSubmit={handleQuestionSubmit}>
            <div className="space-y-4">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Type your business question..."
                className="w-full px-6 py-4 text-lg border-2 border-neutral-200 rounded-2xl focus:border-rose-400 focus:outline-none shadow-sm bg-white/80 backdrop-blur-sm min-h-[120px] resize-none"
              />
              <button
                type="submit"
                disabled={isSubmitting || !question.trim()}
                className="bg-rose-500 hover:bg-rose-600 text-white px-8 py-3 rounded-xl transition-colors disabled:opacity-50 flex items-center gap-2 mx-auto"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Ask Question</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        <div className="mt-16">
  <div className="flex justify-between items-center mb-4">
    <h2 className="text-xl font-semibold text-neutral-900">Active Sessions</h2>
    <Link 
      to="/sessions"
      className="text-rose-500 hover:text-rose-600 text-sm font-medium"
    >
      View All
    </Link>
  </div>
  <div className="space-y-3">
    {isLoading ? (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-rose-500 mx-auto"></div>
      </div>
    ) : recentSessions.length > 0 ? (
      recentSessions.map((session) => (
        <Link
          key={session.id}
          to={`/sessions/${session.id}`}
          className="block bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-neutral-200/50 hover:border-rose-200 transition-all duration-300"
        >
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-medium text-neutral-800">
                Session with {session.expert_name}
              </h3>
              {session.messages?.length > 0 && (
                <p className="text-neutral-600 text-sm mt-1">
                  {session.messages[session.messages.length - 1].content.substring(0, 100)}
                  {session.messages[session.messages.length - 1].content.length > 100 ? '...' : ''}
                </p>
              )}
              <p className="text-neutral-500 text-sm mt-2">
                Started {new Date(session.created_at).toLocaleString()}
              </p>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Active
            </span>
          </div>
        </Link>
      ))
    ) : (
      <div className="text-center py-8 text-neutral-600">
        No active sessions
      </div>
    )}
  </div>
</div>
      </main>
    </div>
  );
};

export default Home;