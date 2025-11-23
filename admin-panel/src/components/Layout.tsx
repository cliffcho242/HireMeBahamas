import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import {
  HomeIcon,
  UsersIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';

export default function Layout() {
  const location = useLocation();
  const logout = useAuthStore((state) => state.logout);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Users', href: '/users', icon: UsersIcon },
    { name: 'Logs', href: '/logs', icon: DocumentTextIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-primary-800">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <h1 className="text-white text-xl font-bold">HireBahamas Admin</h1>
            </div>
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      isActive
                        ? 'bg-primary-900 text-white'
                        : 'text-primary-100 hover:bg-primary-700'
                    } group flex items-center px-2 py-2 text-sm font-medium rounded-md touch-manipulation min-h-touch`}
                  >
                    <item.icon
                      className="mr-3 flex-shrink-0 h-6 w-6"
                      aria-hidden="true"
                    />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className="flex-shrink-0 flex border-t border-primary-700 p-4">
            <button
              onClick={logout}
              className="flex-shrink-0 w-full group block text-primary-100 hover:bg-primary-700 px-2 py-2 text-sm font-medium rounded-md touch-manipulation min-h-touch"
            >
              <div className="flex items-center">
                <ArrowRightOnRectangleIcon className="inline-block h-6 w-6 mr-3" />
                <span>Logout</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="md:hidden">
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-inset z-50">
          <nav className="flex justify-around">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    isActive ? 'text-primary-600' : 'text-gray-600'
                  } flex flex-col items-center py-2 px-3 touch-manipulation min-h-touch-android`}
                >
                  <item.icon className="h-6 w-6" />
                  <span className="text-xs mt-1">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-64 flex flex-col flex-1">
        <main className="flex-1 pb-16 md:pb-0">
          <div className="py-6 px-4 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
