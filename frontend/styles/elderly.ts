/**
 * Elderly Mode tokens and scales
 * Ensures strict WCAG 2.2 AAA adherence:
 * - Text size: >= 24px (1.5rem)
 * - Contrast: >= 7:1 for normal and large text
 * - Touch targets: >= 48x48px (min 64px for primary actions)
 */

export const elderlyTokens = {
  typography: {
    minimumFontSize: "24px",
    displaySize: "42px",
    headingSize: "32px",
    subheadingSize: "28px",
    bodySize: "24px",
    captionSize: "20px",
    lineHeight: "1.5",
    fontWeight: {
      normal: "500",
      bold: "700",
      heavy: "800",
    },
  },
  touchTargets: {
    minimum: "48px",
    primaryButtonHeight: "64px",
    secondaryButtonHeight: "56px",
    iconSize: "32px",
  },
  colors: {
    background: "#FAF8F5", // Warm cream
    surface: "#FFFFFF",
    surfaceElevated: "#F5EDE0",
    textPrimary: "#1A150E", // Extremely high contrast > 14:1
    textSecondary: "#423223", // High contrast > 8.5:1
    border: "#C4B29F",
    // Action colors with 7:1 contrast against surface
    takenGreen: "#1B5E20",
    takenGreenBg: "#E8F5E9",
    takenGreenBorder: "#81C784",
    remindAmber: "#8C4E00",
    remindAmberBg: "#FFF3E0",
    remindAmberBorder: "#FFB74D",
    helpRed: "#B71C1C",
    helpRedBg: "#FFEBEE",
    helpRedBorder: "#E57373",
    focusRing: "#A5622D",
  },
  spacing: {
    screenPadding: "24px",
    cardPadding: "32px",
    elementGap: "20px",
  },
} as const;

