/* eslint-disable @typescript-eslint/no-explicit-any */
// Event types use const assertions that require type casting
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  XMarkIcon,
  VideoCameraIcon,
  CalendarDaysIcon,
  ClockIcon,
  MapPinIcon,
  BellIcon,
  LinkIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { CreateEventRequest, DEFAULT_REMINDERS, EVENT_TYPES, VIDEO_PLATFORMS, Reminder } from '../types/event';
import { isValidUrl } from '../utils/validation';

interface CreateEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onEventCreated?: () => void;
}

const CreateEventModal = ({ isOpen, onClose, onEventCreated }: CreateEventModalProps) => {
  const [step, setStep] = useState(1);
  const [isCreating, setIsCreating] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [eventType, setEventType] = useState<CreateEventRequest['event_type']>('video_call');
  const [startDate, setStartDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [duration, setDuration] = useState(30);
  const [videoPlatform, setVideoPlatform] = useState<'zoom' | 'teams' | 'google_meet' | 'other'>('zoom');
  const [meetingLink, setMeetingLink] = useState('');
  const [location, setLocation] = useState('');
  const [selectedReminders, setSelectedReminders] = useState<Reminder[]>(DEFAULT_REMINDERS);
  const [customReminder, setCustomReminder] = useState(15);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setStep(1);
      setTitle('');
      setDescription('');
      setEventType('video_call');
      setStartDate('');
      setStartTime('');
      setDuration(30);
      setVideoPlatform('zoom');
      setMeetingLink('');
      setLocation('');
      setSelectedReminders(DEFAULT_REMINDERS);
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!title.trim() || !startDate || !startTime) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Validate meeting link URL if provided (isValidUrl handles trimming internally)
    if (meetingLink && !isValidUrl(meetingLink)) {
      toast.error('Please enter a valid meeting link URL');
      return;
    }

    setIsCreating(true);
    try {
      // Combine date and time
      const startDateTime = new Date(`${startDate}T${startTime}`);
      const endDateTime = new Date(startDateTime.getTime() + duration * 60000);

      const eventData: CreateEventRequest = {
        title: title.trim(),
        description: description.trim(),
        event_type: eventType,
        start_date: startDateTime.toISOString(),
        end_date: endDateTime.toISOString(),
        duration,
        location: location.trim() || undefined,
        video_platform: videoPlatform,
        meeting_link: meetingLink.trim() || undefined,
        reminder_settings: {
          enabled: selectedReminders.length > 0,
          reminders: selectedReminders,
        },
      };

      // In a real app, this would call the API
      console.log('Creating event:', eventData);
      
      // Simulated API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success(
        <div>
          <p className="font-semibold">Event Created Successfully!</p>
          <p className="text-sm">You'll receive reminders before the meeting.</p>
        </div>,
        { duration: 4000 }
      );
      
      onEventCreated?.();
      onClose();
    } catch (error) {
      toast.error('Failed to create event');
      console.error('Error creating event:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const addCustomReminder = () => {
    if (customReminder > 0) {
      setSelectedReminders([
        ...selectedReminders,
        { time_before: customReminder, type: 'both', sent: false },
      ]);
      setCustomReminder(15);
    }
  };

  const removeReminder = (index: number) => {
    setSelectedReminders(selectedReminders.filter((_, i) => i !== index));
  };

  const formatReminderTime = (minutes: number): string => {
    if (minutes < 60) return `${minutes} minutes`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)} hour${minutes >= 120 ? 's' : ''}`;
    return `${Math.floor(minutes / 1440)} day${minutes >= 2880 ? 's' : ''}`;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={onClose}
          >
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Schedule Video Call</h2>
                  <p className="text-sm text-gray-600 mt-1">Plan your business meeting with reminders</p>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-full hover:bg-gray-200 transition-colors"
                  disabled={isCreating}
                >
                  <XMarkIcon className="w-6 h-6 text-gray-500" />
                </button>
              </div>

              {/* Progress Indicator */}
              <div className="flex items-center justify-center space-x-2 px-6 py-4 bg-gray-50">
                {[1, 2, 3].map((s) => (
                  <div key={s} className="flex items-center">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
                        step >= s
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {step > s ? <CheckIcon className="w-5 h-5" /> : s}
                    </div>
                    {s < 3 && (
                      <div
                        className={`w-16 h-1 mx-2 rounded ${
                          step > s ? 'bg-blue-600' : 'bg-gray-200'
                        }`}
                      />
                    )}
                  </div>
                ))}
              </div>

              {/* Content */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {/* Step 1: Basic Info */}
                {step === 1 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-4"
                  >
                    {/* Event Type */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Event Type <span className="text-red-500">*</span>
                      </label>
                      <div className="grid grid-cols-3 gap-3">
                        {EVENT_TYPES.map((type) => (
                          <button
                            key={type.value}
                            type="button"
                            onClick={() => setEventType(type.value as any)}
                            className={`p-3 rounded-lg border-2 transition-all ${
                              eventType === type.value
                                ? 'border-blue-600 bg-blue-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <div className="text-2xl mb-1">{type.icon}</div>
                            <div className={`text-sm font-medium ${type.color}`}>
                              {type.label}
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Title */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Event Title <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="e.g., Client Strategy Meeting"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        maxLength={100}
                      />
                    </div>

                    {/* Description */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description
                      </label>
                      <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Add details about this meeting..."
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={3}
                        maxLength={500}
                      />
                      <div className="text-right text-xs text-gray-500 mt-1">
                        {description.length}/500
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Step 2: Date & Time */}
                {step === 2 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-4"
                  >
                    {/* Date */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <CalendarDaysIcon className="w-5 h-5 inline mr-2" />
                        Date <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    {/* Time */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <ClockIcon className="w-5 h-5 inline mr-2" />
                        Start Time <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="time"
                        value={startTime}
                        onChange={(e) => setStartTime(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    {/* Duration */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Duration
                      </label>
                      <div className="grid grid-cols-4 gap-2">
                        {[15, 30, 45, 60].map((mins) => (
                          <button
                            key={mins}
                            type="button"
                            onClick={() => setDuration(mins)}
                            className={`px-4 py-2 rounded-lg border-2 transition-all ${
                              duration === mins
                                ? 'border-blue-600 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            {mins} min
                          </button>
                        ))}
                      </div>
                      <input
                        type="number"
                        value={duration}
                        onChange={(e) => setDuration(Number(e.target.value))}
                        min="5"
                        max="480"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mt-2"
                        placeholder="Custom duration (minutes)"
                      />
                    </div>

                    {/* Video Platform */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <VideoCameraIcon className="w-5 h-5 inline mr-2" />
                        Video Platform
                      </label>
                      <div className="grid grid-cols-2 gap-3">
                        {VIDEO_PLATFORMS.map((platform) => (
                          <button
                            key={platform.value}
                            type="button"
                            onClick={() => setVideoPlatform(platform.value as any)}
                            className={`p-3 rounded-lg border-2 transition-all flex items-center space-x-2 ${
                              videoPlatform === platform.value
                                ? 'border-blue-600 bg-blue-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <span className="text-xl">{platform.icon}</span>
                            <span className="text-sm font-medium">{platform.label}</span>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Meeting Link */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <LinkIcon className="w-5 h-5 inline mr-2" />
                        Meeting Link (Optional)
                      </label>
                      <input
                        type="text"
                        value={meetingLink}
                        onChange={(e) => setMeetingLink(e.target.value)}
                        placeholder="https://zoom.us/j/..."
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    {/* Location */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <MapPinIcon className="w-5 h-5 inline mr-2" />
                        Location (Optional)
                      </label>
                      <input
                        type="text"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        placeholder="Virtual or physical location"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </motion.div>
                )}

                {/* Step 3: Reminders */}
                {step === 3 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-4"
                  >
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                      <div className="flex items-start space-x-3">
                        <BellIcon className="w-6 h-6 text-blue-600 mt-0.5" />
                        <div>
                          <h3 className="font-semibold text-blue-900">Never Miss a Meeting</h3>
                          <p className="text-sm text-blue-700 mt-1">
                            Set up reminders to get notifications before your video call starts.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Active Reminders */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-3">
                        Active Reminders ({selectedReminders.length})
                      </label>
                      <div className="space-y-2">
                        {selectedReminders.map((reminder, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                          >
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                                <BellIcon className="w-5 h-5 text-blue-600" />
                              </div>
                              <div>
                                <p className="font-medium text-gray-900">
                                  {formatReminderTime(reminder.time_before)} before
                                </p>
                                <p className="text-xs text-gray-500">
                                  {reminder.type === 'both' ? 'Email & Push' : 
                                   reminder.type === 'email' ? 'Email only' : 'Push only'}
                                </p>
                              </div>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeReminder(index)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            >
                              <XMarkIcon className="w-5 h-5" />
                            </button>
                          </div>
                        ))}

                        {selectedReminders.length === 0 && (
                          <div className="text-center py-8 text-gray-500">
                            <BellIcon className="w-12 h-12 mx-auto mb-2 opacity-20" />
                            <p className="text-sm">No reminders set</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Add Custom Reminder */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Add Custom Reminder
                      </label>
                      <div className="flex space-x-2">
                        <input
                          type="number"
                          value={customReminder}
                          onChange={(e) => setCustomReminder(Number(e.target.value))}
                          min="1"
                          max="10080"
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Minutes before"
                        />
                        <button
                          type="button"
                          onClick={addCustomReminder}
                          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        >
                          Add
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        Quick options: 5min, 15min, 30min, 1hr, 2hrs, 24hrs, 1 week
                      </p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {[5, 15, 30, 60, 120, 1440, 10080].map((mins) => (
                          <button
                            key={mins}
                            type="button"
                            onClick={() => {
                              setSelectedReminders([
                                ...selectedReminders,
                                { time_before: mins, type: 'both', sent: false },
                              ]);
                            }}
                            className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                          >
                            {formatReminderTime(mins)}
                          </button>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
                <button
                  onClick={() => setStep(Math.max(1, step - 1))}
                  disabled={step === 1 || isCreating}
                  className="px-6 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Back
                </button>

                <div className="flex space-x-3">
                  <button
                    onClick={onClose}
                    disabled={isCreating}
                    className="px-6 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors font-medium"
                  >
                    Cancel
                  </button>

                  {step < 3 ? (
                    <button
                      onClick={() => setStep(step + 1)}
                      disabled={
                        (step === 1 && !title.trim()) ||
                        (step === 2 && (!startDate || !startTime))
                      }
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      <span>Next</span>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmit}
                      disabled={isCreating || !title.trim() || !startDate || !startTime}
                      className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {isCreating ? (
                        <>
                          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <span>Creating...</span>
                        </>
                      ) : (
                        <>
                          <CheckIcon className="w-5 h-5" />
                          <span>Create Event</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default CreateEventModal;
