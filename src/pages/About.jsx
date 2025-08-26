import { useState, useEffect, useRef } from 'react';
import SEO from '../components/common/SEO.jsx';
import AboutSection from '../components/sections/AboutSection.jsx';
import { COMPANY_INFO, SERVICE_AREAS, BUSINESS_HOURS } from '../utils/constants.js';
import { formatPhone } from '../utils/helpers.js';
import Button from '../components/common/Button.jsx';

const About = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [teamVisible, setTeamVisible] = useState(false);
  const sectionRef = useRef(null);
  const teamRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const teamObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTeamVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    if (teamRef.current) {
      teamObserver.observe(teamRef.current);
    }

    return () => {
      observer.disconnect();
      teamObserver.disconnect();
    };
  }, []);

  const handleGetQuote = () => {
    window.location.href = '/quote';
  };

  const handleContact = () => {
    window.location.href = '/contact';
  };

  const teamMembers = [
    {
      name: 'Sarah Johnson',
      role: 'Operations Manager',
      experience: '8+ years',
      specialization: 'NDIS Services & Quality Control',
      color: 'from-[#006da6] to-[#0080c7]'
    },
    {
      name: 'Michael Chen',
      role: 'Lead Cleaner',
      experience: '6+ years',
      specialization: 'End-of-Lease & Deep Cleaning',
      color: 'from-[#0080c7] to-[#006da6]'
    },
    {
      name: 'Emma Williams',
      role: 'Customer Relations',
      experience: '5+ years',
      specialization: 'Client Support & Scheduling',
      color: 'from-[#006da6] to-[#005a8a]'
    }
  ];

  const companyValues = [
    {
      title: 'Reliability',
      description: 'We show up on time, every time, and deliver consistent quality service.',
      icon: '⏰',
      color: 'from-[#006da6] to-[#0080c7]'
    },
    {
      title: 'Respect',
      description: 'We treat every home and client with the utmost respect and care.',
      icon: '🤝',
      color: 'from-[#0080c7] to-[#006da6]'
    },
    {
      title: 'Quality',
      description: 'We use professional-grade equipment and eco-friendly products.',
      icon: '⭐',
      color: 'from-[#006da6] to-[#005a8a]'
    },
    {
      title: 'Transparency',
      description: 'Clear pricing, detailed invoices, and honest communication always.',
      icon: '💎',
      color: 'from-[#005a8a] to-[#0080c7]'
    }
  ];

  return (
    <>
      <SEO
        title="About Us - Professional Cleaning Team"
        description="Learn about NSW Cleaning Company - your trusted local cleaning professionals. Experienced team serving homes, rentals & NDIS participants across NSW with reliability and care."
        keywords="about NSW cleaning company, professional cleaning team, NDIS cleaning specialists, experienced cleaners NSW, reliable cleaning service"
      />

      <main className="pt-24 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
        </div>

        <section className="section-padding bg-white relative z-10">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center mb-16">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-black mb-8 animate-fade-in-up leading-tight">
              About
            </h1>
              <p className="text-base md:text-lg text-[#4B4B4B] leading-relaxed font-medium animate-fade-in-up delay-300">
                Your trusted local cleaning professionals dedicated to making your space shine
              </p>
            </div>

            <AboutSection />
          </div>
        </section>

        <section ref={sectionRef} className="section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl relative z-10">
          <div className="container mx-auto">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
                  Our Story
                </h2>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-16">
                <div className="animate-fade-in-up delay-300">
                  <h3 className="text-2xl font-black text-gray-900 mb-8">
                    Founded on Trust and Excellence
                  </h3>
                  <div className="space-y-6 text-[#4B4B4B] leading-relaxed text-base">
                    <p>
                      {COMPANY_INFO.name} was established with a simple mission: to provide reliable, 
                      professional cleaning services that exceed expectations. What started as a small 
                      local business has grown into NSW's trusted cleaning partner.
                    </p>
                    <p>
                      We recognized the unique needs of NDIS participants and made it our priority to 
                      offer specialized, respectful services that support independent living. Our team 
                      is trained not just in cleaning techniques, but in understanding and respecting 
                      the diverse needs of our clients.
                    </p>
                    <p>
                      Today, we're proud to serve hundreds of satisfied customers across NSW, from 
                      busy families to NDIS participants, property managers to real estate agents. 
                      Our commitment to quality, reliability, and respect remains unchanged.
                    </p>
                  </div>
                </div>

                <div className="relative group animate-fade-in-up delay-600">
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                  <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                    
                    <h4 className="text-lg font-black text-gray-900 mb-8 group-hover:text-[#006da6] transition-colors duration-500">Company Details</h4>
                    <div className="space-y-6">
                      <div className="flex justify-between items-center border-b border-gray-100 pb-4 group-hover:border-[#006da6]/20 transition-colors duration-500">
                        <span className="text-[#666] font-semibold text-sm">Business Name:</span>
                        <span className="font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500 text-sm">{COMPANY_INFO.name}</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-gray-100 pb-4 group-hover:border-[#006da6]/20 transition-colors duration-500">
                        <span className="text-[#666] font-semibold text-sm">ABN:</span>
                        <span className="font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500 text-sm">{COMPANY_INFO.abn}</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-gray-100 pb-4 group-hover:border-[#006da6]/20 transition-colors duration-500">
                        <span className="text-[#666] font-semibold text-sm">Phone:</span>
                        <span className="font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500 text-sm">{formatPhone(COMPANY_INFO.phone)}</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-gray-100 pb-4 group-hover:border-[#006da6]/20 transition-colors duration-500">
                        <span className="text-[#666] font-semibold text-sm">Email:</span>
                        <span className="font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500 text-sm">{COMPANY_INFO.email.support}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[#666] font-semibold text-sm">Service Area:</span>
                        <span className="font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500 text-sm">NSW Wide</span>
                      </div>
                    </div>
                    
                    <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                {companyValues.map((value, index) => (
                  <div key={index} className="relative group animate-fade-in-up" style={{ animationDelay: `${800 + index * 200}ms` }}>
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                    <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu text-center overflow-hidden border-2 border-white/40">
                      <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#006da6] to-transparent transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700"></div>
                      <div className="absolute -top-2 -right-2 w-4 h-4 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                      
                      <div className={`relative w-12 h-12 bg-gradient-to-br ${value.color} rounded-2xl flex items-center justify-center mb-4 mx-auto shadow-lg group-hover:shadow-2xl transition-all duration-700 group-hover:scale-110 group-hover:rotate-12 transform-gpu`}>
                        <span className="text-2xl group-hover:animate-bounce">{value.icon}</span>
                        <div className="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                      </div>
                      
                      <h4 className="text-base font-black text-gray-900 mb-3 group-hover:text-[#006da6] transition-colors duration-500">{value.title}</h4>
                      <p className="text-sm text-[#666] leading-relaxed group-hover:text-[#333] transition-colors duration-500">{value.description}</p>
                      
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
        <section ref={teamRef} className="section-padding bg-white relative z-10">
          <div className="container mx-auto">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
                  Meet Our <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Team</span>
                </h2>
                <p className="text-base text-[#4B4B4B] max-w-2xl mx-auto font-medium animate-fade-in-up delay-300">
                  Our experienced professionals are the heart of our service
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                {teamMembers.map((member, index) => (
                  <div key={index} className="relative group animate-fade-in-up" style={{ animationDelay: `${teamVisible ? index * 200 : 0}ms` }}>
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                    <div className="relative bg-gradient-to-br from-gray-50/80 via-white/90 to-gray-50/80 backdrop-blur-xl rounded-3xl p-8 text-center shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu overflow-hidden border-2 border-white/40">
                      <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                      <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                      
                      <div className={`relative w-20 h-20 bg-gradient-to-br ${member.color} rounded-full mx-auto mb-6 flex items-center justify-center shadow-2xl group-hover:shadow-[0_0_30px_rgba(0,109,166,0.4)] transition-all duration-700 group-hover:scale-110 group-hover:rotate-12 transform-gpu overflow-hidden`}>
                        <span className="text-2xl font-black text-white group-hover:animate-bounce">
                          {member.name.split(' ').map(n => n[0]).join('')}
                        </span>
                        <div className="absolute inset-0 bg-white/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                        <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/20 to-[#0080c7]/20 rounded-full blur opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                      </div>
                      
                      <h3 className="text-lg font-black text-gray-900 mb-2 group-hover:text-[#006da6] transition-colors duration-500">{member.name}</h3>
                      <p className="text-[#006da6] font-black mb-2 group-hover:text-black transition-colors duration-500 text-sm">{member.role}</p>
                      <p className="text-sm text-[#666] mb-3 font-semibold group-hover:text-[#333] transition-colors duration-500">{member.experience} experience</p>
                      <p className="text-sm text-[#4B4B4B] group-hover:text-[#006da6] transition-colors duration-500 font-medium">{member.specialization}</p>
                      
                      <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl relative z-10">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-black text-black mb-8 animate-fade-in-up">
                  Service Areas & <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Hours</span>
                </h2>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div className="relative group animate-fade-in-up delay-300">
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                  <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                    
                    <h3 className="text-lg font-black text-gray-900 mb-6 group-hover:text-[#006da6] transition-colors duration-500">Service Areas</h3>
                    <div className="grid grid-cols-2 gap-4">
                      {SERVICE_AREAS.map((area, index) => (
                        <div key={index} className="flex items-center group/area">
                          <div className="w-3 h-3 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mr-3 group-hover/area:animate-pulse"></div>
                          <span className="text-[#4B4B4B] font-medium group-hover/area:text-[#006da6] transition-colors duration-300 text-sm">{area}</span>
                        </div>
                      ))}
                    </div>
                    <p className="text-sm text-[#666] mt-6 group-hover:text-[#333] transition-colors duration-500 font-medium">
                      Don't see your area? Contact us to check availability.
                    </p>
                    
                    <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                  </div>
                </div>

                <div className="relative group animate-fade-in-up delay-600">
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                  <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                    
                    <h3 className="text-lg font-black text-gray-900 mb-6 group-hover:text-[#006da6] transition-colors duration-500">Business Hours</h3>
                    <div className="space-y-4">
                      {Object.entries(BUSINESS_HOURS).map(([day, hours]) => (
                        <div key={day} className="flex justify-between items-center border-b border-gray-100 pb-3 group-hover:border-[#006da6]/20 transition-colors duration-500 group/hour">
                          <span className="text-[#4B4B4B] font-semibold capitalize group-hover/hour:text-[#006da6] transition-colors duration-300 text-sm">{day}:</span>
                          <span className="text-gray-900 font-black group-hover/hour:text-[#006da6] transition-colors duration-300 text-sm">{hours}</span>
                        </div>
                      ))}
                    </div>
                    <p className="text-sm text-[#666] mt-6 group-hover:text-[#333] transition-colors duration-500 font-medium">
                      Emergency services available 24/7 for urgent situations.
                    </p>
                    
                    <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="section-padding bg-white relative z-10">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center">
              <div className="relative group animate-fade-in-up">
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-gradient-to-br from-gray-50/80 via-white/90 to-gray-50/80 backdrop-blur-xl rounded-3xl p-12 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
                  
                  <h2 className="text-3xl md:text-4xl font-black text-black mb-8 group-hover:text-[#006da6] transition-colors duration-500">
                    Ready to Experience the Difference?
                  </h2>
                  <p className="text-base text-[#4B4B4B] mb-12 max-w-2xl mx-auto font-medium group-hover:text-[#333] transition-colors duration-500">
                    Join hundreds of satisfied customers who trust us with their cleaning needs. 
                    Get your free quote today and discover why we're NSW's preferred cleaning service.
                  </p>
                  
                  <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
                    <Button
                      onClick={handleGetQuote}
                      className="btn-primary group/btn relative overflow-hidden"
                    >
                      <span className="relative z-10">Get Free Quote</span>
                      <div className="absolute inset-0 bg-gradient-to-r from-[#180c2e] to-[#2d1b4e] transform scale-x-0 group-hover/btn:scale-x-100 transition-transform duration-300 origin-left"></div>
                    </Button>
                    
                    <Button
                      onClick={handleContact}
                      className="btn-secondary group/btn relative overflow-hidden"
                    >
                      <span className="relative z-10">Contact Us</span>
                      <div className="absolute inset-0 bg-gradient-to-r from-[#180c2e] to-[#2d1b4e] transform scale-x-0 group-hover/btn:scale-x-100 transition-transform duration-300 origin-left"></div>
                    </Button>
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

export default About;

