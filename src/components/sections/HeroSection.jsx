import { useState, useEffect, useRef } from 'react';
import Button from '../common/Button.jsx';
import { COMPANY_INFO } from '../../utils/constants.js';
import { scrollToElement } from '../../utils/helpers.js';

const HeroSection = () => {
  const [email, setEmail] = useState('');
  const [currentBadge, setCurrentBadge] = useState(0);
  const [happyCustomers, setHappyCustomers] = useState(20);
  const [satisfactionRate, setSatisfactionRate] = useState(10);
  const [isVisible, setIsVisible] = useState(false);
  const [worldClassVisible, setWorldClassVisible] = useState(false);
  const [statsVisible, setStatsVisible] = useState(false);
  const sectionRef = useRef(null);
  const statsRef = useRef(null);

  const badges = [
    { text: "Trusted by 500+ NSW Families", icon: "👨‍👩‍👧‍👦" },
    { text: "NDIS Approved Provider", icon: "🛡️" },
    { text: "Fully Insured & Licensed", icon: "🏢" },
    { text: "Bond-Back Guarantee", icon: "🔑" },
    { text: "Available 24/7 Support", icon: "📞" },
    { text: "Eco-Friendly Products", icon: "🌿" }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentBadge((prev) => (prev + 1) % badges.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          setWorldClassVisible(false);
          setTimeout(() => setWorldClassVisible(true), 500);
        } else {
          setWorldClassVisible(false);
          setTimeout(() => setWorldClassVisible(true), 300);
        }
      },
      { threshold: 0.3 }
    );

    const statsObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setStatsVisible(true);
          setHappyCustomers(20);
          setSatisfactionRate(10);
          
          const customerInterval = setInterval(() => {
            setHappyCustomers(prev => {
              if (prev >= 500) {
                clearInterval(customerInterval);
                return 500;
              }
              return prev + 15;
            });
          }, 50);

          const satisfactionInterval = setInterval(() => {
            setSatisfactionRate(prev => {
              if (prev >= 100) {
                clearInterval(satisfactionInterval);
                return 100;
              }
              return prev + 3;
            });
          }, 80);
        } else {
          setStatsVisible(false);
          setTimeout(() => {
            setStatsVisible(true);
            setHappyCustomers(20);
            setSatisfactionRate(10);
            
            const customerInterval = setInterval(() => {
              setHappyCustomers(prev => {
                if (prev >= 500) {
                  clearInterval(customerInterval);
                  return 500;
                }
                return prev + 15;
              });
            }, 50);

            const satisfactionInterval = setInterval(() => {
              setSatisfactionRate(prev => {
                if (prev >= 100) {
                  clearInterval(satisfactionInterval);
                  return 100;
                }
                return prev + 3;
              });
            }, 80);
          }, 200);
        }
      },
      { threshold: 0.5 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    if (statsRef.current) {
      statsObserver.observe(statsRef.current);
    }

    return () => {
      observer.disconnect();
      statsObserver.disconnect();
    };
  }, []);

  const handleGetQuote = () => {
    scrollToElement('quote-calculator', 80);
  };

  const handleSendPhotos = () => {
    scrollToElement('contact-section', 80);
  };

  const handleCallNow = () => {
    window.location.href = `tel:${COMPANY_INFO.phone}`;
  };

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    if (email) {
      scrollToElement('contact-section', 80);
    }
  };

  return (
    <section ref={sectionRef} className="relative min-h-screen app-bg-primary flex items-center justify-center overflow-hidden pt-32">
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-gray-50/30 to-transparent app-bg-primary"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#180c2e]/3 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/3 to-[#180c2e]/3 rounded-full blur-3xl animate-spin-slow"></div>
      </div>
      
      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative inline-flex items-center gap-3 app-bg-glass backdrop-blur-lg border-2 border-[#006da6]/30 rounded-full px-6 py-3 mb-12 shadow-2xl hover:shadow-[0_0_40px_rgba(0,109,166,0.3)] transition-all duration-700 group overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 via-transparent to-[#180c2e]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
            <div className="flex -space-x-2 relative z-10">
              <div className="w-8 h-8 bg-gradient-to-br from-[#006da6] to-[#180c2e] rounded-full border-2 border-white shadow-lg animate-pulse"></div>
              <div className="w-8 h-8 bg-gradient-to-br from-[#180c2e] to-[#006da6] rounded-full border-2 border-white shadow-lg animate-pulse delay-300"></div>
              <div className="w-8 h-8 bg-gradient-to-br from-[#006da6] to-[#180c2e] rounded-full border-2 border-white shadow-lg animate-pulse delay-700"></div>
            </div>
            <div className="relative z-10 flex items-center gap-2">
              <span className="text-lg animate-bounce">{badges[currentBadge].icon}</span>
              <span className="text-sm font-bold app-text-primary transition-all duration-500 transform">
                {badges[currentBadge].text}
              </span>
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#006da6] rounded-full animate-ping"></div>
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black app-text-primary mb-8 leading-[0.9] tracking-tight">
            Cleaning Services by
            <span className="block mt-4 relative perspective-1000">
              <span 
                className={`relative z-10 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] bg-clip-text text-transparent transform transition-all duration-1200 ${
                  worldClassVisible 
                    ? 'translate-y-0 rotate-0 scale-100 opacity-100' 
                    : 'translate-y-32 rotate-x-90 scale-75 opacity-0'
                } hover:scale-110 hover:rotate-1 hover:drop-shadow-2xl`}
                style={{
                  transformStyle: 'preserve-3d',
                  filter: 'drop-shadow(0 10px 20px rgba(0,109,166,0.3))',
                }}
              >
                World-Class
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/30 to-[#180c2e]/30 blur-3xl transform scale-150 animate-pulse"></div>
              <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6]/10 to-[#180c2e]/10 blur-2xl rounded-3xl animate-pulse delay-500"></div>
            </span>
            <span className="block mt-4 app-text-primary hover:text-[#006da6] transition-colors duration-500">Professionals</span>
          </h1>

          <p className="text-base md:text-lg app-text-secondary mb-12 max-w-2xl mx-auto leading-relaxed font-medium animate-fade-in-up delay-1000">
            NDIS-approved cleaning services across NSW. From regular home maintenance to deep cleans and end-of-lease services — we deliver exceptional results with full insurance and documentation.
          </p>

          <form onSubmit={handleEmailSubmit} className="max-w-md mx-auto mb-16 animate-fade-in-up delay-1200">
            <div className="relative group">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email for instant quote"
                className="w-full px-6 py-4 text-base border-2 border-[#006da6]/40 rounded-full focus:border-[#006da6] focus:outline-none transition-all duration-500 app-bg-glass backdrop-blur-lg shadow-xl focus:shadow-2xl focus:scale-105 group-hover:shadow-[0_0_30px_rgba(0,109,166,0.2)] app-text-primary"
                required
              />
              <button
                type="submit"
                className="absolute right-2 top-2 bottom-2 px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu"
              >
                Get Quote
              </button>
            </div>
          </form>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-20 animate-fade-in-up delay-1400">
          <Button
            onClick={handleGetQuote}
            className="px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu"
          >
            <span className="!text-white hover:!text-white flex items-center gap-2">
              <span className="text-xl !text-white hover:!text-white">💰</span>
              Free Instant Quote
            </span>
          </Button>
          
          <Button
            onClick={handleSendPhotos}
            className="px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu"
          >
            <span className="!text-white hover:!text-white flex items-center gap-2">
              <span className="text-xl !text-white hover:!text-white">📸</span>
              Send Photos
            </span>
          </Button>

          <Button
            onClick={handleCallNow}
            className="px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu"
          >
            <span className="!text-white hover:!text-white flex items-center gap-2">
              <span className="text-xl !text-white hover:!text-white">📞</span>
              Call Now
            </span>
          </Button>
  
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16 animate-fade-in-up delay-1600">
            {[
              { icon: "🏠", title: "Regular Cleaning", desc: "Weekly, fortnightly, or monthly home maintenance", color: "from-[#006da6] to-[#180c2e]" },
              { icon: "✨", title: "Deep Cleaning", desc: "Comprehensive top-to-bottom property cleaning", color: "from-[#180c2e] to-[#006da6]" },
              { icon: "🔑", title: "End of Lease", desc: "Bond-back guarantee cleaning services", color: "from-[#006da6] to-[#0080c7]" },
              { icon: "🛡️", title: "NDIS Support", desc: "Registered provider with compliant invoicing", color: "from-[#0080c7] to-[#180c2e]" }
            ].map((service, index) => (
              <div key={index} className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700 animate-pulse"></div>
                <div className="relative app-bg-glass backdrop-blur-xl rounded-2xl p-6 border-2 app-border-glass shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu group overflow-hidden h-full flex flex-col">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#180c2e]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#006da6] to-transparent transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700"></div>
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                  
                  <div className="flex flex-col items-center text-center flex-grow">
                    <div className={`w-12 h-12 bg-gradient-to-br ${service.color} rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:shadow-2xl transition-all duration-700 group-hover:scale-110 group-hover:rotate-12 transform-gpu`}>
                      <span className="text-2xl group-hover:animate-bounce">{service.icon}</span>
                      <div className="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                    </div>
                    
                    <h3 className="font-black text-lg app-text-primary mb-2 group-hover:text-[#006da6] transition-colors duration-500">{service.title}</h3>
                    <p className="text-sm app-text-secondary leading-relaxed group-hover:app-text-primary transition-colors duration-500 flex-grow">{service.desc}</p>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#180c2e] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-2xl"></div>
                </div>
              </div>
            ))}
          </div>

          <div ref={statsRef} className="relative bg-gradient-to-r from-[#006da6]/15 via-transparent to-[#180c2e]/15 app-bg-glass backdrop-blur-xl rounded-3xl p-8 border-2 border-[#006da6]/30 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.2)] transition-all duration-700 group overflow-hidden animate-fade-in-up delay-1800">
            <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 via-transparent to-[#180c2e]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
            
            <div className="relative flex flex-col lg:flex-row items-center justify-between gap-8">
              <div className="text-left">
                <h3 className="text-3xl font-black app-text-primary mb-3 group-hover:text-[#006da6] transition-colors duration-500">Ready to Experience the Difference?</h3>
                <p className="app-text-secondary text-lg leading-relaxed max-w-lg group-hover:app-text-primary transition-colors duration-500">
                  Join hundreds of satisfied customers across NSW. Professional, reliable, and fully insured cleaning services.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-6 shrink-0">
                <div className="text-center group/stat">
                  <div className="text-4xl font-black text-[#006da6] group-hover:app-text-primary mb-2 transition-all duration-500 group-hover/stat:scale-110 group-hover/stat:animate-pulse">
                    {happyCustomers}+
                  </div>
                  <div className="text-sm app-text-secondary font-semibold group-hover/stat:text-[#006da6] transition-colors duration-500">Happy Customers</div>
                </div>
                
                <div className="text-center group/stat">
                  <div className="text-4xl font-black text-[#006da6] group-hover:app-text-primary mb-2 transition-all duration-500 group-hover/stat:scale-110 group-hover/stat:animate-pulse">
                    {satisfactionRate}%
                  </div>
                  <div className="text-sm app-text-secondary font-semibold group-hover/stat:text-[#006da6] transition-colors duration-500">Satisfaction Rate</div>
                </div>
                
                <div className="text-center group/stat">
                  <div className={`text-4xl font-black text-[#006da6] group-hover:app-text-primary mb-2 transition-all duration-1000 group-hover/stat:scale-110 ${statsVisible ? 'animate-bounce-in' : 'opacity-0 translate-y-10'}`}>
                    24/7
                  </div>
                  <div className="text-sm app-text-secondary font-semibold group-hover/stat:text-[#006da6] transition-colors duration-500">Support Available</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-[#006da6]/60 rounded-full flex justify-center app-bg-glass backdrop-blur-lg shadow-lg hover:shadow-2xl transition-all duration-500 hover:scale-110 group cursor-pointer">
          <div className="w-1 h-3 bg-gradient-to-b from-[#006da6] to-[#180c2e] rounded-full mt-2 animate-pulse group-hover:animate-bounce"></div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

