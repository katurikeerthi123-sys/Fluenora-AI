import React, { useState } from 'react';
import { X, Lock, Mail, User as UserIcon, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { User } from '../types/academy';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (user: User) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        const data = await api.login({ username_or_email: username || email, password });
        localStorage.setItem('academy_token', data.access_token);
        onAuthSuccess(data.user);
        onClose();
      } else {
        if (!email || !username || !password) {
          setError('Please fill in all required fields.');
          setLoading(false);
          return;
        }
        const data = await api.register({ email, username, password, full_name: fullName });
        localStorage.setItem('academy_token', data.access_token);
        onAuthSuccess(data.user);
        onClose();
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl relative text-slate-100">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 mx-auto flex items-center justify-center text-2xl shadow-lg shadow-purple-500/20 mb-3">
            🎓
          </div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-indigo-300 bg-clip-text text-transparent">
            {isLogin ? 'Welcome Back!' : 'Create Your Academy Account'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {isLogin
              ? 'Sign in to access your grammar courses and track mastery.'
              : 'Join English Learning Academy to master English grammar step by step.'}
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {!isLogin && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Full Name (Optional)</label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Alex Johnson"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              {isLogin ? 'Username or Email' : 'Username'}
            </label>
            <div className="relative">
              <UserIcon className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={isLogin ? 'username or name@domain.com' : 'e.g. alex2026'}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          {!isLogin && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@example.com"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-purple-500/20 disabled:opacity-50 transition mt-2"
          >
            {loading ? 'Processing...' : isLogin ? 'Sign In to Academy' : 'Create Free Account'}
          </button>
        </form>

        <div className="mt-5 text-center text-xs text-slate-400 border-t border-slate-800/80 pt-4">
          {isLogin ? "Don't have an account yet?" : 'Already registered?'}{' '}
          <button
            type="button"
            onClick={() => { setIsLogin(!isLogin); setError(null); }}
            className="text-purple-400 hover:text-purple-300 font-semibold ml-1"
          >
            {isLogin ? 'Sign up here' : 'Sign in here'}
          </button>
        </div>
      </div>
    </div>
  );
};
