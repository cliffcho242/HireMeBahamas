"use client";

import { useState } from "react";

/**
 * Heavy client-side component for job applications
 * This component should be dynamically imported to reduce initial bundle size
 * 
 * Example usage:
 * ```tsx
 * import dynamic from "next/dynamic";
 * 
 * const JobApplicationModal = dynamic(
 *   () => import("@/components/job-application-modal"),
 *   {
 *     ssr: false,
 *     loading: () => <p>Loading application form...</p>,
 *   }
 * );
 * ```
 */

interface JobApplicationModalProps {
  jobId: number;
  jobTitle: string;
  onClose: () => void;
}

export default function JobApplicationModal({
  jobId,
  jobTitle,
  onClose,
}: JobApplicationModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    coverLetter: "",
    resume: null as File | null,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission - TODO: implement API call
    // POST to /api/applications with formData and jobId
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Apply for Position
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                {jobTitle}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              aria-label="Close"
            >
              <svg
                className="w-6 h-6 text-slate-600 dark:text-slate-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
            >
              Full Name *
            </label>
            <input
              type="text"
              id="name"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
            >
              Email Address *
            </label>
            <input
              type="email"
              id="email"
              required
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="john@example.com"
            />
          </div>

          <div>
            <label
              htmlFor="phone"
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
            >
              Phone Number
            </label>
            <input
              type="tel"
              id="phone"
              value={formData.phone}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="+1 (242) 555-0123"
            />
          </div>

          <div>
            <label
              htmlFor="coverLetter"
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
            >
              Cover Letter *
            </label>
            <textarea
              id="coverLetter"
              required
              rows={6}
              value={formData.coverLetter}
              onChange={(e) =>
                setFormData({ ...formData, coverLetter: e.target.value })
              }
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent dark:bg-slate-700 dark:text-white resize-none"
              placeholder="Tell us why you're a great fit for this position..."
            />
          </div>

          <div>
            <label
              htmlFor="resume"
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
            >
              Resume (PDF) *
            </label>
            <input
              type="file"
              id="resume"
              required
              accept=".pdf"
              onChange={(e) =>
                setFormData({
                  ...formData,
                  resume: e.target.files?.[0] || null,
                })
              }
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent dark:bg-slate-700 dark:text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-slate-300 dark:border-slate-600 rounded-lg font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-sky-500 hover:bg-sky-600 rounded-lg font-semibold text-white transition-colors shadow-lg"
            >
              Submit Application
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
