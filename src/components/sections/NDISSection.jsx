import { useState, useEffect, useRef } from 'react';
import { NDIS_INFO, COMPANY_INFO } from '../../utils/constants.js';
import { getNDISServices } from '../../data/services.js';
import { getNDISTestimonials } from '../../data/testimonials.js';
import { formatCurrency } from '../../utils/helpers.js';
import Button from '../common/Button.jsx';
import { scrollToElement } from '../../utils/helpers.js';

const NDISSection = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);
  const ndisServices = getNDISServices();
  const ndisTestimonials = getNDISTestimonials();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'eligibility', label: 'Eligibility' },
    { id: 'services', label: 'Services' },
    { id: 'invoicing', label: 'Invoicing' }
  ];

  const handleBookNDIS = () => {
    scrollToElement('quote-calculator', 80);
  };

  const handleContact = () => {
    scrollToElement('contact-section', 80);
  };

  const handleCallNow = () => {
    window.location.href = `tel:${COMPANY_INFO.phone}`;
  };

  return (
    <section ref={sectionRef} className="section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl relative overflow-hidden" id="ndis">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="container mx-auto relative z-10">
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-gradient-to-r from-blue-100/80 via-white/90 to-blue-100/80 backdrop-blur-xl border-2 border-blue-200/50 rounded-full px-4 py-2 mb-8 shadow-lg hover:shadow-2xl transition-all duration-700 hover:scale-105 animate-fade-in-up">
            <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full mr-2 animate-pulse"></div>
            <span className="text-sm font-black text-blue-700">NDIS Approved Provider</span>
          </div>
          
          <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up delay-300">
            NDIS Support <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Cleaning — Made Easy</span>
          </h2>
          
          <p className="text-base text-[#4B4B4B] max-w-3xl mx-auto font-medium animate-fade-in-up delay-600">
            We work with self-managed and plan-managed participants to provide routine or one-off 
            cleaning services that meet your NDIS goals.
          </p>
        </div>

        <div className="relative group mb-12 animate-fade-in-up delay-800">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
          <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu">
            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-t-3xl"></div>
            
            <div className="border-b border-white/20 relative z-10">
              <nav className="flex">
                {tabs.map((tab, index) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`relative flex-1 px-6 py-4 text-sm font-black transition-all duration-700 hover:scale-105 hover:-translate-y-1 transform-gpu group/tab overflow-hidden ${
                      activeTab === tab.id
                        ? 'text-[#006da6] bg-gradient-to-r from-[#006da6]/10 via-white/50 to-[#0080c7]/10'
                        : 'text-[#4B4B4B] hover:text-[#006da6] hover:bg-gradient-to-r hover:from-[#006da6]/5 hover:to-[#0080c7]/5'
                    }`}
                    style={{ animationDelay: `${1000 + index * 100}ms` }}
                  >
                    <span className="relative z-10">{tab.label}</span>
                    {activeTab === tab.id && (
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full"></div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/tab:opacity-100 transition-opacity duration-700"></div>
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-8 relative z-10">
              {activeTab === 'overview' && (
                <div className="space-y-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="animate-fade-in-up delay-1200">
                      <h3 className="text-xl font-black text-gray-900 mb-4">Why Choose Our NDIS Services?</h3>
                      <ul className="space-y-3">
                        <li className="flex items-start group/item">
                          <div className="w-2 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mt-2 mr-3 flex-shrink-0 group-hover/item:animate-pulse"></div>
                          <span className="text-[#4B4B4B] font-medium group-hover/item:text-[#006da6] transition-colors duration-300">Clear invoices with service codes</span>
                        </li>
                        <li className="flex items-start group/item">
                          <div className="w-2 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mt-2 mr-3 flex-shrink-0 group-hover/item:animate-pulse"></div>
                          <span className="text-[#4B4B4B] font-medium group-hover/item:text-[#006da6] transition-colors duration-300">Flexible booking times</span>
                        </li>
                        <li className="flex items-start group/item">
                          <div className="w-2 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mt-2 mr-3 flex-shrink-0 group-hover/item:animate-pulse"></div>
                          <span className="text-[#4B4B4B] font-medium group-hover/item:text-[#006da6] transition-colors duration-300">We respect your privacy, space, and schedule</span>
                        </li>
                        <li className="flex items-start group/item">
                          <div className="w-2 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mt-2 mr-3 flex-shrink-0 group-hover/item:animate-pulse"></div>
                          <span className="text-[#4B4B4B] font-medium group-hover/item:text-[#006da6] transition-colors duration-300">Fast response and documentation for plan managers</span>
                        </li>
                      </ul>
                    </div>
                    
                    <div className="relative group/card animate-fade-in-up delay-1400">
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/card:opacity-30 transition-all duration-700"></div>
                      <div className="relative bg-gradient-to-r from-[#006da6]/10 via-white/80 to-[#0080c7]/10 backdrop-blur-lg rounded-2xl p-6 border-2 border-[#006da6]/20 shadow-lg hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover/card:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover/card:scale-x-100 transition-transform duration-700 rounded-t-2xl"></div>
                        
                        <div className="relative z-10">
                          <h4 className="font-black text-gray-900 mb-3 group-hover/card:text-[#006da6] transition-colors duration-500">Quick Facts</h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-[#666] font-semibold">Starting Price:</span>
                              <span className="font-black text-gray-900 group-hover/card:text-[#006da6] transition-colors duration-500">{formatCurrency(140)}/service</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-[#666] font-semibold">Response Time:</span>
                              <span className="font-black text-gray-900 group-hover/card:text-[#006da6] transition-colors duration-500">Within 2 hours</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-[#666] font-semibold">Service Areas:</span>
                              <span className="font-black text-gray-900 group-hover/card:text-[#006da6] transition-colors duration-500">All NSW</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-[#666] font-semibold">Documentation:</span>
                              <span className="font-black text-gray-900 group-hover/card:text-[#006da6] transition-colors duration-500">Complete</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover/card:scale-x-100 transition-transform duration-700 rounded-b-2xl"></div>
                      </div>
                    </div>
                  </div>

                  {ndisTestimonials.length > 0 && (
                    <div className="animate-fade-in-up delay-1600">
                      <h3 className="text-xl font-black text-gray-900 mb-6">What NDIS Participants Say</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {ndisTestimonials.slice(0, 2).map((testimonial, index) => (
                          <div key={testimonial.id} className="relative group/testimonial">
                            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/testimonial:opacity-30 transition-all duration-700"></div>
                            <div className="relative bg-gradient-to-br from-gray-50/80 via-white/90 to-gray-50/80 backdrop-blur-lg rounded-2xl p-6 border-2 border-white/40 shadow-lg hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                              <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover/testimonial:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover/testimonial:scale-x-100 transition-transform duration-700 rounded-t-2xl"></div>
                              
                              <div className="relative z-10">
                                <div className="flex items-center mb-3">
                                  <div className="flex text-yellow-400 mr-2">
                                    {[...Array(testimonial.rating)].map((_, i) => (
                                      <span key={i} className="group-hover/testimonial:animate-bounce" style={{ animationDelay: `${i * 100}ms` }}>★</span>
                                    ))}
                                  </div>
                                  <span className="text-sm text-[#666] font-semibold">{testimonial.location}</span>
                                </div>
                                <p className="text-[#4B4B4B] mb-3 italic font-medium group-hover/testimonial:text-[#333] transition-colors duration-500">"{testimonial.text}"</p>
                                <p className="text-sm font-black text-gray-900 group-hover/testimonial:text-[#006da6] transition-colors duration-500">- {testimonial.name}</p>
                              </div>
                              
                              <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover/testimonial:scale-x-100 transition-transform duration-700 rounded-b-2xl"></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
                            {activeTab === 'eligibility' && (
                <div className="space-y-6">
                  <div className="animate-fade-in-up delay-1200">
                    <h3 className="text-xl font-black text-gray-900 mb-4">Who Can Use Our NDIS Services?</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {NDIS_INFO.eligibility.map((type, index) => (
                        <div key={index} className="relative group/eligibility">
                          <div className="absolute -inset-1 bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 rounded-2xl blur opacity-0 group-hover/eligibility:opacity-30 transition-all duration-700"></div>
                          <div className="relative bg-gradient-to-br from-blue-50/80 via-white/90 to-blue-50/80 backdrop-blur-lg rounded-2xl p-6 text-center border-2 border-blue-200/50 shadow-lg hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-blue-600 transform scale-x-0 group-hover/eligibility:scale-x-100 transition-transform duration-700 rounded-t-2xl"></div>
                            <h4 className="font-black text-gray-900 mb-2 group-hover/eligibility:text-blue-600 transition-colors duration-500">{type}</h4>
                            <p className="text-sm text-[#4B4B4B] font-medium group-hover/eligibility:text-[#333] transition-colors duration-500">
                              {index === 0 && "You manage your own NDIS funds and choose your providers"}
                              {index === 1 && "Your plan manager handles payments and provider coordination"}
                              {index === 2 && "NDIA manages your plan with pre-approved services"}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'services' && (
                <div className="space-y-6">
                  {ndisServices.map((service, index) => (
                    <div key={service.id} className="relative group/service animate-fade-in-up" style={{ animationDelay: `${1200 + index * 200}ms` }}>
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/service:opacity-30 transition-all duration-700"></div>
                      <div className="relative border-2 border-white/40 rounded-2xl p-6 bg-white/90 backdrop-blur-xl shadow-lg hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover/service:scale-x-100 transition-transform duration-700 rounded-t-2xl"></div>
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="text-xl font-black text-gray-900 mb-2 group-hover/service:text-[#006da6] transition-colors duration-500">{service.title}</h3>
                            <p className="text-[#4B4B4B] font-medium group-hover/service:text-[#333] transition-colors duration-500">{service.description}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-black text-[#006da6] group-hover/service:text-black transition-colors duration-500">
                              {formatCurrency(service.basePrice)}
                            </div>
                            <div className="text-sm text-[#666] font-semibold">{service.duration}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'invoicing' && (
                <div className="space-y-6 animate-fade-in-up delay-1200">
                  <div>
                    <h3 className="text-xl font-black text-gray-900 mb-4">NDIS Compliant Invoicing</h3>
                    <p className="text-[#4B4B4B] mb-6 font-medium">
                      Our invoices meet all NDIS requirements and include all necessary information 
                      for your plan manager or NDIA review.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="relative group animate-fade-in-up delay-1800">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
          <div className="relative bg-gradient-to-r from-[#006da6]/10 via-white/80 to-[#0080c7]/10 backdrop-blur-xl rounded-3xl p-8 md:p-12 text-center shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-t-3xl"></div>
            
            <div className="relative z-10">
              <h3 className="text-2xl md:text-3xl font-black text-gray-900 mb-6 group-hover:text-[#006da6] transition-colors duration-500">
                Ready to Start Your NDIS Cleaning Service?
              </h3>
              <p className="text-base text-[#4B4B4B] mb-8 max-w-2xl mx-auto font-medium group-hover:text-[#333] transition-colors duration-500">
                Get started with a free consultation. We'll help you understand how our services 
                fit within your NDIS plan and provide a detailed quote.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
                <Button
                  onClick={handleBookNDIS}
                  className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-2 hover:rotate-1 shadow-xl hover:shadow-[0_15px_30px_rgba(0,0,0,0.3)] transform-gpu group/cta overflow-hidden"
                  style={{ transformStyle: 'preserve-3d' }}
                >
                  <span className="relative z-10 flex items-center gap-2">
                    <span className="text-lg group-hover/cta:animate-bounce">🛡️</span>
                    Book NDIS Service
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/cta:opacity-100 transition-opacity duration-700 transform group-hover/cta:translate-x-full"></div>
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-30 group-hover/cta:opacity-60 transition-opacity duration-700"></div>
                </Button>
                
                <Button
                  onClick={handleCallNow}
                  className="relative bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#180c2e] hover:to-[#2d1b4e] hover:text-white hover:border-[#180c2e] font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-2 shadow-xl hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    <span className="text-lg group-hover/btn:animate-pulse">📞</span>
                    Call {COMPANY_INFO.phone}
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                </Button>
              </div>
              
              <div className="mt-8 text-sm text-[#666] font-medium group-hover:text-[#333] transition-colors duration-500">
                <p>✅ NDIS Compliant • 📋 Detailed Invoicing • 🤝 Respectful Service • ⚡ Quick Response</p>
              </div>
            </div>
            
            <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default NDISSection;

