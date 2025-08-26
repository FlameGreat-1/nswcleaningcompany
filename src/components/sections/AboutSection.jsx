import { useState, useEffect, useRef } from 'react';
import { COMPANY_INFO } from '../../utils/constants.js';

const AboutSection = () => {
  const [happyCustomers, setHappyCustomers] = useState(20);
  const [bondBack, setBondBack] = useState(10);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  const features = [
    {
      icon: '🛡️',
      text: 'NDIS registered provider',
      highlight: true,
      color: 'from-[#006da6] to-[#0080c7]'
    },
    {
      icon: '📋', 
      text: 'ABN-registered & GST-included invoices',
      color: 'from-[#0080c7] to-[#006da6]'
    },
    {
      icon: '📸',
      text: 'Before & After job photo documentation',
      color: 'from-[#006da6] to-[#005a8a]'
    },
    {
      icon: '🔒',
      text: 'Fully insured & police-checked team',
      color: 'from-[#005a8a] to-[#0080c7]'
    }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          
          const customerInterval = setInterval(() => {
            setHappyCustomers(prev => {
              if (prev >= 500) {
                clearInterval(customerInterval);
                return 500;
              }
              return prev + 15;
            });
          }, 50);

          const bondInterval = setInterval(() => {
            setBondBack(prev => {
              if (prev >= 100) {
                clearInterval(bondInterval);
                return 100;
              }
              return prev + 3;
            });
          }, 80);
        } else {
          setIsVisible(false);
          setTimeout(() => {
            setIsVisible(true);
            setHappyCustomers(20);
            setBondBack(10);
            
            const customerInterval = setInterval(() => {
              setHappyCustomers(prev => {
                if (prev >= 500) {
                  clearInterval(customerInterval);
                  return 500;
                }
                return prev + 15;
              });
            }, 50);

            const bondInterval = setInterval(() => {
              setBondBack(prev => {
                if (prev >= 100) {
                  clearInterval(bondInterval);
                  return 100;
                }
                return prev + 3;
              });
            }, 80);
          }, 200);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="section-padding bg-white relative overflow-hidden" id="about">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="container mx-auto relative z-10">
        <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-black text-black mb-12 animate-fade-in-up">
          About
        </h2>         
          <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 md:p-12 mb-16 border-2 border-white/40 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 group overflow-hidden animate-fade-in-up delay-300">
            <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
            
            <div className="relative z-10">
              <p className="text-base md:text-lg text-[#4B4B4B] leading-relaxed mb-12 max-w-4xl mx-auto font-medium group-hover:text-[#333] transition-colors duration-500">
                We're a local Australian cleaning company proudly serving homes, rentals, and NDIS participants 
                with respect, care, and reliability. Whether you're after a one-time deep clean, end-of-lease service, 
                or ongoing NDIS support, we're here to make your space shine — and your experience hassle-free.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {features.map((feature, index) => (
                  <div 
                    key={index}
                    className={`relative group/feature animate-fade-in-up`}
                    style={{ animationDelay: `${600 + index * 200}ms` }}
                  >
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/feature:opacity-30 transition-all duration-700"></div>
                    <div className={`relative flex items-center p-6 rounded-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden ${
                      feature.highlight 
                        ? 'bg-gradient-to-br from-[#006da6]/10 via-white/90 to-[#0080c7]/10 border-2 border-[#006da6]/30 shadow-lg' 
                        : 'bg-white/90 backdrop-blur-lg border-2 border-white/40 shadow-lg hover:shadow-2xl'
                    }`}>
                      <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover/feature:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#006da6] to-transparent transform scale-x-0 group-hover/feature:scale-x-100 transition-transform duration-700"></div>
                      <div className="absolute -top-2 -right-2 w-4 h-4 bg-[#006da6] rounded-full opacity-0 group-hover/feature:opacity-100 animate-ping transition-opacity duration-700"></div>
                      
                      <div className={`relative w-12 h-12 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mr-4 shadow-lg group-hover/feature:shadow-2xl transition-all duration-700 group-hover/feature:scale-110 group-hover/feature:rotate-12 transform-gpu flex-shrink-0`}>
                        <span className="text-2xl group-hover/feature:animate-bounce">{feature.icon}</span>
                        <div className="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover/feature:opacity-100 transition-opacity duration-700"></div>
                      </div>
                      
                      <span className={`relative font-bold text-sm ${
                        feature.highlight ? 'text-[#0080c7]' : 'text-gray-800 group-hover/feature:text-[#006da6]'
                      } transition-colors duration-500`}>
                        {feature.text}
                      </span>
                      
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover/feature:scale-x-100 transition-transform duration-700 rounded-b-2xl"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-fade-in-up delay-1000">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/40 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                
                <div className="relative z-10">
                  <div className="text-4xl font-black text-[#006da6] group-hover:text-black mb-3 transition-all duration-500 group-hover:scale-110 group-hover:animate-pulse">
                    {happyCustomers}+
                  </div>
                  <p className="text-[#666] font-bold group-hover:text-[#006da6] transition-colors duration-500 text-sm">Happy Customers</p>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>
            
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/40 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                
                <div className="relative z-10">
                  <div className="text-4xl font-black text-[#006da6] group-hover:text-black mb-3 transition-all duration-500 group-hover:scale-110 group-hover:animate-pulse">
                    {bondBack}%
                  </div>
                  <p className="text-[#666] font-bold group-hover:text-[#006da6] transition-colors duration-500 text-sm">Bond-Back Guarantee</p>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>
            
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/40 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                
                <div className="relative z-10">
                  <div className={`text-4xl font-black text-[#006da6] group-hover:text-black mb-3 transition-all duration-1000 group-hover:scale-110 ${isVisible ? 'animate-bounce-in' : 'opacity-0 translate-y-10'}`}>
                    24/7
                  </div>
                  <p className="text-[#666] font-bold group-hover:text-[#006da6] transition-colors duration-500 text-sm">Customer Support</p>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
