"use client";

import Link from 'next/link';
import Image from 'next/image';
import siteBg from '../assets/site-bg.png';
import { useState, useEffect } from 'react';
import { ArrowRightIcon, CopyIcon, TerminalIcon } from 'lucide-react';

export default function HomePage() {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Prevent scrolling on this page
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';

    return () => {
      // Clean up when component unmounts
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
    };
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText('pip install peargent');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <>
      <div className="fixed inset-0 w-full h-full overflow-hidden">
        {/* Full Screen Background Image */}
        <div className="absolute inset-0 w-full h-full -z-10">
          <Image
            src={siteBg}
            alt="Site Background"
            fill
            className="object-cover"
            priority
          />
        </div>
        <main className="flex flex-col justify-center items-start min-h-screen px-4 sm:px-8 md:px-16 lg:px-20 xl:px-32 pt-1">
          <div className="w-full max-w-5xl">
            {/* Hero Heading */}
            {/* <h1 className="font-normal text-black text-[2.25rem] sm:text-4xl md:text-6xl lg:text-7xl xl:text-8xl leading-[1.1] font-[var(--font-instrument-serif),serif]">
      peargent.
    </h1> */}

            <div className="mt-4">
              <p className="max-w-2xl font-['Inter',Helvetica] font-medium text-black text-2xl sm:text-4xl md:text-5xl leading-tight">
                Building powerful AI agents,
              </p>
              <p className="mt-1 max-w-xl font-['Inter',Helvetica] font-medium text-black text-2xl sm:text-4xl md:text-5xl leading-tight">
                made simple.
              </p>
            </div>

            {/* CTA Section */}
            <div className="mt-10 sm:mt-14 md:mt-16 flex flex-col sm:flex-row items-stretch sm:items-center gap-4 sm:gap-6">
              <div className="relative w-full sm:w-auto min-w-[260px] sm:min-w-[300px] h-12 bg-[#ffffff70] border-2 border-black rounded-lg flex items-center px-4">
                <TerminalIcon className="w-5 h-5 text-black" />
                <span className="ml-3 font-medium font-['Inter',Helvetica] text-black text-base sm:text-lg truncate">
                  pip install peargent
                </span>
                <CopyIcon className="absolute right-3 w-5 h-5 text-black cursor-pointer" />
              </div>

              <Link
                href="/docs"
                className="w-full sm:w-44 h-12 bg-[#2c2c2c] hover:bg-[#3c3c3c] rounded-lg border border-black flex items-center justify-center gap-2">
                <span className="font-['Inter',Helvetica] font-medium text-white text-lg">
                  Get Started
                </span>
                <ArrowRightIcon className="w-5 h-5 text-white" />
              </Link>
            </div>
          </div>
        </main>

      </div>
    </>
  );
}