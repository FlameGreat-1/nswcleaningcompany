import HeroSection from '../components/sections/HeroSection.jsx';
import AboutSection from '../components/sections/AboutSection.jsx';
import ServicesSection from '../components/sections/ServicesSection.jsx';
import GallerySection from '../components/sections/GallerySection.jsx';
import NDISSection from '../components/sections/NDISSection.jsx';
import TestimonialsSection from '../components/sections/TestimonialsSection.jsx';
import QuoteCalculatorSection from '../components/sections/QuoteCalculatorSection.jsx';
import ContactSection from '../components/sections/ContactSection.jsx';
import SEO from '../components/common/SEO.jsx';

const Home = () => {
  return (
    <>
      <SEO 
        title="Professional Cleaning Services NSW"
        description="Professional cleaning services across NSW including NDIS support, end-of-lease cleaning, deep cleaning and general home cleaning. Reliable, insured and bond-back guaranteed."
        keywords="cleaning services NSW, NDIS cleaning, end of lease cleaning, deep cleaning, home cleaning, bond cleaning, professional cleaners Sydney"
      />
      
      <HeroSection />
      <AboutSection />
      <ServicesSection />
      <GallerySection />
      <NDISSection />
      <TestimonialsSection />
      <QuoteCalculatorSection />
      <ContactSection />
    </>
  );
};

export default Home;
