import React from 'react';

const Experience = () => {
  return (
    <section id="experience" className="py-20 px-4 bg-gray-900">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">Experience</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{ backgroundColor: '#7F5AF0' }}></div>
        
        <div className="space-y-0">
          
          <div className="relative pl-8 pb-12 border-l-2 border-gray-700 last:pb-0">
            <div className="absolute left-[-9px] top-0 w-4 h-4 rounded-full" style={{ backgroundColor: '#7F5AF0' }}></div>
            <div className="bg-gray-800 rounded-xl p-6">
              <p className="text-sm text-gray-400 mb-1">Jan 2025 - Present</p>
              <h3 className="text-xl font-semibold text-white">Development Intern</h3>
              <p className="font-medium mb-3" style={{ color: '#7F5AF0' }}>CSIT Department - NED</p>
              <p className="text-gray-400 mb-3">Collaborated with the department's tech team to develop and maintain internal web applications.</p>
              <ul className="list-disc list-inside space-y-1"><li className="text-gray-400">Led the development of a dynamic and responsive Angular-based interface for internal platforms, resulting in a 30% increase in user engagement.</li> <li className="text-gray-400">Improved UI performance by 25% through optimization techniques and code reviews, ensuring seamless user experiences.</li> <li className="text-gray-400">Participated in code reviews, testing, and documentation to ensure high-quality deliverables, contributing to a 20% reduction in bugs and errors.</li></ul>
            </div>
          </div>
          <div className="relative pl-8 pb-12 border-l-2 border-gray-700 last:pb-0">
            <div className="absolute left-[-9px] top-0 w-4 h-4 rounded-full" style={{ backgroundColor: '#7F5AF0' }}></div>
            <div className="bg-gray-800 rounded-xl p-6">
              <p className="text-sm text-gray-400 mb-1">Jun 2023 - Aug 2023</p>
              <h3 className="text-xl font-semibold text-white">AI/ML Intern</h3>
              <p className="font-medium mb-3" style={{ color: '#7F5AF0' }}>NCL - NED</p>
              <p className="text-gray-400 mb-3">Developed multiple machine learning projects, including a Unit Consumption Predictor and a Loan Approval Predictor, showcasing expertise in NLP and predictive modeling.</p>
              <ul className="list-disc list-inside space-y-1"><li className="text-gray-400">Built and deployed a Music Sentiment Analysis Tool using NLP techniques, achieving an accuracy rate of 92%.</li> <li className="text-gray-400">Applied feature engineering, model evaluation, and performance optimization across various datasets, resulting in a 25% improvement in model efficiency.</li> <li className="text-gray-400">Collaborated with cross-functional teams to integrate models into user-friendly interfaces and dashboards, enhancing user experience and productivity by 30%.</li></ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Experience;
