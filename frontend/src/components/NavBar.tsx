import React from "react";
import { Link, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/wiki", label: "Wiki" },
  { to: "/scraping", label: "Scraping" },
  { to: "/ingestion", label: "Ingestion" },
  { to: "/curation", label: "Curation" },
  { to: "/about", label: "About" },
];

export default function NavBar() {
  const loc = useLocation();
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem("API_KEY") : null;
  return (
    <nav style={{display: 'flex', alignItems: 'center', gap: 24, background: '#f6f6f6', padding: '8px 32px'}}>
      {NAV_ITEMS.map(item => (
        <Link to={item.to} key={item.to}
          style={{fontWeight: loc.pathname.startsWith(item.to) ? 'bold' : undefined, textDecoration: 'none'}}>
          {item.label}
        </Link>
      ))}
      <span style={{marginLeft: 'auto', fontSize: 14}}>
        {apiKey ? `API key active` : '🔒 Not logged in'}
      </span>
    </nav>
  );
}
