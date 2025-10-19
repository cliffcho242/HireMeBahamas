/**
 * Event types for HireBahamas platform
 * Supports business meetings, video calls, interviews, and more
 */

export interface Event {
  id: number;
  title: string;
  description: string;
  event_type: 'video_call' | 'meeting' | 'interview' | 'webinar' | 'consultation' | 'other';
  start_date: string; // ISO 8601 format
  end_date: string; // ISO 8601 format
  duration: number; // in minutes
  location?: string; // Virtual meeting link or physical location
  video_platform?: 'zoom' | 'teams' | 'google_meet' | 'other';
  meeting_link?: string;
  organizer_id: number;
  organizer: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    avatar?: string;
  };
  attendees: EventAttendee[];
  reminder_settings: ReminderSettings;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  is_recurring: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly';
  created_at: string;
  updated_at: string;
}

export interface EventAttendee {
  id: number;
  event_id: number;
  user_id: number;
  user: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    avatar?: string;
  };
  status: 'invited' | 'accepted' | 'declined' | 'maybe';
  notified: boolean;
  joined_at?: string;
}

export interface ReminderSettings {
  enabled: boolean;
  reminders: Reminder[];
}

export interface Reminder {
  id?: number;
  time_before: number; // minutes before event
  type: 'email' | 'push' | 'both';
  sent: boolean;
  sent_at?: string;
}

export interface CreateEventRequest {
  title: string;
  description: string;
  event_type: Event['event_type'];
  start_date: string;
  end_date: string;
  duration: number;
  location?: string;
  video_platform?: Event['video_platform'];
  meeting_link?: string;
  attendee_ids?: number[];
  reminder_settings: ReminderSettings;
  is_recurring?: boolean;
  recurrence_pattern?: Event['recurrence_pattern'];
}

export interface EventNotification {
  id: number;
  event_id: number;
  event: Event;
  user_id: number;
  message: string;
  notification_type: 'reminder' | 'invitation' | 'update' | 'cancellation';
  read: boolean;
  created_at: string;
}

export const DEFAULT_REMINDERS: Reminder[] = [
  { time_before: 15, type: 'both', sent: false }, // 15 minutes before
  { time_before: 60, type: 'push', sent: false }, // 1 hour before
  { time_before: 1440, type: 'email', sent: false }, // 24 hours before
];

export const EVENT_TYPES = [
  { value: 'video_call', label: 'Video Call', icon: '📹', color: 'text-blue-600' },
  { value: 'meeting', label: 'Meeting', icon: '🤝', color: 'text-green-600' },
  { value: 'interview', label: 'Interview', icon: '💼', color: 'text-purple-600' },
  { value: 'webinar', label: 'Webinar', icon: '🎓', color: 'text-orange-600' },
  { value: 'consultation', label: 'Consultation', icon: '💡', color: 'text-yellow-600' },
  { value: 'other', label: 'Other', icon: '📅', color: 'text-gray-600' },
] as const;

export const VIDEO_PLATFORMS = [
  { value: 'zoom', label: 'Zoom', icon: '🎥' },
  { value: 'teams', label: 'Microsoft Teams', icon: '👥' },
  { value: 'google_meet', label: 'Google Meet', icon: '📞' },
  { value: 'other', label: 'Other', icon: '💻' },
] as const;
