export const testimonialsData = [
    {
      id: 1,
      name: 'Sarah M.',
      location: 'North Shore, NSW',
      service: 'End-of-Lease Cleaning',
      rating: 5,
      text: 'Absolutely fantastic service! The team was professional, thorough, and helped me get my full bond back. The before and after photos they provided were perfect for the real estate agent.',
      date: '2024-01-15',
      verified: true
    },
    {
      id: 2,
      name: 'Michael T.',
      location: 'Western Sydney, NSW',
      service: 'NDIS Cleaning Support',
      rating: 5,
      text: 'As an NDIS participant, I appreciate how respectful and understanding the team is. They work around my schedule and provide clear invoices for my plan manager. Highly recommended!',
      date: '2024-01-20',
      verified: true,
      ndisParticipant: true
    },
    {
      id: 3,
      name: 'Jennifer L.',
      location: 'Eastern Suburbs, NSW',
      service: 'Deep Cleaning',
      rating: 5,
      text: 'The deep clean was incredible! They got into every corner and crevice. My home has never looked better. The attention to detail was outstanding.',
      date: '2024-01-25',
      verified: true
    },
    {
      id: 4,
      name: 'David R.',
      location: 'Inner West, NSW',
      service: 'General Home Cleaning',
      rating: 5,
      text: 'Regular fortnightly service that keeps our busy household running smoothly. The team is reliable, efficient, and always does a great job. Worth every dollar!',
      date: '2024-02-01',
      verified: true
    },
    {
      id: 5,
      name: 'Lisa K.',
      location: 'Hills District, NSW',
      service: 'office and commecial cleaning',
      rating: 5,
      text: 'Amazing work removing pet hair from our furniture and carpets. Our golden retriever sheds everywhere, but they made our home look and smell fresh again!',
      date: '2024-02-05',
      verified: true
    },
    {
      id: 6,
      name: 'Robert P.',
      location: 'Northern Beaches, NSW',
      service: 'Window & Carpet Cleaning',
      rating: 5,
      text: 'Professional window and carpet cleaning service. The carpets look brand new and the windows are crystal clear. Great value for money and excellent customer service.',
      date: '2024-02-10',
      verified: true
    },
    {
      id: 7,
      name: 'Amanda S.',
      location: 'Greater Western Sydney, NSW',
      service: 'NDIS Cleaning Support',
      rating: 5,
      text: 'The team understands my specific needs as an NDIS participant. They are patient, kind, and always deliver quality cleaning services. The invoicing is perfect for my plan manager.',
      date: '2024-02-15',
      verified: true,
      ndisParticipant: true
    },
    {
      id: 8,
      name: 'Mark W.',
      location: 'Sydney CBD, NSW',
      service: 'End-of-Lease Cleaning',
      rating: 5,
      text: 'Stress-free bond cleaning experience. They handled everything professionally and I got my full deposit back. The bond-back guarantee gave me peace of mind.',
      date: '2024-02-20',
      verified: true
    }
  ];
  
  export const getTestimonialsByService = (serviceType) => {
    return testimonialsData.filter(testimonial => 
      testimonial.service.toLowerCase().includes(serviceType.toLowerCase())
    );
  };
  
  export const getNDISTestimonials = () => {
    return testimonialsData.filter(testimonial => testimonial.ndisParticipant);
  };
  
  export const getVerifiedTestimonials = () => {
    return testimonialsData.filter(testimonial => testimonial.verified);
  };
  
  export const getRecentTestimonials = (limit = 6) => {
    return testimonialsData
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, limit);
  };
  
  export const getAverageRating = () => {
    const totalRating = testimonialsData.reduce((sum, testimonial) => sum + testimonial.rating, 0);
    return (totalRating / testimonialsData.length).toFixed(1);
  };
  
  export const getTotalTestimonials = () => {
    return testimonialsData.length;
  };
  
  export const getTestimonialById = (id) => {
    return testimonialsData.find(testimonial => testimonial.id === id);
  };
  