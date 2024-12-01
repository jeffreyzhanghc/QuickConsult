import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Brain, Sparkles } from 'lucide-react';

const FadeInDiv = ({ delay, children, className }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div className={`transition-all duration-700 ease-out ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'} ${className}`}>
      {children}
    </div>
  );
};

const LoginPage = () => {
  const { loginAsUser, loginAsExpert } = useAuth();
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Left Panel - Branding with animated background */}
      <div className={`lg:w-1/2 relative p-8 lg:p-16 flex flex-col justify-between overflow-hidden transition-all duration-1000 
        ${isLoaded ? 'opacity-100' : 'opacity-0'}`}>
        
        {/* Animated background container */}
        <div className="absolute inset-0 bg-gradient-to-br from-rose-50 via-neutral-50 to-amber-50 animate-gradient-shift">
          {/* First animated layer */}
          <div className="absolute inset-0 opacity-70">
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-rose-200/30 via-amber-200/20 to-rose-100/30 animate-flow" />
          </div>
          
          {/* Second animated layer */}
          <div className="absolute inset-0 opacity-50">
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-tl from-amber-100/20 via-rose-200/20 to-amber-100/30 animate-flow-reverse" />
          </div>

          {/* Glowing orbs */}
          <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br from-rose-200/30 via-amber-200/30 to-rose-200/30 rounded-full filter blur-3xl -translate-x-1/2 -translate-y-1/2 animate-glow" />
          <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-gradient-to-br from-amber-200/20 via-rose-200/20 to-amber-200/20 rounded-full filter blur-3xl translate-x-1/2 translate-y-1/2 animate-glow-reverse" />
        </div>

        {/* Content */}
        <div className="relative z-10">
          <FadeInDiv delay={200} className="flex items-center gap-2 mb-12">
            <Brain className="w-8 h-8 text-neutral-800" />
            <h1 className="text-2xl font-bold text-neutral-800">QuickConsult</h1>
          </FadeInDiv>

          <FadeInDiv delay={400} className="mb-8">
            <h2 className="text-4xl lg:text-6xl font-bold text-neutral-900 leading-tight">
              Get Your Question<br />
              Answered by Experts
            </h2>
          </FadeInDiv>

          <FadeInDiv delay={600}>
            <p className="text-neutral-700 text-lg max-w-md">
              Access AI matching consulting platform with ultimate speed and experience
            </p>
          </FadeInDiv>
        </div>
        
        <FadeInDiv delay={800} className="hidden lg:block relative z-10">
          <div className="flex items-center gap-4 p-6 bg-white/80 rounded-2xl backdrop-blur-md border border-neutral-200/50 hover:bg-white/90 transition-all duration-300 group">
            <Sparkles className="w-10 h-10 text-amber-500 group-hover:text-amber-600 transition-colors duration-300" />
            <div>
              <p className="text-neutral-900 font-medium">Innovation Starts Here</p>
              <p className="text-neutral-600 text-sm">Join our community of AI experts and innovators</p>
            </div>
          </div>
        </FadeInDiv>
      </div>

      {/* Right Panel - Login Options */}
      <div className="lg:w-1/2 p-8 lg:p-16 flex items-center justify-center bg-white">
        <div className="w-full max-w-md space-y-8">
          <FadeInDiv delay={600}>
            <div>
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Welcome Back</h3>
              <p className="text-neutral-600">Choose your login method to continue</p>
            </div>
          </FadeInDiv>

          <div className="space-y-4">
            <FadeInDiv delay={800}>
              <button
                onClick={loginAsUser}
                className="w-full group flex items-center justify-between bg-white px-6 py-4 rounded-2xl border border-neutral-200 hover:border-rose-200 hover:bg-rose-50/50 transition-all duration-300 ease-out"
              >
                <div className="flex items-center gap-4">
                  <svg viewBox="0 0 24 24" className="w-6 h-6" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  <div className="text-left">
                    <p className="font-medium text-neutral-900">Continue with Google</p>
                    <p className="text-sm text-neutral-500">For Business Users</p>
                  </div>
                </div>
                <div className="w-8 h-8 rounded-full bg-neutral-50 flex items-center justify-center group-hover:bg-rose-100/50 transition-colors duration-300">
                  <svg 
                    className="w-4 h-4 text-neutral-400 group-hover:text-rose-600 transition-all duration-300 group-hover:translate-x-0.5" 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            </FadeInDiv>

            <FadeInDiv delay={1000}>
              <button
                onClick={loginAsExpert}
                className="w-full group flex items-center justify-between bg-white px-6 py-4 rounded-2xl border border-neutral-200 hover:border-amber-200 hover:bg-amber-50/50 transition-all duration-300 ease-out"
              >
                <div className="flex items-center gap-4">
                  <svg viewBox="0 0 24 24" className="w-6 h-6" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" fill="#0077B5"/>
                  </svg>
                  <div className="text-left">
                    <p className="font-medium text-neutral-900">Continue with LinkedIn</p>
                    <p className="text-sm text-neutral-500">For Experts Login</p>
                  </div>
                </div>
                <div className="w-8 h-8 rounded-full bg-neutral-50 flex items-center justify-center group-hover:bg-amber-100/50 transition-colors duration-300">
                  <svg 
                    className="w-4 h-4 text-neutral-400 group-hover:text-amber-600 transition-all duration-300 group-hover:translate-x-0.5" 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            </FadeInDiv>
          </div>

          <FadeInDiv delay={1200}>
            <p className="text-center text-sm text-neutral-500">
              By continuing, you agree to our{' '}
              <a href="#" className="text-rose-600 hover:text-rose-700 font-medium">Terms of Service</a>
              {' '}and{' '}
              <a href="#" className="text-rose-600 hover:text-rose-700 font-medium">Privacy Policy</a>
            </p>
          </FadeInDiv>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;