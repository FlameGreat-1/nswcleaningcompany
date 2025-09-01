import { Link } from 'react-router-dom';
import { COMPANY_INFO, NAVIGATION_LINKS, SOCIAL_LINKS, SERVICE_AREAS, BUSINESS_HOURS } from '../../utils/constants.js';
import { formatPhone } from '../../utils/helpers.js';
import Button from './Button.jsx';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const quickLinks = NAVIGATION_LINKS.filter(link => 
    ['Home', 'Services', 'Quote Calculator', 'NDIS Info', 'Contact'].includes(link.name)
  );

  const serviceLinks = [
    { name: 'General Cleaning', path: '/services#general' },
    { name: 'Deep Cleaning', path: '/services#deep' },
    { name: 'End-of-Lease', path: '/services#end-of-lease' },
    { name: 'NDIS Support', path: '/services#ndis' }
  ];

  const handleNewsletterSubmit = (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    if (email) {
      window.open(`mailto:${COMPANY_INFO.email.support}?subject=Newsletter Subscription&body=Please add ${email} to your newsletter.`, '_blank');
      e.target.reset();
    }
  };

  return (
    <footer className="relative bg-gradient-to-br from-black via-gray-900 to-black overflow-hidden">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#005a8a]/3 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/3 to-[#005a8a]/3 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          
          <div className="space-y-8 animate-fade-in-up">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                <div className="relative z-10">
                  <h3 className="text-3xl font-black text-transparent bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text mb-4 group-hover:scale-110 transition-transform duration-500">
                    {COMPANY_INFO.name}
                  </h3>
                  <p className="text-[#CCCCCC] text-sm leading-relaxed font-medium group-hover:text-white transition-colors duration-500">
                    Professional cleaning services across NSW including NDIS support, 
                    end-of-lease cleaning, and general home cleaning. Reliable, insured, 
                    and bond-back guaranteed.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-2xl blur opacity-0 group-hover:opacity-40 transition-all duration-700"></div>
              <div className="relative flex items-center gap-3 bg-gradient-to-r from-[#006da6]/10 via-white/5 to-[#005a8a]/10 backdrop-blur-xl border border-[#006da6]/30 p-4 rounded-2xl hover:border-[#006da6]/50 transition-all duration-700 hover:-translate-y-1 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#005a8a]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                <div className="relative w-4 h-4 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full animate-pulse shadow-lg group-hover:animate-bounce"></div>
                <span className="relative text-sm font-black text-[#006da6] group-hover:text-white transition-colors duration-500">NDIS Approved Provider</span>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
              </div>
            </div>
          </div>

          <div className="animate-fade-in-up delay-200">
            <h4 className="text-2xl font-black text-[#006da6] mb-8 relative group drop-shadow-md">
              <span className="relative z-10 group-hover:text-white transition-colors duration-500">Quick Links</span>
              <div className="absolute -bottom-2 left-0 w-0 h-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] group-hover:w-full transition-all duration-700 rounded-full"></div>
            </h4>
            <ul className="space-y-4">
              {quickLinks.map((link, index) => (
                <li key={link.name} className="group/link">
                  <Link 
                    to={link.path}
                    className="relative inline-flex items-center text-white hover:text-[#006da6] transition-all duration-500 text-base font-medium group-hover/link:translate-x-2 group-hover/link:scale-105 transform-gpu"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="w-0 h-0.5 bg-gradient-to-r from-[#006da6] to-[#005a8a] group-hover/link:w-4 transition-all duration-500 mr-0 group-hover/link:mr-2 rounded-full"></div>
                    <span className="relative z-10">{link.name}</span>
                    <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/link:opacity-100 transition-opacity duration-500 rounded-lg -m-2 p-2"></div>
                  </Link>
                </li>
              ))}
              <li className="group/link">
                <Link 
                  to="/gallery"
                  className="relative inline-flex items-center text-[#CCCCCC] hover:text-[#006da6] transition-all duration-500 text-sm font-medium group-hover/link:translate-x-2 group-hover/link:scale-105 transform-gpu"
                >
                  <div className="w-0 h-0.5 bg-gradient-to-r from-[#006da6] to-[#005a8a] group-hover/link:w-4 transition-all duration-500 mr-0 group-hover/link:mr-2 rounded-full"></div>
                  <span className="relative z-10">Before & After Gallery</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/link:opacity-100 transition-opacity duration-500 rounded-lg -m-2 p-2"></div>
                </Link>
              </li>
              <li className="group/link">
                <Link 
                  to="/faq"
                  className="relative inline-flex items-center text-[#CCCCCC] hover:text-[#006da6] transition-all duration-500 text-sm font-medium group-hover/link:translate-x-2 group-hover/link:scale-105 transform-gpu"
                >
                  <div className="w-0 h-0.5 bg-gradient-to-r from-[#006da6] to-[#005a8a] group-hover/link:w-4 transition-all duration-500 mr-0 group-hover/link:mr-2 rounded-full"></div>
                  <span className="relative z-10">FAQ</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/link:opacity-100 transition-opacity duration-500 rounded-lg -m-2 p-2"></div>
                </Link>
              </li>
            </ul>
          </div>
          <div className="animate-fade-in-up delay-400">
            <h4 className="text-xl font-black text-white mb-8 relative group">
              <span className="relative z-10 group-hover:text-[#006da6] transition-colors duration-500">Our Services</span>
              <div className="absolute -bottom-2 left-0 w-0 h-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] group-hover:w-full transition-all duration-700 rounded-full"></div>
            </h4>
            <ul className="space-y-4 mb-8">
              {serviceLinks.map((service, index) => (
                <li key={service.name} className="group/service">
                  <Link 
                    to={service.path}
                    className="relative inline-flex items-center text-[#CCCCCC] hover:text-[#006da6] transition-all duration-500 text-sm font-medium group-hover/service:translate-x-2 group-hover/service:scale-105 transform-gpu"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="w-0 h-0.5 bg-gradient-to-r from-[#006da6] to-[#005a8a] group-hover/service:w-4 transition-all duration-500 mr-0 group-hover/service:mr-2 rounded-full"></div>
                    <span className="relative z-10">{service.name}</span>
                    <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/service:opacity-100 transition-opacity duration-500 rounded-lg -m-2 p-2"></div>
                  </Link>
                </li>
              ))}
            </ul>
            
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4 hover:bg-white/10 transition-all duration-700 hover:-translate-y-1 hover:scale-105 transform-gpu overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                <div className="relative z-10">
                  <h5 className="text-sm font-black mb-4 text-white group-hover:text-[#006da6] transition-colors duration-500">Service Areas</h5>
                  <div className="grid grid-cols-2 gap-2 text-xs text-[#CCCCCC] mb-3">
                    {SERVICE_AREAS.slice(0, 6).map((area, index) => (
                      <div key={area} className="group/area flex items-center">
                        <div className="w-1 h-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full mr-2 group-hover/area:animate-pulse"></div>
                        <span className="group-hover/area:text-[#006da6] transition-colors duration-300">{area}</span>
                      </div>
                    ))}
                  </div>
                  <span className="text-xs text-[#006da6] font-black group-hover:text-white transition-colors duration-500 inline-flex items-center gap-1">
                    <span className="group-hover:animate-bounce"></span>
                    + More areas available
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="animate-fade-in-up delay-600">
            <h4 className="text-xl font-black text-white mb-8 relative group">
              <span className="relative z-10 group-hover:text-[#006da6] transition-colors duration-500">Contact Info</span>
              <div className="absolute -bottom-2 left-0 w-0 h-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] group-hover:w-full transition-all duration-700 rounded-full"></div>
            </h4>
            <div className="space-y-6">
              <div className="relative group/contact">
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-xl blur opacity-0 group-hover/contact:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-700 hover:-translate-y-1 hover:scale-105 transform-gpu">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover/contact:opacity-100 transition-opacity duration-700 rounded-xl"></div>
                  <div className="relative z-10">
                    <p className="text-base font-black mb-2 text-[#006da6] group-hover/contact:text-white transition-colors duration-500">Phone</p>
                    <a 
                      href={`tel:${COMPANY_INFO.phone}`}
                      className="text-[#006da6] hover:text-white transition-all duration-500 font-black text-lg group-hover/contact:scale-110 inline-block transform-gpu"
                    >
                      {formatPhone(COMPANY_INFO.phone)}
                    </a>
                  </div>
                </div>
              </div>
              
              <div className="relative group/email">
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-xl blur opacity-0 group-hover/email:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-700 hover:-translate-y-1 hover:scale-105 transform-gpu">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover/email:opacity-100 transition-opacity duration-700 rounded-xl"></div>
                  <div className="relative z-10">
                    <p className="text-sm font-black mb-2 text-white group-hover/email:text-[#006da6] transition-colors duration-500">Email</p>
                    <a 
                      href={`mailto:${COMPANY_INFO.email.support}`}
                      className="text-[#CCCCCC] hover:text-[#006da6] transition-colors duration-500 text-sm break-all font-medium group-hover/email:scale-105 inline-block transform-gpu"
                    >
                      {COMPANY_INFO.email.support}
                    </a>
                  </div>
                </div>
              </div>

              <div className="relative group/hours">
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-xl blur opacity-0 group-hover/hours:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-700 hover:-translate-y-1 hover:scale-105 transform-gpu">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover/hours:opacity-100 transition-opacity duration-700 rounded-xl"></div>
                  <div className="relative z-10">
                  <p className="text-base font-black mb-3 text-[#006da6] group-hover/hours:text-white transition-colors duration-500">Business Hours</p>
                  <div className="text-sm text-white space-y-2 font-medium">
                      <div className="flex justify-between items-center group/day hover:text-[#006da6] transition-colors duration-300">
                        <span>Mon - Fri:</span>
                        <span className="font-black">{BUSINESS_HOURS.monday}</span>
                      </div>
                      <div className="flex justify-between items-center group/day hover:text-[#006da6] transition-colors duration-300">
                        <span>Saturday:</span>
                        <span className="font-black">{BUSINESS_HOURS.saturday}</span>
                      </div>
                      <div className="flex justify-between items-center group/day hover:text-red-400 transition-colors duration-300">
                        <span>Sunday:</span>
                        <span className="text-red-400 font-black">{BUSINESS_HOURS.sunday}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="relative group mb-12">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
          <div className="relative bg-gradient-to-r from-white/5 via-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-3xl p-1 hover:border-[#006da6]/50 transition-all duration-700">
            <div className="bg-gradient-to-r from-black/50 via-gray-900/50 to-black/50 rounded-3xl p-8 hover:bg-gradient-to-r hover:from-black/70 hover:via-gray-900/70 hover:to-black/70 transition-all duration-700">
              <div className="flex flex-col lg:flex-row justify-between items-center gap-8">
                
                <div className="flex flex-col sm:flex-row items-center gap-6 animate-fade-in-up delay-800">
                  <div className="flex items-center gap-4">
                    <a
                      href={SOCIAL_LINKS.facebook}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="relative group/social perspective-1000"
                      aria-label="Facebook"
                    >
                      <div className="absolute -inset-2 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl blur opacity-0 group-hover/social:opacity-40 transition-all duration-700"></div>
                      <div className="relative w-12 h-12 bg-gradient-to-br from-white/10 via-white/5 to-transparent backdrop-blur-xl border border-white/20 rounded-2xl flex items-center justify-center hover:bg-gradient-to-br hover:from-blue-500 hover:to-blue-600 hover:text-white hover:border-blue-400 transition-all duration-700 hover:-translate-y-2 hover:scale-110 hover:rotate-12 transform-gpu group-hover/social:shadow-2xl overflow-hidden"
                           style={{ transformStyle: 'preserve-3d' }}>
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-transparent to-blue-600/20 opacity-0 group-hover/social:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                        <svg className="relative z-10 w-6 h-6 text-[#CCCCCC] group-hover/social:text-white transition-all duration-500 group-hover/social:scale-110 group-hover/social:animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                        </svg>
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full opacity-0 group-hover/social:opacity-100 animate-ping transition-opacity duration-700"></div>
                      </div>
                    </a>
                    
                    <a
                      href={SOCIAL_LINKS.instagram}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="relative group/social perspective-1000"
                      aria-label="Instagram"
                    >
                      <div className="absolute -inset-2 bg-gradient-to-r from-pink-500 via-purple-500 to-orange-500 rounded-2xl blur opacity-0 group-hover/social:opacity-40 transition-all duration-700"></div>
                      <div className="relative w-12 h-12 bg-gradient-to-br from-white/10 via-white/5 to-transparent backdrop-blur-xl border border-white/20 rounded-2xl flex items-center justify-center hover:bg-gradient-to-br hover:from-pink-500 hover:via-purple-500 hover:to-orange-500 hover:text-white hover:border-pink-400 transition-all duration-700 hover:-translate-y-2 hover:scale-110 hover:rotate-12 transform-gpu group-hover/social:shadow-2xl overflow-hidden"
                           style={{ transformStyle: 'preserve-3d' }}>
                        <div className="absolute inset-0 bg-gradient-to-br from-pink-500/20 via-purple-500/20 to-orange-500/20 opacity-0 group-hover/social:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                        <svg className="relative z-10 w-6 h-6 text-[#CCCCCC] group-hover/social:text-white transition-all duration-500 group-hover/social:scale-110 group-hover/social:animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                        </svg>
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-pink-500 rounded-full opacity-0 group-hover/social:opacity-100 animate-ping transition-opacity duration-700"></div>
                      </div>
                    </a>
                  </div>
                  
                  <div className="text-center sm:text-left">
                  <p className="text-[#006da6] font-black text-xl mb-2 group-hover:text-white transition-colors duration-500">Follow Us</p>
                  <p className="text-white text-base font-medium">Stay updated with our latest work</p>
                  </div>
                </div>

                <div className="relative group/newsletter">
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-2xl blur opacity-0 group-hover/newsletter:opacity-30 transition-all duration-700"></div>
                  <form onSubmit={handleNewsletterSubmit} className="relative flex flex-col sm:flex-row gap-4 items-center">
                    <div className="relative">
                      <input
                        type="email"
                        name="email"
                        placeholder="Enter your email"
                        required
                        className="w-full sm:w-64 px-4 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-white placeholder-[#CCCCCC] focus:outline-none focus:border-[#006da6] focus:bg-white/20 transition-all duration-500 font-medium"
                      />
                      <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#005a8a]/10 opacity-0 focus-within:opacity-100 transition-opacity duration-500 rounded-xl pointer-events-none"></div>
                    </div>
                    <Button
                      type="submit"
                      variant="primary"
                      size="md"
                      className="whitespace-nowrap bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] transform hover:scale-105 hover:-translate-y-1 transition-all duration-500"
                    >
                      Subscribe
                    </Button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/20 via-transparent to-[#005a8a]/20 blur-xl"></div>
          <div className="relative border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex flex-col sm:flex-row items-center gap-4 text-base text-white font-medium">
              <p className="group hover:text-[#006da6] transition-colors duration-500">
                © {currentYear} {COMPANY_INFO.name}. All rights reserved.
              </p>
              <div className="flex items-center gap-4">
                <Link to="/privacy" className="hover:text-[#006da6] transition-colors duration-500 group">
                  <span className="relative">
                    Privacy Policy
                    <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-[#006da6] group-hover:w-full transition-all duration-500"></div>
                  </span>
                </Link>
                <span className="text-white/20">•</span>
                <Link to="/terms" className="hover:text-[#006da6] transition-colors duration-500 group">
                  <span className="relative">
                    Terms of Service
                    <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-[#006da6] group-hover:w-full transition-all duration-500"></div>
                  </span>
                </Link>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-[#CCCCCC] font-medium">
              <span className="group hover:text-[#006da6] transition-colors duration-500">Made with</span>
              <div className="relative group">
                <div className="w-4 h-4 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full animate-pulse group-hover:animate-bounce transition-all duration-500"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full blur opacity-0 group-hover:opacity-50 transition-opacity duration-500"></div>
              </div>
              <span className="group hover:text-[#006da6] transition-colors duration-500">in Australia</span>
            </div>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#006da6]/50 to-transparent"></div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/50 to-transparent pointer-events-none"></div>
    </footer>
  );
};

export default Footer;

            
           

      

   



