/**
 * Browser Web Speech API wrappers
 * Safe, graceful degradation on unsupported devices
 */

type SpeechRecognitionType = any;

export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === 'undefined') return false;
  return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
}

export function isSpeechSynthesisSupported(): boolean {
  if (typeof window === 'undefined') return false;
  return 'speechSynthesis' in window;
}

export function createSpeechRecognizer(
  onResult: (text: string) => void,
  onError?: (err: unknown) => void,
  onEnd?: () => void,
): SpeechRecognitionType | null {
  if (!isSpeechRecognitionSupported()) return null;

  const SpeechRec =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognizer = new SpeechRec();
  recognizer.continuous = false;
  recognizer.interimResults = false;
  recognizer.lang = 'en-IN'; // Default to Indian English / Hindi accent support

  recognizer.onresult = (event: any) => {
    const transcript = event.results[0]?.[0]?.transcript || '';
    onResult(transcript);
  };

  recognizer.onerror = (event: any) => {
    onError?.(event);
  };

  recognizer.onend = () => {
    onEnd?.();
  };

  return recognizer;
}

export function speakText(text: string, onEnd?: () => void): void {
  if (!isSpeechSynthesisSupported()) {
    onEnd?.();
    return;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.9; // Slightly slower, calm cadence for elderly comprehension
  utterance.pitch = 1.0;
  utterance.onend = () => {
    onEnd?.();
  };
  utterance.onerror = () => {
    onEnd?.();
  };

  window.speechSynthesis.speak(utterance);
}

