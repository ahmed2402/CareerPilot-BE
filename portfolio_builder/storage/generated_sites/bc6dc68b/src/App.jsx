import React from 'react';
import { Menu, X } from 'lucide-react';
import Hero from './components/Hero';
import About from './components/About';
import Skills from './components/Skills';
import Experience from './components/Experience';
import Projects from './components/Projects';
import Contact from './components/Contact';

const navItems = [{ id: "hero", label: "Hero" }, { id: "about", label: "About" }, { id: "skills", label: "Skills" }, { id: "experience", label: "Experience" }, { id: "projects", label: "Projects" }, { id: "contact", label: "Contact" }];

function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  
  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-900/90 backdrop-blur-sm border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <a href="#hero" className="text-xl font-bold text-white">Portfolio</a>
          
          {/* Desktop Nav */}
          <ul className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <li key={item.id}>
                <button 
                  onClick={() => scrollToSection(item.id)}
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
          
          {/* Mobile Menu Button */}
          <button 
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
        
        {/* Mobile Nav */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-gray-800 border-t border-gray-700">
            <ul className="px-4 py-4 space-y-4">
              {navItems.map((item) => (
                <li key={item.id}>
                  <button 
                    onClick={() => scrollToSection(item.id)}
                    className="text-gray-300 hover:text-white transition-colors block w-full text-left"
                  >
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </nav>

      {/* Sections */}
      <main className="pt-16">
      <Hero />
      <About />
      <Skills />
      <Experience />
      <Projects />
      <Contact />
      </main>
    </div>
  );
}

export default App;
