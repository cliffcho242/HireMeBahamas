import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  DevicePhoneMobileIcon,
  DeviceTabletIcon,
  ComputerDesktopIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const Download: React.FC = () => {
  const navigate = useNavigate();
  const [isIOS, setIsIOS] = useState(false);
  const [isAndroid, setIsAndroid] = useState(false);
  const [isDesktop, setIsDesktop] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showIOSInstructions, setShowIOSInstructions] = useState(false);

  useEffect(() => {
    // Detect platform
    const userAgent = navigator.userAgent;
    const iOS = /iPad|iPhone|iPod/.test(userAgent) && !(window as any).MSStream;
    const android = /Android/.test(userAgent);
    const desktop = !/Android|iPhone|iPad|iPod/.test(userAgent);
    
    setIsIOS(iOS);
    setIsAndroid(android);
    setIsDesktop(desktop);

    // Check if already installed
    const standalone = window.matchMedia('(display-mode: standalone)').matches ||
      (navigator as any).standalone ||
      document.referrer.includes('android-app://');
    setIsInstalled(standalone);

    // Listen for beforeinstallprompt event (Android/Desktop)
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    console.log('Install button clicked!', { isIOS, isAndroid, isDesktop, deferredPrompt });

    if (isIOS) {
      // Show iOS instructions
      setShowIOSInstructions(true);
      // Scroll to instructions
      setTimeout(() => {
        const instructionsElement = document.getElementById('ios-instructions');
        instructionsElement?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      return;
    }

    if (deferredPrompt) {
      // Android/Desktop install
      try {
        console.log('Triggering install prompt...');
        await deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        
        console.log('Install outcome:', outcome);
        if (outcome === 'accepted') {
          setIsInstalled(true);
        }
        
        setDeferredPrompt(null);
      } catch (error) {
        console.error('Install prompt error:', error);
        // Fallback: navigate to app
        navigate('/');
      }
    } else {
      // If no install prompt available, just go to app
      console.log('No install prompt available, navigating to app...');
      navigate('/');
    }
  };

  const handleOpenApp = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    console.log('Opening app...');
    navigate('/');
  };

  const features = [
    {
      icon: DevicePhoneMobileIcon,
      title: 'Install on Mobile',
      description: 'One tap to install. Works like a native app on iOS and Android.',
    },
    {
      icon: DeviceTabletIcon,
      title: 'Tablet Support',
      description: 'Optimized for iPad, Samsung tablets, and all tablet devices.',
    },
    {
      icon: ComputerDesktopIcon,
      title: 'Desktop Ready',
      description: 'Install on Windows, Mac, and Linux for quick desktop access.',
    },
    {
      icon: GlobeAltIcon,
      title: 'Works Offline',
      description: 'Browse cached content even when you lose connection.',
    },
  ];

  return (
    <div className="min-h-screen min-h-[100dvh] bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <nav className="bg-white/80 backdrop-blur-lg shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold">HB</span>
              </div>
              <span className="text-xl font-bold text-gray-900">HireMeBahamas</span>
            </div>
            <Link
              to="/"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Open App
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <div className="w-24 h-24 sm:w-32 sm:h-32 mx-auto mb-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl shadow-2xl flex items-center justify-center">
            <span className="text-white font-bold text-4xl sm:text-5xl">HB</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            Get HireMeBahamas
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              On Any Device
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Install our Progressive Web App and access HireMeBahamas anytime, anywhere.
            Works like a native app on all devices.
          </p>

          {isInstalled ? (
            <div className="flex flex-col items-center space-y-4">
              <div className="inline-flex items-center space-x-2 px-6 py-3 bg-green-100 text-green-700 rounded-full">
                <CheckCircleIcon className="w-6 h-6" />
                <span className="font-semibold">Already Installed!</span>
              </div>
              <button
                type="button"
                onClick={handleOpenApp}
                className="inline-flex items-center space-x-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transition-all hover:scale-105 active:scale-95 cursor-pointer"
              >
                <span>Open App</span>
              </button>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
              <button
                type="button"
                onClick={handleInstallClick}
                className="inline-flex items-center space-x-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transition-all hover:scale-105 active:scale-95 cursor-pointer touch-manipulation"
              >
                <ArrowDownTrayIcon className="w-6 h-6" />
                <span>
                  {isIOS ? 'View Install Instructions' : 'Install Now'}
                </span>
              </button>
              <button
                type="button"
                onClick={handleOpenApp}
                className="inline-flex items-center space-x-2 px-8 py-4 bg-white text-gray-700 rounded-full font-semibold text-lg shadow-md hover:shadow-lg transition-all cursor-pointer hover:scale-105 active:scale-95 touch-manipulation"
              >
                <span>Use Web Version</span>
              </button>
            </div>
          )}
        </motion.div>

        {/* Installation Instructions */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {/* iOS Instructions - Show when iOS or when user clicks button */}
          {(isIOS || showIOSInstructions) && (
            <motion.div
              id="ios-instructions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-2xl shadow-lg p-8 border-2 border-blue-200"
            >
              <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                <DevicePhoneMobileIcon className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Install on iOS</h3>
              <ol className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-blue-600">1.</span>
                  <span>Tap the <strong>Share</strong> button (
                    <svg className="inline w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"/>
                    </svg>
                  ) in Safari</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-blue-600">2.</span>
                  <span>Scroll down and tap <strong>"Add to Home Screen"</strong></span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-blue-600">3.</span>
                  <span>Tap <strong>"Add"</strong> in the top right</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-blue-600">4.</span>
                  <span>Launch from your home screen!</span>
                </li>
              </ol>
            </motion.div>
          )}

          {/* Android Instructions */}
          {isAndroid && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-2xl shadow-lg p-8"
            >
              <div className="w-16 h-16 bg-green-100 rounded-xl flex items-center justify-center mb-4">
                <DevicePhoneMobileIcon className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Install on Android</h3>
              <ol className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-green-600">1.</span>
                  <span>Tap the <strong>menu</strong> (three dots) in Chrome</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-green-600">2.</span>
                  <span>Tap <strong>"Add to Home screen"</strong> or <strong>"Install app"</strong></span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-green-600">3.</span>
                  <span>Tap <strong>"Install"</strong> to confirm</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-green-600">4.</span>
                  <span>Open from your app drawer!</span>
                </li>
              </ol>
            </motion.div>
          )}

          {/* Desktop Instructions */}
          {isDesktop && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-2xl shadow-lg p-8"
            >
              <div className="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                <ComputerDesktopIcon className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Install on Desktop</h3>
              <ol className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-purple-600">1.</span>
                  <span>Click the <strong>install icon</strong> in the address bar</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-purple-600">2.</span>
                  <span>Click <strong>"Install"</strong> in the popup</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-purple-600">3.</span>
                  <span>The app will open in its own window</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2 text-purple-600">4.</span>
                  <span>Access from your applications!</span>
                </li>
              </ol>
            </motion.div>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              className="bg-white rounded-xl shadow-md p-6 text-center hover:shadow-lg transition-shadow"
            >
              <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <feature.icon className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-8 sm:p-12 text-white"
        >
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-lg sm:text-xl mb-8 text-blue-100">
            Join thousands of professionals connecting in the Bahamas
          </p>
          <button
            type="button"
            onClick={handleInstallClick}
            className="inline-flex items-center space-x-2 px-8 py-4 bg-white text-blue-600 rounded-full font-bold text-lg shadow-lg hover:shadow-xl transition-all hover:scale-105 active:scale-95 cursor-pointer touch-manipulation"
          >
            <ArrowDownTrayIcon className="w-6 h-6" />
            <span>{isInstalled ? 'Open HireMeBahamas' : 'Install HireMeBahamas'}</span>
          </button>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2025 HireMeBahamas. All rights reserved.</p>
            <p className="mt-2 text-sm">Caribbean's Premier Professional Network</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Download;
