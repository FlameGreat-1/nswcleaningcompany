import { Helmet } from 'react-helmet-async';
import { COMPANY_INFO } from '../../utils/constants.js';

const SEO = ({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website',
  noIndex = false
}) => {
  const siteTitle = `${title} | ${COMPANY_INFO.name}`;
  const siteDescription = description || 'Professional cleaning services across NSW including NDIS support, end-of-lease cleaning, deep cleaning and general home cleaning. Reliable, insured and bond-back guaranteed.';
  const siteKeywords = keywords || 'cleaning services NSW, NDIS cleaning, end of lease cleaning, deep cleaning, home cleaning, bond cleaning, professional cleaners Sydney';
  const siteImage = image || '/logo.png';
  const siteUrl = url || `https://${COMPANY_INFO.domain}`;

  return (
    <Helmet>
      <title>{siteTitle}</title>
      <meta name="description" content={siteDescription} />
      <meta name="keywords" content={siteKeywords} />
      
      {noIndex && <meta name="robots" content="noindex,nofollow" />}
      
      <meta property="og:title" content={siteTitle} />
      <meta property="og:description" content={siteDescription} />
      <meta property="og:image" content={siteImage} />
      <meta property="og:url" content={siteUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content={COMPANY_INFO.name} />
      
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={siteTitle} />
      <meta name="twitter:description" content={siteDescription} />
      <meta name="twitter:image" content={siteImage} />
      
      <link rel="canonical" href={siteUrl} />
      
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "LocalBusiness",
          "name": COMPANY_INFO.name,
          "description": siteDescription,
          "url": `https://${COMPANY_INFO.domain}`,
          "telephone": COMPANY_INFO.phone,
          "email": COMPANY_INFO.email.support,
          "address": {
            "@type": "PostalAddress",
            "addressRegion": COMPANY_INFO.address.state,
            "addressCountry": COMPANY_INFO.address.country
          },
          "serviceArea": {
            "@type": "State",
            "name": "New South Wales"
          },
          "priceRange": "$$",
          "openingHours": "Mo-Fr 07:00-18:00, Sa 08:00-16:00"
        })}
      </script>
    </Helmet>
  );
};

export default SEO;
