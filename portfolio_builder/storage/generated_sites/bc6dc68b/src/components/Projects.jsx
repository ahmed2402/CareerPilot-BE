import React from 'react';

const Projects = () => {
  return (
    <section id="projects" className="py-20 px-4 bg-gray-800">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">Featured Projects</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{ backgroundColor: '#7F5AF0' }}></div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          <div className="bg-gray-800 rounded-xl overflow-hidden hover:transform hover:scale-105 transition-transform duration-300">
            <div className="h-48 bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
              <span className="text-6xl">🚀</span>
            </div>
            <div className="p-6">
              <h3 className="text-xl font-semibold text-white mb-2">ARIA - Agentic Resume Intelligence Analyzer</h3>
              <p className="text-gray-400 text-sm mb-4">Transform your job search with a personalized AI assistant that analyzes resumes, checks ATS, and prepares you for interviews.</p>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">LangGraph</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">LangChain</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">Prefect</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">RAG</span>
              </div>
              <div className="flex gap-4">
                
                <a href="https://github.com/ahmed2402/Agentic-Resume-Intelligence-Analyzer-ARIA" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-400 hover:text-white">GitHub</a>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-xl overflow-hidden hover:transform hover:scale-105 transition-transform duration-300">
            <div className="h-48 bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
              <span className="text-6xl">🚀</span>
            </div>
            <div className="p-6">
              <h3 className="text-xl font-semibold text-white mb-2">Loan Prediction System</h3>
              <p className="text-gray-400 text-sm mb-4">Unlock loan approval predictions with a user-friendly interface that utilizes machine learning algorithms and real-time data.</p>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">Python</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">Logistic Regression</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">Random Forest</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">XGBoost</span>
              </div>
              <div className="flex gap-4">
                
                <a href="https://github.com/ahmed2402/Loan-Prediction.git" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-400 hover:text-white">GitHub</a>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-xl overflow-hidden hover:transform hover:scale-105 transition-transform duration-300">
            <div className="h-48 bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
              <span className="text-6xl">🚀</span>
            </div>
            <div className="p-6">
              <h3 className="text-xl font-semibold text-white mb-2">Unit Consumption Predictor</h3>
              <p className="text-gray-400 text-sm mb-4">Optimize energy consumption with a time-series forecasting model that predicts electricity unit consumption for the upcoming month.</p>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">Python</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">SARIMA</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">Holt’s Winter Exponential Smoothing</span>
              </div>
              <div className="flex gap-4">
                
                
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-xl overflow-hidden hover:transform hover:scale-105 transition-transform duration-300">
            <div className="h-48 bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
              <span className="text-6xl">🚀</span>
            </div>
            <div className="p-6">
              <h3 className="text-xl font-semibold text-white mb-2">CSIT-RAG Chatbot (In Development)</h3>
              <p className="text-gray-400 text-sm mb-4">Improve departmental communication with a chatbot that handles queries related to admissions, examinations, and general departmental information.</p>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">LangChain</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">RAG</span> <span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">Knowledge Graph</span>
              </div>
              <div className="flex gap-4">
                
                
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Projects;
