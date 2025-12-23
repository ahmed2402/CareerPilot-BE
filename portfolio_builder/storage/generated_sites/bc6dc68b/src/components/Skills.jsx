import React from 'react';

const Skills = () => {
  return (
    <section id="skills" className="py-20 px-4 bg-gray-900">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">Skills & Technologies</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{ backgroundColor: '#7F5AF0' }}></div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Frontend</h3>
          <div className="flex flex-wrap gap-2">
            <span key="Angular" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Angular</span> <span key="HTML" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">HTML</span> <span key="CSS" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">CSS</span> <span key="JavaScript" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">JavaScript</span> <span key="Tailwind CSS" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Tailwind CSS</span>
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Backend</h3>
          <div className="flex flex-wrap gap-2">
            <span key="Flask" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Flask</span> <span key="Python" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Python</span>
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Databases</h3>
          <div className="flex flex-wrap gap-2">
            <span key="MySQL" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">MySQL</span>
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Machine Learning</h3>
          <div className="flex flex-wrap gap-2">
            <span key="NumPy" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">NumPy</span> <span key="Pandas" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Pandas</span> <span key="Scikit-learn" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Scikit-learn</span> <span key="PyCaret" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">PyCaret</span> <span key="OpenCV" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">OpenCV</span>
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Natural Language Processing</h3>
          <div className="flex flex-wrap gap-2">
            <span key="LangChain" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">LangChain</span> <span key="HuggingFace" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">HuggingFace</span>
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Development Tools</h3>
          <div className="flex flex-wrap gap-2">
            <span key="Git" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Git</span> <span key="GitHub" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">GitHub</span>
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Soft Skills</h3>
          <div className="flex flex-wrap gap-2">
            <span key="Problem-solving" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Problem-solving</span> <span key="Fast learning" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Fast learning</span> <span key="Collaboration" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">Collaboration</span>
          </div>
        </div>
        </div>
      </div>
    </section>
  );
};

export default Skills;
