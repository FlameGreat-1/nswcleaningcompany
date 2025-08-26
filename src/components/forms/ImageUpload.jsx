import { useState, useRef, useEffect } from 'react';
import SEO from '../components/common/SEO.jsx';
import ContactSection from '../components/sections/ContactSection.jsx';
import { COMPANY_INFO, BUSINESS_HOURS, SERVICE_AREAS } from '../utils/constants.js';
import { formatPhone } from '../utils/helpers.js';
import Button from '../components/common/Button.jsx';

const Contact = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [contactMethodsVisible, setContactMethodsVisible] = useState(false);
  const [businessInfoVisible, setBusinessInfoVisible] = useState(false);
  const sectionRef = useRef(null);
  const contactMethodsRef = useRef(null);
  const businessInfoRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const contactMethodsObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setContactMethodsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const businessInfoObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setBusinessInfoVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }
    if (contactMethodsRef.current) {
      contactMethodsObserver.observe(contactMethodsRef.current);
    }
    if (businessInfoRef.current) {
      businessInfoObserver.observe(businessInfoRef.current);
    }

    return () => {
      observer.disconnect();
      contactMethodsObserver.disconnect();
      businessInfoObserver.disconnect();
    };
  }, []);

  const handleCallNow = () => {
    window.location.href = `tel:${COMPANY_INFO.phone}`;
  };

  const handleEmailSupport = () => {
    window.location.href = `mailto:${COMPANY_INFO.email.support}`;
  };

  const handleEmailBookings = () => {
    window.location.href = `mailto:${COMPANY_INFO.email.bookings}`;
  };

  const handleGetQuote = () => {
    window.location.href = '/quote';
  };

  const contactMethods = [
    {
      title: 'Phone',
      value: formatPhone(COMPANY_INFO.phone),
      description: 'Call us for immediate assistance',
      action: handleCallNow,
      buttonText: 'Call Now',
      icon: '📞',
      gradient: 'from-[#006da6] to-[#0080c7]'
    },
    {
      title: 'Email Support',
      value: COMPANY_INFO.email.support,
      description: 'General inquiries and support',
      action: handleEmailSupport,
      buttonText: 'Send Email',
      icon: '📧',
      gradient: 'from-[#006da6] to-[#005a8a]'
    },
    {
      title: 'Email Bookings',
      value: COMPANY_INFO.email.bookings,
      description: 'Service bookings and scheduling',
      action: handleEmailBookings,
      buttonText: 'Send Email',
      icon: '📅',
      gradient: 'from-[#180c2e] to-[#2d1b4e]'
    }
  ];

  const responseTimeInfo = [
    {
      method: 'Phone Calls',
      time: 'Immediate',
      availability: 'Business Hours',
      icon: '⚡'
    },
    {
      method: 'Email Inquiries',
      time: 'Within 2 hours',
      availability: 'Business Days',
      icon: '📨'
    },
    {
      method: 'Quote Requests',
      time: 'Within 1 hour',
      availability: '7 Days a Week',
      icon: '💰'
    },
    {
      method: 'Emergency Services',
      time: 'Within 30 minutes',
      availability: '24/7 Available',
      icon: '🚨'
    }
  ];

  return (
    <>
      <SEO
        title="Contact Us - Get Your Free Cleaning Quote"
        description="Contact NSW Cleaning Company for professional cleaning services. Call us, email us, or request a free quote online. Fast response times and excellent customer service."
        keywords="contact NSW cleaning company, cleaning quote, professional cleaners contact, cleaning services inquiry, book cleaning service"
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
                Get in <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Touch</span>
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed font-medium animate-fade-in-up delay-300">
                Ready to book your cleaning service? We're here to help with any questions or special requests.
              </p>
            </div>

            <div ref={contactMethodsRef} className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
              {contactMethods.map((method, index) => (
                <div 
                  key={index} 
                  className="relative group animate-fade-in-up"
                  style={{ animationDelay: `${contactMethodsVisible ? 400 + index * 200 : 0}ms` }}
                >
                  <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                  <div className="relative bg-white/90 backdrop-blur-xl border-2 border-white/40 rounded-3xl p-8 text-center shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu overflow-hidden h-full flex flex-col">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                    
                    <div className="relative z-10 flex flex-col h-full">
                      <div className="relative group/icon mb-6">
                        <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full blur opacity-0 group-hover/icon:opacity-40 transition-all duration-500"></div>
                        <div className="relative text-6xl group-hover/icon:animate-bounce group-hover/icon:scale-110 transition-transform duration-500">{method.icon}</div>
                      </div>
                      
                      <h3 className="text-xl font-black text-gray-900 mb-3 group-hover:text-[#006da6] transition-colors duration-500">{method.title}</h3>
                      <p className="text-[#006da6] font-black mb-3 text-lg group-hover:scale-105 transition-transform duration-500">{method.value}</p>
                      <p className="text-sm text-gray-600 mb-8 font-medium flex-grow group-hover:text-gray-800 transition-colors duration-500">{method.description}</p>
                      
                      <Button
                        onClick={method.action}
                        className={`relative bg-gradient-to-r ${method.gradient} hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-6 py-3 rounded-full text-sm transition-all duration-700 hover:scale-110 hover:-translate-y-2 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden mt-auto`}
                      >
                        <span className="relative z-10 flex items-center justify-center gap-2">
                          <span className="text-lg group-hover/btn:animate-pulse">{method.icon}</span>
                          {method.buttonText}
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 transform group-hover/btn:translate-x-full"></div>
                      </Button>
                    </div>
                    
                    <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <ContactSection />

        <section ref={businessInfoRef} className="relative z-10 section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl">
          <div className="container mx-auto">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-20">
                <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
                  Business <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Information</span>
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto font-medium animate-fade-in-up delay-300">
                  Everything you need to know about our availability and service areas
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20">
                <div className="relative group animate-fade-in-up" style={{ animationDelay: `${businessInfoVisible ? 400 : 0}ms` }}>
                  <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                  <div className="relative bg-white/90 backdrop-blur-xl border-2 border-white/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                    
                    <div className="relative z-10">
                      <h3 className="text-xl font-black text-gray-900 mb-8 group-hover:text-[#006da6] transition-colors duration-500">Business Hours</h3>
                      <div className="space-y-6">
                        {Object.entries(BUSINESS_HOURS).map(([day, hours]) => (
                          <div key={day} className="relative group/day flex justify-between items-center border-b border-[#006da6]/20 pb-4">
                            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/day:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                            <span className="relative text-gray-700 capitalize font-black group-hover/day:text-[#006da6] transition-colors duration-500">{day}</span>
                            <span className={`relative font-black transition-colors duration-500 ${hours === 'Closed' ? 'text-red-600' : 'text-gray-900 group-hover/day:text-[#006da6]'}`}>{hours}</span>
                          </div>
                        ))}
                      </div>
                      <div className="relative group/emergency mt-8">
                        <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/emergency:opacity-20 transition-all duration-500"></div>
                        <div className="relative p-6 bg-gradient-to-r from-[#006da6]/10 via-white/80 to-[#005a8a]/10 backdrop-blur-lg border-2 border-[#006da6]/30 rounded-2xl hover:border-[#006da6]/50 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                          <p className="relative text-sm text-[#005a8a] font-black group-hover/emergency:text-[#180c2e] transition-colors duration-500">
                            Emergency and urgent cleaning services available outside regular hours
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                  </div>
                </div>
                <div className="relative group animate-fade-in-up" style={{ animationDelay: `${businessInfoVisible ? 600 : 0}ms` }}>
                  <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                  <div className="relative bg-white/90 backdrop-blur-xl border-2 border-white/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                    
                    <div className="relative z-10">
                      <h3 className="text-xl font-black text-gray-900 mb-8 group-hover:text-[#006da6] transition-colors duration-500">Service Areas</h3>
                      <div className="grid grid-cols-2 gap-4 mb-8">
                        {SERVICE_AREAS.map((area, index) => (
                          <div key={index} className="relative group/area flex items-center">
                            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/area:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                            <div className="relative w-3 h-3 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full mr-4 group-hover/area:animate-pulse shadow-lg"></div>
                            <span className="relative text-gray-700 font-medium group-hover/area:text-[#006da6] transition-colors duration-500">{area}</span>
                          </div>
                        ))}
                      </div>
                      <div className="relative group/note">
                        <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-2xl blur opacity-0 group-hover/note:opacity-20 transition-all duration-500"></div>
                        <div className="relative p-6 bg-gradient-to-r from-[#006da6]/10 via-white/80 to-[#0080c7]/10 backdrop-blur-lg border-2 border-[#006da6]/30 rounded-2xl hover:border-[#006da6]/50 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                          <p className="text-sm text-[#006da6] font-black mb-2 group-hover/note:text-[#005a8a] transition-colors duration-500">
                            Don't see your area listed?
                          </p>
                          <p className="text-sm text-[#0080c7] font-medium group-hover/note:text-[#006da6] transition-colors duration-500">
                            Contact us to check availability in your location. We're always expanding our service areas.
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                  </div>
                </div>
              </div>

              <div className="relative group animate-fade-in-up" style={{ animationDelay: `${businessInfoVisible ? 800 : 0}ms` }}>
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-white/90 backdrop-blur-xl border-2 border-white/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                  
                  <div className="relative z-10">
                    <h3 className="text-xl font-black text-gray-900 mb-8 text-center group-hover:text-[#006da6] transition-colors duration-500">
                      Response Times
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      {responseTimeInfo.map((info, index) => (
                        <div key={index} className="relative group/response text-center">
                          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/response:opacity-30 transition-all duration-500"></div>
                          <div className="relative p-6 bg-gradient-to-r from-gray-50/90 via-white/90 to-gray-50/90 backdrop-blur-lg border border-white/40 rounded-2xl hover:bg-white/90 transition-all duration-500 hover:scale-105 hover:-translate-y-2 transform-gpu shadow-lg hover:shadow-xl overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover/response:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#006da6] to-transparent transform scale-x-0 group-hover/response:scale-x-100 transition-transform duration-700"></div>
                            <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#006da6] rounded-full opacity-0 group-hover/response:opacity-100 animate-ping transition-opacity duration-700"></div>
                            
                            <div className="relative z-10">
                              <div className="relative group/response-icon mb-4">
                                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full blur opacity-0 group-hover/response-icon:opacity-40 transition-all duration-500"></div>
                                <div className="relative text-3xl group-hover/response-icon:animate-bounce group-hover/response-icon:scale-110 transition-transform duration-500">{info.icon}</div>
                              </div>
                              <h4 className="font-black text-gray-900 text-sm mb-2 group-hover/response:text-[#006da6] transition-colors duration-500">{info.method}</h4>
                              <p className="text-[#006da6] font-black text-lg mb-1 group-hover/response:scale-105 transition-transform duration-500">{info.time}</p>
                              <p className="text-xs text-gray-600 font-medium group-hover/response:text-gray-800 transition-colors duration-500">{info.availability}</p>
                            </div>
                            
                            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover/response:scale-x-100 transition-transform duration-700"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="relative z-10 section-padding bg-white">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center">
              <div className="relative group">
                <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-white/90 backdrop-blur-xl border-2 border-white/40 rounded-3xl p-12 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                  
                  <div className="relative z-10">
                    <div className="relative group/cta-icon mb-8">
                      <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full blur opacity-0 group-hover/cta-icon:opacity-40 transition-all duration-500"></div>
                      <div className="relative text-6xl group-hover/cta-icon:animate-bounce group-hover/cta-icon:scale-110 transition-transform duration-500">🎯</div>
                    </div>
                    
                    <h2 className="text-3xl md:text-4xl font-black text-gray-900 mb-6 group-hover:text-[#006da6] transition-colors duration-500">
                      Ready to Get Started?
                    </h2>
                    <p className="text-lg text-gray-600 mb-10 font-medium group-hover:text-gray-800 transition-colors duration-500">
                      Don't wait - contact us today for your free cleaning quote and experience the difference professional cleaning makes.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
                      <Button
                        onClick={handleGetQuote}
                        className="relative bg-gradient-to-r from-[#006da6] to-[#0080c7] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white font-black px-8 py-4 rounded-full text-lg transition-all duration-700 hover:scale-110 hover:-translate-y-2 shadow-lg hover:shadow-2xl transform-gpu group/quote-btn overflow-hidden"
                      >
                        <span className="relative z-10 flex items-center gap-3">
                          <span className="text-2xl group-hover/quote-btn:animate-pulse">💰</span>
                          Get Free Quote
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/quote-btn:opacity-100 transition-opacity duration-700 transform group-hover/quote-btn:translate-x-full"></div>
                      </Button>
                      
                      <Button
                        onClick={handleCallNow}
                        className="relative bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#005a8a] hover:text-white hover:border-transparent font-black px-8 py-4 rounded-full text-lg transition-all duration-700 hover:scale-110 hover:-translate-y-2 shadow-lg hover:shadow-2xl transform-gpu group/call-btn overflow-hidden"
                      >
                        <span className="relative z-10 flex items-center gap-3">
                          <span className="text-2xl group-hover/call-btn:animate-pulse">📞</span>
                          Call {formatPhone(COMPANY_INFO.phone)}
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#005a8a]/10 opacity-0 group-hover/call-btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                      </Button>
                    </div>
                    
                    <div className="mt-10 pt-8 border-t border-[#006da6]/20">
                      <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-600">
                        <div className="relative group/feature flex items-center gap-2">
                          <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/feature:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                          <span className="relative text-[#006da6] text-lg group-hover/feature:animate-bounce">✅</span>
                          <span className="relative font-medium group-hover/feature:text-[#006da6] transition-colors duration-500">Free Quotes</span>
                        </div>
                        <div className="relative group/feature flex items-center gap-2">
                          <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/feature:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                          <span className="relative text-[#006da6] text-lg group-hover/feature:animate-bounce">⚡</span>
                          <span className="relative font-medium group-hover/feature:text-[#006da6] transition-colors duration-500">Fast Response</span>
                        </div>
                        <div className="relative group/feature flex items-center gap-2">
                          <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/feature:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                          <span className="relative text-[#006da6] text-lg group-hover/feature:animate-bounce">🛡️</span>
                          <span className="relative font-medium group-hover/feature:text-[#006da6] transition-colors duration-500">Fully Insured</span>
                        </div>
                        <div className="relative group/feature flex items-center gap-2">
                          <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/feature:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                          <span className="relative text-[#006da6] text-lg group-hover/feature:animate-bounce">⭐</span>
                          <span className="relative font-medium group-hover/feature:text-[#006da6] transition-colors duration-500">5-Star Service</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="relative z-10 py-16 bg-gradient-to-br from-[#006da6]/5 via-white/60 to-[#0080c7]/5 backdrop-blur-xl">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center">
              <div className="relative group">
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover:opacity-20 transition-all duration-500"></div>
                <div className="relative bg-white/80 backdrop-blur-lg border border-white/40 rounded-2xl p-8 hover:bg-white/90 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                  
                  <div className="relative z-10">
                    <h3 className="text-xl font-black text-gray-900 mb-4 group-hover:text-[#006da6] transition-colors duration-500">
                      Need Help Choosing the Right Service?
                    </h3>
                    <p className="text-gray-600 mb-6 font-medium group-hover:text-gray-800 transition-colors duration-500">
                      Our cleaning experts are here to help you find the perfect cleaning solution for your needs and budget.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <a 
                        href="/services" 
                        className="relative inline-flex items-center justify-center gap-2 bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#005a8a] hover:text-white hover:border-transparent font-black px-6 py-3 rounded-full text-sm transition-all duration-700 hover:scale-105 hover:-translate-y-1 shadow-lg hover:shadow-xl transform-gpu group/services-btn overflow-hidden"
                      >
                        <span className="relative z-10 flex items-center gap-2">
                          <span className="text-lg group-hover/services-btn:animate-pulse">🧹</span>
                          View All Services
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#005a8a]/10 opacity-0 group-hover/services-btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                      </a>
                      <a 
                        href="/about" 
                        className="relative inline-flex items-center justify-center gap-2 bg-gradient-to-r from-[#180c2e] to-[#2d1b4e] hover:from-[#006da6] hover:to-[#0080c7] text-white font-black px-6 py-3 rounded-full text-sm transition-all duration-700 hover:scale-105 hover:-translate-y-1 shadow-lg hover:shadow-xl transform-gpu group/about-btn overflow-hidden"
                      >
                        <span className="relative z-10 flex items-center gap-2">
                          <span className="text-lg group-hover/about-btn:animate-pulse">ℹ️</span>
                          Learn About Us
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/about-btn:opacity-100 transition-opacity duration-700 transform group-hover/about-btn:translate-x-full"></div>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
};

export default Contact;



