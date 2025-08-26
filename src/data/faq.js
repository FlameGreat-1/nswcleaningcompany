export const faqData = [
    {
      id: 1,
      category: 'General',
      question: 'What areas do you service?',
      answer: 'We service all major areas across NSW including Sydney CBD, North Shore, Eastern Suburbs, Inner West, Western Sydney, Northern Beaches, Greater Western Sydney, and Hills District. Contact us to confirm if we service your specific location.'
    },
    {
      id: 2,
      category: 'Pricing',
      question: 'How do you calculate your cleaning prices?',
      answer: 'Our pricing is based on the type of cleaning service, number of rooms, additional extras you select, and urgency level. Use our online quote calculator for an instant estimate, or contact us for a detailed quote.'
    },
    {
      id: 3,
      category: 'NDIS',
      question: 'Are you an NDIS registered provider?',
      answer: 'Yes, we work with NDIS participants across all management types - self-managed, plan-managed, and agency-managed. We provide NDIS compliant invoicing with all required details for your plan manager.'
    },
    {
      id: 4,
      category: 'NDIS',
      question: 'What NDIS services do you provide?',
      answer: 'We provide household tasks and assistance with daily life tasks under your NDIS plan. This includes regular cleaning, deep cleaning, and specialized cleaning support tailored to your individual needs and goals.'
    },
    {
      id: 5,
      category: 'Booking',
      question: 'How far in advance do I need to book?',
      answer: 'For standard bookings, we recommend 2-3 days notice. We also offer next-day and same-day services for urgent requests (additional charges apply). NDIS participants can book regular ongoing services.'
    },
    {
      id: 6,
      category: 'Services',
      question: 'Do you provide your own cleaning supplies?',
      answer: 'Yes, we bring all necessary cleaning supplies and equipment. We use professional-grade, eco-friendly products that are safe for your family and pets. If you have specific product preferences, please let us know.'
    },
    {
      id: 7,
      category: 'Bond Cleaning',
      question: 'Do you guarantee bond return for end-of-lease cleaning?',
      answer: 'Yes, we offer a bond-back guarantee for our end-of-lease cleaning service. If your property manager or landlord is not satisfied with our work, we will return to fix any issues at no extra cost.'
    },
    {
      id: 8,
      category: 'Payment',
      question: 'What payment methods do you accept?',
      answer: 'We accept cash, bank transfer, credit cards, and EFTPOS. For NDIS participants, we can invoice your plan manager directly or provide receipts for self-managed participants.'
    },
    {
      id: 9,
      category: 'Insurance',
      question: 'Are you insured and do your staff have police checks?',
      answer: 'Yes, we are fully insured with public liability coverage. All our cleaning staff undergo police background checks and are trained professionals. Your safety and security are our top priorities.'
    },
    {
      id: 10,
      category: 'Booking',
      question: 'Can I reschedule or cancel my booking?',
      answer: 'Yes, you can reschedule or cancel your booking with at least 24 hours notice at no charge. For same-day cancellations, a cancellation fee may apply. NDIS participants have flexible rescheduling options.'
    },
    {
      id: 11,
      category: 'Services',
      question: 'Do you clean inside appliances like ovens and fridges?',
      answer: 'Yes, oven and fridge cleaning are available as add-on services or included in our deep cleaning and end-of-lease packages. We use specialized cleaning products to ensure thorough sanitization.'
    },
    {
      id: 12,
      category: 'Quality',
      question: 'What if I\'m not satisfied with the cleaning?',
      answer: 'Customer satisfaction is our priority. If you\'re not completely happy with our service, contact us within 24 hours and we\'ll return to address any concerns at no additional cost.'
    }
  ];
  
  export const getFAQByCategory = (category) => {
    return faqData.filter(faq => faq.category.toLowerCase() === category.toLowerCase());
  };
  
  export const getNDISFAQs = () => {
    return faqData.filter(faq => faq.category === 'NDIS');
  };
  
  export const getGeneralFAQs = () => {
    return faqData.filter(faq => faq.category === 'General');
  };
  
  export const getPricingFAQs = () => {
    return faqData.filter(faq => faq.category === 'Pricing');
  };
  
  export const getServiceFAQs = () => {
    return faqData.filter(faq => faq.category === 'Services');
  };
  
  export const getBookingFAQs = () => {
    return faqData.filter(faq => faq.category === 'Booking');
  };
  
  export const searchFAQs = (searchTerm) => {
    const term = searchTerm.toLowerCase();
    return faqData.filter(faq => 
      faq.question.toLowerCase().includes(term) || 
      faq.answer.toLowerCase().includes(term)
    );
  };
  
  export const getFAQCategories = () => {
    const categories = [...new Set(faqData.map(faq => faq.category))];
    return categories.sort();
  };
  
  export const getFAQById = (id) => {
    return faqData.find(faq => faq.id === id);
  };
  
  export const getTotalFAQs = () => {
    return faqData.length;
  };
  
