import React from 'react';
import HireMeTab from '../components/HireMeTab';

const HireMe: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            HireMe Board
          </h1>
          <p className="text-lg text-gray-600">
            Discover talented professionals available for hire
          </p>
        </div>

        <HireMeTab />
      </div>
    </div>
  );
};

export default HireMe;