import SEO from '../components/common/SEO.jsx';
import QuoteCalculatorSection from '../components/sections/QuoteCalculatorSection.jsx';
import { COMPANY_INFO } from '../utils/constants.js';
import Button from '../components/common/Button.jsx';

const QuoteCalculator = () => {
  const handleCallNow = () => {
    window.location.href = `tel:${COMPANY_INFO.phone}`;
  };

  const handleContact = () => {
    window.location.href = '/contact';
  };

  const handleViewServices = () => {
    window.location.href = '/services';
  };

  return (
    <>
      <SEO
        title="Free Instant Quote Calculator - Get Your Cleaning Estimate"
        description="Get an instant quote for professional cleaning services. Calculate costs for general cleaning, deep cleaning, end-of-lease cleaning, and NDIS support services across NSW."
        keywords="cleaning quote calculator, instant cleaning estimate, cleaning cost calculator, free cleaning quote, NSW cleaning prices, NDIS cleaning quote"
      />

      <main className="pt-20">
        <section className="section-padding bg-white">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center mb-16">
              <h1 className="text-4xl md:text-5xl font-bold text-black mb-6">
                Get Your Instant Cleaning Quote
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed mb-8">
                Calculate your cleaning service cost in minutes with our easy-to-use quote calculator
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <div className="text-2xl font-bold text-[#006da6] mb-2">Instant</div>
                  <p className="text-sm text-gray-600">Get your quote immediately</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <div className="text-2xl font-bold text-[#006da6] mb-2">Accurate</div>
                  <p className="text-sm text-gray-600">Based on real service data</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <div className="text-2xl font-bold text-[#006da6] mb-2">No Obligation</div>
                  <p className="text-sm text-gray-600">Free quote with no commitment</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <QuoteCalculatorSection />

        <section className="section-padding bg-gray-50">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold text-black mb-6">
                  How Our Quote Calculator Works
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16">
                <div className="text-center">
                  <div className="w-16 h-16 bg-[#006da6] text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                    1
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2">Select Service</h3>
                  <p className="text-sm text-gray-600">Choose your cleaning type</p>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 bg-[#006da6] text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                    2
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2">Add Details</h3>
                  <p className="text-sm text-gray-600">Specify rooms and extras</p>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 bg-[#006da6] text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                    3
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2">Set Preferences</h3>
                  <p className="text-sm text-gray-600">Choose timing and location</p>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 bg-[#006da6] text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                    4
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2">Get Quote</h3>
                  <p className="text-sm text-gray-600">Receive instant estimate</p>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-8 md:p-12 shadow-lg">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                  Quote Includes Everything
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h4 className="font-bold text-gray-900 mb-4">What's Included:</h4>
                    <ul className="space-y-3">
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">All cleaning supplies and equipment</span>
                      </li>
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">Professional cleaning team</span>
                      </li>
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">Before and after photos</span>
                      </li>
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">Quality guarantee</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-bold text-gray-900 mb-4">Additional Benefits:</h4>
                    <ul className="space-y-3">
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">Fully insured service</span>
                      </li>
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">Police-checked cleaners</span>
                      </li>
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">NDIS compliant invoicing</span>
                      </li>
                      <li className="flex items-start">
                        <div className="w-2 h-2 bg-[#006da6] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">Flexible scheduling</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="section-padding bg-white">
          <div className="container mx-auto">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-3xl md:text-4xl font-bold text-black mb-6">
                Need Help with Your Quote?
              </h2>
              <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
                Our friendly team is here to help you get the most accurate quote for your cleaning needs.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  onClick={handleCallNow}
                  variant="primary"
                  size="lg"
                >
                  Call {COMPANY_INFO.phone}
                </Button>
                
                <Button
                  onClick={handleContact}
                  variant="secondary"
                  size="lg"
                >
                  Send Message
                </Button>
                
                <Button
                  onClick={handleViewServices}
                  variant="outline"
                  size="lg"
                >
                  View All Services
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
};

export default QuoteCalculator;
