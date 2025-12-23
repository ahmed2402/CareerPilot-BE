import React from 'react';
import { Mail, Github, Linkedin, Send } from 'lucide-react';

const Contact = () => {
  return (
    <section id="contact" className="py-20 px-4 bg-gray-800">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl font-bold text-white mb-4">Get In Touch</h2>
        <div className="w-24 h-1 mx-auto mb-8" style={{ backgroundColor: '#7F5AF0' }}></div>
        
        <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
          I'm always open to new opportunities and collaborations. 
          Feel free to reach out if you'd like to connect!
        </p>
        
        <div className="flex justify-center gap-8 mb-12">
          
          <a 
            href="mailto:ahmedraza312682@gmail.com" 
            className="flex items-center gap-2 px-6 py-3 rounded-full text-white font-semibold hover:scale-105 transition-transform"
            style={{ backgroundColor: '#7F5AF0' }}
          >
            <Mail size={20} />
            Email Me
          </a>
          
        </div>
        
        <div className="flex justify-center gap-6">
          <a href="https://github.com/ahmed2402" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors"><Github size={28} /></a>
          
          <a href="mailto:ahmedraza312682@gmail.com" className="text-gray-400 hover:text-white transition-colors"><Mail size={28} /></a>
        </div>
        
        <p className="mt-16 text-gray-500 text-sm">
          © 2024 Ahmed Raza. All rights reserved.
        </p>
      </div>
    </section>
  );
};

export default Contact;
