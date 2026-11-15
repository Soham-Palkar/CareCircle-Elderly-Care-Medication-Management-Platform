/**
 * CareCircle Domain & API Types
 * Grounded directly in PROJECT_DESIGN.md specifications
 */

export type Role = 'elder' | 'caretaker' | 'family' | 'doctor';

export interface CareCircle {
  id: string;
  name: string;
  circleCode: string;
  createdAt: string;
}

export interface CareRecipient {
  id: string;
  circleId: string;
  fullName: string;
  dateOfBirth?: string;
  timezone: string;
  language: 'en' | 'hi';
  wakeTime: string;
  sleepTime: string;
  routineTimes: {
    breakfast: string;
    lunch: string;
    dinner: string;
    bedtime?: string;
  };
}

export interface Member {
  id: string;
  circleId: string;
  displayName: string;
  role: Role;
  email?: string;
  telegramChatId?: number | null;
  notifyPrefs?: {
    email: boolean;
    telegram: boolean;
    inApp: boolean;
    quietHoursStart?: string;
    quietHoursEnd?: string;
  };
  isActive: boolean;
  createdAt: string;
  permissions?: MemberPermissions;
}

export interface MemberPermissions {
  memberId: string;
  canViewMeds: boolean;
  canEditMeds: boolean;
  canMarkDoses: boolean;
  canViewAppointments: boolean;
  canEditAppointments: boolean;
  canViewHealth: boolean;
  receivesAlerts: boolean;
  alertLevelMin: number;
}

export interface Invite {
  id: string;
  circleId: string;
  role: Role;
  code: string;
  expiresAt: string;
  usedAt?: string | null;
  createdBy: string;
}

export interface PurposeCard {
  purpose: string;
  cautions: string;
  foodToAvoid?: string;
  bestTime?: string;
  advisoryDisclaimer: string;
}

export interface Medication {
  id: string;
  recipientId: string;
  name: string;
  strength: string; // e.g. "500 mg"
  form: string; // e.g. "tablet", "syrup"
  instructions: string;
  purposeCard?: PurposeCard;
  criticality: 'normal' | 'critical';
  doseQuantity: number;
  stockCount: number;
  refillThresholdDays: number;
  status: 'active' | 'archived';
  source: 'manual' | 'scan';
  confirmedWithDoctor: boolean;
  createdBy: string;
  createdAt: string;
  schedules?: MedicationSchedule[];
}

export interface MedicationSchedule {
  id: string;
  medicationId: string;
  kind: 'fixed_time' | 'routine_anchor';
  timeOfDay?: string | null; // e.g. "08:30"
  anchor?: 'breakfast' | 'lunch' | 'dinner' | 'bedtime' | null;
  anchorOffsetMin?: number; // e.g. +15
  daysOfWeek: number; // 1-127 bitmask or day array
  startDate: string;
  endDate?: string | null;
  graceMinutes: number;
  isActive: boolean;
  supersedesId?: string | null;
}

export type DoseState =
  | 'scheduled'
  | 'reminded'
  | 'snoozed'
  | 'taken'
  | 'taken_late'
  | 'skipped'
  | 'missed';

export interface DoseEvent {
  id: string;
  scheduleId: string;
  medicationId: string;
  recipientId: string;
  scheduledAt: string;
  state: DoseState;
  escalationLevel: number; // 0..3
  snoozeUntil?: string | null;
  takenAt?: string | null;
  recordedBy?: string | null;
  recordedVia?: 'app' | 'voice' | 'telegram' | 'email_link' | 'caretaker';
  skipReason?: string | null;
  medication?: Medication;
  undoToken?: string;
}

export interface Appointment {
  id: string;
  recipientId: string;
  doctorName: string;
  specialty?: string;
  location: string;
  scheduledAt: string;
  notes?: string;
  status: 'upcoming' | 'done' | 'cancelled';
  reminderOffsetsMin: number[];
  createdBy: string;
}

export interface NotificationItem {
  id: string;
  memberId: string;
  channel: 'email' | 'telegram' | 'in_app';
  type: 'dose_due' | 'dose_missed' | 'appointment' | 'refill' | 'risk_flag' | 'help';
  payload: {
    title: string;
    body: string;
    actionUrl?: string;
    details?: Record<string, unknown>;
  };
  status: 'pending' | 'sent' | 'failed';
  attempts: number;
  sentAt?: string | null;
  relatedEventId?: string | null;
}

export interface EscalationPolicy {
  level: number;
  delayMinutes: number;
  targetRole: Role;
  channel: string;
  description: string;
}

export type HealthReadingKind =
  | 'heart_rate'
  | 'sleep_hours'
  | 'steps'
  | 'bp_sys'
  | 'bp_dia'
  | 'glucose'
  | 'mood';

export interface HealthReading {
  id: string;
  recipientId: string;
  kind: HealthReadingKind;
  value: number;
  unit: string;
  recordedAt: string;
  source: 'simulated' | 'manual' | 'device';
}

export type RiskRuleCode = 'R1' | 'R2' | 'R3' | 'R4' | 'R5' | 'R6';

export interface RiskFlag {
  id: string;
  recipientId: string;
  ruleCode: RiskRuleCode;
  ruleName: string;
  severity: 'info' | 'warning' | 'high';
  message: string;
  evidence: Record<string, unknown>;
  status: 'open' | 'acknowledged' | 'resolved';
  createdAt: string;
}

export interface RiskForecastSlot {
  slot: string; // e.g. "Morning", "Afternoon", "Evening", "Night"
  time: string; // e.g. "08:30 AM"
  date: string;
  risk: 'low' | 'medium' | 'high';
  evidence: string;
  missProbability: number;
}

export interface ScheduleProposal {
  id: string;
  medicationId: string;
  medicationName: string;
  proposedBy: string | null;
  proposedByName?: string;
  change: {
    oldSchedule: string;
    newSchedule: string;
    anchorOffsetChange?: string;
  };
  rationale: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  decidedBy?: string | null;
  decidedAt?: string | null;
  elderConsentConfirmed?: boolean;
}

export interface ScanDraft {
  id: string;
  recipientId: string;
  uploadedBy: string;
  extracted: {
    name?: string;
    strength?: string;
    form?: string;
    frequency?: string;
    instructions?: string;
    confidence: {
      name: number;
      strength: number;
      form: number;
      frequency: number;
      instructions: number;
    };
  };
  overallConfidence: number;
  status: 'pending' | 'confirmed' | 'rejected' | 'expired';
  imageUrl?: string;
  createdAt: string;
}

export interface Streak {
  recipientId: string;
  currentStreak: number;
  bestStreak: number;
  lastDate: string;
}

export interface Reward {
  id: string;
  recipientId: string;
  thresholdDays: number;
  rewardType: 'call' | 'photo' | 'message';
  rewardRef: string;
  unlockedAt: string;
  claimedAt?: string | null;
}

export interface AdherenceDaily {
  recipientId: string;
  date: string;
  scheduledCount: number;
  takenCount: number;
  missedCount: number;
  adherencePct: number;
}

export interface AuditLogItem {
  id: string;
  circleId: string;
  actorMemberId: string | null;
  actorName: string;
  actorRole: Role;
  action: string;
  entityType: string;
  entityId: string;
  before?: unknown;
  after?: unknown;
  createdAt: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

