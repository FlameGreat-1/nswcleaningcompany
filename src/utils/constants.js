export const COMPANY_INFO = {
    name: 'NSW Cleaning Company',
    domain: 'nswcleaningcompany.com',
    abn: '82 512 603 347',
    email: {
      support: 'support@nswcleaningcompany.com',
      bookings: 'bookings@nswcleaningcompany.com'
    },
    phone: '+61 0406977014',
    address: {
      state: 'NSW',
      country: 'Australia'
    }
  };

  export const SERVICES = {
    GENERAL: 'general',
    DEEP: 'deep',
    END_OF_LEASE: 'end-of-lease',
    NDIS: 'ndis',
    AIRBNB: 'airbnb',
    POST_RENOVATION: 'post-renovation',
    AFTER_BUILDERS: 'after-builders',
    CUSTOM_ONE_OFF: 'custom-one-off',
    PET_TREATMENT: 'pet-treatment',
    WINDOW_CARPET: 'window-carpet'
  };

  export const CLEANING_TYPES = [
    { id: SERVICES.GENERAL, name: 'Regular / General House Cleaning', basePrice: 120 },
    { id: SERVICES.DEEP, name: 'Deep Cleaning', basePrice: 180 },
    { id: SERVICES.END_OF_LEASE, name: 'End-of-Lease Cleaning', basePrice: 250 },
    { id: SERVICES.NDIS, name: 'NDIS Cleaning Services', basePrice: 140 },
    { id: SERVICES.AIRBNB, name: 'Airbnb Turnover', basePrice: 160 },
    { id: SERVICES.POST_RENOVATION, name: 'Post Renovation', basePrice: 280 },
    { id: SERVICES.AFTER_BUILDERS, name: 'After Builders Clean', basePrice: 300 },
    { id: SERVICES.CUSTOM_ONE_OFF, name: 'Custom One Off', basePrice: 150 }
  ];
  
  export const ROOM_TYPES = {
    BEDROOM: { name: 'Bedroom', price: 25 },
    BATHROOM: { name: 'Bathroom', price: 35 },
    KITCHEN: { name: 'Kitchen', price: 45 },
    LIVING_ROOM: { name: 'Living Room', price: 30 },
    DINING_ROOM: { name: 'Dining Room', price: 20 }
  };
  
  export const EXTRAS = {
    WINDOWS: { name: 'Window Cleaning', price: 40 },
    CARPET: { name: 'Carpet Steam Cleaning', price: 60 },
    OVEN: { name: 'Oven Deep Clean', price: 35 },
    FRIDGE: { name: 'Fridge Clean', price: 25 },
    GARAGE: { name: 'Garage Clean', price: 50 },
    BALCONY: { name: 'Balcony/Patio Clean', price: 30 }
  };

  export const URGENCY_MULTIPLIERS = {
    STANDARD: { name: 'Standard (2-3 days)', multiplier: 1.0, depositRequired: false },
    URGENT: { name: 'Urgent (Next day)', multiplier: 1.2, depositRequired: true, depositPercentage: 30 },
    SAME_DAY: { name: 'Same Day', multiplier: 1.5, depositRequired: true, depositPercentage: 30 }
  };
  
  export const NDIS_INFO = {
    serviceTypes: [
      'Household Tasks',
      'Assistance with Daily Life Tasks in a Group or Shared Living Arrangement',
      'Specialist Disability Accommodation'
    ],
    eligibility: [
      'Self-managed NDIS participants',
      'Plan-managed participants',
      'Agency-managed participants (with pre-approval)'
    ],
    invoiceRequirements: [
      'Participant Name',
      'NDIS Number',
      'Service Dates',
      'Provider Details',
      'GST/Non-GST clarification',
      'Service breakdown by hours'
    ]
  };
  
  export const NAVIGATION_LINKS = [
    { name: 'Home', path: '/' },
    { name: 'About', path: '/about' },
    { name: 'Services', path: '/services' },
    { name: 'Quote Calculator', path: '/quote' },
    { name: 'Gallery', path: '/gallery' },
    { name: 'NDIS Info', path: '/ndis' },
    { name: 'FAQ', path: '/faq' },
    { name: 'Contact', path: '/contact' }
  ];
  
  export const SOCIAL_LINKS = {
    facebook: 'https://www.facebook.com/NSWCleaningCompanyOfficial?mibextid=wwXIfr&mibextid=wwXIfr',
    instagram: 'https://instagram.com/nswcc'
  };
  
  export const FILE_UPLOAD = {
    maxSize: 5 * 1024 * 1024,
    allowedTypes: ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'],
    maxFiles: 5
  };
  
  export const FORM_VALIDATION = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone: /^(\+61|0)[2-9]\d{8}$/,
    abn: /^\d{11}$/,
    ndisNumber: /^\d{9}$/
  };
  
  export const API_ENDPOINTS = {
    quote: '/api/quote',
    contact: '/api/contact',
    upload: '/api/upload',
    invoice: '/api/invoice'
  };
  
  export const STORAGE_KEYS = {
    quoteData: 'ncwcc_quote_data',
    userPreferences: 'ncwcc_user_preferences'
  };
  
  export const TESTIMONIALS_LIMIT = 6;
  export const GALLERY_ITEMS_LIMIT = 12;
  export const FAQ_ITEMS_LIMIT = 10;
  
  export const BUSINESS_HOURS = {
    monday: '7:00 AM - 6:00 PM',
    tuesday: '7:00 AM - 6:00 PM',
    wednesday: '7:00 AM - 6:00 PM',
    thursday: '7:00 AM - 6:00 PM',
    friday: '7:00 AM - 6:00 PM',
    saturday: '7:00 AM - 6:00 PM',
    sunday: '7:00 AM - 4:00 PM'
  };
  
  export const SERVICE_AREAS = [
    'Sydney CBD',
    'North Shore',
    'Eastern Suburbs',
    'Inner West',
    'Western Sydney',
    'Northern Beaches',
    'Greater Western Sydney',
    'Hills District'
  ];
  