/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Warm, reassuring palette — NOT clinical
        primary: {
          DEFAULT: "#C97B4B",
          light: "#D99068",
          dark: "#A5622D",
          foreground: "#FFFFFF",
        },
        surface: {
          DEFAULT: "#FAF8F5",
          raised: "#F2EDE6",
          overlay: "#EBE4DB",
        },
        content: {
          primary: "#2D2318",
          secondary: "#5C4A38",
          muted: "#8B7560",
          disabled: "#B5A594",
          inverse: "#FAF8F5",
        },
        success: {
          DEFAULT: "#5C8C5A",
          light: "#7AAD78",
          dark: "#3E6B3C",
          foreground: "#FFFFFF",
          surface: "#EEF5EE",
        },
        warning: {
          DEFAULT: "#C97B4B",
          light: "#D99068",
          dark: "#A5622D",
          foreground: "#FFFFFF",
          surface: "#FDF3EB",
        },
        danger: {
          DEFAULT: "#B54040",
          light: "#C85C5C",
          dark: "#8C2D2D",
          foreground: "#FFFFFF",
          surface: "#FAEAEA",
        },
        neutral: {
          50: "#FAF8F5",
          100: "#F2EDE6",
          200: "#EBE4DB",
          300: "#D6CCC0",
          400: "#B5A594",
          500: "#8B7560",
          600: "#5C4A38",
          700: "#3D2F22",
          800: "#2D2318",
          900: "#1A150E",
        },
        // shadcn/ui compatibility
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          "1": "hsl(var(--chart-1))",
          "2": "hsl(var(--chart-2))",
          "3": "hsl(var(--chart-3))",
          "4": "hsl(var(--chart-4))",
          "5": "hsl(var(--chart-5))",
        },
      },
      fontSize: {
        // Base 18px minimum for accessibility
        xs: ["0.75rem", { lineHeight: "1.25rem" }],
        sm: ["0.875rem", { lineHeight: "1.375rem" }],
        base: ["1.125rem", { lineHeight: "1.75rem" }], // 18px base
        lg: ["1.25rem", { lineHeight: "1.875rem" }],
        xl: ["1.5rem", { lineHeight: "2rem" }],
        "2xl": ["1.875rem", { lineHeight: "2.25rem" }],
        "3xl": ["2.25rem", { lineHeight: "2.5rem" }],
        "4xl": ["3rem", { lineHeight: "1" }],
        // Elderly mode sizes (24px+)
        "elder-sm": ["1.5rem", { lineHeight: "2rem" }],     // 24px
        "elder-base": ["1.75rem", { lineHeight: "2.25rem" }], // 28px
        "elder-lg": ["2rem", { lineHeight: "2.5rem" }],      // 32px
        "elder-xl": ["2.5rem", { lineHeight: "3rem" }],      // 40px
        "elder-2xl": ["3rem", { lineHeight: "3.5rem" }],     // 48px
      },
      spacing: {
        // Elderly-safe touch targets (48px+ minimum)
        "touch-min": "3rem",    // 48px
        "touch-safe": "3.5rem", // 56px
        "touch-elder": "4rem",  // 64px
      },
      minHeight: {
        "touch-min": "3rem",
        "touch-safe": "3.5rem",
        "touch-elder": "4rem",
      },
      minWidth: {
        "touch-min": "3rem",
        "touch-safe": "3.5rem",
        "touch-elder": "4rem",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
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
        "fade-in": {
          from: { opacity: "0", transform: "translateY(4px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "fade-out": {
          from: { opacity: "1" },
          to: { opacity: "0" },
        },
        "spin-slow": {
          from: { transform: "rotate(0deg)" },
          to: { transform: "rotate(360deg)" },
        },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
        "fade-out": "fade-out 0.2s ease-out",
        "spin-slow": "spin-slow 1.5s linear infinite",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(45,35,24,0.08), 0 1px 2px -1px rgba(45,35,24,0.08)",
        "card-elevated":
          "0 4px 6px -1px rgba(45,35,24,0.10), 0 2px 4px -2px rgba(45,35,24,0.10)",
        "elder-focus":
          "0 0 0 3px #FAF8F5, 0 0 0 6px #C97B4B",
      },
    },
  },
  plugins: [],
};

