import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Input } from '../UI/Input';
import { Alert, AlertDescription } from '../UI/Alert';
// Using emoji icons instead of lucide-react for simplicity
const MessageCircle = () => <span>💬</span>;
const Send = () => <span>📤</span>;
const Bot = () => <span>🤖</span>;
const User = () => <span>👤</span>;
const Loader2 = () => <span>⏳</span>;
const TrendingUp = () => <span>📈</span>;
const TrendingDown = () => <span>📉</span>;
const BarChart3 = () => <span>📊</span>;
const Lightbulb = () => <span>💡</span>;
const ExternalLink = () => <span>🔗</span>;
const RefreshCw = () => <span>🔄</span>;

const generateMockResponse = (message) => {
  const lowerMessage = message.toLowerCase();
  
  if (lowerMessage.includes('carbon') || lowerMessage.includes('emission')) {
    return {
      message: "Based on your ESG data, your carbon emissions are performing well compared to industry benchmarks. Your Scope 1 emissions of 1,250 tCO2e place you in the 35th percentile, which is better than 65% of similar companies. Consider implementing renewable energy initiatives to further reduce your Scope 2 emissions.",
      metadata: {
        analysis: {
          scope1_emissions: { value: 1250, percentile: 35, performance: "Good" },
          scope2_emissions: { value: 2100, percentile: 55, performance: "Average" }
        },
        recommendations: [
          "Increase renewable energy adoption to 70%",
          "Implement energy efficiency measures",
          "Consider carbon offset programs"
        ]
      }
    };
  } else if (lowerMessage.includes('water') || lowerMessage.includes('consumption')) {
    return {
      message: "Your water consumption metrics show room for improvement. At 8,500 m³ annually, you're in the 70th percentile, meaning 30% of companies use less water. I recommend implementing water recycling systems and smart irrigation technologies.",
      metadata: {
        analysis: { water_consumption: { value: 8500, percentile: 70, performance: "Needs Improvement" } },
        recommendations: ["Install water recycling systems", "Implement smart water meters", "Rainwater harvesting"]
      }
    };
  } else if (lowerMessage.includes('waste') || lowerMessage.includes('recycling')) {
    return {
      message: "Your waste management is excellent! Generating only 450 tonnes annually puts you in the 25th percentile - better than 75% of peer companies. Keep up the great work with your circular economy initiatives.",
      metadata: {
        analysis: { waste_generated: { value: 450, percentile: 25, performance: "Excellent" } },
        recommendations: ["Maintain current waste reduction programs", "Explore zero-waste initiatives"]
      }
    };
  } else if (lowerMessage.includes('energy') || lowerMessage.includes('renewable')) {
    return {
      message: "Your energy profile shows mixed results. Total consumption of 12,000 MWh is average for your sector, but your renewable energy percentage could be higher. Currently at 45%, increasing to 70% would significantly improve your ESG score.",
      metadata: {
        analysis: { 
          energy_consumption: { value: 12000, percentile: 50, performance: "Average" },
          renewable_energy: { value: 45, percentile: 60, performance: "Good" }
        },
        recommendations: ["Install solar panels", "Sign renewable energy contracts", "Implement energy storage"]
      }
    };
  } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
    return {
      message: "Hello! I'm your ESG AI Assistant. I can help you analyze your environmental, social, and governance performance. Ask me about your carbon emissions, water usage, waste management, or energy consumption. I can also provide industry benchmarks and improvement recommendations.",
      metadata: {
        suggested_questions: [
          "How do my carbon emissions compare to industry peers?",
          "What are my top ESG improvement opportunities?",
          "Show me my sustainability score breakdown",
          "What renewable energy options should I consider?"
        ]
      }
    };
  } else {
    return {
      message: "I'm here to help with your ESG analysis! I can provide insights on carbon emissions, water usage, waste management, energy consumption, and industry benchmarking. What specific ESG topic would you like to explore?",
      metadata: {
        suggested_questions: [
          "Analyze my carbon footprint",
          "Compare my water usage to industry standards",
          "Show me waste reduction opportunities",
          "What's my overall ESG score?"
        ]
      }
    };
  }
};

