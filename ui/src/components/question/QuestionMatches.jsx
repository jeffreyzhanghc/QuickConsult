import React, { useState, useEffect} from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Brain, 
  ArrowLeft, 
  LogOut, 
  X, 
  MessageSquare, 
  Star, 
  Clock
} from 'lucide-react';
import { useAuth } from '../../auth/context/AuthContext';
import authService from '../../auth/services/authService';

// Expert details panel component
const ExpertPanel = ({ expert, question, onClose, onStartSession }) => {
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [testExperts, setTestExperts] = useState([]);

  useEffect(() => {
    // Fetch test experts when component mounts
    const fetchTestExperts = async () => {
      try {
        const response = await authService.api.get('/experts/test-experts');
        setTestExperts(response.data);
        console.log('Test experts:', response.data);
      } catch (error) {
        console.error('Error fetching test experts:', error);
      }
    };
  
    fetchTestExperts();
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const testExpert = testExperts[Math.floor(Math.random() * testExperts.length)];
      
      if (!testExpert) {
        throw new Error('No test experts available');
      }

      console.log('Creating session with expert:', testExpert);

      const response = await authService.api.post('/sessions', {
        expert_id: testExpert.id,
        initial_message: message
      });

      console.log('Session created:', response.data);
      
      // Check if we have a valid ID in response
      const sessionId = response.data.id; // Changed from session_id to id
      if (!sessionId) {
        throw new Error('No session ID received');
      }

      onStartSession(sessionId);
    } catch (error) {
      console.error('Session creation error:', error);
      setError('Failed to create session. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
};

  return (
    <div className="fixed inset-y-0 right-0 w-[480px] bg-white shadow-xl border-l border-neutral-200">
      <div className="h-full flex flex-col">
        <div className="p-6 border-b border-neutral-200">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold">Expert Profile</h3>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-neutral-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-neutral-500" />
            </button>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center text-rose-600 text-xl font-semibold">
              {expert.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div>
              <h4 className="text-lg font-medium">{expert.name}</h4>
              <p className="text-neutral-600">{expert.expertise}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-400" />
              <span>{expert.rating} Rating</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{expert.responseTime}</span>
            </div>
            <div className="flex items-center gap-2">
              <span>{expert.totalSessions} Sessions</span>
            </div>
            <div className="flex items-center gap-2">
              <span>{expert.hourlyRate}</span>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            <div>
              <h5 className="font-medium mb-2">Areas of Expertise</h5>
              <div className="flex flex-wrap gap-2">
                {expert.expertiseAreas?.map((area, index) => (
                  <span 
                    key={index}
                    className="px-3 py-1 bg-rose-50 text-rose-600 rounded-full text-sm"
                  >
                    {area}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-neutral-200">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Your Question</label>
              <div className="p-3 bg-neutral-50 rounded-lg text-neutral-700">
                {question}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Additional Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full p-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-rose-500 focus:border-transparent"
                rows={4}
                placeholder="Add any specific details or context..."
                required
              />
            </div>

            {error && (
              <div className="text-sm text-red-600">{error}</div>
            )}

            <button
              type="submit"
              disabled={isSubmitting || !message.trim()}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-rose-500 text-white rounded-lg hover:bg-rose-600 disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? (
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
              ) : (
                <>
                  <MessageSquare className="w-4 h-4" />
                  Start Session
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Main component
export default function QuestionMatches() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const questions = location.state?.questions || [];
  const [selectedExpert, setSelectedExpert] = useState(null);
  const [selectedQuestion, setSelectedQuestion] = useState(null);

  // Default expert pool for MVP
  const defaultExperts = [
    {
      id: "exp1",
      name: "Emma Watson",
      expertise: "Operations Management",
      rating: 4.9,
      responseTime: "< 45 mins",
      hourlyRate: "$190/hr",
      totalSessions: 156,
      expertiseAreas: ["Market Analysis", "Growth Strategy", "Operations", "Business Planning"]
    },
    {
      id: "exp2",
      name: "David Kimawdawd",
      expertise: "Business Strategy",
      rating: 4.7,
      responseTime: "< 1 hour",
      hourlyRate: "$190/hr",
      totalSessions: 203,
      expertiseAreas: ["Market Analysis", "Growth Strategy", "Competitive Analysis", "Business Planning"]
    }
  ];

  // Add experts to each question
  const questionsWithExperts = questions.map(question => ({
    ...question,
    experts: defaultExperts
  }));

  const handleStartSession = (sessionId) => {
    navigate(`/sessions/${sessionId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-neutral-50 to-amber-50">
      <nav className="bg-white/80 backdrop-blur-md border-b border-neutral-200/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-neutral-800" />
              <span className="text-xl font-bold text-neutral-800">QuickConsult</span>
            </div>
            
            <div className="flex items-center space-x-6">
              <button
                onClick={() => navigate('/home')}
                className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Home
              </button>
              
              <div className="h-6 w-px bg-neutral-200"></div>
              <div className="flex items-center gap-4">
                <span className="text-neutral-600">{user?.email}</span>
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

      <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-semibold text-neutral-900">Expert Matches</h1>
        <p className="text-neutral-600 mt-2">Review your questions and matched experts</p>

        <div className="mt-8 space-y-6">
          {questionsWithExperts.map((question, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-sm border border-neutral-100">
              <div className="p-6">
                <h3 className="text-lg font-medium text-neutral-900 mb-6">
                  {question.title}
                </h3>

                <div className="space-y-4">
                  {question.experts?.map((expert, expertIndex) => (
                    <button
                      key={expertIndex}
                      onClick={() => {
                        setSelectedExpert(expert);
                        setSelectedQuestion(question.title);
                      }}
                      className="w-full flex items-start p-4 rounded-xl hover:bg-rose-50 transition-all text-left"
                    >
                      <div className="flex items-center gap-4 w-full">
                        <div className="w-12 h-12 bg-rose-100 rounded-full flex items-center justify-center text-rose-600 font-medium shrink-0">
                          {expert.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-neutral-900">{expert.name}</p>
                          <p className="text-sm text-neutral-600 mb-2">{expert.expertise}</p>
                          <div className="flex items-center gap-3 text-sm text-neutral-500">
                            <div className="flex items-center gap-1">
                              <Star className="w-3 h-3 text-yellow-400" />
                              <span>{expert.rating}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              <span>{expert.responseTime}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedExpert && (
        <ExpertPanel
          expert={selectedExpert}
          question={selectedQuestion}
          onClose={() => setSelectedExpert(null)}
          onStartSession={handleStartSession}
        />
      )}
    </div>
  );
}