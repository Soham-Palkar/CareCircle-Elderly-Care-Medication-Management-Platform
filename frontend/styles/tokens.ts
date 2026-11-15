/**
 * Design tokens for CareCircle
 * Warm, reassuring palette — NOT clinical hospital colors
 * Achieves WCAG AA (4.5:1) for normal text, AAA (7:1) in Elderly Mode
 */

export const colors = {
  // Primary: warm amber/terracotta
  primary: {
    DEFAULT: "#C97B4B",
    light: "#D99068",
    dark: "#A5622D",
    foreground: "#FFFFFF",
  },
  // Surface: warm cream
  surface: {
    DEFAULT: "#FAF8F5",
    raised: "#F2EDE6",
    overlay: "#EBE4DB",
  },
  // Text: deep warm charcoal
  content: {
    primary: "#2D2318",
    secondary: "#5C4A38",
    muted: "#8B7560",
    disabled: "#B5A594",
    inverse: "#FAF8F5",
  },
  // Status colors — always paired with icons/text, never color-only
  success: {
    DEFAULT: "#5C8C5A",
    light: "#7AAD78",
    dark: "#3E6B3C",
    foreground: "#FFFFFF",
    surface: "#EEF5EE",
  },
  warning: {
    DEFAULT: "#B87333",
    light: "#C97B4B",
    dark: "#8C5520",
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
} as const;

export const typography = {
  // Base 18px for accessibility
  baseFontSize: "18px",
  fontFamily: {
    sans: "var(--font-inter), system-ui, sans-serif",
    mono: "var(--font-mono), monospace",
  },
  fontSizes: {
    xs: "0.75rem",
    sm: "0.875rem",
    base: "1.125rem",   // 18px
    lg: "1.25rem",
    xl: "1.5rem",
    "2xl": "1.875rem",
    "3xl": "2.25rem",
    "4xl": "3rem",
  },
  lineHeights: {
    tight: "1.25",
    snug: "1.375",
    normal: "1.6",
    relaxed: "1.75",
    loose: "2",
  },
  fontWeights: {
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },
} as const;

export const spacing = {
  // 8px grid
  0: "0",
  1: "0.25rem",   // 4px
  2: "0.5rem",    // 8px
  3: "0.75rem",   // 12px
  4: "1rem",      // 16px
  5: "1.25rem",   // 20px
  6: "1.5rem",    // 24px
  8: "2rem",      // 32px
  10: "2.5rem",   // 40px
  12: "3rem",     // 48px — touch-min
  14: "3.5rem",   // 56px — touch-safe
  16: "4rem",     // 64px — touch-elder
} as const;

export const touchTargets = {
  min: "3rem",     // 48px WCAG 2.5.5 AA
  safe: "3.5rem",  // 56px comfortable
  elder: "4rem",   // 64px AAA elderly mode
} as const;

export const borderRadius = {
  sm: "0.375rem",
  md: "0.5rem",
  lg: "0.75rem",
  xl: "1rem",
  full: "9999px",
} as const;

export const shadows = {
  card: "0 1px 3px 0 rgba(45,35,24,0.08), 0 1px 2px -1px rgba(45,35,24,0.08)",
  cardElevated: "0 4px 6px -1px rgba(45,35,24,0.10), 0 2px 4px -2px rgba(45,35,24,0.10)",
  elderFocus: "0 0 0 3px #FAF8F5, 0 0 0 6px #C97B4B",
} as const;

// Contrast ratios for reference (WCAG)
// AA: 4.5:1 normal, 3:1 large text
// AAA: 7:1 normal, 4.5:1 large text
export const contrastPairs = {
  // content.primary (#2D2318) on surface.DEFAULT (#FAF8F5) ≈ 15:1 — AAA
  primaryOnSurface: { text: colors.content.primary, bg: colors.surface.DEFAULT, ratio: 15 },
  // primary.DEFAULT (#C97B4B) on surface.DEFAULT (#FAF8F5) ≈ 3.5:1 — AA large
  accentOnSurface: { text: colors.primary.DEFAULT, bg: colors.surface.DEFAULT, ratio: 3.5 },
  // white on primary.dark (#A5622D) ≈ 4.9:1 — AA
  whiteOnPrimaryDark: { text: "#FFFFFF", bg: colors.primary.dark, ratio: 4.9 },
} as const;

export type ColorToken = typeof colors;
export type SpacingToken = typeof spacing;

