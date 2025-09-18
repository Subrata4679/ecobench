import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import {
  HomeIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  ChartBarIcon,
  ScaleIcon,
  LightBulbIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Organizations', href: '/organizations', icon: BuildingOfficeIcon },
  { name: 'Reports', href: '/reports', icon: DocumentTextIcon },
  { name: 'Ingestion', href: '/ingestion', icon: CloudArrowUpIcon },
  { name: 'KPIs', href: '/kpis', icon: ChartBarIcon },
  { name: 'Benchmarks', href: '/benchmarks', icon: ScaleIcon },
  { name: 'Recommendations', href: '/recommendations', icon: LightBulbIcon },
  { name: 'Search', href: '/search', icon: MagnifyingGlassIcon },
];

const Sidebar = () => {
  const { sidebarOpen, setSidebarOpen } = useApp();
  const location = useLocation();

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-white border-r border-gray-200">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <div className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <ScaleIcon className="w-5 h-5 text-white" />
                </div>
                <div className="ml-3">
                  <h1 className="text-xl font-bold text-gray-900">EcoBench</h1>
                  <p className="text-xs text-gray-500">ESG Benchmarking</p>
                </div>
              </div>
            </div>
            <nav className="mt-8 flex-1 px-2 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href || 
                  (item.href === '/dashboard' && location.pathname === '/');
                
                return (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={
                      isActive
                        ? 'sidebar-nav-item-active'
                        : 'sidebar-nav-item-inactive'
                    }
                  >
                    <item.icon className="mr-3 flex-shrink-0 h-5 w-5" />
                    {item.name}
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Mobile sidebar */}
      <div className={`fixed inset-0 flex z-40 md:hidden ${sidebarOpen ? '' : 'pointer-events-none'}`}>
        <div
          className={`fixed inset-0 bg-gray-600 bg-opacity-75 transition-opacity ease-linear duration-300 ${
            sidebarOpen ? 'opacity-100' : 'opacity-0'
          }`}
          onClick={() => setSidebarOpen(false)}
        />

        <div
          className={`relative flex-1 flex flex-col max-w-xs w-full bg-white transform ease-in-out duration-300 ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              type="button"
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <span className="sr-only">Close sidebar</span>
              <XMarkIcon className="h-6 w-6 text-white" />
            </button>
          </div>

          <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
            <div className="flex-shrink-0 flex items-center px-4">
              <div className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <ScaleIcon className="w-5 h-5 text-white" />
                </div>
                <div className="ml-3">
                  <h1 className="text-xl font-bold text-gray-900">EcoBench</h1>
                  <p className="text-xs text-gray-500">ESG Benchmarking</p>
                </div>
              </div>
            </div>
            <nav className="mt-8 px-2 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href || 
                  (item.href === '/dashboard' && location.pathname === '/');
                
                return (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={
                      isActive
                        ? 'sidebar-nav-item-active'
                        : 'sidebar-nav-item-inactive'
                    }
                    onClick={() => setSidebarOpen(false)}
                  >
                    <item.icon className="mr-3 flex-shrink-0 h-5 w-5" />
                    {item.name}
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
