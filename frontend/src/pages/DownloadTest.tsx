import { useNavigate } from 'react-router-dom';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

const DownloadTest = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    console.log('🎯 BUTTON CLICKED!');
    alert('Button is working!');
  };

  const handleNavigate = () => {
    console.log('🚀 Navigating to home...');
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-4xl font-bold text-center mb-8">
          Button Click Test
        </h1>
        
        <div className="space-y-4">
          {/* Test 1: Simple Button */}
          <button
            type="button"
            onClick={handleClick}
            style={{ cursor: 'pointer', touchAction: 'manipulation' }}
            className="w-full px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold text-lg hover:bg-blue-700 active:bg-blue-800"
          >
            <span>Test 1: Click Me (Alert)</span>
          </button>

          {/* Test 2: Navigation Button */}
          <button
            type="button"
            onClick={handleNavigate}
            style={{ cursor: 'pointer', touchAction: 'manipulation' }}
            className="w-full px-8 py-4 bg-green-600 text-white rounded-lg font-semibold text-lg hover:bg-green-700 active:bg-green-800"
          >
            <span>Test 2: Navigate Home</span>
          </button>

          {/* Test 3: Install Button Simulation */}
          <button
            type="button"
            onClick={() => {
              console.log('Install button clicked');
              alert('This would trigger PWA install');
              navigate('/');
            }}
            style={{ cursor: 'pointer', touchAction: 'manipulation' }}
            className="w-full px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-bold text-lg hover:shadow-xl"
          >
            <ArrowDownTrayIcon className="inline w-6 h-6 mr-2" />
            <span>Test 3: Simulate Install</span>
          </button>
        </div>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">
            ✓ Open browser console (F12) to see click events<br/>
            ✓ Each button should respond immediately<br/>
            ✓ Check for console.log messages
          </p>
        </div>
      </div>
    </div>
  );
};

export default DownloadTest;
