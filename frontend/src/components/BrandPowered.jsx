import React from 'react';

/**
 * Reusable branding component for "Powered by GSKᴬᴵ"
 * Renders consistent creator/brand identity with styled superscript AI.
 */
export function BrandPowered({ className = '', emphasis = false, prefix = 'Powered by ' }) {
  return (
    <span className={`brand-powered-badge ${className}`}>
      {prefix && <span className="brand-prefix">{prefix}</span>}
      <span className={emphasis ? 'brand-gsk brand-gsk-emphasis' : 'brand-gsk'}>GSK</span>
      <sup className="brand-ai">AI</sup>
    </span>
  );
}

export default BrandPowered;
