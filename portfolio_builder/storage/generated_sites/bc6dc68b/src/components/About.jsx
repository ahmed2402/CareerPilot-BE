import React from 'react';
import { User } from 'lucide-react';

const About = () => {
  return (
    <section id="about" className="py-20 px-4 bg-gray-800">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">About Me</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{ backgroundColor: '#7F5AF0' }}></div>
        
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="flex justify-center">
            <div className="w-64 h-64 rounded-full bg-gray-700 flex items-center justify-center border-4" style={{ borderColor: '#7F5AF0' }}>
              <User size={120} className="text-gray-500" />
            </div>
          </div>
          
          <div>
            <p className="text-lg text-gray-300 leading-relaxed mb-6">
              As a detail-oriented and motivated Computer Science undergraduate, I've always been driven to make a meaningful impact through innovative technology solutions. Currently, I'm a Development Intern at the CSIT Department - NED, where I'm leveraging my front-end development skills to build dynamic and responsive interfaces for internal web applications.
            </p>
            <p className="text-lg text-gray-300 leading-relaxed">My journey in the world of tech began during my undergraduate studies at NED University, where I delved into the realms of machine learning, natural language processing, and generative AI. I was fascinated by the potential of these technologies to transform industries and improve lives. Since then, I've been actively honing my skills, working on diverse projects, and exploring the applications of AI and ML in real-world scenarios.</p>
          </div>
        </div>
        
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16">
          
          <div className="text-center p-4">
            <p className="text-3xl font-bold" style={{ color: '#7F5AF0' }}>1+ Years</p>
            <p className="text-gray-400">Experience</p>
          </div>

          <div className="text-center p-4">
            <p className="text-3xl font-bold" style={{ color: '#7F5AF0' }}>5+ Projects</p>
            <p className="text-gray-400">Projects</p>
          </div>

          <div className="text-center p-4">
            <p className="text-3xl font-bold" style={{ color: '#7F5AF0' }}>Bachelor of Science in Computer Science and Information Technology</p>
            <p className="text-gray-400">Education</p>
          </div>
        </div>
        
      </div>
    </section>
  );
};

export default About;
