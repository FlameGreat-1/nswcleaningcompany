import { useState, useEffect, useRef } from 'react';
import SEO from '../components/common/SEO.jsx';
import { 
  faqData, 
  getFAQCategories, 
  getFAQByCategory, 
  searchFAQs, 
  getTotalFAQs 
} from '../data/faq.js';
import { COMPANY_INFO } from '../utils/constants.js';
import Button from '../components/common/Button.jsx';

const FAQ = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [filteredFAQs, setFilteredFAQs] = useState(faqData);
  const [openItems, setOpenItems] = useState(new Set());
  const [isVisible, setIsVisible] = useState(false);
  const [searchVisible, setSearchVisible] = useState(false);
  const [faqsVisible, setFaqsVisible] = useState(false);
  const sectionRef = useRef(null);
  const searchRef = useRef(null);
  const faqsRef = useRef(null);

  const categories = getFAQCategories();
  const totalFAQs = getTotalFAQs();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const searchObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setSearchVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const faqsObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setFaqsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }
    if (searchRef.current) {
      searchObserver.observe(searchRef.current);
    }
    if (faqsRef.current) {
      faqsObserver.observe(faqsRef.current);
    }

    return () => {
      observer.disconnect();
      searchObserver.disconnect();
      faqsObserver.disconnect();
    };
  }, []);

  useEffect(() => {
    filterFAQs();
  }, [searchTerm, selectedCategory]);

  const filterFAQs = () => {
    let filtered = faqData;

    if (searchTerm.trim()) {
      filtered = searchFAQs(searchTerm);
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(faq => 
        faq.category.toLowerCase() === selectedCategory.toLowerCase()
      );
    }

    setFilteredFAQs(filtered);
    setOpenItems(new Set());
  };

  const toggleItem = (id) => {
    const newOpenItems = new Set(openItems);
    if (newOpenItems.has(id)) {
      newOpenItems.delete(id);
    } else {
      newOpenItems.add(id);
    }
    setOpenItems(newOpenItems);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setSelectedCategory('all');
  };

  const handleContact = () => {
    window.location.href = '/contact';
  };

  const handleCallNow = () => {
    window.location.href = `tel:${COMPANY_INFO.phone}`;
  };

  const handleGetQuote = () => {
    window.location.href = '/quote';
  };

  const getCategoryColor = (category) => {
    const colors = {
      'General': 'from-blue-500 to-blue-600 text-white',
      'Pricing': 'from-[#006da6] to-[#0080c7] text-white',
      'NDIS': 'from-purple-500 to-purple-600 text-white',
      'Services': 'from-orange-500 to-orange-600 text-white',
      'Booking': 'from-indigo-500 to-indigo-600 text-white',
      'Bond Cleaning': 'from-red-500 to-red-600 text-white',
      'Payment': 'from-yellow-500 to-yellow-600 text-black',
      'Insurance': 'from-gray-500 to-gray-600 text-white',
      'Quality': 'from-pink-500 to-pink-600 text-white'
    };
    return colors[category] || 'from-gray-500 to-gray-600 text-white';
  };

  return (
    <>
      <SEO
        title="Frequently Asked Questions - Cleaning Services FAQ"
        description="Find answers to common questions about our professional cleaning services, NDIS support, pricing, booking process, and service areas across NSW."
        keywords="cleaning services FAQ, NDIS cleaning questions, cleaning service answers, NSW cleaning FAQ, professional cleaning questions"
      />

      <main className="relative pt-24 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
        </div>

        <section ref={sectionRef} className="relative z-10 section-padding bg-white">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center mb-20">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-black mb-8 animate-fade-in-up leading-tight">
                Frequently Asked <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] bg-clip-text text-transparent">Questions</span>
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed mb-12 font-medium animate-fade-in-up delay-300">
                Find answers to common questions about our professional cleaning services
              </p>
              
              <div className="relative group animate-fade-in-up delay-500">
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-gradient-to-r from-[#006da6]/10 via-white/80 to-[#0080c7]/10 backdrop-blur-xl border-2 border-[#006da6]/30 rounded-3xl p-6 inline-block hover:border-[#006da6]/50 transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu shadow-xl hover:shadow-2xl overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                  <div className="relative z-10">
                    <p className="text-sm text-gray-700 font-medium group-hover:text-gray-900 transition-colors duration-500">
                      <span className="font-black text-[#0080c7] text-lg group-hover:text-black transition-colors duration-500">{totalFAQs} questions</span> answered to help you make informed decisions
                    </p>
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section ref={searchRef} className="relative z-10 section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto">
              <div className="relative group animate-fade-in-up">
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu mb-16 overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                  
                  <div className="relative z-10">
                    <div className="flex flex-col md:flex-row gap-6 mb-8">
                      <div className="flex-1 relative group/search">
                        <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-2xl blur opacity-0 group-hover/search:opacity-30 transition-all duration-500"></div>
                        <input
                          type="text"
                          placeholder="Search questions..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="relative w-full px-6 py-4 border-2 border-[#006da6]/30 rounded-2xl focus:outline-none focus:border-[#006da6] focus:ring-4 focus:ring-[#006da6]/20 transition-all duration-500 bg-white/90 backdrop-blur-lg shadow-lg focus:shadow-2xl font-medium text-gray-900 placeholder-gray-500 hover:border-[#006da6]/50 hover:shadow-xl group-hover/search:scale-105 transform-gpu"
                        />
                        <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                          <div className="w-6 h-6 text-[#006da6] group-hover/search:animate-pulse">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                          </div>
                        </div>
                      </div>
                      
                      <div className="relative group/select">
                        <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-2xl blur opacity-0 group-hover/select:opacity-30 transition-all duration-500"></div>
                        <select
                          value={selectedCategory}
                          onChange={(e) => setSelectedCategory(e.target.value)}
                          className="relative px-6 py-4 border-2 border-[#006da6]/30 rounded-2xl focus:outline-none focus:border-[#006da6] focus:ring-4 focus:ring-[#006da6]/20 transition-all duration-500 bg-white/90 backdrop-blur-lg shadow-lg focus:shadow-2xl font-medium text-gray-900 hover:border-[#006da6]/50 hover:shadow-xl group-hover/select:scale-105 transform-gpu min-w-[200px]"
                        >
                          <option value="all">All Categories</option>
                          {categories.map((category) => (
                            <option key={category} value={category.toLowerCase()}>
                              {category}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {(searchTerm || selectedCategory !== 'all') && (
                      <div className="flex items-center justify-between bg-gradient-to-r from-[#006da6]/10 via-white/50 to-[#0080c7]/10 backdrop-blur-lg border border-[#006da6]/20 rounded-2xl p-4">
                        <p className="text-sm text-gray-600 font-medium">
                          Showing <span className="font-black text-[#006da6]">{filteredFAQs.length}</span> of <span className="font-black">{totalFAQs}</span> questions
                          {searchTerm && <span className="text-gray-800"> for "<span className="font-black text-[#0080c7]">{searchTerm}</span>"</span>}
                          {selectedCategory !== 'all' && <span className="text-gray-800"> in <span className="font-black text-[#0080c7]">{selectedCategory}</span></span>}
                        </p>
                        <button
                          onClick={handleClearSearch}
                          className="relative group/clear text-sm text-[#006da6] hover:text-white font-black px-4 py-2 rounded-xl bg-transparent hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#0080c7] transition-all duration-500 hover:scale-110 hover:-translate-y-1 transform-gpu shadow-lg hover:shadow-2xl overflow-hidden"
                        >
                          <span className="relative z-10">Clear filters</span>
                          <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/clear:opacity-100 transition-opacity duration-500 rounded-xl"></div>
                        </button>
                      </div>
                    )}
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                </div>
              </div>
              {filteredFAQs.length === 0 ? (
                <div className="relative group animate-fade-in-up delay-300">
                  <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                  <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-16 text-center shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                    <div className="relative z-10">
                      <div className="text-8xl mb-8 animate-bounce">🔍</div>
                      <h3 className="text-2xl font-black text-gray-900 mb-6 group-hover:text-[#006da6] transition-colors duration-500">No questions found</h3>
                      <p className="text-gray-600 mb-8 font-medium group-hover:text-gray-800 transition-colors duration-500">
                        Try adjusting your search terms or browse all categories
                      </p>
                      <Button 
                        onClick={handleClearSearch}
                        className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] hover:from-black hover:to-gray-800 text-white hover:text-white font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-2 shadow-2xl hover:shadow-[0_20px_40px_rgba(0,0,0,0.4)] transform-gpu group/btn overflow-hidden"
                      >
                        <span className="relative z-10 flex items-center gap-2">
                          <span className="text-xl group-hover/btn:animate-bounce">👀</span>
                          View All Questions
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 transform group-hover/btn:translate-x-full"></div>
                      </Button>
                    </div>
                  </div>
                </div>
              ) : (
                <div ref={faqsRef} className="space-y-6">
                  {filteredFAQs.map((faq, index) => (
                    <div 
                      key={faq.id} 
                      className="relative group animate-fade-in-up"
                      style={{ animationDelay: `${faqsVisible ? 100 + index * 100 : 0}ms` }}
                    >
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                      <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu border-2 border-white/40 overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                        
                        <button
                          onClick={() => toggleItem(faq.id)}
                          className="relative z-10 w-full px-8 py-6 text-left hover:bg-white/50 transition-all duration-500 focus:outline-none focus:bg-white/50 group/button"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-4 mb-4">
                                <div className="relative group/badge">
                                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-2xl blur opacity-0 group-hover/badge:opacity-40 transition-all duration-500"></div>
                                  <span className={`relative px-4 py-2 rounded-2xl text-xs font-black bg-gradient-to-r ${getCategoryColor(faq.category)} shadow-lg hover:shadow-xl transition-all duration-500 hover:scale-110 transform-gpu`}>
                                    {faq.category}
                                  </span>
                                </div>
                              </div>
                              <h3 className="text-lg md:text-xl font-black text-gray-900 pr-4 group-hover/button:text-[#006da6] transition-colors duration-500 leading-tight">
                                {faq.question}
                              </h3>
                            </div>
                            <div className="relative group/arrow">
                              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-0 group-hover/arrow:opacity-40 transition-all duration-500"></div>
                              <div className={`relative w-12 h-12 bg-white/80 backdrop-blur-lg border-2 border-[#006da6]/30 rounded-full flex items-center justify-center transition-all duration-500 hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#0080c7] hover:border-[#006da6] hover:scale-110 transform-gpu shadow-lg hover:shadow-xl ${
                                openItems.has(faq.id) ? 'rotate-180 bg-gradient-to-r from-[#006da6] to-[#0080c7] border-[#006da6]' : ''
                              }`}>
                                <svg className={`w-6 h-6 transition-colors duration-500 ${openItems.has(faq.id) ? 'text-white' : 'text-gray-500 group-hover/arrow:text-white'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 9l-7 7-7-7" />
                                </svg>
                              </div>
                            </div>
                          </div>
                        </button>
                        
                        {openItems.has(faq.id) && (
                          <div className="relative z-10 px-8 pb-8 animate-fade-in-up">
                            <div className="border-t border-[#006da6]/20 pt-6">
                              <div className="relative group/answer">
                                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/answer:opacity-100 transition-opacity duration-500 rounded-2xl"></div>
                                <p className="relative text-gray-700 leading-relaxed font-medium text-base group-hover/answer:text-gray-900 transition-colors duration-500">
                                  {faq.answer}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="relative z-10 section-padding bg-white">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto">
              <div className="relative group">
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-gradient-to-r from-[#006da6]/10 via-white/80 to-blue-50/80 backdrop-blur-xl rounded-3xl p-8 md:p-16 text-center shadow-2xl border-2 border-[#006da6]/30 hover:border-[#006da6]/50 transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-blue-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                  
                  <div className="relative z-10">
                    <h2 className="text-3xl md:text-4xl font-black text-black mb-8 group-hover:text-[#006da6] transition-colors duration-500">
                      Still Have Questions?
                    </h2>
                    <p className="text-lg text-gray-600 mb-12 max-w-2xl mx-auto font-medium leading-relaxed group-hover:text-gray-800 transition-colors duration-500">
                      Can't find the answer you're looking for? Our friendly team is here to help you with any questions about our cleaning services.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-6 justify-center">
                      <Button
                        onClick={handleCallNow}
                        className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] hover:from-black hover:to-gray-800 text-white hover:text-white font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-3 hover:rotate-1 shadow-2xl hover:shadow-[0_20px_40px_rgba(0,0,0,0.4)] transform-gpu group/btn overflow-hidden"
                        style={{ transformStyle: 'preserve-3d' }}
                      >
                        <span className="relative z-10 flex items-center gap-2">
                          <span className="text-xl group-hover/btn:animate-bounce">📞</span>
                          Call {COMPANY_INFO.phone}
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 transform group-hover/btn:translate-x-full"></div>
                        <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-30 group-hover/btn:opacity-60 transition-opacity duration-700"></div>
                      </Button>
                      
                      <Button
                        onClick={handleContact}
                        className="relative bg-transparent border-3 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-black hover:to-gray-800 hover:text-white hover:border-black font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-3 hover:-rotate-1 shadow-2xl hover:shadow-[0_20px_40px_rgba(0,0,0,0.3)] transform-gpu group/btn overflow-hidden"
                        style={{ transformStyle: 'preserve-3d' }}
                      >
                        <span className="relative z-10 flex items-center gap-2">
                          <span className="text-xl group-hover/btn:animate-pulse">💬</span>
                          Send Message
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                      </Button>

                      <Button
                        onClick={handleGetQuote}
                        className="relative bg-gradient-to-r from-black to-gray-800 hover:from-gray-800 hover:to-black text-white hover:text-[#006da6] font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-3 hover:rotate-1 shadow-2xl hover:shadow-[0_20px_40px_rgba(0,0,0,0.4)] transform-gpu group/btn overflow-hidden"
                        style={{ transformStyle: 'preserve-3d' }}
                      >
                        <span className="relative z-10 flex items-center gap-2">
                          <span className="text-xl group-hover/btn:animate-spin">💰</span>
                          Get Quote
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700"></div>
                      </Button>
                    </div>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-blue-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="relative z-10 section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl">
          <div className="container mx-auto">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
                  Quick Help <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] bg-clip-text text-transparent">Topics</span>
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                  { emoji: "💰", title: "Pricing & Quotes", desc: "Learn about our transparent pricing structure and how to get accurate quotes", category: "pricing" },
                  { emoji: "🏥", title: "NDIS Services", desc: "Everything you need to know about our NDIS cleaning support services", category: "ndis" },
                  { emoji: "📅", title: "Booking & Scheduling", desc: "Find out how to book services and manage your cleaning schedule", category: "booking" }
                ].map((topic, index) => (
                  <div key={index} className="relative group animate-fade-in-up" style={{ animationDelay: `${400 + index * 200}ms` }}>
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                    <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu border-2 border-white/40 text-center overflow-hidden h-full flex flex-col">
                      <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                      <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                      
                      <div className="relative z-10 flex flex-col h-full">
                        <div className="text-6xl mb-6 group-hover:animate-bounce">{topic.emoji}</div>
                        <h3 className="text-xl font-black text-gray-900 mb-4 group-hover:text-[#006da6] transition-colors duration-500">{topic.title}</h3>
                        <p className="text-gray-600 mb-6 text-sm leading-relaxed font-medium flex-grow group-hover:text-gray-800 transition-colors duration-500">
                          {topic.desc}
                        </p>
                        <button
                          onClick={() => setSelectedCategory(topic.category)}
                          className="relative text-[#006da6] hover:text-white font-black text-sm bg-transparent hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#0080c7] px-6 py-3 rounded-2xl border-2 border-[#006da6] hover:border-[#006da6] transition-all duration-500 hover:scale-110 hover:-translate-y-1 transform-gpu shadow-lg hover:shadow-2xl group/btn overflow-hidden mt-auto"
                        >
                          <span className="relative z-10">View {topic.title.split(' ')[0]} FAQs</span>
                          <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                        </button>
                      </div>
                      
                      <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
};

export default FAQ;


