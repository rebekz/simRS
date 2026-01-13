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
        // Medical Blue-Teal (Primary)
        primary: {
          50: '#e0f2f1',
          100: '#b2dfdb',
          200: '#80cbc4',
          300: '#4db6ac',
          400: '#26a69a',
          500: '#009688',
          600: '#00897b',
          700: '#00796b',
          800: '#00695c',
          900: '#004d40',
        },
        // Warm Coral (Accent)
        accent: {
          50: '#fff3ed',
          100: '#ffdec5',
          200: '#ffc49b',
          300: '#ffaa71',
          400: '#ff9155',
          500: '#ff773a',
          600: '#f45d1f',
          700: '#c74619',
          800: '#9a3515',
          900: '#6d2411',
        },
        // Warm Grays (Neutral)
        neutral: {
          50: '#faf9f7',
          100: '#f5f3f0',
          200: '#e8e5e0',
          300: '#d3cfc7',
          400: '#b8b3a9',
          500: '#9e9891',
          600: '#817c77',
          700: '#68625f',
          800: '#4d4947',
          900: '#262424',
        },
        // Semantic Colors
        success: {
          light: '#81c784',
          DEFAULT: '#4caf50',
          dark: '#388e3c',
        },
        warning: {
          light: '#ffb74d',
          DEFAULT: '#ff9800',
          dark: '#f57c00',
        },
        error: {
          light: '#e57373',
          DEFAULT: '#f44336',
          dark: '#d32f2f',
        },
        info: {
          light: '#64b5f6',
          DEFAULT: '#2196f3',
          dark: '#1976d2',
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
