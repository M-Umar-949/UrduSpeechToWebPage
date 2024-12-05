import React, { useState } from 'react';
import { Mic, Globe, ToggleLeft, ToggleRight } from 'lucide-react';
import LanguageContent from '../components/LanguageContent';
import { useRouter } from 'next/router';

const Home = () => {
  const [language, setLanguage] = useState('english');
  const currentContent = LanguageContent[language];
  const router = useRouter();

  const toggleLanguage = () => {
    setLanguage(language === 'english' ? 'urdu' : 'english');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-purple-950 text-white font-mono">
      <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="text-2xl font-mono font-bold text-purple-400">
          {currentContent.title}
        </div>
        <div className="flex items-center space-x-4">
          <div onClick={toggleLanguage} className="cursor-pointer flex items-center">
            {language === 'english' ? <ToggleLeft className="text-purple-400" /> : <ToggleRight className="text-purple-400" />}
            <span className="ml-2 text-purple-400 font-mono">
              {language === 'english' ? 'اردو' : 'English'}
            </span>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-16 grid md:grid-cols-2 gap-12 items-center">
        <div className="space-y-6 text-right">
          <h1 className="text-4xl font-mono font-bold text-purple-200 ">
            {currentContent.subtitle}
          </h1>
          <p className="text-xl font-mono text-gray-400 ">
            {currentContent.description}
          </p>
          <div className="flex justify-end space-x-4">
            <button
              onClick={() => router.push('/Main')}
              className="px-6 py-3 bg-purple-700 text-white rounded-lg hover:bg-purple-600 flex font-mono items-center"
            >
              <Mic className="mr-2" /> {currentContent.cta}
            </button>
            <button className="px-6 py-3 border-2 border-purple-500 text-purple-400 rounded-lg hover:bg-purple-800 font-mono flex items-center">
              <Globe className="mr-2" /> {currentContent.learnMore}
            </button>
          </div>
        </div>
        <div className="flex justify-center">
          <div className="bg-purple-800 p-8 rounded-xl shadow-lg">
            <Globe size={200} className="text-purple-400 mx-auto" />
          </div>
        </div>
      </main>

      <section className="container mx-auto px-6 py-16 text-right">
        <h2 className="text-3xl font-mono font-bold text-purple-200 mb-12 text-center">
          {language === 'english' ? 'Features' : 'خصوصیات'}
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {currentContent.features.map((feature, index) => (
            <div key={index} className="bg-purple-700 p-6 rounded-xl shadow-md text-center">
              <Mic className="text-purple-300 w-12 h-12 mx-auto mb-4" />
              <h3 className="text-xl font-mono font-bold mb-3 text-purple-200">{feature.title}</h3>
              <p className="text-gray-300 font-mono">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="bg-purple-950 font-mono py-8">
        <div className="container mx-auto px-6 text-center">
          <p>© 2024 Speech to Webpage. All Rights Reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
