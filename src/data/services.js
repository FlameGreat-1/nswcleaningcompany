import { SERVICES } from '../utils/constants.js';

export const servicesData = [
  {
    id: SERVICES.GENERAL,
    title: 'Regular / General House Cleaning',
    description: 'Routine cleaning to keep your home fresh and tidy.',
    icon: '🏠',
    basePrice: 120,
    duration: '2-3 hours',
    includes: [
      'Dusting surfaces, furniture & décor',
      'Vacuum carpets & rugs',
      'Mop hard floors',
      'Wipe kitchen benches & splashbacks',
      'Clean stovetop (external)',
      'Empty bins & replace liners',
      'Wipe bathroom surfaces (sink, toilet, mirror)',
      'Spot clean marks on walls/doors',
    ],
    popular: false
  },
  {
    id: SERVICES.DEEP,
    title: 'Deep Cleaning',
    description: 'In-depth, detailed cleaning including skirtings, tiles, and hard-to-reach areas.',
    icon: '🧹',
    basePrice: 180,
    duration: '4-6 hours',
    includes: [
      'Scrub shower tiles & grout',
      'Clean inside oven',
      'Clean inside rangehood filters',
      'Clean skirting boards',
      'Dust light fittings',
      'Clean behind/under furniture (if accessible)',
      'Window sills & tracks',
      'Ceiling fans'
    ],
    popular: true
  },
  {
    id: SERVICES.END_OF_LEASE,
    title: 'End-of-Lease Cleaning',
    description: 'Bond-back guaranteed cleaning for tenants and agents.',
    icon: '🛋',
    basePrice: 250,
    duration: '6-8 hours',
    includes: [
      'All rooms top-to-bottom cleaning',
      'Inside & outside cupboards',
      'Inside oven, rangehood, and stovetop',
      'Windows (internal & external upon request)',
      'Walls spot cleaned or full wipe down',
      'Carpet steam cleaning (optional/add-on)',
      'Bathrooms: descaling tiles, scrubbing grout',
      'Full kitchen detail incl. appliances',
      'Blinds dusted or wiped'
    ],
    popular: false,
    guarantee: 'Bond-back guarantee included'
  },
  {
    id: SERVICES.NDIS,
    title: 'NDIS Cleaning Services',
    description: 'Reliable, respectful cleaning for participants with invoices tailored to your plan manager.',
    icon: '🧽',
    basePrice: 140,
    duration: '2-4 hours',
    includes: [
      'Tailored to participant\'s needs & support plan',
      'General cleaning of kitchen, bathroom, living areas',
      'Safety-focused cleaning (non-toxic products)',
      'Optional linen change or laundry support',
      'Flexible frequency (weekly, fortnightly, etc.)'
    ],
    popular: false,
    ndisCompliant: true
  },
  {
    id: SERVICES.PET_TREATMENT,
    title: 'Office & Commercial Cleaning',
    description: 'Professional cleaning for office spaces and commercial properties.',
    icon: '🏢',
    basePrice: 50,
    duration: '1-2 hours',
    includes: [
      'Dust desks, chairs, and equipment',
      'Sanitise shared surfaces (phones, keyboards)',
      'Kitchenette wipe-down',
      'Rubbish bin emptying',
      'Bathroom sanitisation',
      'Vacuum and mop all floors',
      'Supply restocking (toilet paper, hand soap, etc.)'
    ],
    popular: false,
    addon: true
  },
  {
    id: SERVICES.WINDOW_CARPET,
    title: 'Add-on Services',
    description: 'Additional cleaning services that can be added to any package.',
    icon: '🪟',
    basePrice: 80,
    duration: '2-3 hours',
    includes: [
      'Carpet steam cleaning',
      'Window cleaning (internal/external)',
      'Fridge cleaning (inside)',
      'Oven deep cleaning',
      'Balcony sweep & mop',
      'Pressure washing (driveway, walls)',
      'Mould treatment',
      'Post-construction cleaning',
      'After-party/event clean-up'
    ],
    popular: false,
    addon: true
  },
  {
    id: 'airbnb',
    title: 'Airbnb Turnover Cleaning',
    description: 'Quick and thorough cleaning between guest stays.',
    icon: '🏨',
    basePrice: 150,
    duration: '2-4 hours',
    includes: [
      'Complete linen change',
      'Bathroom sanitization',
      'Kitchen deep clean',
      'Dust and vacuum all areas',
      'Restock essentials',
      'Trash removal',
      'Property inspection'
    ],
    popular: false
  },
  {
    id: 'post_renovation',
    title: 'Post-Renovation Cleaning',
    description: 'Thorough cleaning after construction or renovation work.',
    icon: '🔨',
    basePrice: 280,
    duration: '6-8 hours',
    includes: [
      'Construction dust removal',
      'Paint splatter cleaning',
      'Debris removal',
      'Window and frame cleaning',
      'Floor deep cleaning',
      'Surface sanitization',
      'Final inspection'
    ],
    popular: false
  },
  {
    id: 'pressure_washing',
    title: 'Pressure Washing',
    description: 'High-pressure cleaning for outdoor surfaces.',
    icon: '💦',
    basePrice: 120,
    duration: '2-3 hours',
    includes: [
      'Driveway cleaning',
      'Patio/deck washing',
      'Exterior wall cleaning',
      'Fence cleaning',
      'Removal of mold and mildew',
      'Gutter exterior cleaning'
    ],
    popular: false,
    addon: true
  },
  {
    id: 'mould_removal',
    title: 'Mould Removal',
    description: 'Specialized cleaning to remove mould and prevent regrowth.',
    icon: '🧫',
    basePrice: 150,
    duration: '3-4 hours',
    includes: [
      'Mould identification',
      'Safe removal treatment',
      'Surface sanitization',
      'Preventative treatment',
      'Humidity control recommendations'
    ],
    popular: false,
    addon: true
  },
  {
    id: 'after_builders',
    title: 'After Builders Clean',
    description: 'Comprehensive cleaning after construction work is completed.',
    icon: '🏗️',
    basePrice: 300,
    duration: '8-10 hours',
    includes: [
      'Removal of construction debris',
      'Dust elimination from all surfaces',
      'Window and frame cleaning',
      'Floor scrubbing and polishing',
      'Fixture and fitting cleaning',
      'Paint and adhesive residue removal',
      'Final inspection'
    ],
    popular: false
  },
  {
    id: 'custom',
    title: 'Custom One-off Cleans',
    description: 'Tailored cleaning services for specific needs.',
    icon: '✨',
    basePrice: 160,
    duration: 'Varies',
    includes: [
      'Consultation to determine needs',
      'Customized cleaning plan',
      'Specialized equipment as needed',
      'Flexible scheduling',
      'Detailed follow-up'
    ],
    popular: false
  }
];

export const getServiceById = (serviceId) => {
  return servicesData.find(service => service.id === serviceId);
};

export const getPopularServices = () => {
  return servicesData.filter(service => service.popular);
};

export const getMainServices = () => {
  return servicesData.filter(service => !service.addon);
};

export const getAddonServices = () => {
  return servicesData.filter(service => service.addon);
};

export const getNDISServices = () => {
  return servicesData.filter(service => service.ndisCompliant);
};

export const getServicePrice = (serviceId) => {
  const service = getServiceById(serviceId);
  return service ? service.basePrice : 0;
};

export const getServiceDuration = (serviceId) => {
  const service = getServiceById(serviceId);
  return service ? service.duration : 'N/A';
};

export const getServiceIncludes = (serviceId) => {
  const service = getServiceById(serviceId);
  return service ? service.includes : [];
};
