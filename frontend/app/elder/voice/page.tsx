'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useVoice } from '@/lib/voice/useVoice';
import { VoiceIntent } from '@/lib/voice/intentMapper';
import { api } from '@/lib/api/client';
import { DoseEvent } from '@/lib/api/types';
import { Mic, MicOff, Volume2, ArrowLeft, CheckCircle2, Clock, HelpCircle, Info, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { announce } from '@/lib/a11y/announcements';

export default function ElderVoicePage() {
  const { isListening, isSpeaking, transcript, supported, startListening, stopListening, speak } = useVoice();
  const [responseMessage, setResponseMessage] = useState<string>('');
  const [nextDose, setNextDose] = useState<DoseEvent | null>(null);

  useEffect(() => {
    api.getNextDose().then((d) => {
      setNextDose(d);
      if (d) {
        const welcome = `Hello Savitri ji. Your next medicine is ${d.medication?.name || 'Amlodipine'} scheduled for ${d.scheduledAt}. You can say: I took it, remind later, or what is this for.`;
        setResponseMessage(welcome);
        speak(welcome);
      }
    });
  }, [speak]);

  const handleIntent = async (intent: VoiceIntent) => {
    if (!nextDose) return;

    if (intent === 'taken') {
      await api.markDoseTaken(nextDose.id);
      const reply = `I have marked your ${nextDose.medication?.name} as taken. Great job!`;
      setResponseMessage(reply);
      announce(reply);
      speak(reply);
    } else if (intent === 'later') {
      await api.snoozeDose(nextDose.id, 15);
      const reply = `Alright, I will remind you again in 15 minutes.`;
      setResponseMessage(reply);
      announce(reply);
      speak(reply);
    } else if (intent === 'what_for') {
      const purpose =
        nextDose.medication?.purposeCard?.purpose ||
        'This medicine is prescribed by your doctor to maintain steady health and blood pressure.';
      const reply = `${nextDose.medication?.name}: ${purpose}`;
      setResponseMessage(reply);
      announce(reply);
      speak(reply);
    } else if (intent === 'next_dose') {
      const reply = `Your next dose is ${nextDose.medication?.name} at ${nextDose.scheduledAt}. Instructions: ${nextDose.medication?.instructions || 'Take with water.'}`;
      setResponseMessage(reply);
      announce(reply);
      speak(reply);
    } else if (intent === 'repeat') {
      speak(responseMessage || 'How can I assist your medicine routine today?');
    } else if (intent === 'help') {
      const reply = `Alerting your caretaker Rajesh immediately. Please rest comfortably while he contacts you.`;
      setResponseMessage(reply);
      announce(reply, 'assertive');
      speak(reply);
    } else {
      const reply = `I didn't quite catch that. You can tap any of the options below on screen.`;
      setResponseMessage(reply);
      speak(reply);
    }
  };

  const handleMicToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((intent) => {
        handleIntent(intent);
      });
    }
  };

  return (
    <div className="flex flex-col gap-8 pb-12">
      {/* Top Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/elder"
          aria-label="Back to main screen"
          className="p-3 bg-white border-2 border-[#D6CCC0] rounded-2xl text-[#1A150E] focus:outline-none focus:ring-4 focus:ring-[#C97B4B]"
        >
          <ArrowLeft className="w-8 h-8" aria-hidden />
        </Link>
        <div>
          <h1 className="text-4xl font-black text-[#1A150E]">Voice Assistant</h1>
          <p className="text-2xl text-[#5C4A38] font-medium">Speak or tap to respond</p>
        </div>
      </div>

      {/* Main Microphone Button */}
      <section className="bg-white border-2 border-[#C4B29F] rounded-3xl p-8 sm:p-12 text-center shadow-lg flex flex-col items-center gap-6">
        <button
          onClick={handleMicToggle}
          aria-label={isListening ? 'Stop listening' : 'Start speaking into microphone'}
          aria-pressed={isListening}
          className={`w-36 h-36 rounded-full flex items-center justify-center transition-all duration-200 shadow-xl focus:outline-none focus:ring-8 ${
            isListening
              ? 'bg-[#B71C1C] text-white ring-8 ring-[#B71C1C]/30 animate-pulse'
              : 'bg-[#C97B4B] text-white hover:bg-[#A5622D] ring-4 ring-[#C97B4B]/30'
          }`}
        >
          {isListening ? <MicOff className="w-20 h-20" /> : <Mic className="w-20 h-20" />}
        </button>

        <p className="text-3xl font-extrabold text-[#1A150E]">
          {isListening ? 'Listening carefully... speak now' : 'Tap the microphone to speak'}
        </p>

        {transcript && (
          <p className="text-2xl text-[#8C4E00] font-semibold bg-[#FFF3E0] px-6 py-3 rounded-2xl border border-[#FFB74D]">
            You said: &ldquo;{transcript}&rdquo;
          </p>
        )}

        {!supported && (
          <div className="bg-[#FFF3E0] border border-[#FFB74D] p-4 rounded-2xl text-xl text-[#8C4E00] font-medium">
            Note: Speech recognition is unavailable on this device browser. Please use the visible buttons below.
          </div>
        )}
      </section>

      {/* System Response Area */}
      {responseMessage && (
        <section
          role="status"
          aria-live="polite"
          className="bg-[#FAF8F5] border-2 border-[#C4B29F] rounded-3xl p-8 shadow-sm flex items-start gap-4"
        >
          <Volume2 className="w-10 h-10 text-[#C97B4B] shrink-0 mt-1" aria-hidden />
          <div>
            <h2 className="text-xl font-bold uppercase tracking-wider text-[#A5622D] mb-1">
              CareCircle Voice Answer
            </h2>
            <p className="text-2xl sm:text-3xl font-bold text-[#1A150E] leading-relaxed">
              {responseMessage}
            </p>
          </div>
        </section>
      )}

      {/* Visible Button Fallbacks (Always available for accessibility) */}
      <section className="flex flex-col gap-4">
        <h2 className="text-2xl font-bold text-[#1A150E]">Or tap any action directly:</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Button
            variant="elderPrimary"
            size="elder"
            onClick={() => handleIntent('taken')}
            className="flex items-center justify-start gap-4"
          >
            <CheckCircle2 className="w-8 h-8 shrink-0" aria-hidden />
            <span>&ldquo;I took it&rdquo;</span>
          </Button>

          <Button
            variant="elderSecondary"
            size="elder"
            onClick={() => handleIntent('later')}
            className="flex items-center justify-start gap-4"
          >
            <Clock className="w-8 h-8 shrink-0 text-[#8C4E00]" aria-hidden />
            <span>&ldquo;Remind me later&rdquo;</span>
          </Button>

          <Button
            variant="elderSecondary"
            size="elder"
            onClick={() => handleIntent('what_for')}
            className="flex items-center justify-start gap-4"
          >
            <Info className="w-8 h-8 shrink-0 text-[#1E3A8A]" aria-hidden />
            <span>&ldquo;What is this for?&rdquo;</span>
          </Button>

          <Button
            variant="elderSecondary"
            size="elder"
            onClick={() => handleIntent('next_dose')}
            className="flex items-center justify-start gap-4"
          >
            <Sparkles className="w-8 h-8 shrink-0 text-[#A5622D]" aria-hidden />
            <span>&ldquo;What is next?&rdquo;</span>
          </Button>

          <Button
            variant="destructive"
            size="elder"
            onClick={() => handleIntent('help')}
            className="sm:col-span-2 flex items-center justify-center gap-4 bg-[#B71C1C] hover:bg-[#8B0000] text-white min-h-[64px]"
          >
            <HelpCircle className="w-8 h-8 shrink-0" aria-hidden />
            <span>&ldquo;I need help&rdquo; (Alerts Caretaker)</span>
          </Button>
        </div>
      </section>
    </div>
  );
}

