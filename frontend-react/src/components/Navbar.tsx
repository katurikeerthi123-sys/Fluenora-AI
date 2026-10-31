import React from 'react';
import { BookOpen, User as UserIcon, LogOut } from 'lucide-react';
import { User } from '../types/academy';

interface NavbarProps {
  currentTab: 'dashboard' | 'courses';
  onSelectTab: (tab: 'dashboard' | 'courses') => void;
  user: User | null;
  onOpenAuth: () => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  user,
  onOpenAuth,
  onLogout,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand */}
        <div
          onClick={() => onSelectTab('dashboard')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-xl shadow-lg shadow-purple-500/25 group-hover:scale-105 transition-transform">
            🎓
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 via-indigo-300 to-sky-400 bg-clip-text text-transparent">
                English Learning Academy
              </h1>
            </div>
            <p className="text-[11px] text-slate-400">Complete English Grammar Learning Platform</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/80">
          <button
            onClick={() => onSelectTab('dashboard')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
              currentTab === 'dashboard'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => onSelectTab('courses')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
              currentTab === 'courses'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>📚</span>
            <span>All Courses</span>
          </button>

          <a
            href="/"
            className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5"
            title="Return to Fluenora AI"
          >
            <span>✨</span>
            <span>Fluenora AI</span>
          </a>
        </nav>

        {/* User Auth Info */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-200">
                <UserIcon className="w-3.5 h-3.5 text-purple-400" />
                <span className="font-medium">{user.full_name || user.username}</span>
              </div>
              <button
                onClick={onLogout}
                title="Sign Out"
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700/60 transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-purple-500/20 transition"
            >
              Sign In / Register
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
