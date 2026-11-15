'use client';

import { useState, useCallback, useRef } from 'react';
import {
  isSpeechRecognitionSupported,
  isSpeechSynthesisSupported,
  createSpeechRecognizer,
  speakText,
} from './speech';
import { matchVoiceIntent, VoiceIntent } from './intentMapper';

export function useVoice() {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [lastIntent, setLastIntent] = useState<VoiceIntent | null>(null);
  const recognizerRef = useRef<any>(null);

  const supported = isSpeechRecognitionSupported();
  const synthSupported = isSpeechSynthesisSupported();

  const startListening = useCallback(
    (onIntentDetected?: (intent: VoiceIntent, raw: string) => void) => {
      if (!supported) return;

      try {
        if (recognizerRef.current) {
          recognizerRef.current.abort();
        }

        const recognizer = createSpeechRecognizer(
          (text) => {
            setTranscript(text);
            const { intent } = matchVoiceIntent(text);
            setLastIntent(intent);
            onIntentDetected?.(intent, text);
          },
          () => {
            setIsListening(false);
          },
          () => {
            setIsListening(false);
          },
        );

        recognizerRef.current = recognizer;
        recognizer?.start();
        setIsListening(true);
      } catch {
        setIsListening(false);
      }
    },
    [supported],
  );

  const stopListening = useCallback(() => {
    if (recognizerRef.current) {
      recognizerRef.current.stop();
    }
    setIsListening(false);
  }, []);

  const speak = useCallback(
    (text: string, callback?: () => void) => {
      setIsSpeaking(true);
      speakText(text, () => {
        setIsSpeaking(false);
        callback?.();
      });
    },
    [],
  );

  return {
    isListening,
    isSpeaking,
    transcript,
    lastIntent,
    supported,
    synthSupported,
    startListening,
    stopListening,
    speak,
  };
}

