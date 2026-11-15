'use client';

import React, { useState } from 'react';
import { Volume2, VolumeX, ShieldAlert, Utensils, AlertTriangle, Clock } from 'lucide-react';
import { Medication } from '@/lib/api/types';
import { speakText, isSpeechSynthesisSupported } from '@/lib/voice/speech';
import { Button } from '../ui/Button';

export function MedicineCard({ medication }: { medication: Medication }) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const synthAvailable = isSpeechSynthesisSupported();

  const handleReadAloud = () => {
    if (isSpeaking) {
      window.speechSynthesis?.cancel();
      setIsSpeaking(false);
      return;
    }

    const speechText = `${medication.name}, ${medication.strength}. ${
      medication.instructions
    }. What this is for: ${
      medication.purposeCard?.purpose || 'Prescribed health routine.'
    }. Caution: ${medication.purposeCard?.cautions || 'Follow doctor advice.'}`;

    setIsSpeaking(true);
    speakText(speechText, () => setIsSpeaking(false));
  };

  return (
    <article
      aria-label={`Medicine Details for ${medication.name}`}
      className="bg-white border-2 border-[#C4B29F] rounded-3xl p-8 sm:p-10 shadow-lg flex flex-col gap-8"
    >
      {/* Title & Speech Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#EBE4DB] pb-6">
        <div>
          <span className="text-xl font-bold uppercase tracking-wider text-[#A5622D]">
            {medication.form}
          </span>
          <h1 className="text-4xl sm:text-5xl font-black text-[#1A150E] mt-1">
            {medication.name}
            <span className="ml-3 text-3xl font-semibold text-[#5C4A38]">
              {medication.strength}
            </span>
          </h1>
        </div>

        {synthAvailable && (
          <Button
            variant="secondary"
            size="elder"
            onClick={handleReadAloud}
            aria-label={isSpeaking ? 'Stop reading aloud' : 'Read medicine information aloud'}
            className="flex items-center gap-3 bg-[#F5EDE0] text-[#1A150E] border-2 border-[#C4B29F]"
          >
            {isSpeaking ? (
              <>
                <VolumeX className="w-8 h-8 text-[#B54040]" aria-hidden />
                <span>Stop</span>
              </>
            ) : (
              <>
                <Volume2 className="w-8 h-8 text-[#A5622D]" aria-hidden />
                <span>Read Aloud</span>
              </>
            )}
          </Button>
        )}
      </div>

      {/* Purpose: Plain Language */}
      <div className="bg-[#FAF8F5] border-2 border-[#EBE4DB] rounded-2xl p-6">
        <h2 className="text-2xl font-bold text-[#1A150E] flex items-center gap-3 mb-2">
          <Clock className="w-7 h-7 text-[#A5622D]" aria-hidden />
          <span>What is this for?</span>
        </h2>
        <p className="text-2xl text-[#2D2318] leading-relaxed font-medium">
          {medication.purposeCard?.purpose || 'Prescribed as part of your daily health regimen.'}
        </p>
      </div>

      {/* How to Take */}
      <div className="bg-[#FAF8F5] border-2 border-[#EBE4DB] rounded-2xl p-6">
        <h2 className="text-2xl font-bold text-[#1A150E] flex items-center gap-3 mb-2">
          <Utensils className="w-7 h-7 text-[#5C8C5A]" aria-hidden />
          <span>How to take it:</span>
        </h2>
        <p className="text-2xl text-[#2D2318] leading-relaxed font-medium">
          {medication.instructions}
        </p>
      </div>

      {/* Caution and Diet */}
      {medication.purposeCard?.cautions && (
        <div className="bg-[#FFF3E0] border-2 border-[#FFB74D] rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-[#8C4E00] flex items-center gap-3 mb-2">
            <AlertTriangle className="w-7 h-7 text-[#8C4E00]" aria-hidden />
            <span>Safety & diet note:</span>
          </h2>
          <p className="text-2xl text-[#423223] leading-relaxed font-medium">
            {medication.purposeCard.cautions}
            {medication.purposeCard.foodToAvoid && ` Avoid: ${medication.purposeCard.foodToAvoid}`}
          </p>
        </div>
      )}

      {/* Advisory Disclaimer */}
      <div className="mt-4 p-4 rounded-xl bg-[#F2EDE6] border border-[#D6CCC0] flex items-start gap-3">
        <ShieldAlert className="w-6 h-6 text-[#5C4A38] shrink-0 mt-1" aria-hidden />
        <p className="text-lg text-[#5C4A38] leading-normal font-medium">
          This explanation is provided for your everyday routine. It does not replace medical advice or change your doctor&apos;s prescription.
        </p>
      </div>
    </article>
  );
}

