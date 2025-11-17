import Link from 'next/link';
import Image from 'next/image';
import peargentLogo from '../assets/peargent.png';

export default function HomePage() {
  return (
    <>
      {/* Watercolor Background */}
      <div className="watercolor-bg">
        <div className="watercolor-blob watercolor-blob-1"></div>
        <div className="watercolor-blob watercolor-blob-2"></div>
        <div className="watercolor-blob watercolor-blob-3"></div>
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 md:px-12 py-12 md:py-24">
        <div className="min-h-[70vh] flex flex-col items-center justify-center text-center md:text-left md:items-start relative overflow-hidden rounded-3xl p-4 md:p-12">
          {/* Logo */}
          <div className="mb-8 md:mb-12 mx-auto md:mx-0">
            <div className="glass-card rounded-3xl p-8 md:p-10">
              <Image
                src={peargentLogo}
                alt="Peargent"
                priority
                className="w-auto h-auto max-w-[280px] md:max-w-[400px]"
              />
            </div>
          </div>

          {/* Headline */}
          <div className="max-w-4xl mx-auto md:mx-0 mb-8">
            <p className="text-sm md:text-base text-gray-600 mb-3 font-medium tracking-tight">
              the Python agent framework you need
            </p>
            <h1 className="text-4xl md:text-5xl xl:text-6xl font-bold tracking-tight leading-tight">
              Build intelligent agents,{' '}
              <span className="bg-gradient-to-r from-amber-600 via-yellow-500 to-amber-700 bg-clip-text text-transparent">
                your style
              </span>
            </h1>
          </div>

          {/* Description */}
          <p className="text-lg md:text-xl text-gray-700 max-w-2xl mx-auto md:mx-0 mb-8 leading-relaxed">
            A powerful Python framework for building intelligent agents with ease
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 mx-auto md:mx-0">
            <Link href="/docs">
              <button className="px-5 py-3 rounded-full font-medium tracking-tight transition-colors bg-gradient-to-br from-amber-500 to-yellow-600 text-white hover:from-amber-600 hover:to-yellow-700 shadow-lg shadow-amber-200/50 min-w-[160px]">
                Getting Started
              </button>
            </Link>
            <a
              href="https://github.com/quanta-naut/peargent"
              target="_blank"
              rel="noopener noreferrer"
            >
              <button className="px-5 py-3 rounded-full font-medium tracking-tight transition-colors bg-gray-100 text-gray-800 hover:bg-gray-200 border border-gray-200 min-w-[160px]">
                View on GitHub
              </button>
            </a>
          </div>
        </div>

        {/* Feature Description */}
        <div className="mt-20 md:mt-32 max-w-5xl mx-auto">
          <h2 className="text-2xl md:text-4xl font-bold text-gray-800 mb-6 leading-tight">
            A Python framework designed for developers who want to build powerful AI agents without the complexity
          </h2>
          <p className="text-lg md:text-xl text-gray-600 leading-relaxed">
            Peargent provides an intuitive API for creating intelligent agents with custom tools, integrations, and workflows.
            Focus on what matters—building great AI experiences.
          </p>
        </div>
      </div>
    </>
  );
}
