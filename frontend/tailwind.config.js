/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    colors: {
      // Studio Dark Palette
      transparent: 'transparent',
      white: '#ffffff',
      black: '#000000',
      
      // Base surfaces
      'bg-base': '#09090b',
      'bg-card': '#18181b',
      'bg-surface': '#27272a',
      'bg-overlay': '#3f3f46',
      
      // Accents (Signal colors - inspired by mixer LEDs)
      'accent-primary': 'var(--accent-primary, #f59e0b)',    // amber-500 default
      'accent-secondary': 'var(--accent-secondary, #3b82f6)',  // blue-500 default
      'accent-success': '#10b981',    // emerald-500
      'accent-warning': '#ef4444',    // red-500
      'accent-muted': '#6b7280',      // gray-500
      
      // Brand theming support (CSS variables set by ThemeContext)
      // The "Chameleon" system: dynamically set by ThemeContext
      brand: {
        primary: 'var(--color-brand-primary, #ef4444)',      // Main brand color (Roland red default)
        secondary: 'var(--color-brand-secondary, #1f2937)',  // Supporting color
        accent: 'var(--color-brand-accent, #fbbf24)',        // Highlight/CTA
        background: 'var(--color-brand-background, #18181b)', // Panel background
        text: 'var(--color-brand-text, #ffffff)',            // Brand text color
      },
      
      // Backwards compatibility with old naming
      'brand-primary': 'var(--color-brand-primary, #ef4444)',
      'brand-secondary': 'var(--color-brand-secondary, #1f2937)',
      'brand-accent': 'var(--color-brand-accent, #fbbf24)',
      
      // Roland theme
      'roland-red': '#E31E24',
      'roland-dark': '#000000',
      'roland-gold': '#FFD700',
      
      // Text colors
      'text-primary': '#fafafa',      // zinc-50
      'text-secondary': '#d4d4d8',    // zinc-300
      'text-muted': '#a1a1aa',        // zinc-400
      'text-dimmed': '#71717a',       // zinc-500
      
      // Borders
      'border-strong': 'rgba(255, 255, 255, 0.15)',
      'border-subtle': 'rgba(255, 255, 255, 0.05)',
      
      // Legacy support (existing components)
      zinc: {
        50: '#fafafa',
        100: '#f4f4f5',
        200: '#e4e4e7',
        300: '#d4d4d8',
        400: '#a1a1aa',
        500: '#71717a',
        600: '#52525b',
        700: '#3f3f46',
        800: '#27272a',
        900: '#18181b',
        950: '#09090b',
      },
      slate: {
        900: '#0f172a',
        800: '#1e293b',
        700: '#334155',
        600: '#475569',
        500: '#64748b',
        400: '#94a3b8',
        300: '#cbd5e1',
        200: '#e2e8f0',
      },
      amber: {
        500: '#f59e0b',
        400: '#fbbf24',
        600: '#d97706',
      },
      blue: {
        500: '#3b82f6',
      },
      emerald: {
        500: '#10b981',
        400: '#34d399',
      },
      red: {
        500: '#ef4444',
      },
      gray: {
        500: '#6b7280',
      },
    },
    extend: {
      animation: {
        'fade-in-up': 'fadeInUp 0.6s cubic-bezier(0.21, 1.02, 0.73, 1) forwards',
        'scale-in': 'scaleIn 0.5s cubic-bezier(0.21, 1.02, 0.73, 1) forwards',
        'slide-in-right': 'slideInRight 0.8s cubic-bezier(0.4, 0.0, 0.2, 1) forwards',
        'shimmer': 'shimmer 3s infinite',
        'pulse-gentle': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-pulse': 'glowPulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(40px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        glowPulse: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        },
      },
      backgroundImage: {
        'noise': 'url("data:image/svg+xml,%3Csvg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noise"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" /%3E%3CfeColorMatrix type="saturate" values="0"/%3E%3C/filter%3E%3Crect width="400" height="400" filter="url(%23noise)" opacity="0.05"/%3E%3C/svg%3E")',
      },
      fontFamily: {
        sans: ["'Inter'", '-apple-system', 'BlinkMacSystemFont', "'Segoe UI'", 'sans-serif'],
        mono: ["'JetBrains Mono'", "'Courier New'", 'monospace'],
      },
      boxShadow: {
        'glow-amber': '0 0 20px -5px rgb(245, 158, 11)',
        'glow-blue': '0 0 20px -5px rgb(59, 130, 246)',
        'glow-green': '0 0 20px -5px rgb(16, 185, 129)',
        'glow-red': '0 0 20px -5px rgb(239, 68, 68)',
        'glow-brand': '0 0 20px -5px var(--color-brand-primary)',
      },
    },
  },
  plugins: [],
}
