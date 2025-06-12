import type { SVGProps } from 'react';

export function BlazeLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 100 100"
      width="80"
      height="80"
      aria-label="InvoiceBlaze Logo"
      className="filter drop-shadow-[0_0_8px_hsl(var(--primary))] transition-all duration-300 hover:drop-shadow-[0_0_15px_hsl(var(--primary))]"
      {...props}
    >
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: 'hsl(var(--primary))', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: 'hsl(var(--accent))', stopOpacity: 1 }} />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
      </defs>
      <path
        fill="url(#logoGradient)"
        d="M50 5 L15 30 L15 70 L50 95 L85 70 L85 30 Z M50 15 L75 30 L75 60 L50 75 L25 60 L25 30 Z"
        stroke="hsl(var(--accent))"
        strokeWidth="2"
      />
      <path
        fill="transparent"
        stroke="hsl(var(--foreground))"
        strokeWidth="1.5"
        d="M35 40 L50 50 L65 40 M35 60 L50 50 L65 60 M50 30 V 70"
      />
    </svg>
  );
}
