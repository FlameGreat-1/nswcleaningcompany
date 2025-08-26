import { useState, useEffect, useRef } from 'react';
import { testimonialsData, getRecentTestimonials, getAverageRating } from '../../data/testimonials.js';
import LoadingSpinner from '../common/LoadingSpinner.jsx';
import Button from '../common/Button.jsx';

const TestimonialsSection = () => {
  const [testimonials, setTestimonials] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  const [loading, setLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(false);
  const [cardsVisible, setCardsVisible] = useState(false);
  const sectionRef = useRef(null);
  const cardsRef = useRef(null);

  // Avatar generator function for consistent avatars
  const generateAvatar = (name, index) => {
    const avatarStyles = [
      'avataaars', 'open-peeps', 'personas', 'miniavs', 'micah', 'adventurer'
    ];
    const style = avatarStyles[index % avatarStyles.length];
    const seed = name.replace(/\s+/g, '').toLowerCase();
    return `https://api.dicebear.com/7.x/${style}/svg?seed=${seed}&backgroundColor=006da6,0080c7,180c2e&size=80`;
  };

  useEffect(() => {
    const loadTestimonials = () => {
      setLoading(true);
      const recentTestimonials = getRecentTestimonials(6);
      setTestimonials(recentTestimonials);
      setLoading(false);
    };
    loadTestimonials();
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const cardsObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setCardsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }
    if (cardsRef.current) {
      cardsObserver.observe(cardsRef.current);
    }

    return () => {
      observer.disconnect();
      cardsObserver.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!isAutoPlaying || testimonials.length === 0) return;
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => 
        prevIndex === testimonials.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000);
    return () => clearInterval(interval);
  }, [isAutoPlaying, testimonials.length]);

  const handlePrevious = () => {
    setIsAutoPlaying(false);
    setCurrentIndex(currentIndex === 0 ? testimonials.length - 1 : currentIndex - 1);
  };

  const handleNext = () => {
    setIsAutoPlaying(false);
    setCurrentIndex(currentIndex === testimonials.length - 1 ? 0 : currentIndex + 1);
  };

  const handleDotClick = (index) => {
    setIsAutoPlaying(false);
    setCurrentIndex(index);
  };

  const handleViewAllTestimonials = () => {
    window.location.href = '/testimonials';
  };

  const renderStars = (rating) => {
    return [...Array(5)].map((_, index) => (
      <div key={index} className="relative group/star">
        <div className="absolute -inset-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full blur opacity-0 group-hover/star:opacity-60 transition-all duration-500"></div>
        <span
          className={`relative text-2xl transition-all duration-500 hover:scale-125 hover:rotate-12 transform-gpu ${
            index < rating 
              ? 'text-transparent bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500 bg-clip-text drop-shadow-lg' 
              : 'text-gray-300 hover:text-gray-400'
          }`}
          style={{ 
            filter: index < rating ? 'drop-shadow(0 0 8px rgba(251, 191, 36, 0.5))' : 'none',
            transformStyle: 'preserve-3d'
          }}
        >
          ★
        </span>
      </div>
    ));
  };

  const getServiceBadgeColor = (service) => {
    const serviceColors = {
      'End-of-Lease Cleaning': 'from-blue-500 to-blue-600 text-white',
      'NDIS Cleaning Support': 'from-[#006da6] to-[#0080c7] text-white',
      'Deep Cleaning': 'from-purple-500 to-purple-600 text-white',
      'General Home Cleaning': 'from-gray-500 to-gray-600 text-white',
      'office and commecial cleaning': 'from-orange-500 to-orange-600 text-white',
      'Window & Carpet Cleaning': 'from-indigo-500 to-indigo-600 text-white'
    };
    return serviceColors[service] || 'from-gray-500 to-gray-600 text-white';
  };

  if (loading) {
    return (
      <section className="relative section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl overflow-hidden" id="testimonials">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
        </div>
        <div className="relative z-10 container mx-auto text-center">
          <div className="relative group">
            <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-30 animate-pulse"></div>
            <div className="relative bg-white/95 backdrop-blur-xl border-2 border-white/60 rounded-3xl p-12 shadow-2xl">
              <LoadingSpinner size="lg" text="Loading testimonials..." />
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (testimonials.length === 0) {
    return null;
  }

  const averageRating = getAverageRating();
  const totalTestimonials = testimonialsData.length;

  return (
    <section ref={sectionRef} className="relative section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl overflow-hidden" id="testimonials">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/2 to-[#0080c7]/2 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="relative z-10 container mx-auto">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-8 animate-fade-in-up leading-tight drop-shadow-sm">
            What Our <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] bg-clip-text text-transparent">Clients Say</span>
          </h2>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-8 mb-12 animate-fade-in-up delay-300">
            <div className="relative group">
              <div className="absolute -inset-2 bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500 rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative text-center bg-white/95 backdrop-blur-xl border-2 border-white/60 rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu">
                <div className="absolute inset-0 bg-gradient-to-br from-yellow-400/5 via-transparent to-orange-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="relative z-10">
                  <div className="flex items-center justify-center gap-1 mb-3">
                    {renderStars(Math.round(averageRating))}
                    <span className="ml-3 text-2xl font-black text-gray-900 group-hover:text-[#006da6] transition-colors duration-500">{averageRating}</span>
                  </div>
                  <p className="text-sm font-black text-gray-700 group-hover:text-gray-900 transition-colors duration-500">Average Rating</p>
                </div>
              </div>
            </div>
            
            <div className="w-px h-16 bg-gradient-to-b from-transparent via-[#006da6] to-transparent hidden sm:block"></div>
            
            <div className="relative group">
              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative text-center bg-white/95 backdrop-blur-xl border-2 border-white/60 rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="relative z-10">
                  <div className="text-3xl font-black text-transparent bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] bg-clip-text mb-2 group-hover:scale-110 transition-transform duration-500">{totalTestimonials}+</div>
                  <p className="text-sm font-black text-gray-700 group-hover:text-gray-900 transition-colors duration-500">Happy Customers</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="relative max-w-5xl mx-auto mb-16">
          <div className="relative group">
            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
            <div className="relative bg-white/95 backdrop-blur-xl border-2 border-white/60 rounded-3xl p-8 md:p-12 shadow-2xl hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu min-h-[400px] flex items-center overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-1000 rounded-t-3xl"></div>
              
              {testimonials.length > 0 && (
                <div className="relative z-10 w-full text-center">
                  {/* Avatar */}
                  <div className="flex justify-center mb-6">
                    <div className="relative group/avatar">
                      <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-0 group-hover/avatar:opacity-40 transition-all duration-500"></div>
                      <img
                        src={generateAvatar(testimonials[currentIndex].name, currentIndex)}
                        alt={`${testimonials[currentIndex].name} avatar`}
                        className="relative w-20 h-20 rounded-full border-4 border-white shadow-lg group-hover/avatar:scale-110 transition-all duration-500"
                      />
                    </div>
                  </div>

                  <div className="flex justify-center mb-8">
                    <div className="flex gap-1">
                      {renderStars(testimonials[currentIndex].rating)}
                    </div>
                  </div>
                  
                  <blockquote className="text-xl md:text-2xl text-gray-800 mb-10 leading-relaxed italic font-medium relative group/quote">
                    <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6]/10 to-transparent opacity-0 group-hover/quote:opacity-100 transition-opacity duration-500 rounded-2xl"></div>
                    <span className="relative z-10 group-hover/quote:text-gray-900 transition-colors duration-500 drop-shadow-sm">
                      "{testimonials[currentIndex].text}"
                    </span>
                  </blockquote>
                  
                  <div className="flex flex-col items-center">
                    <div className="font-black text-gray-900 text-xl mb-3 group-hover:text-[#006da6] transition-colors duration-500 drop-shadow-sm">
                      {testimonials[currentIndex].name}
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-6 font-medium">
                      {testimonials[currentIndex].location}
                    </div>
                    
                    <div className="flex flex-wrap items-center justify-center gap-3">
                      <div className="relative group/badge">
                        <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-2xl blur opacity-0 group-hover/badge:opacity-40 transition-all duration-500"></div>
                        <span className={`relative px-4 py-2 rounded-2xl text-sm font-black bg-gradient-to-r ${getServiceBadgeColor(testimonials[currentIndex].service)} shadow-lg hover:shadow-2xl transition-all duration-500 hover:scale-110 hover:-translate-y-1 transform-gpu`}>
                          {testimonials[currentIndex].service}
                        </span>
                      </div>
                      
                      {testimonials[currentIndex].verified && (
                        <div className="relative group/verified">
                          <div className="absolute -inset-1 bg-gradient-to-r from-green-400 to-green-500 rounded-2xl blur opacity-0 group-hover/verified:opacity-40 transition-all duration-500"></div>
                          <span className="relative flex items-center text-sm text-green-700 bg-green-50 px-3 py-2 rounded-2xl font-black hover:bg-green-100 transition-all duration-500 hover:scale-110 hover:-translate-y-1 transform-gpu shadow-lg">
                            <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-green-500 rounded-full mr-2 animate-pulse shadow-lg"></div>
                            Verified
                          </span>
                        </div>
                      )}
                      
                      {testimonials[currentIndex].ndisParticipant && (
                        <div className="relative group/ndis">
                          <div className="absolute -inset-1 bg-gradient-to-r from-blue-400 to-blue-500 rounded-2xl blur opacity-0 group-hover/ndis:opacity-40 transition-all duration-500"></div>
                          <span className="relative px-3 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-black rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 hover:scale-110 hover:-translate-y-1 transform-gpu">
                            NDIS Participant
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
              
              <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
            </div>
          </div>

          {testimonials.length > 1 && (
            <>
              <button
                onClick={handlePrevious}
                className="absolute left-4 top-1/2 transform -translate-y-1/2 group perspective-1000"
              >
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-2xl blur opacity-0 group-hover:opacity-40 transition-all duration-700"></div>
                <div className="relative w-14 h-14 bg-white/95 backdrop-blur-xl border-2 border-white/60 rounded-2xl flex items-center justify-center text-gray-700 hover:text-white hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#0080c7] hover:border-[#006da6] transition-all duration-700 hover:-translate-y-2 hover:scale-110 hover:rotate-12 transform-gpu shadow-xl hover:shadow-2xl overflow-hidden"
                     style={{ transformStyle: 'preserve-3d' }}>
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#0080c7]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                  <span className="relative z-10 text-2xl font-black group-hover:animate-bounce">←</span>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                </div>
              </button>
              
              <button
                onClick={handleNext}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 group perspective-1000"
              >
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-2xl blur opacity-0 group-hover:opacity-40 transition-all duration-700"></div>
                <div className="relative w-14 h-14 bg-white/95 backdrop-blur-xl border-2 border-white/60 rounded-2xl flex items-center justify-center text-gray-700 hover:text-white hover:bg-gradient-to-r hover:from-[#006da6] hover:to-[#0080c7] hover:border-[#006da6] transition-all duration-700 hover:-translate-y-2 hover:scale-110 hover:-rotate-12 transform-gpu shadow-xl hover:shadow-2xl overflow-hidden"
                     style={{ transformStyle: 'preserve-3d' }}>
                  <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#0080c7]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
                  <span className="relative z-10 text-2xl font-black group-hover:animate-bounce">→</span>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                </div>
              </button>
            </>
          )}
        </div>

        {testimonials.length > 1 && (
          <div className="flex justify-center gap-3 mb-16">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => handleDotClick(index)}
                className="relative group"
              >
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-0 group-hover:opacity-60 transition-all duration-500"></div>
                <div className={`relative w-4 h-4 rounded-full transition-all duration-500 hover:scale-125 transform-gpu ${
                  index === currentIndex 
                    ? 'bg-gradient-to-r from-[#006da6] to-[#0080c7] shadow-lg' 
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}></div>
              </button>
            ))}
          </div>
        )}

        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {testimonials.slice(0, 3).map((testimonial, index) => (
            <div 
              key={testimonial.id}
              className="relative group animate-fade-in-up h-full"
              style={{ animationDelay: `${cardsVisible ? 400 + index * 200 : 0}ms` }}
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
              <div className="relative bg-white/95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu border-2 border-white/60 overflow-hidden h-full flex flex-col">
                <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#0080c7]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
                
                <div className="relative z-10 flex flex-col h-full">
                  {/* Avatar for card */}
                  <div className="flex justify-center mb-4">
                    <div className="relative group/card-avatar">
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-0 group-hover/card-avatar:opacity-40 transition-all duration-500"></div>
                      <img
                        src={generateAvatar(testimonial.name, index)}
                        alt={`${testimonial.name} avatar`}
                        className="relative w-16 h-16 rounded-full border-3 border-white shadow-lg group-hover/card-avatar:scale-110 transition-all duration-500"
                      />
                    </div>
                  </div>

                  <div className="flex justify-center mb-4">
                    <div className="flex gap-1">
                      {renderStars(testimonial.rating)}
                    </div>
                  </div>
                  
                  <blockquote className="text-gray-800 mb-6 leading-relaxed italic flex-grow text-center">
                    <span className="drop-shadow-sm">"{testimonial.text}"</span>
                  </blockquote>
                  
                  <div className="text-center mt-auto">
                    <div className="font-bold text-gray-900 mb-2 group-hover:text-[#006da6] transition-colors duration-500 drop-shadow-sm">
                      {testimonial.name}
                    </div>
                    <div className="text-sm text-gray-600 mb-4">
                      {testimonial.location}
                    </div>
                    
                    <div className="flex flex-wrap justify-center gap-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r ${getServiceBadgeColor(testimonial.service)} shadow-md`}>
                        {testimonial.service}
                      </span>
                      
                      {testimonial.verified && (
                        <span className="flex items-center text-xs text-green-700 bg-green-50 px-2 py-1 rounded-full font-bold">
                          <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                          Verified
                        </span>
                      )}
                      
                      {testimonial.ndisParticipant && (
                        <span className="px-2 py-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-bold rounded-full">
                          NDIS
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <div className="relative group inline-block">
            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-0 group-hover:opacity-40 transition-all duration-700"></div>
            <Button
              onClick={handleViewAllTestimonials}
              variant="primary"
              size="lg"
              className="relative transform-gpu hover:-translate-y-2 hover:scale-105 transition-all duration-700"
            >
              View All Testimonials
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;

