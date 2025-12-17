import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { ChatbotWidget } from '../components/ChatbotWidget';

// Docusaurus Root component wrapper
// This component wraps all pages and allows us to add global components
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <BrowserOnly fallback={<div />}>
        {() => <ChatbotWidget />}
      </BrowserOnly>
    </>
  );
}