const ChatInterface = ({ 
  sessionId = 'demo-session', 
  onNewSession, 
  apiService,
  userESGData = null 
}) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (sessionId) {
      loadChatHistory();
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    if (!sessionId) return;
    
    setIsLoadingHistory(true);
    try {
      const history = await apiService.getChatHistory(sessionId);
      setMessages(history);
    } catch (err) {
      console.error('Error loading chat history:', err);
      setError('Failed to load chat history');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage.trim(),
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      let response;
      try {
        response = await apiService.request(`/chatbot/chat/sessions/${sessionId}/messages`, {
          method: 'POST',
          body: JSON.stringify({ message: currentMessage })
        });
      } catch (apiError) {
        console.log('API not available, using mock response');
        // Generate mock response based on the message
        response = generateMockResponse(currentMessage);
      }
      
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        metadata: response.metadata,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your message. Please try again or rephrase your question.',
        created_at: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for better readability
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');
  };

  const getMessageIcon = (role) => {
    switch (role) {
      case 'user':
        return <span className="text-blue-600">👤</span>;
      case 'assistant':
        return <span className="text-green-600">🤖</span>;
      default:
        return <span className="text-gray-600">💬</span>;
    }
  };

  const renderMetadata = (metadata) => {
    if (!metadata) return null;

    return (
      <div className="mt-3 p-3 bg-gray-50 rounded-lg text-sm">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-blue-600">📊</span>
          <span className="font-medium text-gray-700">Analysis Details</span>
        </div>
        
        {metadata.analysis_type && (
          <div className="mb-2">
            <span className="font-medium">Analysis Type:</span> {metadata.analysis_type}
          </div>
        )}
        
        {metadata.has_user_data !== undefined && (
          <div className="mb-2">
            <span className="font-medium">User Data Available:</span> 
            <span className={metadata.has_user_data ? 'text-green-600' : 'text-orange-600'}>
              {metadata.has_user_data ? ' Yes' : ' No'}
            </span>
          </div>
        )}
        
        {metadata.industry_context !== undefined && (
          <div className="mb-2">
            <span className="font-medium">Industry Context:</span> 
            <span className={metadata.industry_context ? 'text-green-600' : 'text-orange-600'}>
              {metadata.industry_context ? ' Available' : ' Limited'}
            </span>
          </div>
        )}
      </div>
    );
  };

  const suggestedQuestions = [
    "How does my company's carbon footprint compare to industry peers?",
    "What are the top 3 areas where I can improve my ESG performance?",
    "Show me the latest regulatory requirements for IT companies",
    "What ESG metrics should I focus on for better investor relations?",
    "How can I reduce my Scope 3 emissions?",
    "What are the industry benchmarks for renewable energy adoption?"
  ];

  const handleSuggestedQuestion = (question) => {
    setInputMessage(question);
  };

  if (!sessionId) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-8 text-center">
          <span className="text-6xl text-gray-400 block mb-4">🤖</span>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            ESG Intelligence Assistant
          </h3>
          <p className="text-gray-600 mb-6">
            Get personalized ESG insights and recommendations based on your company's data and industry benchmarks.
          </p>
          <Button onClick={onNewSession} className="bg-blue-600 hover:bg-blue-700 text-white">
            <span className="mr-2">💬</span>
            Start New Chat
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl mx-auto h-[600px] flex flex-col">
      <CardHeader className="border-b">
        <CardTitle className="flex items-center gap-2">
          <span className="text-green-600 text-xl">🤖</span>
          ESG Intelligence Assistant
          <Button
            variant="outline"
            size="sm"
            onClick={onNewSession}
            className="ml-auto"
          >
            <span className="mr-1">🔄</span>
            New Chat
          </Button>
        </CardTitle>
        
        {userESGData && (
          <div className="text-sm text-gray-600">
            Analyzing data for <strong>{userESGData.company_name}</strong> ({userESGData.year})
          </div>
        )}
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoadingHistory ? (
            <div className="flex items-center justify-center py-8">
              <span className="text-gray-400 animate-spin text-xl">⏳</span>
              <span className="ml-2 text-gray-600">Loading chat history...</span>
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center py-8">
              <div className="mb-6">
                <span className="text-4xl text-gray-400 block mb-3">🤖</span>
                <p className="text-gray-600">
                  Welcome! I'm your ESG Intelligence Assistant. Ask me anything about your ESG performance, 
                  industry benchmarks, or regulatory requirements.
                </p>
              </div>
              
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestedQuestion(question)}
                      className="text-left p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-sm text-blue-800 transition-colors"
                    >
                      <span className="mr-2">💡</span>
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 mt-1">
                    {getMessageIcon(message.role)}
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.isError
                      ? 'bg-red-50 border border-red-200 text-red-800'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div
                    dangerouslySetInnerHTML={{
                      __html: formatMessage(message.content)
                    }}
                  />
                  
                  {message.role === 'assistant' && renderMetadata(message.metadata)}
                  
                  <div className="text-xs opacity-70 mt-2">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </div>
                </div>
                
                {message.role === 'user' && (
                  <div className="flex-shrink-0 mt-1">
                    {getMessageIcon(message.role)}
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 mt-1">
                <span className="text-green-600">🤖</span>
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span>
                  <span className="text-gray-600">Analyzing your question...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4 border-t">
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about your ESG performance, industry benchmarks, or regulatory requirements..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4"
            >
              {isLoading ? (
                <span className="animate-spin">⏳</span>
              ) : (
                <span>📤</span>
              )}
            </Button>
          </div>
          
          <div className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ChatInterface;
