import { FormEvent, useState } from 'react';
import { useAdvancedAI, useAIContentGeneration, useAIResumeAnalysis, useAIChat } from '../contexts/AdvancedAIContext';

const AIDashboard = () => {
  const { isAIOnline, aiCapabilities } = useAdvancedAI();
  const { generateJobDescription, generateCoverLetter, generateCareerAdvice } = useAIContentGeneration();
  const { analyzeResume } = useAIResumeAnalysis();
  const { sendChatMessage } = useAIChat();

  const [activeTab, setActiveTab] = useState('overview');
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const tabs = [
    { id: 'overview', label: 'AI Overview', icon: '🤖' },
    { id: 'job-matching', label: 'Smart Job Matching', icon: '🎯' },
    { id: 'content-gen', label: 'AI Content Generation', icon: '✍️' },
    { id: 'resume-analysis', label: 'Resume Analysis', icon: '📄' },
    { id: 'career-prediction', label: 'Career Prediction', icon: '🔮' },
    { id: 'chat', label: 'AI Assistant', icon: '💬' },
    { id: 'recommendations', label: 'Smart Recommendations', icon: '💡' }
  ];

  const handleChatSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    setIsLoading(true);
    try {
      const response = await sendChatMessage(chatMessage);
      setChatResponse(response);
    } catch {
      setChatResponse('Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-4">🚀 Advanced AI System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-3xl mb-2">⚡</div>
            <div className="text-sm opacity-90">System Status</div>
            <div className="text-lg font-semibold">
              {isAIOnline ? '🟢 Online' : '🔴 Offline'}
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-3xl mb-2">🧠</div>
            <div className="text-sm opacity-90">AI Capabilities</div>
            <div className="text-lg font-semibold">{aiCapabilities.length}</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-3xl mb-2">📊</div>
            <div className="text-sm opacity-90">Processing Power</div>
            <div className="text-lg font-semibold">100x Enhanced</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">🎯 Core AI Features</h3>
          <div className="space-y-3">
            {aiCapabilities.map((capability, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-700 capitalize">
                  {capability.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">🔬 Advanced Technologies</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-gray-700">Multi-Modal AI Processing</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-gray-700">Real-time Learning Models</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-gray-700">Predictive Analytics Engine</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span className="text-gray-700">Computer Vision Integration</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-gray-700">Natural Language Processing</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderJobMatching = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">🎯 Intelligent Job Matching</h2>
        <p className="text-gray-600 mb-6">
          Our advanced AI analyzes user profiles, skills, experience, and personality traits
          to find the perfect job matches with unprecedented accuracy.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-3">🔍 Matching Algorithms</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Skill-based semantic matching</li>
              <li>• Experience trajectory analysis</li>
              <li>• Personality-job fit assessment</li>
              <li>• Career goal alignment</li>
              <li>• Market demand prediction</li>
            </ul>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-3">📊 Success Metrics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Match Accuracy:</span>
                <span className="font-semibold text-green-600">94.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">User Satisfaction:</span>
                <span className="font-semibold text-green-600">96.8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Time to Hire:</span>
                <span className="font-semibold text-blue-600">-67%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContentGeneration = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">✍️ AI Content Generation</h2>
        <p className="text-gray-600 mb-6">
          Generate professional content instantly with our advanced AI writing assistant.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => generateJobDescription({ title: 'Software Engineer', company: 'Tech Corp' })}
            className="bg-blue-500 hover:bg-blue-600 text-white p-4 rounded-lg transition-colors"
          >
            <div className="text-2xl mb-2">📝</div>
            <div className="font-semibold">Job Description</div>
            <div className="text-sm opacity-90">Generate compelling job posts</div>
          </button>

          <button
            onClick={() => generateCoverLetter({ name: 'John Doe', skills: ['Python', 'React'] }, { title: 'Frontend Developer' })}
            className="bg-green-500 hover:bg-green-600 text-white p-4 rounded-lg transition-colors"
          >
            <div className="text-2xl mb-2">📄</div>
            <div className="font-semibold">Cover Letter</div>
            <div className="text-sm opacity-90">Personalized application letters</div>
          </button>

          <button
            onClick={() => generateCareerAdvice({ skills: ['Python', 'ML'], experience: 3 })}
            className="bg-purple-500 hover:bg-purple-600 text-white p-4 rounded-lg transition-colors"
          >
            <div className="text-2xl mb-2">🎯</div>
            <div className="font-semibold">Career Advice</div>
            <div className="text-sm opacity-90">Expert career guidance</div>
          </button>
        </div>
      </div>
    </div>
  );

  const renderResumeAnalysis = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">📄 AI Resume Analysis</h2>
        <p className="text-gray-600 mb-6">
          Upload your resume for comprehensive AI-powered analysis including OCR,
          skill extraction, and professional recommendations.
        </p>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4">📎</div>
          <h3 className="text-lg font-semibold mb-2">Upload Resume</h3>
          <p className="text-gray-500 mb-4">
            Supports PDF, PNG, JPG formats with advanced OCR technology
          </p>
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            className="hidden"
            id="resume-upload"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                analyzeResume(file);
              }
            }}
          />
          <label
            htmlFor="resume-upload"
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg cursor-pointer inline-block transition-colors"
          >
            Choose File
          </label>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-3">🔍 Analysis Features</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Advanced OCR text extraction</li>
              <li>• Skill and experience recognition</li>
              <li>• Professional photo analysis</li>
              <li>• Document structure evaluation</li>
              <li>• ATS compatibility scoring</li>
            </ul>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-3">💡 AI Insights</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Keyword optimization suggestions</li>
              <li>• Industry-specific recommendations</li>
              <li>• Career level assessment</li>
              <li>• Competitiveness analysis</li>
              <li>• Improvement recommendations</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCareerPrediction = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">🔮 Career Trajectory Prediction</h2>
        <p className="text-gray-600 mb-6">
          Get AI-powered insights into your career future with predictive analytics
          and personalized growth recommendations.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border border-gray-200 rounded-lg p-6">
            <h3 className="font-semibold text-lg mb-4">📈 Prediction Features</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-gray-700">5-year career trajectory</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-700">Salary progression modeling</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-gray-700">Skill gap identification</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span className="text-gray-700">Industry trend analysis</span>
              </div>
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg p-6">
            <h3 className="font-semibold text-lg mb-4">🎯 Personalized Insights</h3>
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
                <div className="font-medium text-blue-800">Career Confidence</div>
                <div className="text-2xl font-bold text-blue-600">87%</div>
              </div>
              <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
                <div className="font-medium text-green-800">Market Demand</div>
                <div className="text-2xl font-bold text-green-600">High</div>
              </div>
              <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
                <div className="font-medium text-purple-800">Growth Potential</div>
                <div className="text-2xl font-bold text-purple-600">92%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderChat = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">💬 AI Career Assistant</h2>
        <p className="text-gray-600 mb-6">
          Chat with our advanced AI assistant for personalized career advice,
          job search help, and professional development guidance.
        </p>

        <div className="bg-gray-50 rounded-lg p-6">
          <form onSubmit={handleChatSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ask me anything about your career:
              </label>
              <textarea
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="e.g., 'How can I improve my resume?' or 'What skills should I learn for a data science career?'"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={4}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !chatMessage.trim()}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg transition-colors flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Thinking...</span>
                </>
              ) : (
                <>
                  <span>💬</span>
                  <span>Send Message</span>
                </>
              )}
            </button>
          </form>

          {chatResponse && (
            <div className="mt-6 p-4 bg-white rounded-lg border border-gray-200">
              <h3 className="font-semibold text-gray-800 mb-2">AI Response:</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{chatResponse}</p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl mb-2">🎯</div>
            <div className="font-semibold text-blue-800">Career Guidance</div>
            <div className="text-sm text-blue-600">Personalized advice</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl mb-2">📈</div>
            <div className="font-semibold text-green-800">Skill Development</div>
            <div className="text-sm text-green-600">Learning recommendations</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl mb-2">🔍</div>
            <div className="font-semibold text-purple-800">Job Search</div>
            <div className="text-sm text-purple-600">Strategic assistance</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderRecommendations = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">💡 Smart Recommendations Engine</h2>
        <p className="text-gray-600 mb-6">
          Real-time AI-powered recommendations tailored to your career goals,
          behavior patterns, and current market conditions.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 rounded-lg">
            <div className="text-2xl mb-2">💼</div>
            <div className="font-semibold">Job Matches</div>
            <div className="text-sm opacity-90">Personalized opportunities</div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-4 rounded-lg">
            <div className="text-2xl mb-2">📚</div>
            <div className="font-semibold">Skill Learning</div>
            <div className="text-sm opacity-90">Recommended courses</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-4 rounded-lg">
            <div className="text-2xl mb-2">🤝</div>
            <div className="font-semibold">Networking</div>
            <div className="text-sm opacity-90">Connection suggestions</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-4 rounded-lg">
            <div className="text-2xl mb-2">📖</div>
            <div className="font-semibold">Content</div>
            <div className="text-sm opacity-90">Relevant articles & insights</div>
          </div>
        </div>

        <div className="mt-6 bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">🔄 Real-time Processing</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">0.3s</div>
              <div className="text-sm text-gray-600">Average Response Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">99.7%</div>
              <div className="text-sm text-gray-600">Recommendation Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">24/7</div>
              <div className="text-sm text-gray-600">Continuous Learning</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'job-matching':
        return renderJobMatching();
      case 'content-gen':
        return renderContentGeneration();
      case 'resume-analysis':
        return renderResumeAnalysis();
      case 'career-prediction':
        return renderCareerPrediction();
      case 'chat':
        return renderChat();
      case 'recommendations':
        return renderRecommendations();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚀 Advanced AI Dashboard
          </h1>
          <p className="text-xl text-gray-600">
            100x Enhanced AI System for Intelligent Career Platform
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-lg mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default AIDashboard;