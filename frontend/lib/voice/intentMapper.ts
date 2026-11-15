/**
 * Voice Intent Mapper for CareCircle (F4)
 * Grounded strictly in stored care data. No unverified free-form LLM medical hallucinations.
 * Supports English, Hindi, and common Hinglish phrases.
 */

export type VoiceIntent =
  | 'taken'
  | 'later'
  | 'next_dose'
  | 'what_for'
  | 'repeat'
  | 'help'
  | 'unknown';

export interface IntentMatchResult {
  intent: VoiceIntent;
  confidence: number;
  matchedPhrase: string;
}

const INTENT_PATTERNS: Record<VoiceIntent, RegExp[]> = {
  taken: [
    /\b(taken|took it|i took it|done|yes took|already taken|finished)\b/i,
    /\b(le li|le liya|kha li|kha liya|dawa le li|ho gaya|pi liya)\b/i,
  ],
  later: [
    /\b(later|remind later|snooze|after some time|not now|in a bit|remind me later)\b/i,
    /\b(baad mein|thodi der baad|abhi nahi|baad me yaad dilana|ruk ke)\b/i,
  ],
  next_dose: [
    /\b(what'?s next|next|next dose|next medicine|what is next|when is next)\b/i,
    /\b(agli dawa|agla kya hai|next konsi hai|agli dawai kab hai)\b/i,
  ],
  what_for: [
    /\b(what is this for|what for|why this|explain medicine|what does this do|purpose)\b/i,
    /\b(kis cheez ki hai|ye kyu hai|ye dawai kiski hai|kiske liye hai)\b/i,
  ],
  repeat: [
    /\b(repeat|say that again|what did you say|say again|pardon|one more time)\b/i,
    /\b(phir se bolo|dobara bolo|phir se batana|samajh nahi aaya)\b/i,
  ],
  help: [
    /\b(help|i need help|emergency|alert caretaker|call help|help me)\b/i,
    /\b(madad|madad chahiye|rajesh ko bulao|caretaker ko phone lagao|pareshani hai)\b/i,
  ],
  unknown: [],
};

export function matchVoiceIntent(transcript: string): IntentMatchResult {
  const clean = transcript.trim().toLowerCase();

  for (const [intent, patterns] of Object.entries(INTENT_PATTERNS) as [VoiceIntent, RegExp[]][]) {
    if (intent === 'unknown') continue;
    for (const pattern of patterns) {
      if (pattern.test(clean)) {
        return {
          intent,
          confidence: 0.95,
          matchedPhrase: transcript,
        };
      }
    }
  }

  return {
    intent: 'unknown',
    confidence: 0.2,
    matchedPhrase: transcript,
  };
}

