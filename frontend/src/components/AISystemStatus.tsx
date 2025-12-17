import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAIMonitoring } from '../contexts/AIMonitoringContext';
import Activity from 'lucide-react/dist/esm/icons/activity';
import Wifi from 'lucide-react/dist/esm/icons/wifi';
import WifiOff from 'lucide-react/dist/esm/icons/wifi-off';
import Server from 'lucide-react/dist/esm/icons/server';
import ServerOff from 'lucide-react/dist/esm/icons/server-off';
import Cpu from 'lucide-react/dist/esm/icons/cpu';
import AlertTriangle from 'lucide-react/dist/esm/icons/alert-triangle';
import CheckCircle from 'lucide-react/dist/esm/icons/check-circle';
import XCircle from 'lucide-react/dist/esm/icons/x-circle';
import RefreshCw from 'lucide-react/dist/esm/icons/refresh-cw';
import Zap from 'lucide-react/dist/esm/icons/zap';

const AISystemStatus = () => {
  const { health, performHealthCheck, attemptRecovery, getSystemStatus } = useAIMonitoring();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const systemStatus = getSystemStatus();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      case 'offline': return 'text-gray-600 bg-gray-100';
      default: return 'text-blue-600 bg-blue-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4" />;
      case 'degraded': return <AlertTriangle className="w-4 h-4" />;
      case 'critical': return <XCircle className="w-4 h-4" />;
      case 'offline': return <WifiOff className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await performHealthCheck();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const formatLastCheck = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className="mb-4 bg-white rounded-xl shadow-2xl border border-gray-200 p-6 w-80"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-blue-600" />
                🤖 AI System Monitor
              </h3>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* System Status */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Status</span>
                <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(systemStatus)}`}>
                  {getStatusIcon(systemStatus)}
                  <span className="ml-1 capitalize">{systemStatus}</span>
                </div>
              </div>
              <div className="text-xs text-gray-500">
                Last checked: {formatLastCheck(health.lastCheck)}
              </div>
            </div>

            {/* Health Checks */}
            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Activity className={`w-4 h-4 mr-2 ${health.frontend ? 'text-green-600' : 'text-red-600'}`} />
                  <span className="text-sm text-gray-700">Frontend</span>
                </div>
                <div className={`w-2 h-2 rounded-full ${health.frontend ? 'bg-green-500' : 'bg-red-500'}`}></div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {health.backend ? <Server className="w-4 h-4 mr-2 text-green-600" /> : <ServerOff className="w-4 h-4 mr-2 text-red-600" />}
                  <span className="text-sm text-gray-700">Backend</span>
                </div>
                <div className={`w-2 h-2 rounded-full ${health.backend ? 'bg-green-500' : 'bg-red-500'}`}></div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {health.network ? <Wifi className="w-4 h-4 mr-2 text-green-600" /> : <WifiOff className="w-4 h-4 mr-2 text-red-600" />}
                  <span className="text-sm text-gray-700">Network</span>
                </div>
                <div className={`w-2 h-2 rounded-full ${health.network ? 'bg-green-500' : 'bg-red-500'}`}></div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Cpu className={`w-4 h-4 mr-2 ${health.memory ? 'text-green-600' : 'text-red-600'}`} />
                  <span className="text-sm text-gray-700">Memory</span>
                </div>
                <div className={`w-2 h-2 rounded-full ${health.memory ? 'bg-green-500' : 'bg-red-500'}`}></div>
              </div>
            </div>

            {/* Errors */}
            {health.errors.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Issues</h4>
                <div className="space-y-1 max-h-20 overflow-y-auto">
                  {health.errors.slice(-3).map((error, index) => (
                    <div key={index} className="text-xs text-red-600 bg-red-50 p-2 rounded">
                      {error}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recovery Attempts */}
            {health.recoveryAttempts > 0 && (
              <div className="mb-4 p-2 bg-blue-50 rounded-lg">
                <div className="text-xs text-blue-700">
                  🤖 AI Recovery attempts: {health.recoveryAttempts}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors flex items-center justify-center"
              >
                <RefreshCw className={`w-4 h-4 mr-1 ${isRefreshing ? 'animate-spin' : ''}`} />
                Check
              </button>
              <button
                onClick={attemptRecovery}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
              >
                🤖 Fix
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status Indicator Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-14 h-14 rounded-full shadow-lg border-2 border-white flex items-center justify-center transition-colors ${
          systemStatus === 'healthy' ? 'bg-green-500 hover:bg-green-600' :
          systemStatus === 'degraded' ? 'bg-yellow-500 hover:bg-yellow-600' :
          systemStatus === 'critical' ? 'bg-red-500 hover:bg-red-600' :
          'bg-gray-500 hover:bg-gray-600'
        }`}
      >
        {systemStatus === 'healthy' ? (
          <CheckCircle className="w-6 h-6 text-white" />
        ) : systemStatus === 'degraded' ? (
          <AlertTriangle className="w-6 h-6 text-white" />
        ) : systemStatus === 'critical' ? (
          <XCircle className="w-6 h-6 text-white" />
        ) : (
          <WifiOff className="w-6 h-6 text-white" />
        )}
      </motion.button>
    </div>
  );
};

export default AISystemStatus;