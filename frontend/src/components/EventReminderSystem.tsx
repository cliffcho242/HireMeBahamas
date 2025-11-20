import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BellIcon,
  XMarkIcon,
  VideoCameraIcon,
  ClockIcon,
  CalendarDaysIcon,
} from '@heroicons/react/24/outline';
import { Event } from '../types/event';
import toast from 'react-hot-toast';

interface EventReminderSystemProps {
  events?: Event[];
}

interface ReminderNotification {
  id: string;
  event: Event;
  timeUntil: number; // minutes
  message: string;
  type: 'urgent' | 'warning' | 'info';
}

const EventReminderSystem: React.FC<EventReminderSystemProps> = ({ events = [] }) => {
  const [activeReminders, setActiveReminders] = useState<ReminderNotification[]>([]);
  const [dismissedReminders, setDismissedReminders] = useState<Set<string>>(new Set());

  const checkUpcomingEvents = useCallback(() => {
    const now = new Date();
    const newReminders: ReminderNotification[] = [];

    events.forEach((event) => {
      if (event.status !== 'scheduled') return;

      const eventStart = new Date(event.start_date);
      const minutesUntil = Math.floor((eventStart.getTime() - now.getTime()) / 60000);

      // Only show reminders for events happening in the next 2 hours
      if (minutesUntil > 0 && minutesUntil <= 120) {
        const reminderId = `${event.id}-${minutesUntil}`;

        // Check if this reminder has been dismissed
        if (dismissedReminders.has(reminderId)) return;

        // Check if we should show a reminder based on the event's reminder settings
        const shouldRemind = event.reminder_settings.enabled &&
          event.reminder_settings.reminders.some(r => {
            // Show reminder if we're within 2 minutes of the scheduled time
            return Math.abs(minutesUntil - r.time_before) <= 2 && !r.sent;
          });

        if (shouldRemind || minutesUntil <= 5) {
          let type: 'urgent' | 'warning' | 'info' = 'info';
          let message = '';

          if (minutesUntil <= 5) {
            type = 'urgent';
            message = `Your ${event.event_type.replace('_', ' ')} "${event.title}" starts in ${minutesUntil} minute${minutesUntil !== 1 ? 's' : ''}!`;
          } else if (minutesUntil <= 15) {
            type = 'warning';
            message = `Reminder: "${event.title}" starts in ${minutesUntil} minutes`;
          } else {
            type = 'info';
            message = `Upcoming: "${event.title}" in ${Math.floor(minutesUntil / 60)} hour${minutesUntil >= 120 ? 's' : ''}`;
          }

          newReminders.push({
            id: reminderId,
            event,
            timeUntil: minutesUntil,
            message,
            type,
          });
        }
      }
    });

    setActiveReminders(newReminders);

    // Show toast notifications for urgent reminders
    newReminders.forEach((reminder) => {
      if (reminder.type === 'urgent' && !dismissedReminders.has(reminder.id)) {
        toast.custom(
          (t) => (
            <motion.div
              initial={{ opacity: 0, y: -50, scale: 0.8 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className={`${
                t.visible ? 'animate-enter' : 'animate-leave'
              } max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-2 ring-red-500`}
            >
              <div className="flex-1 w-0 p-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 pt-0.5">
                    <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                      <BellIcon className="w-6 h-6 text-red-600 animate-pulse" />
                    </div>
                  </div>
                  <div className="ml-3 flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      🔔 Don't Forget Your Video Call!
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                      {reminder.message}
                    </p>
                    {reminder.event.meeting_link && (
                      <a
                        href={reminder.event.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-2 inline-flex items-center px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded-md hover:bg-blue-700"
                      >
                        <VideoCameraIcon className="w-4 h-4 mr-1" />
                        Join Now
                      </a>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex border-l border-gray-200">
                <button
                  onClick={() => toast.dismiss(t.id)}
                  className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-gray-600 hover:text-gray-500 focus:outline-none"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          ),
          {
            duration: 10000,
            position: 'top-right',
          }
        );
      }
    });
  }, [events, dismissedReminders]);

  useEffect(() => {
    // Check every minute
    const interval = setInterval(checkUpcomingEvents, 60000);

    return () => clearInterval(interval);
  }, [checkUpcomingEvents]);

  const dismissReminder = (reminderId: string) => {
    setDismissedReminders((prev) => new Set(prev).add(reminderId));
    setActiveReminders((prev) => prev.filter((r) => r.id !== reminderId));
  };

  const formatTimeUntil = (minutes: number): string => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  return (
    <AnimatePresence>
      {activeReminders.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed top-20 right-4 z-40 space-y-2 max-w-sm"
        >
          {activeReminders.map((reminder) => (
            <motion.div
              key={reminder.id}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              className={`bg-white rounded-lg shadow-xl border-l-4 overflow-hidden ${
                reminder.type === 'urgent'
                  ? 'border-red-500'
                  : reminder.type === 'warning'
                  ? 'border-yellow-500'
                  : 'border-blue-500'
              }`}
            >
              {/* Header */}
              <div
                className={`px-4 py-2 flex items-center justify-between ${
                  reminder.type === 'urgent'
                    ? 'bg-red-50'
                    : reminder.type === 'warning'
                    ? 'bg-yellow-50'
                    : 'bg-blue-50'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <BellIcon
                    className={`w-5 h-5 ${
                      reminder.type === 'urgent'
                        ? 'text-red-600 animate-pulse'
                        : reminder.type === 'warning'
                        ? 'text-yellow-600'
                        : 'text-blue-600'
                    }`}
                  />
                  <span
                    className={`text-sm font-semibold ${
                      reminder.type === 'urgent'
                        ? 'text-red-900'
                        : reminder.type === 'warning'
                        ? 'text-yellow-900'
                        : 'text-blue-900'
                    }`}
                  >
                    {reminder.type === 'urgent'
                      ? '🔔 Starting Soon!'
                      : reminder.type === 'warning'
                      ? '⏰ Reminder'
                      : 'ℹ️ Upcoming'}
                  </span>
                </div>
                <button
                  onClick={() => dismissReminder(reminder.id)}
                  className="p-1 hover:bg-white rounded-full transition-colors"
                  aria-label="Dismiss reminder"
                  title="Dismiss reminder"
                >
                  <XMarkIcon className="w-4 h-4 text-gray-500" />
                </button>
              </div>

              {/* Content */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-gray-900 flex-1 mr-2">
                    {reminder.event.title}
                  </h4>
                  <span
                    className={`text-xs font-bold px-2 py-1 rounded-full ${
                      reminder.type === 'urgent'
                        ? 'bg-red-100 text-red-700'
                        : reminder.type === 'warning'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}
                  >
                    {formatTimeUntil(reminder.timeUntil)}
                  </span>
                </div>

                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <CalendarDaysIcon className="w-4 h-4" />
                    <span>
                      {new Date(reminder.event.start_date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <ClockIcon className="w-4 h-4" />
                    <span>
                      {new Date(reminder.event.start_date).toLocaleTimeString('en-US', {
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                  {reminder.event.video_platform && (
                    <div className="flex items-center space-x-2">
                      <VideoCameraIcon className="w-4 h-4" />
                      <span className="capitalize">
                        {reminder.event.video_platform.replace('_', ' ')}
                      </span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="mt-4 flex space-x-2">
                  {reminder.event.meeting_link && (
                    <a
                      href={reminder.event.meeting_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`flex-1 px-4 py-2 rounded-lg text-center text-sm font-medium text-white transition-colors ${
                        reminder.type === 'urgent'
                          ? 'bg-red-600 hover:bg-red-700'
                          : reminder.type === 'warning'
                          ? 'bg-yellow-600 hover:bg-yellow-700'
                          : 'bg-blue-600 hover:bg-blue-700'
                      }`}
                    >
                      <VideoCameraIcon className="w-4 h-4 inline mr-1" />
                      Join Call
                    </a>
                  )}
                  <button
                    onClick={() => dismissReminder(reminder.id)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                    aria-label="Dismiss this reminder"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default EventReminderSystem;
