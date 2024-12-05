import React, { useState } from 'react';
import { ToggleLeft, ToggleRight } from 'lucide-react';

const LanguageContent = {
  english: {
    title: "Learn More",
    introduction: "UrduWebify is an innovative platform that allows users to convert Urdu voice inputs into interactive web pages using AI-powered technology.",
    howToUse: [
      "Click the microphone button to start recording your Urdu voice input.",
      "Once done, click the upload button to generate your web page.",
      "View the AI-generated web page on the right side of the screen."
    ],
  },
  urdu: {
    title: "مزید سیکھیں",
    introduction: "اردو ویبفائی ایک جدید پلیٹ فارم ہے جو صارفین کو اردو وائس ان پٹس کو مصنوعی ذہانت کی طاقت سے انٹرایکٹو ویب صفحات میں تبدیل کرنے کی اجازت دیتا ہے۔",
    howToUse: [
      "ریکارڈنگ شروع کرنے کے لیے مائیکروفون کے بٹن پر کلک کریں۔",
      "ختم ہونے کے بعد، ویب صفحہ بنانے کے لیے اپ لوڈ بٹن پر کلک کریں۔",
      "اسکرین کے دائیں جانب AI کے تیار کردہ ویب صفحہ کو دیکھیں۔"
    ],
  },
};

const LearnMore = () => {
  const [language, setLanguage] = useState('english');
  const currentContent = LanguageContent[language];

  const toggleLanguage = () => {
    setLanguage(language === 'english' ? 'urdu' : 'english');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-purple-950 text-white font-mono">
      {/* Navbar */}
      <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="text-2xl font-mono font-bold text-purple-400">
          {currentContent.title}
        </div>
        <div onClick={toggleLanguage} className="cursor-pointer flex items-center">
          {language === 'english' ? <ToggleLeft className="text-purple-400" /> : <ToggleRight className="text-purple-400" />}
          <span className="ml-2 text-purple-400 font-mono">{language === 'english' ? 'اردو' : 'English'}</span>
        </div>
      </nav>

      {/* Introduction Section */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-mono font-bold text-purple-200 mb-6">
          {language === 'english' ? 'Introduction' : 'تعارف'}
        </h2>
        <p className="text-lg text-gray-300">{currentContent.introduction}</p>
      </section>

      {/* How to Use Section */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-mono font-bold text-purple-200 mb-6">
          {language === 'english' ? 'How to Use' : 'استعمال کرنے کا طریقہ'}
        </h2>
        <ul className="space-y-4 text-lg text-gray-300 list-disc pl-6">
          {currentContent.howToUse.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ul>
      </section>

      {/* Footer */}
      <footer className="bg-purple-950 font-mono py-8">
        <div className="container mx-auto px-6 text-center">
          <p>© 2024 UrduWebify. All Rights Reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LearnMore;
