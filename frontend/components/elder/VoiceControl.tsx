'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Volume2, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

type SpeechRecognitionEvent = {
  results: { [index: number]: { [index: number]: { transcript: string } } };
};

interface VoiceControlProps {
  onIntent: (intent: string, transcript: string) => Promise<void>;
  className?: string;
}

const INTENT_BUTTONS = [
  { label: 'I took it', intent: 'taken', emoji: '✅' },
  { label: 'Remind me later', intent: 'later', emoji: '⏰' },
  { label: "What's next?", intent: 'next_dose', emoji: '❓' },
  { label: 'What is this for?', intent: 'what_for', emoji: '💊' },
  { label: 'Say that again', intent: 'repeat', emoji: '🔁' },
  { label: 'I need help', intent: 'help', emoji: '🆘' },
] as const;

export function VoiceControl({ onIntent, className }: VoiceControlProps) {
  const [permissionState, setPermissionState] = useState<
    'unknown' | 'granted' | 'denied' | 'unavailable'
  >('unknown');
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [systemResponse, setSystemResponse] = useState('');
  const [processing, setProcessing] = useState(false);
  const recognitionRef = useRef<unknown>(null);
  const responseRef = useRef<HTMLDivElement>(null);

  // Check speech recognition availability
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const SR =
      (window as unknown as Record<string, unknown>).SpeechRecognition ||
      (window as unknown as Record<string, unknown>).webkitSpeechRecognition;
    if (!SR) {
      setPermissionState('unavailable');
    }
  }, []);

  const speak = useCallback((text: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.rate = 0.9;
    utt.pitch = 1;
    window.speechSynthesis.speak(utt);
  }, []);

  const handleIntent = useCallback(
    async (intent: string, spokenText: string) => {
      setProcessing(true);
      try {
        await onIntent(intent, spokenText);
      } finally {
        setProcessing(false);
      }
    },
    [onIntent],
  );

  const startListening = useCallback(() => {
    if (typeof window === 'undefined') return;
    const SR =
      (window as unknown as Record<string, unknown>).SpeechRecognition ||
      (window as unknown as Record<string, unknown>).webkitSpeechRecognition;
    if (!SR) return;

    const recognition = new (SR as new () => {
      lang: string;
      interimResults: boolean;
      onresult: (e: SpeechRecognitionEvent) => void;
      onend: () => void;
      onerror: (e: { error: string }) => void;
      start: () => void;
      stop: () => void;
    })();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;

    recognition.onresult = (e: SpeechRecognitionEvent) => {
      const text = e.results[0][0].transcript;
      setTranscript(text);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.onerror = (e: { error: string }) => {
      setListening(false);
      if (e.error === 'not-allowed') {
        setPermissionState('denied');
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    setPermissionState('granted');
    setListening(true);
    setTranscript('');
  }, []);

  const stopListening = useCallback(() => {
    (recognitionRef.current as { stop: () => void } | null)?.stop();
    setListening(false);
  }, []);

  // Announce response changes
  useEffect(() => {
    if (systemResponse) {
      responseRef.current?.focus();
    }
  }, [systemResponse]);

  const micAvailable = permissionState !== 'unavailable';

  return (
    <div className={cn('flex flex-col items-center gap-8', className)}>
      {/* Permission denied warning */}
      {permissionState === 'denied' && (
        <div
          role="alert"
          className="w-full bg-[#FFF3CD] border-2 border-[#F0C040] rounded-2xl p-5 text-[22px] text-[#5C4A3A]"
        >
          <p className="font-bold">Microphone permission needed</p>
          <p className="mt-2">
            To use voice, please allow CareCircle to access your microphone in your
            browser or phone settings, then come back here.
          </p>
        </div>
      )}

      {/* Mic button */}
      {micAvailable ? (
        <button
          onClick={listening ? stopListening : startListening}
          disabled={processing}
          aria-label={listening ? 'Stop listening' : 'Start listening — tap to speak'}
          aria-pressed={listening}
          className={cn(
            'rounded-full flex items-center justify-center',
            'w-40 h-40 text-[#FAF8F5]',
            'transition-all duration-200 shadow-lg',
            'focus:outline-none focus:ring-4 focus:ring-offset-4',
            listening
              ? 'bg-[#8B2500] scale-110 animate-pulse focus:ring-[#8B2500]'
              : 'bg-[#2D6A4F] hover:bg-[#1B4332] focus:ring-[#2D6A4F]',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:animate-none',
          )}
        >
          {listening ? (
            <MicOff aria-hidden size={64} />
          ) : (
            <Mic aria-hidden size={64} />
          )}
        </button>
      ) : (
        <div className="rounded-full w-40 h-40 flex items-center justify-center bg-[#E8E0D6] text-[#A08060]">
          <MicOff aria-hidden size={64} />
        </div>
      )}

      {/* Status label under button */}
      <p
        aria-live="polite"
        className="text-[24px] font-semibold text-[#2D2318] text-center"
      >
        {listening
          ? '🎙️ Listening… speak now'
          : processing
            ? 'Understanding what you said…'
            : micAvailable
              ? 'Tap the button and speak'
              : 'Voice is not available on this device'}
      </p>

      {/* What we heard */}
      {transcript && (
        <div className="w-full bg-[#FDF3E7] border-2 border-[#E8D5B7] rounded-2xl p-5">
          <p className="text-[20px] text-[#7A5A3A] font-medium mb-1">
            CareCircle heard:
          </p>
          <p className="text-[26px] text-[#2D2318] font-bold leading-snug">
            &ldquo;{transcript}&rdquo;
          </p>
        </div>
      )}

      {/* System response */}
      {systemResponse && (
        <div
          ref={responseRef}
          tabIndex={-1}
          role="status"
          aria-live="polite"
          className="w-full bg-[#D8F3DC] border-2 border-[#95D5B2] rounded-2xl p-5 focus:outline-none"
        >
          <div className="flex items-center gap-3 mb-2">
            <Volume2 aria-hidden size={28} className="text-[#2D6A4F]" />
            <p className="text-[20px] text-[#2D6A4F] font-medium">
              CareCircle said:
            </p>
          </div>
          <p className="text-[26px] text-[#2D2318] font-bold leading-snug">
            {systemResponse}
          </p>
        </div>
      )}

      {/* Divider */}
      <div className="w-full border-t-2 border-[#E8E0D6] pt-4">
        <p className="text-[22px] text-[#5C4A3A] font-semibold mb-4 text-center">
          Or tap a button below:
        </p>

        {/* Button fallback grid */}
        <div className="grid grid-cols-2 gap-3 w-full">
          {INTENT_BUTTONS.map(({ label, intent, emoji }) => (
            <button
              key={intent}
              onClick={() => handleIntent(intent, label)}
              disabled={processing || listening}
              aria-label={label}
              className={cn(
                'flex flex-col items-center gap-2 p-4 rounded-2xl',
                'min-h-[80px] text-[20px] font-semibold',
                'bg-[#FAF8F5] border-2 border-[#E8D5B7] text-[#2D2318]',
                'transition-all duration-150',
                'focus:outline-none focus:ring-4 focus:ring-[#C97B4B] focus:ring-offset-2',
                'hover:border-[#C97B4B] hover:bg-[#FDF3E7]',
                'active:scale-95',
                'disabled:opacity-50 disabled:cursor-not-allowed',
              )}
            >
              <span className="text-[32px]" aria-hidden>
                {emoji}
              </span>
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* What you can say */}
      <details className="w-full">
        <summary className="text-[22px] text-[#C97B4B] font-semibold cursor-pointer list-none flex items-center gap-2 focus:outline-none">
          <span>What can I say to CareCircle?</span>
        </summary>
        <ul className="mt-4 flex flex-col gap-2 pl-4">
          {INTENT_BUTTONS.map(({ label, emoji }) => (
            <li key={label} className="text-[22px] text-[#5C4A3A] flex items-center gap-3">
              <span aria-hidden>{emoji}</span>
              <span>&ldquo;{label}&rdquo;</span>
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
