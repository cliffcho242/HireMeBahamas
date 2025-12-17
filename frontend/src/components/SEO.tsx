import { useEffect } from 'react';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  ogImage?: string;
  ogType?: string;
  ogUrl?: string;
  canonicalUrl?: string;
  noindex?: boolean;
  nofollow?: boolean;
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
  twitterCard?: 'summary' | 'summary_large_image' | 'app' | 'player';
  structuredData?: Record<string, any>;
}

/**
 * SEO Component for Dynamic Meta Tags
 * 
 * Use this component at the top of any page to set SEO metadata dynamically.
 * Falls back to defaults from index.html if not specified.
 * 
 * @example
 * <SEO 
 *   title="Job Board - Find Jobs in The Bahamas"
 *   description="Browse thousands of job opportunities in The Bahamas"
 *   keywords="bahamas jobs, nassau jobs, caribbean employment"
 *   ogImage="https://www.hiremebahamas.com/jobs-og-image.png"
 * />
 */
export function SEO({
  title,
  description,
  keywords,
  ogImage,
  ogType = 'website',
  ogUrl,
  canonicalUrl,
  noindex = false,
  nofollow = false,
  author,
  publishedTime,
  modifiedTime,
  twitterCard = 'summary_large_image',
  structuredData,
}: SEOProps) {
  useEffect(() => {
    // Update document title
    if (title) {
      document.title = `${title} | HireMeBahamas`;
    }

    // Helper to update or create meta tag
    const updateMetaTag = (
      selector: string,
      content: string | undefined,
      property?: boolean
    ) => {
      if (!content) return;

      const attribute = property ? 'property' : 'name';
      let element = document.querySelector(`meta[${attribute}="${selector}"]`) as HTMLMetaElement;

      if (!element) {
        element = document.createElement('meta');
        element.setAttribute(attribute, selector);
        document.head.appendChild(element);
      }

      element.content = content;
    };

    // Update meta tags
    updateMetaTag('description', description);
    updateMetaTag('keywords', keywords);
    updateMetaTag('author', author);

    // Robots meta tag
    if (noindex || nofollow) {
      const robotsContent = [
        noindex ? 'noindex' : 'index',
        nofollow ? 'nofollow' : 'follow',
      ].join(', ');
      updateMetaTag('robots', robotsContent);
    }

    // Open Graph tags
    updateMetaTag('og:title', title ? `${title} | HireMeBahamas` : undefined, true);
    updateMetaTag('og:description', description, true);
    updateMetaTag('og:type', ogType, true);
    updateMetaTag('og:url', ogUrl || window.location.href, true);
    updateMetaTag('og:image', ogImage, true);

    // Article-specific OG tags
    if (ogType === 'article') {
      updateMetaTag('article:published_time', publishedTime, true);
      updateMetaTag('article:modified_time', modifiedTime, true);
      updateMetaTag('article:author', author, true);
    }

    // Twitter Card tags
    updateMetaTag('twitter:card', twitterCard);
    updateMetaTag('twitter:title', title ? `${title} | HireMeBahamas` : undefined);
    updateMetaTag('twitter:description', description);
    updateMetaTag('twitter:image', ogImage);

    // Canonical URL
    if (canonicalUrl) {
      let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
      if (!canonical) {
        canonical = document.createElement('link');
        canonical.rel = 'canonical';
        document.head.appendChild(canonical);
      }
      canonical.href = canonicalUrl;
    }

    // Structured Data (JSON-LD)
    if (structuredData) {
      const scriptId = 'structured-data';
      let script = document.getElementById(scriptId) as HTMLScriptElement;
      
      if (!script) {
        script = document.createElement('script');
        script.id = scriptId;
        script.type = 'application/ld+json';
        document.head.appendChild(script);
      }
      
      script.textContent = JSON.stringify(structuredData);
    }

    // Cleanup function
    return () => {
      // Optionally reset to defaults on unmount
      // For SPA, we keep the updated meta tags
    };
  }, [
    title,
    description,
    keywords,
    ogImage,
    ogType,
    ogUrl,
    canonicalUrl,
    noindex,
    nofollow,
    author,
    publishedTime,
    modifiedTime,
    twitterCard,
    structuredData,
  ]);

  // This component doesn't render anything
  return null;
}

/**
 * Helper function to generate Job Posting structured data
 */
export function generateJobPostingSchema(job: {
  title: string;
  description: string;
  datePosted: string;
  validThrough?: string;
  employmentType?: string;
  hiringOrganization: {
    name: string;
    url?: string;
  };
  jobLocation: {
    city: string;
    country: string;
  };
  baseSalary?: {
    currency: string;
    minValue: number;
    maxValue: number;
    unitText: string;
  };
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    title: job.title,
    description: job.description,
    datePosted: job.datePosted,
    validThrough: job.validThrough,
    employmentType: job.employmentType || 'FULL_TIME',
    hiringOrganization: {
      '@type': 'Organization',
      name: job.hiringOrganization.name,
      sameAs: job.hiringOrganization.url,
    },
    jobLocation: {
      '@type': 'Place',
      address: {
        '@type': 'PostalAddress',
        addressLocality: job.jobLocation.city,
        addressCountry: job.jobLocation.country,
      },
    },
    ...(job.baseSalary && {
      baseSalary: {
        '@type': 'MonetaryAmount',
        currency: job.baseSalary.currency,
        value: {
          '@type': 'QuantitativeValue',
          minValue: job.baseSalary.minValue,
          maxValue: job.baseSalary.maxValue,
          unitText: job.baseSalary.unitText,
        },
      },
    }),
  };
}

/**
 * Helper function to generate Article structured data
 */
export function generateArticleSchema(article: {
  headline: string;
  description: string;
  image: string;
  datePublished: string;
  dateModified?: string;
  author: {
    name: string;
  };
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.headline,
    description: article.description,
    image: article.image,
    datePublished: article.datePublished,
    dateModified: article.dateModified || article.datePublished,
    author: {
      '@type': 'Person',
      name: article.author.name,
    },
    publisher: {
      '@type': 'Organization',
      name: 'HireMeBahamas',
      logo: {
        '@type': 'ImageObject',
        url: 'https://www.hiremebahamas.com/pwa-512x512.png',
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': window.location.href,
    },
  };
}

/**
 * Helper function to generate BreadcrumbList structured data
 */
export function generateBreadcrumbSchema(items: Array<{ name: string; url: string }>) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

export default SEO;
