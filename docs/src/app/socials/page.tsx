"use client";

import Link from 'next/link';
import Image from 'next/image';
import siteBg from '../assets/water-color-bg.png';
import icon from '../assets/icon.png';
import greenCard from '../assets/green.png';
import blackCard from '../assets/black.png';
import blueCard from '../assets/blue.png';
import purpleCard from '../assets/purple.png';
import yellowCard from '../assets/yellow.png';
import pinkCard from '../assets/pink.png';
import orangeCard from '../assets/orange.png';
import { ArrowLeftIcon, Github, Twitter, BookOpen, MessageCircle, Package, Heart, Coffee, Home } from 'lucide-react';
import { cn } from '@/lib/cn';
import { useState, useEffect } from 'react';

export default function SocialsPage() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const links = [
        {
            name: 'Documentation',
            url: '/docs',
            icon: BookOpen,
            description: 'Read the official docs',
            bgImage: greenCard,
            textColor: 'text-black'
        },
        {
            name: 'GitHub',
            url: 'https://github.com/Quanta-Naut/peargent',
            icon: Github,
            description: 'Star us on GitHub',
            bgImage: blackCard,
            textColor: 'text-black'
        },
        {
            name: 'PyPI',
            url: 'https://pypi.org/project/peargent/',
            icon: Package,
            description: 'Install from Python Package Index',
            bgImage: yellowCard,
            textColor: 'text-black',
        },
        {
            name: 'Sponsor Me',
            url: 'https://github.com/sponsors/Quanta-Naut',
            icon: Heart,
            description: 'Sponsor me on GitHub',
            bgImage: pinkCard,
            textColor: 'text-black',
        },
        {
            name: 'Buy Me a Coffee',
            url: 'https://www.buymeacoffee.com/quanta.naut',
            icon: Coffee,
            description: 'Buy me a coffee',
            bgImage: orangeCard,
            textColor: 'text-black',
        },
        {
            name: 'X (formerly Twitter)',
            url: 'https://twitter.com/peargent',
            icon: Twitter,
            description: 'Follow for updates',
            bgImage: blueCard,
            textColor: 'text-black',
            comingSoon: true
        },
        {
            name: 'Discord',
            url: 'https://discord.gg/peargent',
            icon: MessageCircle,
            description: 'Join the community',
            bgImage: purpleCard,
            textColor: 'text-black',
            comingSoon: true
        }
    ];

    return (
        <div className="relative min-h-screen w-full text-black font-sans">
            {/* Background with Overlay */}
            <div className="fixed inset-0 w-full h-full -z-10">
                <Image
                    src={siteBg}
                    alt="Site Background"
                    fill
                    className="object-cover opacity-100"
                    priority
                />
                {/* Gradient overlay removed as per request */}
            </div>

            <main className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-12 sm:px-6 lg:px-8">

                {/* Back Button */}
                <div className={cn(
                    "absolute top-6 left-6 transition-all duration-700 ease-out",
                    mounted ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-4"
                )}>
                    <Link
                        href="/"
                        className="group flex items-center gap-2 px-4 py-2 rounded-full bg-white/50 hover:bg-white/80 border border-black/5 hover:border-black/10 backdrop-blur-md transition-all duration-300 shadow-sm hover:shadow-md"
                    >
                        <Home className="w-4 h-4 text-gray-600 group-hover:text-black transition-colors" />
                        {/* <span className="text-sm font-medium text-gray-600 group-hover:text-black transition-colors">Back</span> */}
                    </Link>
                </div>

                <div className="w-full max-w-md mx-auto">
                    {/* Profile Section */}
                    <div className={cn(
                        "flex flex-col items-center text-center mb-10 transition-all duration-700 ease-out",
                        mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
                    )}>
                        <div className="relative w-24 h-24 mb-6 group">
                            <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-[#7AA846] to-[#9BCF5E] opacity-20 group-hover:opacity-30 blur-xl transition-opacity duration-500" />
                            <div className="relative w-full h-full rounded-xl overflow-hidden border-3 border-black shadow-lg ring-1 ring-black/5">
                                <Image
                                    src={icon}
                                    alt="Peargent Logo"
                                    fill
                                    className="object-cover"
                                    priority
                                />
                            </div>
                        </div>

                        <span className="font-semibold text-gray-900" style={{ fontFamily: 'var(--font-instrument-serif), serif', fontSize: '2.1rem' }}>
                            peargent.
                        </span>
                        <p className="text-gray-600 text-lg max-w-xs leading-relaxed">
                            Building powerful AI agents, <br /> made simple.
                        </p>
                    </div>

                    {/* Links Section */}
                    <div className="space-y-4">
                        {links.map((link, index) => {
                            const isComingSoon = link.comingSoon;
                            const Wrapper = isComingSoon ? 'div' : Link;
                            // @ts-ignore - Dynamic component props
                            const props = isComingSoon ? {} : {
                                href: link.url,
                                target: link.url.startsWith('http') ? "_blank" : undefined,
                                rel: link.url.startsWith('http') ? "noopener noreferrer" : undefined
                            };

                            return (
                                <Wrapper
                                    key={link.name}
                                    {...props}
                                    className={cn(
                                        "group relative flex items-center p-4 rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 ease-out transform overflow-hidden border-2 border-black",
                                        mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8",
                                        isComingSoon ? "cursor-default" : "cursor-pointer"
                                    )}
                                    style={{ transitionDelay: `${index * 100 + 200}ms` }}
                                >
                                    {/* Background Image */}
                                    <div className="absolute inset-0 z-0">
                                        <Image
                                            src={link.bgImage}
                                            alt={`${link.name} background`}
                                            fill
                                            className="object-cover transition-transform duration-500 group-hover:scale-105"
                                        />
                                        {/* Subtle overlay for text readability if needed */}
                                        <div className="absolute inset-0 bg-black/5 group-hover:bg-black/0 transition-colors duration-300" />
                                    </div>

                                    {/* Content */}
                                    <div className="relative z-10 flex items-center w-full">
                                        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white/20 shadow-sm ring-1 ring-white/20 group-hover:scale-110 transition-transform duration-300 backdrop-blur-sm border border-black">
                                            <link.icon className={cn("w-5 h-5 transition-opacity", link.textColor)} />
                                        </div>
                                        <div className="ml-4 flex-1">
                                            <h3 className={cn("text-base font-semibold transition-colors", link.textColor)}>{link.name}</h3>
                                            <p className={cn("text-xs opacity-90 transition-colors", link.textColor)}>{link.description}</p>
                                        </div>
                                        {!isComingSoon && (
                                            <div className={cn("opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all duration-300", link.textColor)}>
                                                <ArrowLeftIcon className="w-4 h-4 rotate-180" />
                                            </div>
                                        )}
                                    </div>

                                    {/* Coming Soon Badge */}
                                    {isComingSoon && (
                                        <div className="absolute top-0 right-0 px-3 pb-1 bg-black/60 backdrop-blur-md rounded-bl-xl z-20">
                                            <span className="text-[10px] font-bold text-white uppercase tracking-wider">Coming Soon</span>
                                        </div>
                                    )}
                                </Wrapper>
                            );
                        })}
                    </div>

                    {/* Footer */}
                    <div className={cn(
                        "mt-12 text-center transition-all duration-1000 ease-out delay-500",
                        mounted ? "opacity-100" : "opacity-0"
                    )}>
                    </div>
                </div>
            </main>
        </div>
    );
}
