import { useState, FormEvent } from 'react';

export default function Settings() {
  const [settings, setSettings] = useState({
    siteName: 'HireBahamas',
    adminEmail: 'admin@hirebahamas.com',
    maintenanceMode: false,
    allowRegistration: true,
  });

  const [saved, setSaved] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    // Simulate saving settings
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div>
      <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6">Settings</h1>
      <div className="bg-white shadow sm:rounded-lg">
        <form onSubmit={handleSubmit} className="space-y-6 p-6">
          {saved && (
            <div className="rounded-md bg-green-50 p-4">
              <p className="text-sm text-green-800">Settings saved successfully!</p>
            </div>
          )}
          
          <div>
            <label htmlFor="siteName" className="block text-sm font-medium text-gray-700">
              Site Name
            </label>
            <input
              type="text"
              id="siteName"
              value={settings.siteName}
              onChange={(e) => setSettings({ ...settings, siteName: e.target.value })}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm min-h-touch"
            />
          </div>

          <div>
            <label htmlFor="adminEmail" className="block text-sm font-medium text-gray-700">
              Admin Email
            </label>
            <input
              type="email"
              id="adminEmail"
              value={settings.adminEmail}
              onChange={(e) => setSettings({ ...settings, adminEmail: e.target.value })}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm min-h-touch"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="maintenanceMode"
              checked={settings.maintenanceMode}
              onChange={(e) => setSettings({ ...settings, maintenanceMode: e.target.checked })}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded min-h-touch min-w-touch"
            />
            <label htmlFor="maintenanceMode" className="ml-2 block text-sm text-gray-900">
              Maintenance Mode
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="allowRegistration"
              checked={settings.allowRegistration}
              onChange={(e) => setSettings({ ...settings, allowRegistration: e.target.checked })}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded min-h-touch min-w-touch"
            />
            <label htmlFor="allowRegistration" className="ml-2 block text-sm text-gray-900">
              Allow User Registration
            </label>
          </div>

          <div className="pt-5">
            <button
              type="submit"
              className="w-full sm:w-auto flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 min-h-touch touch-manipulation"
            >
              Save Settings
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
