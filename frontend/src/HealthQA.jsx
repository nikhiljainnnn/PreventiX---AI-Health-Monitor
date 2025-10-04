import React, { useState } from 'react';
import { MessageCircle, Send, Bot, User, AlertCircle, CheckCircle, Lightbulb } from 'lucide-react';
import { healthQA } from './api';
import toast from 'react-hot-toast';

const HealthQA = ({ healthData, onClose }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState([]);

  // Debug logging
  console.log('HealthQA received healthData:', healthData);
  console.log('HealthQA healthData type:', typeof healthData);
  console.log('HealthQA healthData keys:', healthData ? Object.keys(healthData) : 'null/undefined');
  console.log('HealthQA healthData length:', healthData ? Object.keys(healthData).length : 'null/undefined');
  console.log('HealthQA diabetes_risk:', healthData?.diabetes_risk);
  console.log('HealthQA hypertension_risk:', healthData?.hypertension_risk);
  console.log('HealthQA metabolic_health_score:', healthData?.metabolic_health_score);
  console.log('HealthQA cardiovascular_health_score:', healthData?.cardiovascular_health_score);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userQuestion = question.trim();
    setQuestion('');
    setLoading(true);

    // Add user question to conversation
    const newConversation = [...conversation, {
      type: 'user',
      content: userQuestion,
      timestamp: new Date()
    }];
    setConversation(newConversation);

    try {
      console.log('Sending question to API:', userQuestion);
      console.log('Sending health data to API:', healthData);
      
      // Check if health data is available (but be more lenient)
      if (!healthData || Object.keys(healthData).length === 0) {
        console.warn('No health data provided, but allowing the request to proceed');
        // Don't throw an error, let the backend handle it gracefully
      }
      
      // Use general Q&A endpoint
      const response = await healthQA.askQuestion(userQuestion, healthData);
      
      // Add AI response to conversation
      setConversation(prev => [...prev, {
        type: 'ai',
        content: response.answer,
        confidence: response.confidence,
        relatedFactors: response.related_factors,
        followUpSuggestions: response.follow_up_suggestions,
        disclaimer: response.disclaimer,
        timestamp: new Date()
      }]);

      toast.success('Answer generated successfully!');
    } catch (error) {
      console.error('Q&A Error:', error);
      
      // Handle different error types
      let errorMessage = 'Sorry, I encountered an error processing your question. Please try again.';
      
      if (error.response?.status === 500) {
        errorMessage = 'The health analysis service is temporarily unavailable. Please try again later.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast.error('Failed to get answer. Please try again.');
      
      // Add error message to conversation
      setConversation(prev => [...prev, {
        type: 'error',
        content: errorMessage,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'High': return 'text-green-600 bg-green-50 border-green-200';
      case 'Moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Low': return 'text-orange-600 bg-orange-50 border-orange-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getConfidenceIcon = (confidence) => {
    switch (confidence) {
      case 'High': return <CheckCircle className="w-4 h-4" />;
      case 'Moderate': return <AlertCircle className="w-4 h-4" />;
      case 'Low': return <AlertCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">Ask About Your Health Report</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Conversation Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {conversation.length === 0 ? (
            <div className="text-center py-8">
              <Bot className="w-16 h-16 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Ask Me Anything About Your Health</h3>
              <p className="text-gray-600 mb-6">
                I can help explain your health assessment results, provide personalized recommendations, 
                and answer questions about your risk factors.
              </p>
              {(!healthData || Object.keys(healthData).length === 0) && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <p className="text-blue-800 text-sm">
                    💡 I can provide general health information. For personalized advice, complete a health assessment first.
                  </p>
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-w-4xl mx-auto">
                <button
                  onClick={() => setQuestion("What is my diabetes risk and how can I reduce it?")}
                  className="p-3 text-left bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-sm"
                >
                  💡 "What is my diabetes risk and how can I reduce it?"
                </button>
                <button
                  onClick={() => setQuestion("How can I improve my blood pressure and heart health?")}
                  className="p-3 text-left bg-red-50 hover:bg-red-100 rounded-lg transition-colors text-sm"
                >
                  ❤️ "How can I improve my blood pressure and heart health?"
                </button>
                <button
                  onClick={() => setQuestion("What diet changes should I make for better health?")}
                  className="p-3 text-left bg-green-50 hover:bg-green-100 rounded-lg transition-colors text-sm"
                >
                  🥗 "What diet changes should I make for better health?"
                </button>
                <button
                  onClick={() => setQuestion("What exercise routine is best for my health?")}
                  className="p-3 text-left bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors text-sm"
                >
                  🏃 "What exercise routine is best for my health?"
                </button>
                <button
                  onClick={() => setQuestion("How can I improve my sleep and energy levels?")}
                  className="p-3 text-left bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors text-sm"
                >
                  😴 "How can I improve my sleep and energy levels?"
                </button>
                <button
                  onClick={() => setQuestion("How can I manage stress and improve my mental health?")}
                  className="p-3 text-left bg-pink-50 hover:bg-pink-100 rounded-lg transition-colors text-sm"
                >
                  🧠 "How can I manage stress and improve my mental health?"
                </button>
                <button
                  onClick={() => setQuestion("What lifestyle changes should I make for better health?")}
                  className="p-3 text-left bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors text-sm"
                >
                  🏠 "What lifestyle changes should I make for better health?"
                </button>
                <button
                  onClick={() => setQuestion("Do I need any medications or supplements?")}
                  className="p-3 text-left bg-teal-50 hover:bg-teal-100 rounded-lg transition-colors text-sm"
                >
                  💊 "Do I need any medications or supplements?"
                </button>
                <button
                  onClick={() => setQuestion("What symptoms should I watch for?")}
                  className="p-3 text-left bg-amber-50 hover:bg-amber-100 rounded-lg transition-colors text-sm"
                >
                  🚨 "What symptoms should I watch for?"
                </button>
              </div>
            </div>
          ) : (
            conversation.map((message, index) => (
              <div key={index} className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.type === 'ai' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                )}
                
                <div className={`max-w-[80%] ${message.type === 'user' ? 'order-1' : ''}`}>
                  <div className={`p-4 rounded-2xl ${
                    message.type === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : message.type === 'error'
                      ? 'bg-red-50 text-red-800 border border-red-200'
                      : 'bg-gray-50 text-gray-900'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    
                    {message.type === 'ai' && (
                      <div className="mt-4 space-y-3">
                        {/* Confidence Level */}
                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${getConfidenceColor(message.confidence)}`}>
                          {getConfidenceIcon(message.confidence)}
                          Confidence: {message.confidence}
                        </div>
                        
                        {/* Related Factors */}
                        {message.relatedFactors && message.relatedFactors.length > 0 && (
                          <div className="bg-blue-50 p-3 rounded-lg">
                            <h4 className="text-sm font-semibold text-blue-900 mb-2">Related Factors:</h4>
                            <div className="flex flex-wrap gap-2">
                              {message.relatedFactors.map((factor, idx) => (
                                <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                  {factor}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Follow-up Suggestions */}
                        {message.followUpSuggestions && message.followUpSuggestions.length > 0 && (
                          <div className="bg-green-50 p-3 rounded-lg">
                            <h4 className="text-sm font-semibold text-green-900 mb-2 flex items-center gap-2">
                              <Lightbulb className="w-4 h-4" />
                              Suggestions:
                            </h4>
                            <ul className="space-y-1">
                              {message.followUpSuggestions.map((suggestion, idx) => (
                                <li key={idx} className="text-sm text-green-800">• {suggestion}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {/* Disclaimer */}
                        <div className="text-xs text-gray-500 italic mt-3 p-2 bg-gray-100 rounded">
                          {message.disclaimer}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="text-xs text-gray-500 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
                
                {message.type === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center order-2">
                    <User className="w-5 h-5 text-white" />
                  </div>
                )}
              </div>
            ))
          )}
          
          {loading && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-gray-50 p-4 rounded-2xl">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                  <span className="text-gray-600">Analyzing your question...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-6">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask me anything about your health assessment..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Ask
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default HealthQA;

