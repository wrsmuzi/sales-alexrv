'use client';

import React, { useState } from 'react';
import { Menu, X, Crown } from 'lucide-react';
import Link from 'next/link';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed w-full z-50 transition-all duration-300 py-4 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center bg-dubai-dark/80 backdrop-blur-md border border-white/10 p-3 rounded-full">
          <Link href="/" className="flex items-center space-x-2 group cursor-pointer px-2">
            <Crown className="w-6 h-6 sm:w-8 sm:h-8 text-dubai-gold group-hover:rotate-12 transition-transform" />
            <span className="text-sm sm:text-xl font-serif font-bold tracking-widest uppercase whitespace-nowrap">
              AI <span className="text-dubai-gold">Sales Engine</span>
            </span>
          </Link>

          <div className="hidden lg:flex items-center space-x-8 text-xs font-medium uppercase tracking-widest">
            <Link href="/" className="hover:text-dubai-gold transition-colors">Dashboard</Link>
            <Link href="/about" className="hover:text-dubai-gold transition-colors">Methodology</Link>
            <Link href="/contact" className="hover:text-dubai-gold transition-colors">Support</Link>
            <Link href="/dashboard" className="bg-dubai-gold text-dubai-dark px-6 py-2 rounded-full font-bold hover:bg-dubai-goldLight transition-all">
              Client Portal
            </Link>
          </div>

          <div className="lg:hidden flex items-center">
            <button onClick={() => setIsOpen(!isOpen)} className="text-white p-2">
              {isOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {isOpen && (
          <div className="lg:hidden absolute top-20 left-4 right-4 bg-dubai-dark border border-dubai-gold/30 p-6 rounded-3xl space-y-6 z-40 shadow-2xl">
            <Link href="/" onClick={() => setIsOpen(false)} className="block text-center py-2 text-lg hover:text-dubai-gold transition-colors">Dashboard</Link>
            <Link href="/about" onClick={() => setIsOpen(false)} className="block text-center py-2 text-lg hover:text-dubai-gold transition-colors">Methodology</Link>
            <Link href="/contact" onClick={() => setIsOpen(false)} className="block text-center py-2 text-lg hover:text-dubai-gold transition-colors">Support</Link>
            <Link href="/dashboard" onClick={() => setIsOpen(false)} className="block text-center py-3 bg-dubai-gold text-dubai-dark rounded-full font-bold text-lg">Client Portal</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
