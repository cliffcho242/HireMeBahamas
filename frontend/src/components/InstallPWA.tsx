import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowDownTrayIcon, XMarkIcon, DevicePhoneMobileIcon } from '@heroicons/react/24/outline';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const InstallPWA: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showInstallBanner, setShowInstallBanner] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if already installed
    const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone ||
      document.referrer.includes('android-app://');

    // Check if iOS
    const ios = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
    
    // Set state in a microtask to avoid synchronous setState in effect
    Promise.resolve().then(() => {
      setIsStandalone(isStandaloneMode);
      setIsIOS(ios);
    });

    // Check if user has dismissed install banner before
    const installDismissed = localStorage.getItem('installBannerDismissed');
    const dismissedDate = installDismissed ? new Date(installDismissed) : null;
    const daysSinceDismissed = dismissedDate 
      ? (Date.now() - dismissedDate.getTime()) / (1000 * 60 * 60 * 24)
      : 999;

    // Show banner if not installed and not recently dismissed (wait 7 days)
    if (!isStandaloneMode && daysSinceDismissed > 7) {
      // Show banner after 3 seconds
      const timer = setTimeout(() => {
        setShowInstallBanner(true);
      }, 3000);

      return () => clearTimeout(timer);
    }

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      if (daysSinceDismissed > 7) {
        setShowInstallBanner(true);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt && !isIOS) return;

    if (isIOS) {
      // Show iOS install instructions
      setShowInstallBanner(true);
      return;
    }

    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
        setShowInstallBanner(false);
      }
      
      setDeferredPrompt(null);
    }
  };

  const handleDismiss = () => {
    setShowInstallBanner(false);
    localStorage.setItem('installBannerDismissed', new Date().toISOString());
  };

  // Don't show if already installed
  if (isStandalone) return null;

  return (
    <>
      {/* Install Banner */}
      <AnimatePresence>
        {showInstallBanner && (
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:w-96 z-50"
          >
            <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
              <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 p-4">
                <button
                  onClick={handleDismiss}
                  className="absolute top-2 right-2 p-1 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                >
                  <XMarkIcon className="w-5 h-5 text-white" />
                </button>
                
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg">
                    <span className="text-blue-600 font-bold text-xl">HB</span>
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg">Install HireMeBahamas</h3>
                    <p className="text-blue-100 text-sm">Access anytime, anywhere</p>
                  </div>
                </div>
              </div>

              <div className="p-4">
                {isIOS ? (
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600">
                      Install this app on your iPhone:
                    </p>
                    <ol className="text-sm text-gray-700 space-y-2">
                      <li className="flex items-start">
                        <span className="font-semibold mr-2">1.</span>
                        <span>Tap the <strong>Share</strong> button in Safari</span>
                      </li>
                      <li className="flex items-start">
                        <span className="font-semibold mr-2">2.</span>
                        <span>Scroll and tap <strong>"Add to Home Screen"</strong></span>
                      </li>
                      <li className="flex items-start">
                        <span className="font-semibold mr-2">3.</span>
                        <span>Tap <strong>"Add"</strong> to confirm</span>
                      </li>
                    </ol>
                    <button
                      onClick={handleDismiss}
                      className="w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                    >
                      Got it!
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600">
                      Install our app for quick access and offline support!
                    </p>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <DevicePhoneMobileIcon className="w-5 h-5" />
                      <span>Works on all devices</span>
                    </div>
                    <button
                      onClick={handleInstallClick}
                      className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold transition-all shadow-lg flex items-center justify-center space-x-2"
                    >
                      <ArrowDownTrayIcon className="w-5 h-5" />
                      <span>Install App</span>
                    </button>
                    <button
                      onClick={handleDismiss}
                      className="w-full py-2 text-gray-600 hover:text-gray-800 text-sm font-medium transition-colors"
                    >
                      Maybe later
                    </button>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Install Button - Shows when banner is dismissed */}
      {!showInstallBanner && !isStandalone && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          onClick={() => setShowInstallBanner(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-2xl flex items-center justify-center text-white hover:scale-110 transition-transform z-40"
          title="Install App"
        >
          <ArrowDownTrayIcon className="w-6 h-6" />
        </motion.button>
      )}
    </>
  );
};

export default InstallPWA;
