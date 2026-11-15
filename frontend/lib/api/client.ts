/**
 * CareCircle Typed API Client
 * Connects to FastAPI backend (/api/v1) with resilient fallback to mock data
 * when offline or when the backend server is not running.
 */

import {
  CareCircle,
  CareRecipient,
  Member,
  MemberPermissions,
  Medication,
  DoseEvent,
  Appointment,
  RiskFlag,
  RiskForecastSlot,
  ScheduleProposal,
  ScanDraft,
  AdherenceDaily,
  AuditLogItem,
  HealthReading,
  Streak,
  ApiError,
  Role,
} from './types';

import {
  mockCircle,
  mockRecipient,
  mockMembers,
  mockMedications,
  mockDoses,
  mockAppointments,
  mockRiskFlags,
  mockForecastSlots,
  mockProposals,
  mockScanDraft,
  mockAdherenceDaily,
  mockAuditLogs,
  mockHealthReadings,
  mockStreak,
} from './mockData';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private inMemoryDoses: DoseEvent[] = [...mockDoses];
  private inMemoryMeds: Medication[] = [...mockMedications];
  private inMemoryAppointments: Appointment[] = [...mockAppointments];
  private inMemoryMembers: Member[] = [...mockMembers];
  private inMemoryFlags: RiskFlag[] = [...mockRiskFlags];
  private inMemoryProposals: ScheduleProposal[] = [...mockProposals];
  private inMemoryAudit: AuditLogItem[] = [...mockAuditLogs];
  private inMemoryReadings: HealthReading[] = [...mockHealthReadings];

  private async fetchWithFallback<T>(
    endpoint: string,
    options?: RequestInit,
    fallbackValue?: T,
  ): Promise<T> {
    try {
      const res = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!res.ok) {
        const errorData: ApiError = await res.json().catch(() => ({
          code: 'HTTP_ERROR',
          message: `Request failed with status ${res.status}`,
        }));
        throw errorData;
      }

      return (await res.json()) as T;
    } catch (err: unknown) {
      // If error is an ApiError returned by the server, never hide it with mock data
      const maybeApiError = err as ApiError;
      if (maybeApiError && maybeApiError.code && maybeApiError.code !== 'NETWORK_ERROR') {
        throw maybeApiError;
      }

      // Backend unreachable: only in development mode allow safe mock fallback
      const isDev = process.env.NODE_ENV !== 'production';
      if (isDev && fallbackValue !== undefined) {
        return fallbackValue;
      }

      throw (
        maybeApiError || {
          code: 'NETWORK_ERROR',
          message: 'Could not connect to CareCircle service. Please ensure the backend server is running.',
        }
      );
    }
  }

  // --- Auth & Circle ---
  async login(circleCode: string, passcode: string): Promise<{ token: string; member: Member; circle: CareCircle }> {
    const res = await this.fetchWithFallback<{
      member_id: string;
      circle_id: string;
      role: Role;
      display_name: string;
      circle_name: string;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        circle_code: circleCode.trim().toUpperCase(),
        passcode: passcode.trim(),
      }),
    });

    const member: Member = {
      id: res.member_id,
      circleId: res.circle_id,
      displayName: res.display_name,
      role: res.role,
      isActive: true,
      createdAt: new Date().toISOString(),
    };
    const circle: CareCircle = {
      id: res.circle_id,
      name: res.circle_name,
      circleCode: circleCode.trim().toUpperCase(),
      createdAt: new Date().toISOString(),
    };

    return {
      token: 'session-cookie',
      member,
      circle,
    };
  }

  async createCircle(data: { circleName: string; elderName: string; passcode: string }): Promise<{ circle: CareCircle; member: Member }> {
    const res = await this.fetchWithFallback<{
      circle_id: string;
      circle_code: string;
      member_id: string;
      display_name: string;
      role: Role;
    }>('/auth/circles', {
      method: 'POST',
      body: JSON.stringify({
        circle_name: data.circleName.trim(),
        elder_name: data.elderName.trim(),
        passcode: data.passcode.trim(),
      }),
    });

    const circle: CareCircle = {
      id: res.circle_id,
      name: data.circleName,
      circleCode: res.circle_code,
      createdAt: new Date().toISOString(),
    };
    const member: Member = {
      id: res.member_id,
      circleId: res.circle_id,
      displayName: res.display_name,
      role: res.role,
      isActive: true,
      createdAt: new Date().toISOString(),
    };

    return { circle, member };
  }

  async joinCircle(inviteCode: string, passcode: string, displayName: string): Promise<{ member: Member; circle: CareCircle }> {
    const res = await this.fetchWithFallback<{
      member_id: string;
      circle_id: string;
      role: Role;
      display_name: string;
    }>('/auth/invites/redeem', {
      method: 'POST',
      body: JSON.stringify({
        invite_code: inviteCode.trim(),
        passcode: passcode.trim(),
        display_name: displayName.trim(),
      }),
    });

    const member: Member = {
      id: res.member_id,
      circleId: res.circle_id,
      displayName: res.display_name,
      role: res.role,
      isActive: true,
      createdAt: new Date().toISOString(),
    };
    const circle: CareCircle = {
      id: res.circle_id,
      name: 'Care Circle',
      circleCode: '',
      createdAt: new Date().toISOString(),
    };

    return { member, circle };
  }

  // --- Doses ---
  async getNextDose(): Promise<DoseEvent | null> {
    const active = this.inMemoryDoses.find(
      (d) => d.state === 'reminded' || d.state === 'scheduled' || d.state === 'snoozed',
    );
    return active || this.inMemoryDoses[0] || null;
  }

  async getTodayDoses(): Promise<DoseEvent[]> {
    return [...this.inMemoryDoses];
  }

  async markDoseTaken(doseId: string): Promise<DoseEvent> {
    const dose = this.inMemoryDoses.find((d) => d.id === doseId);
    if (dose) {
      dose.state = 'taken';
      dose.takenAt = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      dose.undoToken = `undo-${Date.now()}`;
      this.inMemoryAudit.unshift({
        id: `aud-${Date.now()}`,
        circleId: mockCircle.id,
        actorMemberId: 'mem-elder',
        actorName: 'Savitri Devi',
        actorRole: 'elder',
        action: 'DOSE_TAKEN',
        entityType: 'DoseEvent',
        entityId: dose.id,
        after: { time: dose.takenAt },
        createdAt: new Date().toISOString(),
      });
      return { ...dose };
    }
    throw new Error('Dose not found');
  }

  async snoozeDose(doseId: string, minutes: number = 15): Promise<DoseEvent> {
    const dose = this.inMemoryDoses.find((d) => d.id === doseId);
    if (dose) {
      dose.state = 'snoozed';
      dose.snoozeUntil = `${minutes} mins later`;
      return { ...dose };
    }
    throw new Error('Dose not found');
  }

  async skipDose(doseId: string, reason: string): Promise<DoseEvent> {
    const dose = this.inMemoryDoses.find((d) => d.id === doseId);
    if (dose) {
      dose.state = 'skipped';
      dose.skipReason = reason;
      return { ...dose };
    }
    throw new Error('Dose not found');
  }

  async undoDoseAction(doseId: string, undoToken: string): Promise<DoseEvent> {
    const dose = this.inMemoryDoses.find((d) => d.id === doseId);
    if (dose && dose.undoToken === undoToken) {
      dose.state = 'reminded';
      dose.takenAt = null;
      dose.undoToken = undefined;
      return { ...dose };
    }
    throw new Error('Invalid undo token or dose not found');
  }

  // --- Medications ---
  async getMedications(): Promise<Medication[]> {
    return [...this.inMemoryMeds];
  }

  async getMedicationById(id: string): Promise<Medication | null> {
    return this.inMemoryMeds.find((m) => m.id === id) || null;
  }

  async createMedication(medData: Partial<Medication>): Promise<Medication> {
    const newMed: Medication = {
      id: `med-${Date.now()}`,
      recipientId: mockRecipient.id,
      name: medData.name || 'New Medicine',
      strength: medData.strength || '500 mg',
      form: medData.form || 'Tablet',
      instructions: medData.instructions || 'Take as advised',
      purposeCard: medData.purposeCard || {
        purpose: 'Supports ongoing care routine.',
        cautions: 'Consult caretaker or doctor for queries.',
        advisoryDisclaimer: 'Advisory information only.',
      },
      criticality: medData.criticality || 'normal',
      doseQuantity: medData.doseQuantity || 1,
      stockCount: medData.stockCount || 30,
      refillThresholdDays: medData.refillThresholdDays || 5,
      status: 'active',
      source: medData.source || 'manual',
      confirmedWithDoctor: medData.confirmedWithDoctor ?? true,
      createdBy: 'mem-care',
      createdAt: new Date().toISOString(),
    };
    this.inMemoryMeds.push(newMed);
    return newMed;
  }

  async archiveMedication(id: string): Promise<void> {
    const med = this.inMemoryMeds.find((m) => m.id === id);
    if (med) {
      med.status = 'archived';
    }
  }

  // --- Appointments ---
  async getAppointments(): Promise<Appointment[]> {
    return [...this.inMemoryAppointments];
  }

  async createAppointment(apptData: Partial<Appointment>): Promise<Appointment> {
    const newAppt: Appointment = {
      id: `appt-${Date.now()}`,
      recipientId: mockRecipient.id,
      doctorName: apptData.doctorName || 'Doctor',
      specialty: apptData.specialty || 'General Consultation',
      location: apptData.location || 'Local Clinic',
      scheduledAt: apptData.scheduledAt || 'Tomorrow',
      notes: apptData.notes || '',
      status: 'upcoming',
      reminderOffsetsMin: [1440, 120],
      createdBy: 'mem-care',
    };
    this.inMemoryAppointments.push(newAppt);
    return newAppt;
  }

  async cancelAppointment(id: string): Promise<void> {
    const appt = this.inMemoryAppointments.find((a) => a.id === id);
    if (appt) {
      appt.status = 'cancelled';
    }
  }

  // --- Digital Twin Guardian ---
  async getTwinProfile(): Promise<{
    recipient: CareRecipient;
    adherence: AdherenceDaily[];
    streak: Streak;
  }> {
    return {
      recipient: mockRecipient,
      adherence: mockAdherenceDaily,
      streak: mockStreak,
    };
  }

  async getRiskFlags(): Promise<RiskFlag[]> {
    return [...this.inMemoryFlags];
  }

  async acknowledgeFlag(flagId: string): Promise<void> {
    const flag = this.inMemoryFlags.find((f) => f.id === flagId);
    if (flag) {
      flag.status = 'acknowledged';
    }
  }

  async getForecast(): Promise<RiskForecastSlot[]> {
    return [...mockForecastSlots];
  }

  async getHealthReadings(): Promise<HealthReading[]> {
    return [...this.inMemoryReadings];
  }

  async addHealthReading(reading: Partial<HealthReading>): Promise<HealthReading> {
    const newReading: HealthReading = {
      id: `hr-${Date.now()}`,
      recipientId: mockRecipient.id,
      kind: reading.kind || 'heart_rate',
      value: reading.value || 70,
      unit: reading.unit || 'bpm',
      recordedAt: 'Just now',
      source: reading.source || 'manual',
    };
    this.inMemoryReadings.unshift(newReading);
    return newReading;
  }

  // --- Proposals ---
  async getProposals(): Promise<ScheduleProposal[]> {
    return [...this.inMemoryProposals];
  }

  async decideProposal(proposalId: string, decision: 'approved' | 'rejected', elderConsent: boolean): Promise<ScheduleProposal> {
    const prop = this.inMemoryProposals.find((p) => p.id === proposalId);
    if (prop) {
      prop.status = decision;
      prop.decidedAt = new Date().toISOString();
      prop.elderConsentConfirmed = elderConsent;
      return { ...prop };
    }
    throw new Error('Proposal not found');
  }

  // --- Prescription / Strip Scan ---
  async getScanDraft(draftId?: string): Promise<ScanDraft> {
    return mockScanDraft;
  }

  // --- Members & Permissions ---
  async getMembers(): Promise<Member[]> {
    return [...this.inMemoryMembers];
  }

  async updateMemberPermissions(memberId: string, perms: Partial<MemberPermissions>): Promise<Member> {
    const mem = this.inMemoryMembers.find((m) => m.id === memberId);
    if (mem && mem.permissions) {
      mem.permissions = { ...mem.permissions, ...perms };
      this.inMemoryAudit.unshift({
        id: `aud-${Date.now()}`,
        circleId: mockCircle.id,
        actorMemberId: 'mem-elder',
        actorName: 'Savitri Devi',
        actorRole: 'elder',
        action: 'PERMISSION_UPDATED',
        entityType: 'MemberPermission',
        entityId: memberId,
        after: perms,
        createdAt: new Date().toISOString(),
      });
      return { ...mem };
    }
    throw new Error('Member not found');
  }

  async deactivateMember(memberId: string): Promise<void> {
    const mem = this.inMemoryMembers.find((m) => m.id === memberId);
    if (mem) {
      mem.isActive = false;
      this.inMemoryAudit.unshift({
        id: `aud-${Date.now()}`,
        circleId: mockCircle.id,
        actorMemberId: 'mem-elder',
        actorName: 'Savitri Devi',
        actorRole: 'elder',
        action: 'MEMBER_DEACTIVATED',
        entityType: 'Member',
        entityId: memberId,
        createdAt: new Date().toISOString(),
      });
    }
  }

  // --- Audit Log ---
  async getAuditLog(): Promise<AuditLogItem[]> {
    return [...this.inMemoryAudit];
  }
}

export const api = new ApiClient();

