"""Voice-first care coordinator service (Feature F4).

Strict safety constraints:
- All answers are grounded strictly in stored CareCircle database values.
- No free-form generative medical advice.
- Supported intents: taken, later, next_dose, what_for, repeat, help.
- Help intent triggers immediate alert to caretaker.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.intents import match_intent
from app.models.member import Member
from app.models.notification import NotificationChannel, NotificationType
from app.repositories.dose_repo import DoseRepository
from app.repositories.member_repo import MemberRepository
from app.services.dose_service import DoseService
from app.services.notification_service import NotificationService


class VoiceService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.dose_repo = DoseRepository(db, circle_id)

    async def handle_intent(
        self,
        actor: Member,
        recipient_id: UUID,
        text: str,
        language: str = "en",
        dose_event_id: UUID | None = None,
    ) -> dict[str, Any]:
        intent = match_intent(text, language_hint=language)
        action_taken = False
        reply_en = ""
        reply_hi = ""
        advisory: str | None = None

        dose_svc = DoseService(self.db, self.circle_id)

        # 1. TAKEN
        if intent.name == "taken":
            # If no dose_event_id supplied, find the current next due dose
            target_id = dose_event_id
            if not target_id:
                next_due = await dose_svc.get_next_dose(recipient_id)
                if next_due:
                    target_id = next_due.id

            if target_id:
                await dose_svc.mark_taken(actor=actor, event_id=target_id, via="voice")
                action_taken = True
                reply_en = "Recorded! You have taken your medication."
                reply_hi = "बहुत बढ़िया! आपकी दवाई दर्ज कर ली गई है।"
            else:
                reply_en = "No pending scheduled doses found for right now."
                reply_hi = "अभी के लिए कोई बाकी दवाई नहीं मिली।"

        # 2. LATER (Snooze)
        elif intent.name == "later":
            target_id = dose_event_id
            if not target_id:
                next_due = await dose_svc.get_next_dose(recipient_id)
                if next_due:
                    target_id = next_due.id

            if target_id:
                await dose_svc.snooze(actor=actor, event_id=target_id, snooze_minutes=15)
                action_taken = True
                reply_en = "I will remind you again in 15 minutes."
                reply_hi = "मैं आपको 15 मिनट बाद दोबारा याद दिलाऊंगा।"
            else:
                reply_en = "No pending dose to postpone."
                reply_hi = "आगे बढ़ाने के लिए कोई दवाई नहीं मिली।"

        # 3. NEXT DOSE
        elif intent.name == "next_dose":
            next_due = await dose_svc.get_next_dose(recipient_id)
            if next_due and next_due.medication:
                time_str = next_due.scheduled_at.strftime("%I:%M %p")
                reply_en = f"Your next medicine is {next_due.medication.name} ({next_due.medication.strength}) at {time_str}."
                reply_hi = f"आपकी अगली दवाई {next_due.medication.name} ({next_due.medication.strength}) {time_str} पर है।"
            else:
                reply_en = "You have no upcoming medicines scheduled for today."
                reply_hi = "आज के लिए आपकी सभी दवाइयाँ पूरी हो चुकी हैं।"

        # 4. WHAT FOR (Medicine explainer)
        elif intent.name == "what_for":
            next_due = await dose_svc.get_next_dose(recipient_id)
            if next_due and next_due.medication:
                card = next_due.medication.purpose_card or {}
                purpose = card.get("purpose") or "Prescribed by your doctor."
                instructions = card.get("instructions") or next_due.medication.instructions or "Follow prescription."
                reply_en = f"{next_due.medication.name} is for: {purpose}. How to take: {instructions}."
                reply_hi = f"{next_due.medication.name} इस काम के लिए है: {purpose}। लेने का तरीका: {instructions}।"
                advisory = "Advisory only. Always follow your doctor's exact prescription."
            else:
                reply_en = "Could not find an active medicine card. Please consult your prescription."
                reply_hi = "दवाई की जानकारी नहीं मिली। कृपया अपने पर्चे की जांच करें।"

        # 5. REPEAT
        elif intent.name == "repeat":
            next_due = await dose_svc.get_next_dose(recipient_id)
            if next_due and next_due.medication:
                time_str = next_due.scheduled_at.strftime("%I:%M %p")
                reply_en = f"Repeating: {next_due.medication.name} ({next_due.medication.strength}) scheduled for {time_str}."
                reply_hi = f"दोहरा रहे हैं: {next_due.medication.name} ({next_due.medication.strength}) समय {time_str}।"
            else:
                reply_en = "No active reminders at this moment."
                reply_hi = "इस समय कोई सक्रिय अनुस्मारक नहीं है।"

        # 6. HELP (Immediate Caretaker Alert)
        elif intent.name == "help":
            m_repo = MemberRepository(self.db, self.circle_id)
            members = await m_repo.get_by_circle()
            caretakers = [m for m in members if m.role.value == "caretaker" and m.is_active]

            notif_svc = NotificationService(self.db, self.circle_id)
            for ct in caretakers:
                await notif_svc.enqueue(
                    member_id=ct.id,
                    channel=NotificationChannel.in_app,
                    notif_type=NotificationType.help,
                    payload={
                        "message": f"Help alert raised by {actor.display_name}. Immediate check-in requested.",
                        "elder_name": actor.display_name,
                    },
                    dedupe_key=f"voice_help_{actor.id}_{int(datetime.now(timezone.utc).timestamp())}",
                )
            action_taken = True
            reply_en = "I have alerted your caretaker. Someone will check in with you shortly."
            reply_hi = "केयरटेकर को सूचित कर दिया गया है। वे जल्द ही आपसे संपर्क करेंगे।"

        # Fallback
        else:
            reply_en = "I didn't quite catch that. You can say 'I took it', 'Remind later', or tap the button."
            reply_hi = "मुझे समझ नहीं आया। आप 'दवाई ले ली', 'बाद में', या स्क्रीन पर बटन दबा सकते हैं।"

        return {
            "intent": intent.name,
            "confidence": intent.confidence,
            "action_taken": action_taken,
            "reply_text": reply_hi if language == "hi" else reply_en,
            "reply_hi": reply_hi,
            "advisory": advisory,
        }
