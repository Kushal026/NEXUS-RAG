"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  Lock,
  Mail,
  User,
  ArrowRight,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  X,
  KeyRound
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: "signin" | "signup" | "forgot";
  onSuccess?: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialMode = "signin",
  onSuccess,
}) => {
  const { login, register, continueWithGoogle, forgotPassword, resetPassword } = useAuth();
  const [mode, setMode] = useState<"signin" | "signup" | "forgot" | "reset">(initialMode);
  
  // Form fields
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    setLoading(true);

    try {
      if (mode === "signin") {
        const identifier = email || username;
        if (!identifier.trim() || !password) {
          throw new Error("Please enter your email/username and password.");
        }
        await login(identifier.trim(), password);
        if (onSuccess) onSuccess();
        onClose();
      } else if (mode === "signup") {
        if (!username.trim() || !email.trim() || !password) {
          throw new Error("Please fill in all required fields.");
        }
        if (password.length < 6) {
          throw new Error("Password must be at least 6 characters.");
        }
        if (password !== confirmPassword) {
          throw new Error("Passwords do not match.");
        }
        await register(username.trim(), email.trim(), password, name.trim() || undefined);
        if (onSuccess) onSuccess();
        onClose();
      } else if (mode === "forgot") {
        if (!email.trim()) {
          throw new Error("Please enter your registered email address.");
        }
        const res = await forgotPassword(email.trim());
        setSuccessMsg(res.message || "Password recovery token sent.");
        if (res.reset_token) {
          setResetToken(res.reset_token);
          setMode("reset");
        }
      } else if (mode === "reset") {
        if (!resetToken.trim() || !newPassword) {
          throw new Error("Please provide your reset token and new password.");
        }
        if (newPassword.length < 6) {
          throw new Error("New password must be at least 6 characters.");
        }
        const res = await resetPassword(resetToken.trim(), newPassword);
        setSuccessMsg(res.message);
        setTimeout(() => setMode("signin"), 1500);
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    setError(null);
    setLoading(true);
    try {
      await continueWithGoogle();
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Google sign in failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="relative w-full max-w-md bg-white border border-slate-200 rounded-3xl shadow-2xl p-6 sm:p-8 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Subtle Background Radial Glow */}
        <div className="absolute -right-20 -top-20 w-56 h-56 bg-indigo-100/50 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-20 -bottom-20 w-56 h-56 bg-cyan-100/50 rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-all"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Brand Header */}
        <div className="text-center space-y-2 mb-6">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-md shadow-indigo-500/20 mx-auto">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            {mode === "signin" && "Welcome back to NEXUS"}
            {mode === "signup" && "Create your NEXUS account"}
            {mode === "forgot" && "Recover your password"}
            {mode === "reset" && "Set new password"}
          </h2>
          <p className="text-xs text-slate-500">
            {mode === "signin" && "Sign in to access your private evidence workspace"}
            {mode === "signup" && "Get started with evidence-backed AI research"}
            {mode === "forgot" && "Enter your email to receive a recovery token"}
            {mode === "reset" && "Enter the reset token and your new password"}
          </p>
        </div>

        {/* Mode Switcher Tabs (Sign In / Sign Up) */}
        {(mode === "signin" || mode === "signup") && (
          <div className="grid grid-cols-2 p-1 rounded-xl bg-slate-100 border border-slate-200 mb-5">
            <button
              type="button"
              onClick={() => {
                setMode("signin");
                setError(null);
              }}
              className={`py-2 text-xs font-semibold rounded-lg transition-all ${
                mode === "signin"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("signup");
                setError(null);
              }}
              className={`py-2 text-xs font-semibold rounded-lg transition-all ${
                mode === "signup"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              Sign Up
            </button>
          </div>
        )}

        {/* Error / Success Alerts */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
            <span>{error}</span>
          </div>
        )}
        {successMsg && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Continue with Google */}
        {(mode === "signin" || mode === "signup") && (
          <div className="space-y-4 mb-4">
            <button
              type="button"
              onClick={handleGoogleAuth}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold transition-all flex items-center justify-center gap-2.5 shadow-xs"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#EA4335"
                  d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.9C6.2 7.4 8.9 5 12 5z"
                />
                <path
                  fill="#4285F4"
                  d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.3 14.7c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.6 7.2C.6 9.2 0 10.5 0 12s.6 2.8 1.6 4.8l3.7-2.1z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.1 0-5.8-2.4-6.7-5.3L1.6 16C3.5 19.8 7.4 23 12 23z"
                />
              </svg>
              <span>Continue with Google</span>
            </button>

            <div className="relative flex items-center justify-center">
              <div className="w-full border-t border-slate-200" />
              <span className="absolute bg-white px-3 text-[10px] uppercase font-mono text-slate-400">
                or with email
              </span>
            </div>
          </div>
        )}

        {/* Main Authentication Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {mode === "signup" && (
            <div>
              <label className="block text-[11px] font-medium text-slate-700 mb-1">
                Full Name (Optional)
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Dr. Jane Doe"
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition-all font-sans"
                />
              </div>
            </div>
          )}

          {mode === "signup" && (
            <div>
              <label className="block text-[11px] font-medium text-slate-700 mb-1">
                Username *
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="janedoe"
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition-all font-sans"
                />
              </div>
            </div>
          )}

          {(mode === "signin" || mode === "signup" || mode === "forgot") && (
            <div>
              <label className="block text-[11px] font-medium text-slate-700 mb-1">
                {mode === "signin" ? "Email or Username" : "Email Address *"}
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type={mode === "signin" ? "text" : "email"}
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={mode === "signin" ? "admin or user@domain.com" : "user@domain.com"}
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition-all font-sans"
                />
              </div>
            </div>
          )}

          {(mode === "signin" || mode === "signup") && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-medium text-slate-700">Password</label>
                {mode === "signin" && (
                  <button
                    type="button"
                    onClick={() => {
                      setMode("forgot");
                      setError(null);
                    }}
                    className="text-[11px] text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition-all font-sans"
                />
              </div>
            </div>
          )}

          {mode === "signup" && (
            <div>
              <label className="block text-[11px] font-medium text-slate-700 mb-1">
                Confirm Password *
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition-all font-sans"
                />
              </div>
            </div>
          )}

          {mode === "reset" && (
            <>
              <div>
                <label className="block text-[11px] font-medium text-slate-700 mb-1">
                  Reset Token
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={resetToken}
                    onChange={(e) => setResetToken(e.target.value)}
                    placeholder="Enter reset token"
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 font-mono placeholder-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-700 mb-1">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Minimum 6 characters"
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-600 focus:bg-white transition-all font-sans"
                  />
                </div>
              </div>
            </>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 mt-4"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <span>
                  {mode === "signin" && "Sign In to NEXUS"}
                  {mode === "signup" && "Create Account"}
                  {mode === "forgot" && "Send Recovery Link"}
                  {mode === "reset" && "Update Password"}
                </span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </form>

        {/* Switch back link for forgot/reset mode */}
        {(mode === "forgot" || mode === "reset") && (
          <div className="text-center mt-4">
            <button
              type="button"
              onClick={() => {
                setMode("signin");
                setError(null);
                setSuccessMsg(null);
              }}
              className="text-xs text-slate-600 hover:text-slate-900 transition-colors"
            >
              ← Back to Sign In
            </button>
          </div>
        )}

        {/* Demo Credentials Helper Pill */}
        {mode === "signin" && (
          <div className="mt-5 p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600 text-center">
            <span>Default Test Account: </span>
            <strong className="text-indigo-600 font-mono">admin</strong> /{" "}
            <strong className="text-indigo-600 font-mono">AdminSecure2026!</strong>
          </div>
        )}
      </div>
    </div>
  );
};
