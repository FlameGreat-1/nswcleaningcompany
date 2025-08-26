import { useState, useEffect, useRef } from 'react';
import { servicesData, getMainServices } from '../../data/services.js';
import { formatCurrency } from '../../utils/helpers.js';
import { SERVICE_AREAS } from '../../utils/constants.js';
import Button from '../common/Button.jsx';
import { scrollToElement } from '../../utils/helpers.js';

const ServicesSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [areasVisible, setAreasVisible] = useState(false);
  const [showFourthCard, setShowFourthCard] = useState(false);
  const sectionRef = useRef(null);
  const areasRef = useRef(null);
  const mainServices = getMainServices();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const areasObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setAreasVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    if (areasRef.current) {
      areasObserver.observe(areasRef.current);
    }

    return () => {
      observer.disconnect();
      areasObserver.disconnect();
    };
  }, []);

  const handleGetQuote = () => {
    scrollToElement('quote-calculator', 80);
  };

  const handleLearnMore = (serviceId) => {
    window.location.href = `/services#${serviceId}`;
  };

  const handleToggleCard = () => {
    setShowFourthCard(!showFourthCard);
  };

  const getVisibleServices = () => {
    if (showFourthCard) {
      
      return [
        mainServices.find(s => s.id === 'ndis') || mainServices[3],
        mainServices.find(s => s.title.includes('Office')) || mainServices[4],
        mainServices.find(s => s.title.includes('Airbnb')) || mainServices[5]
      ];
    } else {
      
      return [
        mainServices.find(s => s.title.includes('Regular')) || mainServices[0],
        mainServices.find(s => s.title.includes('Deep')) || mainServices[1],
        mainServices.find(s => s.title.includes('End-of-Lease')) || mainServices[2]
      ];
    }
  };

  return (
    <section ref={sectionRef} className="section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl relative overflow-hidden" id="services">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="container mx-auto relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
            Our <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Cleaning Services</span>
          </h2>
          <p className="text-base text-[#4B4B4B] max-w-2xl mx-auto font-medium animate-fade-in-up delay-300">
            Professional cleaning solutions tailored to your specific needs across NSW
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {getVisibleServices().map((service, index) => (
            <div 
              key={service.id}
              className="relative group animate-fade-in-up h-full"
              style={{ animationDelay: `${isVisible ? 400 + index * 200 : 0}ms` }}
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu border-2 border-white/40 overflow-hidden h-full flex flex-col">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>

                <div className="relative z-10 flex flex-col h-full">
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500">
                        {service.title}
                      </h3>
                      {service.popular && (
                        <span className="bg-gradient-to-r from-[#006da6] to-[#0080c7] text-white text-xs font-black px-2 py-1 rounded-full shadow-lg group-hover:shadow-2xl transition-all duration-500 group-hover:scale-110">
                          Popular
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-[#4B4B4B] mb-3 leading-relaxed font-medium group-hover:text-[#333] transition-colors duration-500">
                      {service.description}
                    </p>

                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <span className="text-xl font-black text-[#006da6] group-hover:text-black transition-colors duration-500">
                          {formatCurrency(service.basePrice)}
                        </span>
                        <span className="text-xs text-[#666] ml-1 font-semibold">starting from</span>
                      </div>
                      <span className="text-xs text-[#666] bg-white/80 backdrop-blur-lg px-2 py-1 rounded-full font-semibold border border-white/40 group-hover:bg-[#006da6]/10 group-hover:border-[#006da6]/20 transition-all duration-500">
                        {service.duration}
                      </span>
                    </div>
                  </div>

                  <div className="mb-4 flex-grow">
                    <h4 className="font-black text-gray-900 mb-2 text-sm group-hover:text-[#006da6] transition-colors duration-500">What's included:</h4>
                    <ul className="space-y-1">
                      {service.includes.slice(0, 4).map((item, index) => (
                        <li key={index} className="flex items-start text-xs text-[#4B4B4B] group-hover:text-[#333] transition-colors duration-500 font-medium">
                          <div className="w-1.5 h-1.5 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mt-1.5 mr-2 flex-shrink-0 group-hover:animate-pulse"></div>
                          {item}
                        </li>
                      ))}
                      {service.includes.length > 4 && (
                        <li className="text-xs text-[#006da6] font-black group-hover:text-black transition-colors duration-500">
                          +{service.includes.length - 4} more services
                        </li>
                      )}
                    </ul>
                  </div>

                  {service.guarantee && (
                    <div className="bg-gradient-to-r from-[#006da6]/10 via-white/50 to-[#0080c7]/10 backdrop-blur-lg border-2 border-[#006da6]/30 rounded-xl p-2 mb-4 group-hover:border-[#006da6]/50 transition-all duration-500">
                      <p className="text-xs font-black text-[#0080c7] text-center group-hover:text-black transition-colors duration-500">
                        {service.guarantee}
                      </p>
                    </div>
                  )}

                  {service.ndisCompliant && (
                    <div className="bg-gradient-to-r from-blue-50/80 via-white/50 to-blue-50/80 backdrop-blur-lg border-2 border-blue-200/50 rounded-xl p-2 mb-4 group-hover:border-blue-300/70 transition-all duration-500">
                      <p className="text-xs font-black text-blue-700 text-center group-hover:text-blue-800 transition-colors duration-500">
                        NDIS Compliant Service
                      </p>
                    </div>
                  )}

                  <div className="flex gap-2 mt-auto">
                    <Button
                      onClick={handleGetQuote}
                      className="relative flex-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-3 py-2 rounded-full text-xs transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                    >
                      <span className="relative z-10 flex items-center justify-center gap-1">
                        <span className="text-sm group-hover/btn:animate-bounce">💰</span>
                        Get Quote
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 transform group-hover/btn:translate-x-full"></div>
                    </Button>
                    <Button
                      onClick={() => handleLearnMore(service.id)}
                      className="relative flex-1 bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#180c2e] hover:to-[#2d1b4e] hover:text-white hover:border-[#180c2e] font-black px-3 py-2 rounded-full text-xs transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                    >
                      <span className="relative z-10 flex items-center justify-center gap-1">
                        <span className="text-sm group-hover/btn:animate-pulse">📖</span>
                        Learn More
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                    </Button>
                  </div>
                </div>

                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center mb-16">
          <Button
            onClick={handleToggleCard}
            className="relative bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#0080c7] hover:text-white font-black px-6 py-2 rounded-full text-sm transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group overflow-hidden"
          >
            <span className="relative z-10 flex items-center gap-2">
              <span className="text-lg group-hover:animate-bounce">{showFourthCard ? '👁️' : '👀'}</span>
              {showFourthCard ? 'Show Less' : 'Show More'}
            </span>
            <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-full"></div>
          </Button>
        </div>

        <div ref={areasRef} className="relative group animate-fade-in-up delay-800">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
          <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 md:p-12 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
            
            <div className="relative z-10">
              <div className="text-center mb-8">
                <h3 className="text-2xl md:text-3xl font-black text-gray-900 mb-4 group-hover:text-[#006da6] transition-colors duration-500">
                  Service Areas Across <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">NSW</span>
                </h3>
                <p className="text-[#4B4B4B] max-w-2xl mx-auto font-medium group-hover:text-[#333] transition-colors duration-500">
                  We provide professional cleaning services across multiple areas in New South Wales
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {SERVICE_AREAS.map((area, index) => (
                  <div 
                    key={index}
                    className="relative group/area animate-fade-in-up"
                    style={{ animationDelay: `${areasVisible ? 1000 + index * 100 : 0}ms` }}
                  >
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/area:opacity-30 transition-all duration-700"></div>
                    <div className="relative text-center p-4 bg-white/80 backdrop-blur-lg rounded-2xl hover:bg-gradient-to-br hover:from-[#006da6]/10 hover:via-white/90 hover:to-[#0080c7]/10 transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu border-2 border-white/40 hover:border-[#006da6]/30 shadow-lg hover:shadow-2xl overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover/area:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#006da6] to-transparent transform scale-x-0 group-hover/area:scale-x-100 transition-transform duration-700"></div>
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#006da6] rounded-full opacity-0 group-hover/area:opacity-100 animate-ping transition-opacity duration-700"></div>
                      
                      <span className="relative font-black text-gray-800 group-hover/area:text-[#006da6] transition-colors duration-500 text-sm">
                        {area}
                      </span>
                      
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover/area:scale-x-100 transition-transform duration-700 rounded-b-2xl"></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="text-center">
                <p className="text-[#4B4B4B] mb-6 font-medium group-hover:text-[#333] transition-colors duration-500">
                  Don't see your area listed? Contact us to check availability in your location.
                </p>
                <Button
                  onClick={handleGetQuote}
                  className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-6 py-3 rounded-full text-sm transition-all duration-700 hover:scale-110 hover:-translate-y-2 hover:rotate-1 shadow-xl hover:shadow-[0_15px_30px_rgba(0,0,0,0.3)] transform-gpu group/cta overflow-hidden"
                  style={{ transformStyle: 'preserve-3d' }}
                >
                  <span className="relative z-10 flex items-center gap-2">
                    <span className="text-lg group-hover/cta:animate-bounce">🗺️</span>
                    Check Your Area & Get Quote
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/cta:opacity-100 transition-opacity duration-700 transform group-hover/cta:translate-x-full"></div>
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-30 group-hover/cta:opacity-60 transition-opacity duration-700"></div>
                </Button>
              </div>
            </div>

            <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;





