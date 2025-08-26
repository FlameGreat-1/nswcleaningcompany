import { useState, useEffect, useRef } from 'react';
import SEO from '../components/common/SEO.jsx';
import ServicesSection from '../components/sections/ServicesSection.jsx';
import { servicesData, getMainServices, getAddonServices } from '../data/services.js';
import { formatCurrency } from '../utils/helpers.js';
import { COMPANY_INFO } from '../utils/constants.js';
import Button from '../components/common/Button.jsx';

const Services = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [addonsVisible, setAddonsVisible] = useState(false);
  const sectionRef = useRef(null);
  const detailsRef = useRef(null);
  const addonsRef = useRef(null);
  
  const mainServices = getMainServices();
  const addonServices = getAddonServices();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const detailsObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setDetailsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const addonsObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setAddonsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    if (detailsRef.current) {
      detailsObserver.observe(detailsRef.current);
    }

    if (addonsRef.current) {
      addonsObserver.observe(addonsRef.current);
    }

    return () => {
      observer.disconnect();
      detailsObserver.disconnect();
      addonsObserver.disconnect();
    };
  }, []);

  const handleGetQuote = () => {
    window.location.href = '/quote';
  };

  const handleContact = () => {
    window.location.href = '/contact';
  };

  const handleCallNow = () => {
    window.location.href = `tel:${COMPANY_INFO.phone}`;
  };

  return (
    <>
      <SEO
        title="Professional Cleaning Services - Complete Service List"
        description="Comprehensive cleaning services including general home cleaning, deep cleaning, end-of-lease cleaning, NDIS support, and specialized services across NSW."
        keywords="cleaning services NSW, home cleaning, deep cleaning, end of lease cleaning, NDIS cleaning, carpet cleaning, window cleaning, professional cleaners"
      />

      <main className="pt-24 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
        </div>

        <section ref={sectionRef} className="section-padding bg-white relative z-10">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center mb-16">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-black mb-8 animate-fade-in-up leading-tight">
                Our Professional <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Cleaning Services</span>
              </h1>
              <p className="text-base md:text-lg text-[#4B4B4B] leading-relaxed font-medium animate-fade-in-up delay-300">
                Comprehensive cleaning solutions tailored to your specific needs across NSW
              </p>
            </div>
          </div>
        </section>

        <ServicesSection />

        <section ref={detailsRef} className="section-padding bg-white relative z-10">
          <div className="container mx-auto">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
                  Detailed Service <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Information</span>
                </h2>
                <p className="text-base text-[#4B4B4B] max-w-2xl mx-auto font-medium animate-fade-in-up delay-300">
                  Everything you need to know about our professional cleaning services
                </p>
              </div>

              <div className="space-y-12">
                {mainServices.map((service, index) => (
                  <div 
                    key={service.id} 
                    id={service.id} 
                    className="relative group animate-fade-in-up"
                    style={{ animationDelay: `${detailsVisible ? 400 + index * 200 : 0}ms` }}
                  >
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                    <div className="relative bg-gradient-to-br from-gray-50/80 via-white/90 to-gray-50/80 backdrop-blur-xl rounded-3xl p-8 md:p-12 border-2 border-white/40 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                      <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                      
                      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2">
                          <div className="flex items-center gap-4 mb-6">
                            <h3 className="text-2xl md:text-3xl font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500">
                              {service.title}
                            </h3>
                            {service.popular && (
                              <span className="bg-gradient-to-r from-[#006da6] to-[#0080c7] text-white text-sm font-black px-3 py-1 rounded-full shadow-lg group-hover:shadow-2xl transition-all duration-500 group-hover:scale-110">
                                Most Popular
                              </span>
                            )}
                            {service.ndisCompliant && (
                              <span className="bg-gradient-to-r from-blue-100 to-blue-50 text-blue-800 text-sm font-black px-3 py-1 rounded-full shadow-lg group-hover:shadow-2xl transition-all duration-500 group-hover:scale-110">
                                NDIS Compliant
                              </span>
                            )}
                          </div>

                          <p className="text-base text-[#4B4B4B] mb-8 leading-relaxed font-medium group-hover:text-[#333] transition-colors duration-500">
                            {service.description}
                          </p>

                          <div className="mb-8">
                            <h4 className="text-xl font-black text-gray-900 mb-4 group-hover:text-[#006da6] transition-colors duration-500">What's Included:</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {service.includes.map((item, itemIndex) => (
                                <div key={itemIndex} className="flex items-start group/item">
                                  <div className="w-2 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mt-2 mr-3 flex-shrink-0 group-hover/item:animate-pulse"></div>
                                  <span className="text-[#4B4B4B] font-medium group-hover/item:text-[#006da6] transition-colors duration-300">{item}</span>
                                </div>
                              ))}
                            </div>
                          </div>

                          {service.guarantee && (
                            <div className="bg-gradient-to-r from-[#006da6]/10 via-white/50 to-[#0080c7]/10 backdrop-blur-lg border-2 border-[#006da6]/30 rounded-2xl p-4 mb-6 group-hover:border-[#006da6]/50 transition-all duration-500">
                              <h4 className="font-black text-[#0080c7] mb-2 group-hover:text-black transition-colors duration-500">Our Guarantee</h4>
                              <p className="text-[#0080c7] font-medium group-hover:text-black transition-colors duration-500">{service.guarantee}</p>
                            </div>
                          )}
                        </div>

                        <div className="relative group/card">
                          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/card:opacity-30 transition-all duration-700"></div>
                          <div className="relative bg-white/90 backdrop-blur-xl rounded-2xl p-6 shadow-xl border-2 border-white/40 hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu h-fit overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover/card:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover/card:scale-x-100 transition-transform duration-700 rounded-t-2xl"></div>
                            
                            <div className="relative z-10">
                              <div className="text-center mb-6">
                                <div className="text-3xl font-black text-[#006da6] group-hover/card:text-black mb-2 transition-colors duration-500">
                                  {formatCurrency(service.basePrice)}
                                </div>
                                <p className="text-sm text-[#666] font-semibold">Starting from</p>
                                <p className="text-sm text-[#4B4B4B] mt-1 font-medium">Duration: {service.duration}</p>
                              </div>

                              <div className="space-y-3 mb-6">
                                <Button
                                  onClick={handleGetQuote}
                                  className="relative w-full bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-3 py-2 rounded-full text-xs transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                                >
                                  <span className="relative z-10 flex items-center justify-center gap-1">
                                    <span className="text-sm group-hover/btn:animate-bounce">💰</span>
                                    Get Quote for This Service
                                  </span>
                                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 transform group-hover/btn:translate-x-full"></div>
                                </Button>
                                
                                <Button
                                  onClick={handleCallNow}
                                  className="relative w-full bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#180c2e] hover:to-[#2d1b4e] hover:text-white hover:border-[#180c2e] font-black px-3 py-2 rounded-full text-xs transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                                >
                                  <span className="relative z-10 flex items-center justify-center gap-1">
                                    <span className="text-sm group-hover/btn:animate-pulse">📞</span>
                                    Call {COMPANY_INFO.phone}
                                  </span>
                                  <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                                </Button>
                              </div>

                              <div className="text-xs text-[#666] text-center font-medium">
                                Final price may vary based on property size, condition, and additional requirements
                              </div>
                            </div>
                            
                            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover/card:scale-x-100 transition-transform duration-700 rounded-b-2xl"></div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
        {addonServices.length > 0 && (
          <section ref={addonsRef} className="section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl relative z-10">
            <div className="container mx-auto">
              <div className="max-w-6xl mx-auto">
                <div className="text-center mb-16">
                  <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
                    Additional <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Services</span>
                  </h2>
                  <p className="text-base text-[#4B4B4B] max-w-2xl mx-auto font-medium animate-fade-in-up delay-300">
                    Enhance your cleaning service with these specialized add-ons
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {addonServices.map((service, index) => (
                    <div 
                      key={service.id} 
                      className="relative group animate-fade-in-up h-full"
                      style={{ animationDelay: `${addonsVisible ? 400 + index * 200 : 0}ms` }}
                    >
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                      <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu border-2 border-white/40 overflow-hidden h-full flex flex-col">
                        <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                        
                        <div className="relative z-10 flex flex-col h-full">
                          <div className="flex justify-between items-start mb-4">
                            <h3 className="text-xl font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500">{service.title}</h3>
                            <div className="text-right">
                              <div className="text-2xl font-black text-[#006da6] group-hover:text-black transition-colors duration-500">
                                {formatCurrency(service.basePrice)}
                              </div>
                              <div className="text-sm text-[#666] font-semibold">{service.duration}</div>
                            </div>
                          </div>

                          <p className="text-[#4B4B4B] mb-6 font-medium group-hover:text-[#333] transition-colors duration-500 flex-grow">{service.description}</p>

                          <div className="mb-6 flex-grow">
                            <h4 className="font-black text-gray-900 mb-3 group-hover:text-[#006da6] transition-colors duration-500">Includes:</h4>
                            <ul className="space-y-2">
                              {service.includes.map((item, index) => (
                                <li key={index} className="flex items-start text-sm text-[#4B4B4B] group-hover:text-[#333] transition-colors duration-500 font-medium group/item">
                                  <div className="w-2 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mt-2 mr-3 flex-shrink-0 group-hover/item:animate-pulse"></div>
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>

                          <Button
                            onClick={handleGetQuote}
                            className="relative w-full bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#180c2e] hover:to-[#2d1b4e] hover:text-white hover:border-[#180c2e] font-black px-3 py-2 rounded-full text-xs transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden mt-auto"
                          >
                            <span className="relative z-10 flex items-center justify-center gap-1">
                              <span className="text-sm group-hover/btn:animate-bounce">➕</span>
                              Add to Quote
                            </span>
                            <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                          </Button>
                        </div>
                        
                        <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        <section className="section-padding bg-white relative z-10">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center">
              <div className="relative group animate-fade-in-up">
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-gradient-to-br from-gray-50/80 via-white/90 to-gray-50/80 backdrop-blur-xl rounded-3xl p-12 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                  
                  <h2 className="text-3xl md:text-4xl font-black text-black mb-8 group-hover:text-[#006da6] transition-colors duration-500">
                    Ready to Book Your Service?
                  </h2>
                  <p className="text-base text-[#4B4B4B] mb-12 max-w-2xl mx-auto font-medium group-hover:text-[#333] transition-colors duration-500">
                    Get your personalized quote today and experience the difference professional cleaning makes. 
                    All services come with our satisfaction guarantee.
                  </p>
                  
                  <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
                    <Button
                      onClick={handleGetQuote}
                      className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-2 hover:rotate-1 shadow-xl hover:shadow-[0_15px_30px_rgba(0,0,0,0.3)] transform-gpu group/cta overflow-hidden"
                      style={{ transformStyle: 'preserve-3d' }}
                    >
                      <span className="relative z-10 flex items-center gap-2">
                        <span className="text-lg group-hover/cta:animate-bounce">💰</span>
                        Get Free Quote Now
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/cta:opacity-100 transition-opacity duration-700 transform group-hover/cta:translate-x-full"></div>
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-30 group-hover/cta:opacity-60 transition-opacity duration-700"></div>
                    </Button>
                    
                    <Button
                      onClick={handleContact}
                      className="relative bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#180c2e] hover:to-[#2d1b4e] hover:text-white hover:border-[#180c2e] font-black px-8 py-4 rounded-full text-base transition-all duration-700 hover:scale-110 hover:-translate-y-2 shadow-xl hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                    >
                      <span className="relative z-10 flex items-center gap-2">
                        <span className="text-lg group-hover/btn:animate-pulse">📞</span>
                        Contact Us
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                    </Button>
                  </div>
                  
                  <div className="mt-8 text-sm text-[#666] font-medium group-hover:text-[#333] transition-colors duration-500">
                    <p>📞 Call us at <span className="font-black text-[#006da6]">{COMPANY_INFO.phone}</span> for immediate assistance</p>
                    <p className="mt-2">✅ Free quotes • ⚡ Same-day service available • 🛡️ 100% satisfaction guarantee</p>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
};

export default Services;

