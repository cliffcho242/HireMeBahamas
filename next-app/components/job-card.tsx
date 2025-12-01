import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import type { Job } from "@/lib/db";

interface JobCardProps {
  job: Job;
}

export function JobCard({ job }: JobCardProps) {
  const formatSalary = (min: number | null, max: number | null) => {
    if (!min && !max) return null;
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    if (min) return `From $${min.toLocaleString()}`;
    if (max) return `Up to $${max.toLocaleString()}`;
    return null;
  };

  const salary = formatSalary(job.salary_min, job.salary_max);
  const timeAgo = formatDistanceToNow(new Date(job.created_at), {
    addSuffix: true,
  });

  const jobTypeColors: Record<string, string> = {
    "full-time": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    "part-time": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    contract: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
    remote: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  };

  return (
    <article className="card p-6 group hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <Link
            href={`/jobs/${job.id}`}
            className="block"
          >
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white truncate group-hover:text-sky-500 transition-colors">
              {job.title}
            </h3>
          </Link>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            {job.company}
          </p>
        </div>
        <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-sky-400 to-sky-600 rounded-xl flex items-center justify-center text-white font-bold text-lg">
          {job.company.charAt(0).toUpperCase()}
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mt-4">
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            jobTypeColors[job.job_type] || "bg-slate-100 text-slate-800"
          }`}
        >
          {job.job_type.replace("-", " ")}
        </span>
        <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300">
          📍 {job.location}
        </span>
        {salary && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">
            💰 {salary}
          </span>
        )}
      </div>

      {/* Description */}
      <p className="mt-4 text-sm text-slate-600 dark:text-slate-400 line-clamp-3">
        {job.description}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-100 dark:border-slate-700">
        <span className="text-xs text-slate-500 dark:text-slate-400">
          Posted {timeAgo}
        </span>
        <Link
          href={`/jobs/${job.id}`}
          className="inline-flex items-center gap-1 text-sm font-medium text-sky-500 hover:text-sky-600 transition-colors"
        >
          View Details
          <svg
            className="w-4 h-4 group-hover:translate-x-1 transition-transform"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </Link>
      </div>
    </article>
  );
}
