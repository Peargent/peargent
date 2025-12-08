"use client";

import Link from 'next/link';
import Image from 'next/image';
import siteBg from '../assets/site-bg.png';
import blackBg from '../assets/black.png';
import greenBg from '../assets/green.png';
import { useState, useEffect } from 'react';
import { ArrowRightIcon, CheckIcon, CopyIcon, TerminalIcon, Github, Star } from 'lucide-react';
import { cn } from '@/lib/cn';

export default function HomePage() {
  const [copied, setCopied] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [version, setVersion] = useState('v0.1 Public Beta');
  const [stars, setStars] = useState<number | null>(null);

  useEffect(() => {
    setMounted(true);
    // Prevent scrolling on this page to keep the hero locked
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';

    // Fetch version from API
    fetch('/api/version')
      .then(res => res.json())
      .then(data => setVersion(data.version))
      .catch(() => setVersion('v0.1 Public Beta')); // Fallback

    // Fetch GitHub stars
    fetch('https://api.github.com/repos/quanta-naut/peargent')
      .then(res => res.json())
      .then(data => setStars(data.stargazers_count))
      .catch((e) => console.error('Error fetching stars:', e));

    return () => {
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
    <div className="fixed inset-0 w-full h-full overflow-hidden bg-white text-black">
      {/* Background with Overlay */}
      <div className="absolute inset-0 w-full h-full -z-10">
        <Image
          src={siteBg}
          alt="Site Background"
          fill
          className="object-cover opacity-100"
          priority
        />
        {/* Gradient overlay: White on left for text, transparent on right for pear */}
        <div className="absolute inset-0 lg:bg-gradient-to-r from-white/100 via-white/5 to-transparent backdrop-blur-[0px]" />
      </div>

      <main className="flex flex-col justify-center items-center md:items-start min-h-screen px-4 sm:px-8 md:px-16 lg:px-24 relative z-10">
        <div className={cn(
          "w-full max-w-4xl flex flex-col items-center md:items-start text-center md:text-left transition-all duration-1000 ease-out transform",
          mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
        )}>

          {/* Badge / Pill */}
          <div className="mb-8 inline-flex items-center px-4 py-2 rounded-full border border-[#7AA846]/50 bg-[#7AA846]/20 backdrop-blur-md shadow-lg">
            <span className="text-xs font-semibold text-[#5a7c33] uppercase tracking-wider">{version}</span>
          </div>

          {/* Hero Heading */}
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-black mb-6">
            Building powerful AI agents, <br className="hidden sm:block" />
            <span className="text-[#7AA846]">
              made simple.
            </span>
          </h1>

          {/* Subheadline */}
          <p className="max-w-2xl text-lg sm:text-xl text-gray-700 mb-10 leading-relaxed font-medium">
            A refined, simple approach to building intelligent agents in Python,
            designed for real-world use.
          </p>

          {/* CTA Section */}
          <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6 w-full justify-center md:justify-start">

            {/* pip install command */}
            <div
              onClick={handleCopy}
              className="group relative w-full sm:w-auto min-w-[280px] h-12 bg-white/60 border border-black/10 rounded-lg flex items-center px-4 cursor-pointer hover:bg-white/80 transition-colors backdrop-blur-md shadow-sm"
            >
              <TerminalIcon className="w-4 h-4 text-gray-600 mr-3" />
              <span className="font-mono text-sm text-black mr-auto">
                pip install peargent
              </span>
              <div className="relative">
                <div className={cn(
                  "absolute inset-0 flex items-center justify-center transition-all duration-200",
                  copied ? "opacity-100 scale-100" : "opacity-0 scale-50"
                )}>
                  <CheckIcon className="w-4 h-4 text-green-600" />
                </div>
                <div className={cn(
                  "transition-all duration-200",
                  copied ? "opacity-0 scale-50" : "opacity-100 scale-100"
                )}>
                  <CopyIcon className="w-4 h-4 text-gray-500 group-hover:text-black transition-colors" />
                </div>
              </div>
            </div>

            {/* Get Started Button */}
            <Link
              href="/docs"
              className="w-full sm:w-auto px-8 h-12 bg-[#7AA846] hover:bg-[#6a923d] text-white rounded-lg flex items-center justify-center gap-2 font-medium transition-all hover:scale-105 shadow-lg shadow-[#7AA846]/20"
            >
              <span>Get Started</span>
              <ArrowRightIcon className="w-4 h-4" />
            </Link>

            {/* GitHub Star Button */}
            <Link
              href="https://github.com/quanta-naut/peargent"
              target="_blank"
              rel="noopener noreferrer"
              className="group/github relative w-full sm:w-auto px-6 h-12 rounded-lg flex items-center justify-center gap-3 font-medium transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-black/5 hover:shadow-black/10 overflow-hidden ring-1 ring-black/5"
            >
              <Image
                src={blackBg}
                alt=""
                fill
                className="object-cover absolute inset-0 opacity-[0.50] group-hover/github:opacity-70 transition-opacity duration-300"
              />
              <div className="relative z-10 flex items-center gap-3 text-black">
                <div className="flex items-center gap-2 group-hover/github:gap-2.5 transition-all">
                  <Github className="w-5 h-5 transition-transform group-hover/github:rotate-12" />
                  <span className="font-semibold tracking-tight">Star on GitHub</span>
                </div>

                {stars !== null && (
                  <>
                    <div className="w-px h-4 bg-black/20 mx-2" />
                    <Star className="w-4 h-4 transition-transform" />
                    <span className="font-medium opacity-80 group-hover/github:opacity-100 transition-opacity -ml-1.5">
                      {stars.toLocaleString()}
                    </span>
                  </>
                )}
              </div>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}