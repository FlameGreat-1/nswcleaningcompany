import { useState } from 'react';
import QuoteForm from '../forms/QuoteForm.jsx';
import Button from '../common/Button.jsx';
import { COMPANY_INFO } from '../../utils/constants.js';
import { scrollToElement } from '../../utils/helpers.js';

const QuoteCalculatorSection = () => {
  const [showFullForm, setShowFullForm] = useState(false);
  const [quoteCompleted, setQuoteCompleted] = useState(false);

  const handleQuoteComplete = (result) => {
    setQuoteCompleted(true);
    if (result.success) {
      setTimeout(() => {
        scrollToElement('contact-section', 80);
      }, 2000);
    }
  };

  const handleGetStarted = () => {
    setShowFullForm(true);
  };

  const handleCallInstead = () => {
    window.location.href = `tel:${COMPANY_INFO.phone}`;
  };

  const handleEmailInstead = () => {
    window.location.href = `mailto:${COMPANY_INFO.email.bookings}`;
  };

  const resetCalculator = () => {
    setShowFullForm(false);
    setQuoteCompleted(false);
  };

  return (
    <section className="section-padding bg-white" id="quote-calculator">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-black mb-6">
            Get an Instant Cleaning Quote
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Get a personalized quote in minutes. Choose your service type, rooms, and extras 
            to see transparent pricing with no hidden fees.
          </p>
        </div>

        {!showFullForm ? (
          <div className="max-w-2xl mx-auto">
            <div className="bg-gradient-to-br from-[#006da6]/10 to-[#0080c7]/5 rounded-2xl p-8 md:p-12 text-center border border-[#006da6]/20">
              <div className="mb-8">
                <div className="w-20 h-20 bg-[#006da6]/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl">🧮</span>
                </div>
                
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  Ready to Get Your Quote?
                </h3>
                
                <p className="text-gray-600 mb-8">
                  Our smart calculator will provide you with an accurate estimate based on your specific needs. 
                  Takes less than 3 minutes to complete.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 text-sm">
                  <div className="flex items-center justify-center p-3 bg-white rounded-lg">
                    <span className="text-[#006da6] mr-2">✓</span>
                    <span className="text-gray-700">Instant pricing</span>
                  </div>
                  <div className="flex items-center justify-center p-3 bg-white rounded-lg">
                    <span className="text-[#006da6] mr-2">✓</span>
                    <span className="text-gray-700">No hidden fees</span>
                  </div>
                  <div className="flex items-center justify-center p-3 bg-white rounded-lg">
                    <span className="text-[#006da6] mr-2">✓</span>
                    <span className="text-gray-700">NDIS compliant</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <Button
                  onClick={handleGetStarted}
                  variant="primary"
                  size="lg"
                  className="w-full md:w-auto"
                >
                  Start Quote Calculator
                </Button>
                
                <div className="text-gray-500 text-sm">
                  Or contact us directly:
                </div>
                
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button
                    onClick={handleCallInstead}
                    variant="outline"
                    size="md"
                    className="flex-1 sm:flex-none"
                  >
                    Call {COMPANY_INFO.phone}
                  </Button>
                  
                  <Button
                    onClick={handleEmailInstead}
                    variant="ghost"
                    size="md"
                    className="flex-1 sm:flex-none"
                  >
                    Email Us
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            {!quoteCompleted && (
              <div className="mb-6 flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-900">
                  Quote Calculator
                </h3>
                <Button
                  onClick={resetCalculator}
                  variant="ghost"
                  size="sm"
                >
                  ← Back to Overview
                </Button>
              </div>
            )}
            
            <QuoteForm
              onQuoteComplete={handleQuoteComplete}
              showPricing={true}
              embedded={true}
              className="shadow-xl"
            />
            
            {quoteCompleted && (
              <div className="mt-8 text-center">
                <Button
                  onClick={resetCalculator}
                  variant="secondary"
                  size="lg"
                >
                  Calculate Another Quote
                </Button>
              </div>
            )}
          </div>
        )}

        <div className="mt-16 bg-gray-50 rounded-2xl p-8 md:p-12">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Why Choose Our Quote Calculator?
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-[#006da6]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <h4 className="font-bold text-gray-900 mb-2">Instant Results</h4>
              <p className="text-sm text-gray-600">
                Get your quote immediately with our smart pricing algorithm
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-[#006da6]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h4 className="font-bold text-gray-900 mb-2">Accurate Pricing</h4>
              <p className="text-sm text-gray-600">
                Tailored quotes based on your specific cleaning requirements
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-[#006da6]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">💰</span>
              </div>
              <h4 className="font-bold text-gray-900 mb-2">Transparent Costs</h4>
              <p className="text-sm text-gray-600">
                No hidden fees or surprise charges - see exactly what you pay
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default QuoteCalculatorSection;

