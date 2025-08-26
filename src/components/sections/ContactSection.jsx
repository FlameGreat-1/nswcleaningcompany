import { useState, useRef, useEffect } from 'react';
import { COMPANY_INFO, BUSINESS_HOURS, SERVICE_AREAS } from '../../utils/constants.js';
import { formatPhone } from '../../utils/helpers.js';
import ContactForm from '../forms/ContactForm.jsx';
import Button from '../common/Button.jsx';

const ContactSection = () => {
  const [showMap, setShowMap] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [contactInfoVisible, setContactInfoVisible] = useState(false);
  const [formVisible, setFormVisible] = useState(false);
  const sectionRef = useRef(null);
  const contactInfoRef = useRef(null);
  const formRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const contactInfoObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setContactInfoVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const formObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setFormVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }
    if (contactInfoRef.current) {
      contactInfoObserver.observe(contactInfoRef.current);
    }
    if (formRef.current) {
      formObserver.observe(formRef.current);
    }

    return () => {
      observer.disconnect();
      contactInfoObserver.disconnect();
      formObserver.disconnect();
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

  const handleFormSuccess = (result) => {
    console.log('Contact form submitted successfully:', result);
  };

  const toggleMap = () => {
    setShowMap(!showMap);
  };

  const businessHoursArray = Object.entries(BUSINESS_HOURS).map(([day, hours]) => ({
    day: day.charAt(0).toUpperCase() + day.slice(1),
    hours
  }));

  return (
    <section ref={sectionRef} className="relative section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 dark:from-gray-900/80 dark:via-gray-800/60 dark:to-gray-900/80 backdrop-blur-xl overflow-hidden" id="contact-section">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 dark:bg-[#006da6]/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 dark:bg-[#0080c7]/8 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 dark:from-[#006da6]/10 dark:to-[#0080c7]/10 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="relative z-10 container mx-auto">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-black text-black dark:text-white mb-8 animate-fade-in-up leading-tight">
            Get in <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Touch</span>
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto font-medium leading-relaxed animate-fade-in-up delay-300">
            Ready to book your cleaning service? Contact us today for a free quote 
            or to discuss your specific cleaning needs.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20">
          <div ref={contactInfoRef} className="space-y-10">
            <div className="relative group animate-fade-in-up" style={{ animationDelay: `${contactInfoVisible ? 400 : 0}ms` }}>
              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border-2 border-white/40 dark:border-gray-700/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 dark:from-[#006da6]/10 dark:to-[#005a8a]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                
                <div className="relative z-10">
                  <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-8 group-hover:text-[#006da6] dark:group-hover:text-[#0080c7] transition-colors duration-500">Contact Information</h3>
                  
                  <div className="space-y-8">
                    <div className="relative group/contact-item">
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/contact-item:opacity-20 transition-all duration-500"></div>
                      <div className="relative flex items-start space-x-6 bg-white/80 dark:bg-gray-700/80 backdrop-blur-lg border border-white/40 dark:border-gray-600/40 rounded-2xl p-6 hover:bg-white/90 dark:hover:bg-gray-700/90 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                        <div className="relative group/icon">
                          <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/icon:opacity-40 transition-all duration-500"></div>
                          <div className="relative w-16 h-16 bg-gradient-to-br from-[#006da6]/20 via-white/80 to-[#005a8a]/20 dark:from-[#006da6]/30 dark:via-gray-700/80 dark:to-[#005a8a]/30 backdrop-blur-xl border-2 border-[#006da6]/30 dark:border-[#006da6]/40 rounded-2xl flex items-center justify-center flex-shrink-0 hover:border-[#006da6]/50 transition-all duration-500 hover:scale-110 hover:rotate-12 transform-gpu shadow-lg hover:shadow-2xl overflow-hidden"
                               style={{ transformStyle: 'preserve-3d' }}>
                            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#005a8a]/10 dark:from-[#006da6]/20 dark:to-[#005a8a]/20 opacity-0 group-hover/icon:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                            <span className="relative z-10 text-[#006da6] dark:text-[#0080c7] text-2xl group-hover/icon:animate-bounce">📞</span>
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-[#006da6] rounded-full opacity-0 group-hover/icon:opacity-100 animate-ping transition-opacity duration-700"></div>
                          </div>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-black text-gray-900 dark:text-white mb-2 group-hover/contact-item:text-[#006da6] dark:group-hover/contact-item:text-[#0080c7] transition-colors duration-500">Phone</h4>
                          <p className="text-gray-600 dark:text-gray-300 mb-4 font-medium group-hover/contact-item:text-gray-800 dark:group-hover/contact-item:text-gray-200 transition-colors duration-500">{formatPhone(COMPANY_INFO.phone)}</p>
                          <Button
                            onClick={handleCallNow}
                            className="relative bg-transparent border-2 border-[#006da6] text-[#006da6] dark:text-[#0080c7] dark:border-[#0080c7] hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#005a8a] hover:text-white font-black px-6 py-3 rounded-full text-sm transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                          >
                            <span className="relative z-10 flex items-center gap-2">
                              <span className="text-lg group-hover/btn:animate-pulse">📞</span>
                              Call Now
                            </span>
                            <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#005a8a]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                          </Button>
                        </div>
                      </div>
                    </div>
                    <div className="relative group/contact-item">
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/contact-item:opacity-20 transition-all duration-500"></div>
                      <div className="relative flex items-start space-x-6 bg-white/80 dark:bg-gray-700/80 backdrop-blur-lg border border-white/40 dark:border-gray-600/40 rounded-2xl p-6 hover:bg-white/90 dark:hover:bg-gray-700/90 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                        <div className="relative group/icon">
                          <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/icon:opacity-40 transition-all duration-500"></div>
                          <div className="relative w-16 h-16 bg-gradient-to-br from-[#006da6]/20 via-white/80 to-[#005a8a]/20 dark:from-[#006da6]/30 dark:via-gray-700/80 dark:to-[#005a8a]/30 backdrop-blur-xl border-2 border-[#006da6]/30 dark:border-[#006da6]/40 rounded-2xl flex items-center justify-center flex-shrink-0 hover:border-[#006da6]/50 transition-all duration-500 hover:scale-110 hover:rotate-12 transform-gpu shadow-lg hover:shadow-2xl overflow-hidden"
                               style={{ transformStyle: 'preserve-3d' }}>
                            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#005a8a]/10 dark:from-[#006da6]/20 dark:to-[#005a8a]/20 opacity-0 group-hover/icon:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                            <span className="relative z-10 text-[#006da6] dark:text-[#0080c7] text-2xl group-hover/icon:animate-bounce">✉️</span>
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-[#006da6] rounded-full opacity-0 group-hover/icon:opacity-100 animate-ping transition-opacity duration-700"></div>
                          </div>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-black text-gray-900 dark:text-white mb-2 group-hover/contact-item:text-[#006da6] dark:group-hover/contact-item:text-[#0080c7] transition-colors duration-500">Email</h4>
                          <div className="space-y-3">
                            <div className="relative group/email">
                              <p className="text-gray-600 dark:text-gray-300 text-sm font-medium mb-1">General Support:</p>
                              <button
                                onClick={handleEmailSupport}
                                className="relative text-[#006da6] dark:text-[#0080c7] hover:text-white font-black transition-all duration-500 hover:scale-105 inline-block transform-gpu"
                              >
                                <span className="relative z-10">{COMPANY_INFO.email.support}</span>
                                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-lg opacity-0 group-hover/email:opacity-100 transition-opacity duration-500 -z-10"></div>
                              </button>
                            </div>
                            <div className="relative group/email">
                              <p className="text-gray-600 dark:text-gray-300 text-sm font-medium mb-1">Bookings:</p>
                              <button
                                onClick={handleEmailBookings}
                                className="relative text-[#006da6] dark:text-[#0080c7] hover:text-white font-black transition-all duration-500 hover:scale-105 inline-block transform-gpu"
                              >
                                <span className="relative z-10">{COMPANY_INFO.email.bookings}</span>
                                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-lg opacity-0 group-hover/email:opacity-100 transition-opacity duration-500 -z-10"></div>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="relative group/contact-item">
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/contact-item:opacity-20 transition-all duration-500"></div>
                      <div className="relative flex items-start space-x-6 bg-white/80 dark:bg-gray-700/80 backdrop-blur-lg border border-white/40 dark:border-gray-600/40 rounded-2xl p-6 hover:bg-white/90 dark:hover:bg-gray-700/90 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                        <div className="relative group/icon">
                          <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/icon:opacity-40 transition-all duration-500"></div>
                          <div className="relative w-16 h-16 bg-gradient-to-br from-[#006da6]/20 via-white/80 to-[#005a8a]/20 dark:from-[#006da6]/30 dark:via-gray-700/80 dark:to-[#005a8a]/30 backdrop-blur-xl border-2 border-[#006da6]/30 dark:border-[#006da6]/40 rounded-2xl flex items-center justify-center flex-shrink-0 hover:border-[#006da6]/50 transition-all duration-500 hover:scale-110 hover:rotate-12 transform-gpu shadow-lg hover:shadow-2xl overflow-hidden"
                               style={{ transformStyle: 'preserve-3d' }}>
                            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#005a8a]/10 dark:from-[#006da6]/20 dark:to-[#005a8a]/20 opacity-0 group-hover/icon:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                            <span className="relative z-10 text-[#006da6] dark:text-[#0080c7] text-2xl group-hover/icon:animate-bounce">🏢</span>
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-[#006da6] rounded-full opacity-0 group-hover/icon:opacity-100 animate-ping transition-opacity duration-700"></div>
                          </div>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-black text-gray-900 dark:text-white mb-2 group-hover/contact-item:text-[hsl(201,100%,33%)] dark:group-hover/contact-item:text-[#0080c7] transition-colors duration-500">Business Details</h4>
                          <p className="text-gray-600 dark:text-gray-300 font-medium group-hover/contact-item:text-gray-800 dark:group-hover/contact-item:text-gray-200 transition-colors duration-500">ABN: {COMPANY_INFO.abn}</p>
                          <p className="text-gray-600 dark:text-gray-300 font-medium group-hover/contact-item:text-gray-800 dark:group-hover/contact-item:text-gray-200 transition-colors duration-500">{COMPANY_INFO.address.state}, {COMPANY_INFO.address.country}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>

            <div className="relative group animate-fade-in-up" style={{ animationDelay: `${contactInfoVisible ? 600 : 0}ms` }}>
              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border-2 border-white/40 dark:border-gray-700/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 dark:from-[#006da6]/10 dark:to-[#005a8a]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                
                <div className="relative z-10">
                  <h3 className="text-xl font-black text-gray-900 dark:text-white mb-6 group-hover:text-[#006da6] dark:group-hover:text-[#0080c7] transition-colors duration-500">Business Hours</h3>
                  <div className="relative group/hours">
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/hours:opacity-20 transition-all duration-500"></div>
                    <div className="relative bg-gradient-to-r from-gray-50/90 via-white/90 to-gray-50/90 dark:from-gray-700/90 dark:via-gray-800/90 dark:to-gray-700/90 backdrop-blur-lg border border-white/40 dark:border-gray-600/40 rounded-2xl p-6 hover:bg-white/90 dark:hover:bg-gray-800/90 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                      <div className="space-y-4">
                        {businessHoursArray.map(({ day, hours }) => (
                          <div key={day} className="relative group/day flex justify-between items-center">
                            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/10 to-transparent dark:from-[#006da6]/20 opacity-0 group-hover/day:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                            <span className="relative font-black text-gray-900 dark:text-white group-hover/day:text-[#006da6] dark:group-hover/day:text-[#0080c7] transition-colors duration-500">{day}</span>
                            <span className={`relative text-sm font-medium transition-colors duration-500 ${hours === 'Closed' ? 'text-red-600 dark:text-red-400 group-hover/day:text-red-500' : 'text-gray-600 dark:text-gray-300 group-hover/day:text-gray-800 dark:group-hover/day:text-gray-200'}`}>
                              {hours}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>

            <div className="relative group animate-fade-in-up" style={{ animationDelay: `${contactInfoVisible ? 800 : 0}ms` }}>
              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border-2 border-white/40 dark:border-gray-700/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 dark:from-[#006da6]/10 dark:to-[#005a8a]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                
                <div className="relative z-10">
                  <h3 className="text-xl font-black text-gray-900 dark:text-white mb-6 group-hover:text-[#006da6] dark:group-hover:text-[#0080c7] transition-colors duration-500">Service Areas</h3>
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    {SERVICE_AREAS.map((area, index) => (
                      <div key={index} className="relative group/area">
                        <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/area:opacity-20 transition-all duration-500"></div>
                        <div className="relative bg-white/80 dark:bg-gray-700/80 backdrop-blur-lg border border-white/40 dark:border-gray-600/40 rounded-2xl p-4 hover:bg-white/90 dark:hover:bg-gray-700/90 transition-all duration-500 hover:scale-105 transform-gpu shadow-lg hover:shadow-xl">
                          <div className="flex items-center space-x-3">
                            <div className="relative group/area-icon">
                              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-xl blur opacity-0 group-hover/area-icon:opacity-30 transition-all duration-500"></div>
                              <div className="relative w-10 h-10 bg-gradient-to-br from-[#006da6]/20 via-white/80 to-[#005a8a]/20 dark:from-[#006da6]/30 dark:via-gray-700/80 dark:to-[#005a8a]/30 backdrop-blur-xl border-2 border-[#006da6]/30 dark:border-[#006da6]/40 rounded-xl flex items-center justify-center flex-shrink-0 hover:border-[#006da6]/50 transition-all duration-500 hover:scale-110 hover:rotate-12 transform-gpu shadow-lg hover:shadow-xl overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#005a8a]/10 dark:from-[#006da6]/20 dark:to-[#005a8a]/20 opacity-0 group-hover/area-icon:opacity-100 transition-opacity duration-700 rounded-xl"></div>
                                <span className="relative z-10 text-[#006da6] dark:text-[#0080c7] text-sm group-hover/area-icon:animate-bounce">📍</span>
                              </div>
                            </div>
                            <span className="font-black text-gray-900 dark:text-white text-sm group-hover/area:text-[#006da6] dark:group-hover/area:text-[#0080c7] transition-colors duration-500">{area}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="relative group/map-btn">
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/map-btn:opacity-20 transition-all duration-500"></div>
                    <Button
                      onClick={toggleMap}
                      className="relative w-full bg-gradient-to-r from-[#006da6] to-[#0080c7] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white font-black py-4 px-6 rounded-2xl transition-all duration-700 hover:scale-105 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/map-btn-inner overflow-hidden"
                    >
                      <span className="relative z-10 flex items-center justify-center gap-3">
                        <span className="text-xl group-hover/map-btn-inner:animate-pulse">🗺️</span>
                        {showMap ? 'Hide Service Area Map' : 'View Service Area Map'}
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-[#180c2e]/10 to-[#2d1b4e]/10 opacity-0 group-hover/map-btn-inner:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                    </Button>
                  </div>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>
          </div>

          <div ref={formRef} className="relative group animate-fade-in-up" style={{ animationDelay: `${formVisible ? 400 : 0}ms` }}>
            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
            <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border-2 border-white/40 dark:border-gray-700/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 dark:from-[#006da6]/10 dark:to-[#005a8a]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
              
              <div className="relative z-10">
                <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-8 group-hover:text-[#006da6] dark:group-hover:text-[#0080c7] transition-colors duration-500">Send us a Message</h3>
                <ContactForm onSuccess={handleFormSuccess} />
              </div>
              
              <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
            </div>
          </div>
        </div>

        {showMap && (
          <div className="relative group animate-fade-in-up">
            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
            <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border-2 border-white/40 dark:border-gray-700/40 rounded-3xl p-8 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 dark:from-[#006da6]/10 dark:to-[#005a8a]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
              
              <div className="relative z-10">
                <h3 className="text-xl font-black text-gray-900 dark:text-white mb-6 group-hover:text-[#006da6] dark:group-hover:text-[#0080c7] transition-colors duration-500">Our Service Areas</h3>
                <div className="relative group/map-container">
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/map-container:opacity-20 transition-all duration-500"></div>
                  <div className="relative bg-gray-100 dark:bg-gray-700 rounded-2xl h-96 flex items-center justify-center border-2 border-[#006da6]/20 dark:border-[#006da6]/30 hover:border-[#006da6]/40 dark:hover:border-[#006da6]/50 transition-all duration-500">
                    <div className="text-center">
                      <div className="relative group/map-icon mb-4">
                        <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full blur opacity-0 group-hover/map-icon:opacity-40 transition-all duration-500"></div>
                        <div className="relative w-20 h-20 bg-gradient-to-br from-[#006da6]/20 via-white/80 to-[#005a8a]/20 dark:from-[#006da6]/30 dark:via-gray-700/80 dark:to-[#005a8a]/30 backdrop-blur-xl border-2 border-[#006da6]/30 dark:border-[#006da6]/40 rounded-full flex items-center justify-center mx-auto hover:border-[#006da6]/50 transition-all duration-500 hover:scale-110 hover:rotate-12 transform-gpu shadow-lg hover:shadow-2xl overflow-hidden">
                          <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#005a8a]/10 dark:from-[#006da6]/20 dark:to-[#005a8a]/20 opacity-0 group-hover/map-icon:opacity-100 transition-opacity duration-700 rounded-full"></div>
                          <span className="relative z-10 text-[#006da6] dark:text-[#0080c7] text-3xl group-hover/map-icon:animate-bounce">🗺️</span>
                        </div>
                      </div>
                      <p className="text-gray-600 dark:text-gray-300 font-medium">Interactive map coming soon!</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">We service all areas listed above</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default ContactSection;