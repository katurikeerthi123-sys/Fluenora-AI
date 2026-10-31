import React, { useState } from 'react';
import { Lock, Mail, User as UserIcon, AlertCircle, BookOpen, Eye, EyeOff } from 'lucide-react';
import { api } from '../services/api';
import { User } from '../types/academy';

interface LoginPageProps {
  onAuthSuccess: (user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        const data = await api.login({ username_or_email: username || email, password });
        localStorage.setItem('academy_token', data.access_token);
        onAuthSuccess(data.user);
      } else {
        if (!email || !username || !password) {
          setError('Please fill in all required fields.');
          setLoading(false);
          return;
        }
        const data = await api.register({ email, username, password, full_name: fullName });
        localStorage.setItem('academy_token', data.access_token);
        onAuthSuccess(data.user);
      }
    } catch (err: any) {
      let msg = err?.message || 'Authentication failed. Please check your credentials and try again.';
      if (typeof msg !== 'string' || msg === '[object Object]') {
        msg = 'Invalid inputs. Please verify your details and try again.';
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setError(null);
    setUsername('');
    setEmail('');
    setPassword('');
    setFullName('');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center px-4 py-10 relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header brand */}
      <div className="text-center mb-8 z-10">
        <div className="flex items-center justify-center gap-3 mb-3">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-3xl shadow-xl shadow-purple-500/30">
            🎓
          </div>
        </div>
        <h1 className="text-3xl font-extrabold bg-gradient-to-r from-purple-400 via-indigo-300 to-sky-400 bg-clip-text text-transparent tracking-tight">
          Fluenora AI ✨
        </h1>
        <p className="text-sm text-slate-400 mt-1.5 font-medium">
          English Learning Academy · Deep Learning Grammar Platform
        </p>
      </div>

      {/* Auth Card */}
      <div className="bg-slate-900 border border-slate-800/80 rounded-2xl w-full max-w-md p-7 shadow-2xl shadow-slate-950/80 z-10">
        {/* Tabs */}
        <div className="flex gap-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/80 mb-6">
          <button
            type="button"
            onClick={() => { if (!isLogin) switchMode(); }}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition ${
              isLogin
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/25'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { if (isLogin) switchMode(); }}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition ${
              !isLogin
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/25'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Subtitle */}
        <p className="text-xs text-slate-400 text-center mb-5">
          {isLogin
            ? 'Sign in to access your grammar courses, progress tracking, and personalized learning.'
            : 'Create your free account and start mastering English grammar from beginner to advanced.'}
        </p>

        {/* Error Alert */}
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Full Name (register only) */}
          {!isLogin && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Full Name <span className="text-slate-500">(Optional)</span>
              </label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Ravi Kumar"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30 transition"
                />
              </div>
            </div>
          )}

          {/* Username */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              {isLogin ? 'Username or Email' : 'Username'} <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <UserIcon className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={isLogin ? 'username or email@domain.com' : 'e.g. ravi2026'}
                autoComplete={isLogin ? 'username' : 'username'}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30 transition"
              />
            </div>
          </div>

          {/* Email (register only) */}
          {!isLogin && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Email Address <span className="text-red-400">*</span>
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@example.com"
                  autoComplete="email"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30 transition"
                />
              </div>
            </div>
          )}

          {/* Password */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Password <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-10 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30 transition"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300 transition"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {!isLogin && (
              <p className="text-[11px] text-slate-500 mt-1">Minimum 6 characters.</p>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-purple-500/20 disabled:opacity-60 disabled:cursor-not-allowed transition-all mt-1 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : isLogin ? (
              <>
                <BookOpen className="w-4 h-4" />
                <span>Sign In & Start Learning</span>
              </>
            ) : (
              <>
                <span>🎓</span>
                <span>Create Free Account</span>
              </>
            )}
          </button>
        </form>

        {/* Demo credentials hint */}
        {isLogin && (
          <div className="mt-4 p-3 rounded-lg bg-slate-800/50 border border-slate-700/40 text-center">
            <p className="text-[11px] text-slate-400 font-medium">Demo Account</p>
            <p className="text-[11px] text-slate-300 mt-0.5">
              Username: <code className="bg-slate-700 px-1 rounded">demo_student</code>&nbsp;&nbsp;
              Password: <code className="bg-slate-700 px-1 rounded">Academy123!</code>
            </p>
          </div>
        )}

        {/* Features list */}
        <div className="mt-5 border-t border-slate-800/60 pt-4 grid grid-cols-2 gap-2">
          {[
            ['🎓', '17 Grammar Courses'],
            ['✨', 'Bi-LSTM AI Analyzer'],
            ['📚', 'Interactive Lessons'],
            ['📊', 'Progress Tracking'],
          ].map(([icon, label]) => (
            <div key={label} className="flex items-center gap-1.5 text-[11px] text-slate-500">
              <span>{icon}</span>
              <span>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <p className="mt-6 text-[11px] text-slate-600 text-center z-10">
        Fluenora AI ✨ · Intelligent Grammar Assistant
      </p>
    </div>
  );
};
