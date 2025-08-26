import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { Link } from 'react-router-dom';

const AdminPortal = () => {
  const { user, logout } = useAuth();
  const { isDark } = useTheme();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className={`min-h-screen ${isDark ? 'bg-[#180c2e]' : 'bg-gray-50'} relative overflow-hidden`}>
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#180c2e]/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-3/4 left-1/2 w-64 h-64 bg-[#0080c7]/5 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10">
        <header className={`${isDark ? 'bg-[#1a0f33]/80' : 'bg-white/80'} backdrop-blur-xl border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <Link to="/" className="flex items-center space-x-3">
                  <img src="/logo.svg" alt="NSWCC Logo" className="h-8 w-auto" />
                  <span className={`text-xl font-black ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Admin Portal
                  </span>
                </Link>
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  isDark ? 'bg-red-900/30 text-red-400 border border-red-800/50' : 'bg-red-100 text-red-700 border border-red-200'
                }`}>
                  ADMINISTRATOR
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  {user?.first_name} {user?.last_name}
                </div>
                <button
                  onClick={handleLogout}
                  className="btn-modern-secondary btn-sm"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center space-y-12">
            <div className="space-y-6">
              <div className="flex justify-center">
                <div className={`relative p-6 rounded-full ${isDark ? 'bg-red-900/20' : 'bg-red-100'}`}>
                  <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[#dc2626] to-[#b91c1c] opacity-20 animate-pulse"></div>
                  <svg 
                    className={`relative w-16 h-16 ${isDark ? 'text-red-400' : 'text-red-600'}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={1.5} 
                      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" 
                    />
                  </svg>
                </div>
              </div>

              <div className="space-y-4">
                <h1 className={`text-4xl md:text-5xl font-black ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Welcome to Admin Control Center, {user?.first_name}!
                </h1>
                <p className={`text-xl ${isDark ? 'text-gray-300' : 'text-gray-600'} max-w-3xl mx-auto leading-relaxed`}>
                  Your comprehensive administrative dashboard is being engineered with enterprise-grade security and functionality.
                </p>
              </div>
            </div>

            <div className="card-modern max-w-4xl mx-auto">
              <div className="space-y-8">
                <div className="space-y-4">
                  <h2 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Advanced Admin Suite Coming Soon
                  </h2>
                  <p className={`text-base ${isDark ? 'text-gray-300' : 'text-gray-600'} leading-relaxed`}>
                    We're developing a powerful administrative platform with comprehensive management capabilities:
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className={`p-5 rounded-xl ${isDark ? 'bg-blue-900/10 border border-blue-800/20' : 'bg-blue-50 border border-blue-200'}`}>
                    <div className="space-y-3">
                      <div className={`p-3 rounded-lg ${isDark ? 'bg-blue-900/30' : 'bg-blue-100'} w-fit`}>
                        <svg className={`w-6 h-6 ${isDark ? 'text-blue-400' : 'text-blue-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className={`font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>User Management</h3>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Manage clients, staff, and permissions</p>
                      </div>
                    </div>
                  </div>

                  <div className={`p-5 rounded-xl ${isDark ? 'bg-green-900/10 border border-green-800/20' : 'bg-green-50 border border-green-200'}`}>
                    <div className="space-y-3">
                      <div className={`p-3 rounded-lg ${isDark ? 'bg-green-900/30' : 'bg-green-100'} w-fit`}>
                        <svg className={`w-6 h-6 ${isDark ? 'text-green-400' : 'text-green-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className={`font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Analytics Dashboard</h3>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Real-time insights and reporting</p>
                      </div>
                    </div>
                  </div>

                  <div className={`p-5 rounded-xl ${isDark ? 'bg-purple-900/10 border border-purple-800/20' : 'bg-purple-50 border border-purple-200'}`}>
                    <div className="space-y-3">
                      <div className={`p-3 rounded-lg ${isDark ? 'bg-purple-900/30' : 'bg-purple-100'} w-fit`}>
                        <svg className={`w-6 h-6 ${isDark ? 'text-purple-400' : 'text-purple-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className={`font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>System Settings</h3>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Configure platform settings</p>
                      </div>
                    </div>
                  </div>

                  <div className={`p-5 rounded-xl ${isDark ? 'bg-orange-900/10 border border-orange-800/20' : 'bg-orange-50 border border-orange-200'}`}>
                    <div className="space-y-3">
                      <div className={`p-3 rounded-lg ${isDark ? 'bg-orange-900/30' : 'bg-orange-100'} w-fit`}>
                        <svg className={`w-6 h-6 ${isDark ? 'text-orange-400' : 'text-orange-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                      </div>
                      <div>
                        <h3 className={`font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Service Management</h3>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Oversee all service operations</p>
                      </div>
                    </div>
                  </div>

                  <div className={`p-5 rounded-xl ${isDark ? 'bg-indigo-900/10 border border-indigo-800/20' : 'bg-indigo-50 border border-indigo-200'}`}>
                    <div className="space-y-3">
                      <div className={`p-3 rounded-lg ${isDark ? 'bg-indigo-900/30' : 'bg-indigo-100'} w-fit`}>
                        <svg className={`w-6 h-6 ${isDark ? 'text-indigo-400' : 'text-indigo-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className={`font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Financial Overview</h3>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Revenue and billing management</p>
                      </div>
                    </div>
                  </div>

                  <div className={`p-5 rounded-xl ${isDark ? 'bg-red-900/10 border border-red-800/20' : 'bg-red-50 border border-red-200'}`}>
                    <div className="space-y-3">
                      <div className={`p-3 rounded-lg ${isDark ? 'bg-red-900/30' : 'bg-red-100'} w-fit`}>
                        <svg className={`w-6 h-6 ${isDark ? 'text-red-400' : 'text-red-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className={`font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Security Center</h3>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Monitor system security</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className={`p-8 rounded-xl ${isDark ? 'bg-gradient-to-r from-red-900/20 to-orange-900/20 border border-red-800/20' : 'bg-gradient-to-r from-red-50 to-orange-50 border border-red-200'}`}>
                  <div className="text-center space-y-4">
                    <div className="flex justify-center">
                      <div className={`p-3 rounded-full ${isDark ? 'bg-red-900/30' : 'bg-red-100'}`}>
                        <svg className={`w-8 h-8 ${isDark ? 'text-red-400' : 'text-red-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                    </div>
                    <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                      Enterprise-Grade Platform in Development
                    </h3>
                    <p className={`text-base ${isDark ? 'text-gray-300' : 'text-gray-600'} max-w-2xl mx-auto`}>
                      Our development team is crafting a sophisticated administrative platform with advanced security, comprehensive reporting, and intuitive management tools. You'll be notified when the full admin suite is ready.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                      <Link to="/services" className="btn-modern-primary btn-md">
                        Review Services
                      </Link>
                      <Link to="/contact" className="btn-modern-secondary btn-md">
                        Contact Development Team
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminPortal;
