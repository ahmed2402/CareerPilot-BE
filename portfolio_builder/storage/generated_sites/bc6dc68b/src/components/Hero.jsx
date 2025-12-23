import React from 'react';
import { Github, Linkedin, Mail, ArrowDown } from 'lucide-react';

const Hero = () => {
  return (
    <section id="hero" className="min-h-screen flex items-center justify-center relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%239C92AC%22 fill-opacity=%220.05%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
      
      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <p className="text-lg md:text-xl text-gray-400 mb-4">Hi, I'm</p>
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-4">
          Ahmed Raza
        </h1>
        <h2 className="text-2xl md:text-4xl font-semibold mb-6" style={{ color: '#7F5AF0' }}>
          Building Intelligent Solutions
        </h2>
        <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Empowering businesses with innovative AI, ML, and data-driven applications. Let's transform your vision into reality.
        </p>
        
        <div className="flex justify-center gap-4 mb-12">
          <a 
            href="#projects" 
            className="px-8 py-3 rounded-full font-semibold text-white transition-all hover:scale-105"
            style={{ backgroundColor: '#7F5AF0' }}
          >
            View My Work
          </a>
          <a 
            href="#contact" 
            className="px-8 py-3 rounded-full font-semibold text-white border border-gray-600 hover:border-gray-400 transition-all"
          >
            Get In Touch
          </a>
        </div>
        
        <div className="flex justify-center gap-6">
          <a href="https://github.com/ahmed2402" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors"><Github size={24} /></a>
          
          <a href="#contact" className="text-gray-400 hover:text-white transition-colors">
            <Mail size={24} />
          </a>
        </div>
      </div>
      
      <a href="#about" className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-gray-400 animate-bounce">
        <ArrowDown size={32} />
      </a>
    </section>
  );
};

export default Hero;
