import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // SIMRS Primary Palette - Medical Teal
        primary: {
          light: 'var(--simrs-primary-light)',
          DEFAULT: 'var(--simrs-primary)',
          dark: 'var(--simrs-primary-dark)',
          50: 'var(--simrs-primary-50)',
          100: 'var(--simrs-primary-100)',
          200: 'var(--simrs-primary-200)',
          300: 'var(--simrs-primary-300)',
          400: 'var(--simrs-primary-400)',
          500: 'var(--simrs-primary-500)',
          600: 'var(--simrs-primary-600)',
          700: 'var(--simrs-primary-700)',
          800: 'var(--simrs-primary-800)',
          900: 'var(--simrs-primary-900)',
        },
        // SIMRS Coral Accent
        coral: {
          light: 'var(--simrs-coral-light)',
          DEFAULT: 'var(--simrs-coral)',
          dark: 'var(--simrs-coral-dark)',
          50: 'var(--simrs-coral-50)',
          100: 'var(--simrs-coral-100)',
          200: 'var(--simrs-coral-200)',
          300: 'var(--simrs-coral-300)',
          400: 'var(--simrs-coral-400)',
          500: 'var(--simrs-coral-500)',
          600: 'var(--simrs-coral-600)',
          700: 'var(--simrs-coral-700)',
          800: 'var(--simrs-coral-800)',
          900: 'var(--simrs-coral-900)',
        },
        // SIMRS Gray Scale
        gray: {
          50: 'var(--simrs-gray-50)',
          100: 'var(--simrs-gray-100)',
          200: 'var(--simrs-gray-200)',
          300: 'var(--simrs-gray-300)',
          400: 'var(--simrs-gray-400)',
          500: 'var(--simrs-gray-500)',
          600: 'var(--simrs-gray-600)',
          700: 'var(--simrs-gray-700)',
          800: 'var(--simrs-gray-800)',
          900: 'var(--simrs-gray-900)',
        },
        // Triage Colors
        triage: {
          merah: 'var(--triage-merah)',
          kuning: 'var(--triage-kuning)',
          hijau: 'var(--triage-hijau)',
          biru: 'var(--triage-biru)',
          hitam: 'var(--triage-hitam)',
        },
        // BPJS Colors
        bpjs: {
          blue: 'var(--bpjs-blue)',
          light: 'var(--bpjs-light)',
          bg: 'var(--bpjs-bg)',
        },
        // Semantic Colors - Medical Context
        emergency: 'var(--simrs-emergency)',
        critical: 'var(--simrs-critical)',
        caution: 'var(--simrs-caution)',
        success: 'var(--simrs-success)',
        info: 'var(--simrs-info)',
        // Legacy semantic color names (mapped for compatibility)
        warning: 'var(--simrs-warning)',
        error: 'var(--simrs-emergency)',
        danger: 'var(--simrs-critical)',
        // Warm Grays (Neutral) - Legacy compatibility
        accent: {
          50: 'var(--simrs-coral-50)',
          100: 'var(--simrs-coral-100)',
          200: 'var(--simrs-coral-200)',
          300: 'var(--simrs-coral-300)',
          400: 'var(--simrs-coral-400)',
          500: 'var(--simrs-coral-500)',
          600: 'var(--simrs-coral-600)',
          700: 'var(--simrs-coral-700)',
          800: 'var(--simrs-coral-800)',
          900: 'var(--simrs-coral-900)',
        },
        neutral: {
          50: 'var(--simrs-gray-50)',
          100: 'var(--simrs-gray-100)',
          200: 'var(--simrs-gray-200)',
          300: 'var(--simrs-gray-300)',
          400: 'var(--simrs-gray-400)',
          500: 'var(--simrs-gray-500)',
          600: 'var(--simrs-gray-600)',
          700: 'var(--simrs-gray-700)',
          800: 'var(--simrs-gray-800)',
          900: 'var(--simrs-gray-900)',
        },
      },
      fontFamily: {
        sans: ['var(--font-plus-jakarta)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-ibm-plex)', 'monospace'],
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
