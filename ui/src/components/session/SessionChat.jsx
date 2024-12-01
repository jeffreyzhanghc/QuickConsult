import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/context/AuthContext';
import authService from '../../auth/services/authService';
import { ArrowLeft, Send, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export default function SessionChat() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageContent, setMessageContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  
  const websocketRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Fetch session details
  useEffect(() => {
    const fetchSessionDetails = async () => {
      try {
        const response = await authService.api.get(`/sessions/${sessionId}`);
        setSession(response.data);
        setMessages(response.data.messages || []);
        if (response.data.status === 'completed') {
          setConnectionStatus('closed');
        }
      } catch (error) {
        console.error('Error fetching session:', error);
        setError('Unable to load session');
        navigate('/sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessionDetails();
  }, [sessionId, navigate]);

  // Setup WebSocket connection
  useEffect(() => {
    console.log('Session state:', session);
    console.log('Session status:', session?.status);
    if (!session || session.status === 'completed') {
      setConnectionStatus('closed');
      return;
    }

    const setupWebSocket = () => {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl = `${wsProtocol}://localhost:8000/api/v1/sessions/ws/${sessionId}`;
      console.log('Initializing WebSocket connection to:', wsUrl);

      try {
        const websocket = new WebSocket(wsUrl);
        websocketRef.current = websocket;

        websocket.onopen = () => {
          console.log('WebSocket connection opened successfully');
          setConnectionStatus('connected');
          setError(null);
        };

        websocket.onmessage = (event) => {
          console.log('WebSocket message received:', event.data);
          try {
            const data = JSON.parse(event.data);
            setMessages(prevMessages => [...prevMessages, data]);
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        websocket.onclose = (event) => {
          console.log('WebSocket connection closed:', { 
            code: event.code, 
            reason: event.reason,
            wasClean: event.wasClean 
          });
          switch (event.code) {
            case 4001:
              setError('Authentication failed');
              navigate('/login');
              break;
            case 4003:
              setError('Not authorized to access this session');
              navigate('/sessions');
              break;
            case 1000:
              setConnectionStatus('closed');
              break;
            default:
              if (session.status !== 'completed') {
                setConnectionStatus('disconnected');
                setError('Connection lost. Please refresh the page.');
                console.log('Attempting to reconnect...');
                setTimeout(setupWebSocket, 5000);
              }
          }
        };

        websocket.onerror = (error) => {
          console.error('WebSocket error occurred:', error);
          setConnectionStatus('error');
          setError('Connection error. Please check your internet connection.');
        };

      } catch (error) {
        console.error('Error setting up WebSocket:', error);
        setError('Failed to establish connection');
      }
    };

    console.log('Starting WebSocket setup...');
    setupWebSocket();

    return () => {
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        websocketRef.current.close(1000, 'Component unmounted');
      }
    };
  }, [session, sessionId, navigate]);

  const handleCloseSession = async () => {
    try {
      // 1. First close the WebSocket connection
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        websocketRef.current.close(1000, 'Session closed by user');
      }
      
      // 2. Immediately update local state to prevent reconnection
      setSession(prev => ({ ...prev, status: 'completed' }));
      setConnectionStatus('closed');
      
      // 3. Then make the API call to close the session
      await authService.api.post(`/sessions/${sessionId}/close`);
    } catch (error) {
      console.error('Error closing session:', error);
      setError('Failed to close session on server');
    }
  };

  const sendMessage = () => {
    if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
      setError('Connection lost. Trying to reconnect...');
      return;
    }

    if (messageContent.trim()) {
      try {
        websocketRef.current.send(JSON.stringify({
          content: messageContent.trim()
        }));
        setMessageContent('');
      } catch (error) {
        console.error('Error sending message:', error);
        setError('Failed to send message. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="flex items-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading session...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-neutral-50">
      <nav className="bg-white/80 backdrop-blur-md border-b border-neutral-200/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-3">
              {/* Back buttons group */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => navigate('/')}
                  className="px-3 py-1.5 text-sm rounded-md border border-neutral-200 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50 transition-colors flex items-center gap-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Home
                </button>
                <button
                  onClick={() => navigate('/sessions')}
                  className="px-3 py-1.5 text-sm rounded-md border border-neutral-200 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50 transition-colors flex items-center gap-2"
                >
                  Sessions
                </button>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Connection status */}
              {session?.status !== 'completed' && (
                <>
                  <span className={`text-sm flex items-center gap-1.5 ${
                    connectionStatus === 'connected' ? 'text-green-600' :
                    connectionStatus === 'connecting' ? 'text-amber-600' :
                    'text-red-600'
                  }`}>
                    <span className="w-2 h-2 rounded-full bg-current"></span>
                    {connectionStatus === 'connected' ? 'Connected' :
                     connectionStatus === 'connecting' ? 'Connecting...' :
                     'Disconnected'}
                  </span>
                  {/* End Session button */}
                  <button
                    onClick={handleCloseSession}
                    className="px-3 py-1.5 text-sm rounded-md bg-red-50 border border-red-200 text-red-600 hover:bg-red-100 transition-colors"
                  >
                    End Session
                  </button>
                </>
              )}
              {/* Expert name badge */}
              <div className="px-3 py-1.5 text-sm rounded-md bg-neutral-100 border border-neutral-200 text-neutral-600">
                {session?.expert_name || 'Expert'}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-4 py-6">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold">
            Chat Session
            {session?.status === 'completed' && ' (Completed)'}
          </h2>
          {session?.created_at && (
            <p className="text-sm text-neutral-600">
              Started {new Date(session.created_at).toLocaleString()}
            </p>
          )}
        </div>
        
        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.sender_id === user.id ? 'justify-end' : 'justify-start'
              }`}
            >
              <div className="flex flex-col max-w-xs">
                <div className="flex items-start gap-2">
                  <span className="text-xs text-neutral-600">
                    {msg.sender_id === user.id ? 'You' : 
                     msg.sender_id === session?.expert_id ? session.expert_name : 'Expert'}
                  </span>
                </div>
                <div
                  className={`px-4 py-2 rounded-lg ${
                    msg.sender_id === user.id
                      ? 'bg-rose-500 text-white'
                      : 'bg-neutral-200 text-neutral-900'
                  }`}
                >
                  {msg.content}
                </div>
                {msg.created_at && (
                  <span className="text-xs text-neutral-500 mt-1">
                    {new Date(msg.created_at).toLocaleTimeString()}
                  </span>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {session?.status !== 'completed' && (
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={messageContent}
              onChange={(e) => setMessageContent(e.target.value)}
              className="flex-1 px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-500"
              placeholder="Type your message..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!messageContent.trim() || connectionStatus !== 'connected'}
              className="px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        )}
      </div>
    </div>
  );
}