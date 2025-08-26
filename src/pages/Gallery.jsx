import { useState, useEffect, useRef } from 'react';
import SEO from '../components/common/SEO.jsx';
import GallerySection from '../components/sections/GallerySection.jsx';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import Button from '../components/common/Button.jsx';
import { API_ENDPOINTS } from '../utils/constants.js';

const Gallery = () => {
  const [allGalleryItems, setAllGalleryItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedImage, setSelectedImage] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [error, setError] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [galleryVisible, setGalleryVisible] = useState(false);
  const sectionRef = useRef(null);
  const galleryRef = useRef(null);

  const itemsPerPage = 12;
  
  const filterOptions = [
    { id: 'all', label: 'All Services' },
    { id: 'general', label: 'General Cleaning' },
    { id: 'deep', label: 'Deep Cleaning' },
    { id: 'end-of-lease', label: 'End-of-Lease' },
    { id: 'ndis', label: 'NDIS Support' }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const galleryObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setGalleryVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    if (galleryRef.current) {
      galleryObserver.observe(galleryRef.current);
    }

    return () => {
      observer.disconnect();
      galleryObserver.disconnect();
    };
  }, []);

  useEffect(() => {
    fetchAllGalleryItems();
  }, []);

  useEffect(() => {
    applyFilter();
  }, [filter, allGalleryItems]);

  const fetchAllGalleryItems = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_ENDPOINTS.gallery || '/api/gallery'}?limit=all`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch gallery items');
      }
      
      const data = await response.json();
      setAllGalleryItems(data.items || getDefaultGalleryItems());
    } catch (err) {
      setError(err.message);
      setAllGalleryItems(getDefaultGalleryItems());
    } finally {
      setLoading(false);
    }
  };

  const getDefaultGalleryItems = () => [
    {
      id: 1,
      title: 'End-of-Lease Clean in Box Hill',
      serviceType: 'end-of-lease',
      beforeImage: '/images/gallery/before-1.jpg',
      afterImage: '/images/gallery/after-1.jpg',
      location: 'Box Hill, NSW',
      description: 'Complete bond cleaning transformation with full house and building restoration'
    },
    {
      id: 2,
      title: 'Deep Kitchen Clean',
      serviceType: 'deep',
      beforeImage: '/images/gallery/before-6.jpeg',
      afterImage: '/images/gallery/after-6.jpeg',
      location: 'Sydney CBD, NSW',
      description: 'Professional deep kitchen restoration including oven, rangehood, and appliances'
    },
    {
      id: 3,
      title: 'NDIS Participant Home',
      serviceType: 'ndis',
      beforeImage: '/images/gallery/before-3.jpg',
      afterImage: '/images/gallery/after-3.jpg',
      location: 'Western Sydney, NSW',
      description: 'Respectful NDIS cleaning service supporting independent living'
    },
    {
      id: 4,
      title: 'Bathroom Deep Clean',
      serviceType: 'deep',
      beforeImage: '/images/gallery/before-4.jpeg',
      afterImage: '/images/gallery/after-4.jpeg',
      location: 'North Shore, NSW',
      description: 'Complete bathroom sanitization with tile and grout restoration'
    },
    {
      id: 5,
      title: 'General Home Maintenance',
      serviceType: 'general',
      beforeImage: '/images/gallery/before-5.jpeg',
      afterImage: '/images/gallery/after-5.jpeg',
      location: 'Eastern Suburbs, NSW',
      description: 'Regular home cleaning service maintaining cleanliness and hygiene'
    },
    {
      id: 6,
      title: 'Rug Steam Cleaning',
      serviceType: 'general',
      beforeImage: '/images/gallery/before-7.jpeg',
      afterImage: '/images/gallery/after-7.jpeg',
      location: 'Inner West, NSW',
      description: 'Professional rug restoration removing stains and odors'
    },
    {
      id: 7,
      title: 'Post-Construction Clean',
      serviceType: 'deep',
      beforeImage: '/images/gallery/before-2.jpg',
      afterImage: '/images/gallery/after-2.jpg',
      location: 'Hills District, NSW',
      description: 'Complete post-renovation cleaning including dust and debris removal'
    },
    {
      id: 8,
      title: 'NDIS Weekly Service',
      serviceType: 'ndis',
      beforeImage: '/images/gallery/before-8.jpg',
      afterImage: '/images/gallery/after-8.jpg',
      location: 'Greater Western Sydney, NSW',
      description: 'Regular NDIS cleaning support maintaining participant independence'
    },
    {
      id: 9,
      title: 'Office Deep Clean',
      serviceType: 'deep',
      beforeImage: '/images/gallery/before-9.jpg',
      afterImage: '/images/gallery/after-9.jpg',
      location: 'Sydney CBD, NSW',
      description: 'Commercial office space deep cleaning and sanitization'
    },
    {
      id: 10,
      title: 'End-of-Lease Apartment',
      serviceType: 'end-of-lease',
      beforeImage: '/images/gallery/before-10.jpg',
      afterImage: '/images/gallery/after-10.jpg',
      location: 'Northern Beaches, NSW',
      description: 'Full apartment bond cleaning with guaranteed bond return'
    },
    {
      id: 11,
      title: 'office and commecial cleaning Service',
      serviceType: 'general',
      beforeImage: '/images/gallery/before-11.jpeg',
      afterImage: '/images/gallery/after-11.jpeg',
      location: 'Western Sydney, NSW',
      description: 'Specialized office and commecial cleaning and odor treatment service'
    },
    {
      id: 12,
      title: 'Window Cleaning Service',
      serviceType: 'general',
      beforeImage: '/images/gallery/before-12.jpg',
      afterImage: '/images/gallery/after-12.jpg',
      location: 'Eastern Suburbs, NSW',
      description: 'Professional interior and exterior window cleaning service'
    }
  ];

  const applyFilter = () => {
    if (filter === 'all') {
      setFilteredItems(allGalleryItems);
    } else {
      setFilteredItems(allGalleryItems.filter(item => item.serviceType === filter));
    }
    setCurrentPage(1);
  };

  const openLightbox = (item) => {
    setSelectedImage(item);
  };

  const closeLightbox = () => {
    setSelectedImage(null);
  };

  const handleGetQuote = () => {
    window.location.href = '/quote';
  };

  const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentItems = filteredItems.slice(startIndex, startIndex + itemsPerPage);

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <>
        <SEO
          title="Gallery - Before & After Photos"
          description="View our professional cleaning transformations. Before and after photos showcasing our quality cleaning services across NSW."
        />
        <main className="pt-24 relative overflow-hidden">
          <div className="absolute inset-0">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/3 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#0080c7]/2 rounded-full blur-3xl animate-pulse delay-1000"></div>
          </div>
          <section className="section-padding bg-white relative z-10">
            <div className="container mx-auto text-center">
              <LoadingSpinner size="lg" text="Loading gallery..." />
            </div>
          </section>
        </main>
      </>
    );
  }

  return (
    <>
      <SEO
        title="Gallery - Before & After Photos of Our Cleaning Services"
        description="View real transformations from our professional cleaning services. Before and after photos showcasing general cleaning, deep cleaning, end-of-lease cleaning, and NDIS support services across NSW."
        keywords="cleaning before after photos, cleaning transformations, professional cleaning results, NSW cleaning gallery, cleaning service photos, bond cleaning results"
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
                See the <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Difference We Make</span>
              </h1>
              <p className="text-base md:text-lg text-[#4B4B4B] leading-relaxed font-medium animate-fade-in-up delay-300">
                Real transformations from our professional cleaning services across NSW
              </p>
            </div>
          </div>
        </section>

        <section ref={galleryRef} className="section-padding bg-gradient-to-br from-gray-50/80 via-white/60 to-gray-50/80 backdrop-blur-xl relative z-10">
          <div className="container mx-auto">
            <div className="max-w-6xl mx-auto">
              <div className="flex flex-wrap justify-center gap-3 mb-12 animate-fade-in-up delay-600">
                {filterOptions.map((option, index) => (
                  <button
                    key={option.id}
                    onClick={() => setFilter(option.id)}
                    className={`relative px-6 py-3 rounded-full text-sm font-black transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group overflow-hidden ${
                      filter === option.id
                        ? 'bg-gradient-to-r from-[#006da6] to-[#0080c7] text-white'
                        : 'bg-white/80 backdrop-blur-lg text-[#4B4B4B] hover:bg-gradient-to-r hover:from-[#006da6]/10 hover:to-[#0080c7]/10 border-2 border-white/40 hover:border-[#006da6]/30'
                    }`}
                    style={{ animationDelay: `${800 + index * 100}ms` }}
                  >
                    <span className="relative z-10">{option.label}</span>
                    {filter !== option.id && (
                      <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-full"></div>
                    )}
                  </button>
                ))}
              </div>

              {error && filteredItems.length === 0 ? (
                <div className="text-center py-12 animate-fade-in-up delay-1000">
                  <p className="text-[#4B4B4B] mb-6 font-medium">Unable to load gallery at this time.</p>
                  <Button 
                    onClick={() => window.location.reload()} 
                    className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-6 py-3 rounded-full text-sm transition-all duration-700 hover:scale-110 hover:-translate-y-2 shadow-xl hover:shadow-2xl transform-gpu group overflow-hidden"
                  >
                    <span className="relative z-10">Try Again</span>
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 transform group-hover:translate-x-full"></div>
                  </Button>
                </div>
              ) : (
                <>
                                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                    {currentItems.map((item, index) => (
                      <div 
                        key={item.id}
                        className="relative group animate-fade-in-up cursor-pointer h-full"
                        style={{ animationDelay: `${galleryVisible ? 1000 + index * 150 : 0}ms` }}
                        onClick={() => openLightbox(item)}
                      >
                        <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                        <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-4 hover:scale-105 transform-gpu overflow-hidden border-2 border-white/40 h-full flex flex-col">
                          <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
                          <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-t-3xl"></div>
                          <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>

                          <div className="relative">
                            <div className="grid grid-cols-2 h-56">
                              <div className="relative overflow-hidden rounded-tl-3xl">
                                <img
                                  src={item.beforeImage}
                                  alt={`Before - ${item.title}`}
                                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                  onError={(e) => {
                                    e.target.src = '/images/placeholder-before.jpg';
                                  }}
                                />
                                <div className="absolute top-3 left-3 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-black px-2 py-1 rounded-full shadow-lg">
                                  Before
                                </div>
                                <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                              </div>
                              <div className="relative overflow-hidden rounded-tr-3xl">
                                <img
                                  src={item.afterImage}
                                  alt={`After - ${item.title}`}
                                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                  onError={(e) => {
                                    e.target.src = '/images/placeholder-after.jpg';
                                  }}
                                />
                                <div className="absolute top-3 right-3 bg-gradient-to-r from-[#006da6] to-[#0080c7] text-white text-xs font-black px-2 py-1 rounded-full shadow-lg">
                                  After
                                </div>
                                <div className="absolute inset-0 bg-gradient-to-bl from-[#006da6]/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                              </div>
                            </div>
                          </div>

                          <div className="relative z-10 p-6 flex-grow flex flex-col">
                            <h3 className="font-black text-gray-900 mb-2 text-lg group-hover:text-[#006da6] transition-colors duration-500">{item.title}</h3>
                            <p className="text-sm text-[#4B4B4B] mb-3 leading-relaxed font-medium group-hover:text-[#333] transition-colors duration-500 flex-grow">{item.description}</p>
                            <p className="text-xs text-[#666] flex items-center font-semibold">
                              <span className="w-2 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full mr-2 group-hover:animate-pulse"></span>
                              {item.location}
                            </p>
                          </div>

                          <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 rounded-b-3xl"></div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-2 animate-fade-in-up delay-1200">
                      <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="relative px-4 py-2 rounded-full bg-white/80 backdrop-blur-lg text-[#4B4B4B] hover:bg-gradient-to-r hover:from-[#006da6]/10 hover:to-[#0080c7]/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu font-black text-sm border-2 border-white/40 hover:border-[#006da6]/30 group overflow-hidden"
                      >
                        <span className="relative z-10">Previous</span>
                        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-full"></div>
                      </button>
                      
                      {[...Array(totalPages)].map((_, index) => (
                        <button
                          key={index + 1}
                          onClick={() => handlePageChange(index + 1)}
                          className={`relative px-4 py-2 rounded-full transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu font-black text-sm group overflow-hidden ${
                            currentPage === index + 1
                              ? 'bg-gradient-to-r from-[#006da6] to-[#0080c7] text-white'
                              : 'bg-white/80 backdrop-blur-lg text-[#4B4B4B] hover:bg-gradient-to-r hover:from-[#006da6]/10 hover:to-[#0080c7]/10 border-2 border-white/40 hover:border-[#006da6]/30'
                          }`}
                        >
                          <span className="relative z-10">{index + 1}</span>
                          {currentPage !== index + 1 && (
                            <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-full"></div>
                          )}
                        </button>
                      ))}
                      
                      <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="relative px-4 py-2 rounded-full bg-white/80 backdrop-blur-lg text-[#4B4B4B] hover:bg-gradient-to-r hover:from-[#006da6]/10 hover:to-[#0080c7]/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu font-black text-sm border-2 border-white/40 hover:border-[#006da6]/30 group overflow-hidden"
                      >
                        <span className="relative z-10">Next</span>
                        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-full"></div>
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </section>

        <section className="section-padding bg-white relative z-10">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center">
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-0 group-hover:opacity-30 transition-all duration-700"></div>
                <div className="relative bg-gradient-to-r from-[#006da6]/10 via-white/80 to-[#0080c7]/10 backdrop-blur-xl rounded-3xl p-8 md:p-12 shadow-2xl border-2 border-white/40 hover:shadow-[0_0_60px_rgba(0,109,166,0.15)] transition-all duration-700 hover:-translate-y-2 hover:scale-105 transform-gpu overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-t-3xl"></div>
                  
                  <div className="relative z-10">
                    <h2 className="text-3xl md:text-4xl font-black text-black mb-8 group-hover:text-[#006da6] transition-colors duration-500 animate-fade-in-up">
                      Ready for Your <span className="bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent">Transformation?</span>
                    </h2>
                    <p className="text-base text-[#4B4B4B] mb-8 max-w-2xl mx-auto font-medium group-hover:text-[#333] transition-colors duration-500 animate-fade-in-up delay-300">
                      Join hundreds of satisfied customers who have experienced our professional cleaning services.
                    </p>
                    
                    <Button
                      onClick={handleGetQuote}
                      className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-6 py-3 rounded-full text-sm transition-all duration-700 hover:scale-110 hover:-translate-y-2 hover:rotate-1 shadow-xl hover:shadow-[0_15px_30px_rgba(0,0,0,0.3)] transform-gpu group/cta overflow-hidden animate-fade-in-up delay-600"
                      style={{ transformStyle: 'preserve-3d' }}
                    >
                      <span className="relative z-10 flex items-center gap-2">
                        <span className="text-lg group-hover/cta:animate-bounce">💰</span>
                        Get Your Free Quote Today
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/cta:opacity-100 transition-opacity duration-700 transform group-hover/cta:translate-x-full"></div>
                      <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full blur opacity-30 group-hover/cta:opacity-60 transition-opacity duration-700"></div>
                    </Button>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-b-3xl"></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black/90 backdrop-blur-xl z-50 flex items-center justify-center p-4 animate-fade-in"
          onClick={closeLightbox}
        >
          <div className="max-w-5xl w-full relative group animate-scale-in" onClick={(e) => e.stopPropagation()}>
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-30 animate-pulse"></div>
            <div className="relative bg-white/95 backdrop-blur-xl rounded-3xl overflow-hidden shadow-2xl border-2 border-white/40">
              <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 rounded-3xl"></div>
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-t-3xl"></div>
              
              <div className="relative z-10">
                <div className="flex justify-between items-center p-6 border-b border-white/20">
                  <h3 className="text-xl font-black text-gray-900">{selectedImage.title}</h3>
                  <button
                    onClick={closeLightbox}
                    className="relative w-10 h-10 bg-gradient-to-r from-red-500 to-red-600 hover:from-[#180c2e] hover:to-[#2d1b4e] text-white font-black rounded-full transition-all duration-700 hover:scale-110 hover:-translate-y-1 hover:rotate-90 shadow-lg hover:shadow-2xl transform-gpu group/close overflow-hidden"
                  >
                    <span className="relative z-10 text-xl">×</span>
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/close:opacity-100 transition-opacity duration-700 rounded-full"></div>
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2">
                  <div className="relative group/before">
                    <img
                      src={selectedImage.beforeImage}
                      alt={`Before - ${selectedImage.title}`}
                      className="w-full h-64 md:h-96 object-cover transition-transform duration-700 group-hover/before:scale-105"
                    />
                    <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 via-transparent to-transparent opacity-0 group-hover/before:opacity-100 transition-opacity duration-700"></div>
                    <div className="absolute top-4 left-4 bg-gradient-to-r from-red-500 to-red-600 text-white text-sm font-black px-3 py-2 rounded-full shadow-lg group-hover/before:scale-110 transition-transform duration-500">
                      Before
                    </div>
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="bg-black/50 backdrop-blur-lg text-white p-3 rounded-xl opacity-0 group-hover/before:opacity-100 transition-opacity duration-500">
                        <p className="text-sm font-semibold">Original Condition</p>
                      </div>
                    </div>
                  </div>
                  <div className="relative group/after">
                    <img
                      src={selectedImage.afterImage}
                      alt={`After - ${selectedImage.title}`}
                      className="w-full h-64 md:h-96 object-cover transition-transform duration-700 group-hover/after:scale-105"
                    />
                    <div className="absolute inset-0 bg-gradient-to-bl from-[#006da6]/10 via-transparent to-transparent opacity-0 group-hover/after:opacity-100 transition-opacity duration-700"></div>
                    <div className="absolute top-4 right-4 bg-gradient-to-r from-[#006da6] to-[#0080c7] text-white text-sm font-black px-3 py-2 rounded-full shadow-lg group-hover/after:scale-110 transition-transform duration-500">
                      After
                    </div>
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="bg-black/50 backdrop-blur-lg text-white p-3 rounded-xl opacity-0 group-hover/after:opacity-100 transition-opacity duration-500">
                        <p className="text-sm font-semibold">Professional Result</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-6 bg-gradient-to-r from-gray-50/50 via-white/80 to-gray-50/50 backdrop-blur-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-[#4B4B4B] mb-2 font-medium leading-relaxed">{selectedImage.description}</p>
                      <p className="text-sm text-[#666] font-semibold flex items-center gap-2">
                        <span className="text-lg">📍</span>
                        {selectedImage.location}
                      </p>
                    </div>
                    <div className="flex gap-3">
                      <Button
                        onClick={() => window.location.href = '/quote'}
                        className="relative bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:to-[#2d1b4e] text-white hover:text-white font-black px-3 py-2 rounded-full text-xs transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                      >
                        <span className="relative z-10 flex items-center gap-1">
                          <span className="text-sm group-hover/btn:animate-bounce">💰</span>
                          Get Quote
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 transform group-hover/btn:translate-x-full"></div>
                      </Button>
                      <Button
                        onClick={() => window.location.href = '/contact'}
                        className="relative bg-transparent border-2 border-[#006da6] text-[#006da6] hover:bg-gradient-to-r hover:from-[#180c2e] hover:to-[#2d1b4e] hover:text-white hover:border-transparent font-black px-3 py-2 rounded-full text-xs transition-all duration-700 hover:scale-110 hover:-translate-y-1 shadow-lg hover:shadow-2xl transform-gpu group/btn overflow-hidden"
                      >
                        <span className="relative z-10 flex items-center gap-1">
                          <span className="text-sm group-hover/btn:animate-pulse">📞</span>
                          Contact
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#0080c7]/10 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-700 rounded-full"></div>
                      </Button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-center gap-4 pt-4 border-t border-white/20">
                    <div className="flex items-center gap-2 text-sm text-[#666] font-semibold">
                      <span className="w-3 h-3 bg-gradient-to-r from-red-500 to-red-600 rounded-full"></span>
                      Before Cleaning
                    </div>
                    <div className="w-8 h-0.5 bg-gradient-to-r from-red-500 via-gray-300 to-[#006da6] rounded-full"></div>
                    <div className="flex items-center gap-2 text-sm text-[#666] font-semibold">
                      <span className="w-3 h-3 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-full"></span>
                      After Cleaning
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-[#006da6] to-[#0080c7] rounded-b-3xl"></div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Gallery;


