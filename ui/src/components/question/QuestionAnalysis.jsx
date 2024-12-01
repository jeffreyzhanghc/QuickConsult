import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Brain, ArrowLeft, Loader2, Edit2, Check, Trash2, LogOut, Plus } from 'lucide-react';
import { useAuth } from '../../auth/context/AuthContext';
import authService from '../../auth/services/authService';

const QuestionCard = ({ question, isEditing, onEditStart, onSave, onDelete }) => {
  const [editedContent, setEditedContent] = useState(question);

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all border border-neutral-100 hover:border-rose-100">
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1">
          {isEditing ? (
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="w-full p-4 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-transparent text-[15px] leading-relaxed font-medium"
              rows={3}
            />
          ) : (
            <p className="text-[15px] leading-relaxed font-medium text-neutral-800">
              {question}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {isEditing ? (
            <button
              onClick={() => onSave(editedContent)}
              className="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all"
            >
              <Check className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={onEditStart}
              className="p-2 text-neutral-500 hover:bg-neutral-50 rounded-lg transition-all"
            >
              <Edit2 className="w-5 h-5" />
            </button>
          )}
          <button
            onClick={onDelete}
            className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-all"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default function QuestionAnalysis() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [originalQuestion, setOriginalQuestion] = useState('');
  const [rephrasedQuestions, setRephrasedQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);
  const [reasoning, setReasoning] = useState('');
  const [isAddingQuestion, setIsAddingQuestion] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');

  useEffect(() => {
    const initializeAnalysis = async () => {
      try {
        const questionFromState = location.state?.question;
        if (!questionFromState) {
          navigate('/');
          return;
        }

        setOriginalQuestion(questionFromState);
        await analyzeQuestion(questionFromState);
      } catch (error) {
        setError('Failed to initialize analysis. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAnalysis();
  }, [location, navigate]);

  const analyzeQuestion = async (questionText) => {
    try {
      const response = await authService.api.post('/questions/analyze', {
        content: questionText
      });
      setRephrasedQuestions(response.data.rephrased_versions);
      setReasoning(response.data.reasoning);
    } catch (error) {
      setError('Failed to analyze question. Please try again.');
    }
  };

  const handleEdit = (index) => {
    setEditingIndex(index);
  };

  const handleSave = (index, newContent) => {
    const updatedQuestions = [...rephrasedQuestions];
    updatedQuestions[index] = newContent;
    setRephrasedQuestions(updatedQuestions);
    setEditingIndex(null);
  };

  const handleDelete = (index) => {
    setRephrasedQuestions(rephrasedQuestions.filter((_, i) => i !== index));
  };

  const handleAddQuestion = () => {
    if (newQuestion.trim()) {
      setRephrasedQuestions([...rephrasedQuestions, newQuestion]);
      setNewQuestion('');
      setIsAddingQuestion(false);
    }
  };

  const handleProceed = async () => {
    try {
      await authService.api.post('/questions/verify', {
        original_content: originalQuestion,
        verified_questions: rephrasedQuestions
      });
      // Pass the questions and their matched experts to the next page
      navigate('/questions/matches', { 
        state: { 
          questions: rephrasedQuestions.map(question => ({
            title: question,
            expert: {
              name: `Dr. ${['Sarah Chen', 'Michael Lee', 'Emma Watson', 'David Kim', 'Linda Park'][Math.floor(Math.random() * 5)]}`,
              expertise: ['Business Strategy', 'Market Analysis', 'Financial Planning', 'Technology Consulting', 'Operations Management'][Math.floor(Math.random() * 5)]
            },
            status: 'In Progress',
            date: new Date().toISOString().split('T')[0]
          }))
        }
      });
    } catch (error) {
      setError('Failed to save questions. Please try again.');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-rose-50 via-neutral-50 to-amber-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-rose-500" />
          <p className="text-neutral-600">Analyzing your question...</p>
        </div>
      </div>
    );
  }

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

      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Original Question */}
        <h2 className="text-3xl font-semibold text-neutral-900 mb-4">Your Question</h2>
        <p className="text-lg text-neutral-700 mb-12">{originalQuestion}</p>

        {/* AI Analysis */}
        <h2 className="text-3xl font-semibold text-neutral-900 mb-4">Rephrase Suggestions</h2>
        <p className="text-lg text-neutral-700 mb-12">{reasoning}</p>

        {/* Rephrased Questions */}
        <div className="mb-12">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-semibold text-neutral-900">Rephrased Questions</h2>
            <button
              onClick={() => setIsAddingQuestion(true)}
              className="flex items-center gap-2 px-4 py-2 text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
            >
              <Plus className="w-5 h-5" />
              Add Question
            </button>
          </div>

          <div className="space-y-4">
            {rephrasedQuestions.map((question, index) => (
              <QuestionCard
                key={index}
                question={question}
                isEditing={editingIndex === index}
                onEditStart={() => handleEdit(index)}
                onSave={(newContent) => handleSave(index, newContent)}
                onDelete={() => handleDelete(index)}
              />
            ))}

            {isAddingQuestion && (
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-rose-100">
                <textarea
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  placeholder="Type your question here..."
                  className="w-full p-4 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-transparent text-[15px] leading-relaxed"
                  rows={3}
                />
                <div className="flex justify-end gap-2 mt-4">
                  <button
                    onClick={() => setIsAddingQuestion(false)}
                    className="px-4 py-2 text-neutral-600 hover:bg-neutral-50 rounded-lg transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddQuestion}
                    className="px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-all"
                  >
                    Add
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end">
          <button
            onClick={handleProceed}
            className="px-8 py-3 bg-rose-500 text-white rounded-xl hover:bg-rose-600 transition-all disabled:opacity-50"
            disabled={rephrasedQuestions.length === 0}
          >
            Proceed to Expert Matching
          </button>
        </div>
      </main>
    </div>
  );
}