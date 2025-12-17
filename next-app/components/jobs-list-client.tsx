"use client";

import { useJobs } from "@/lib/hooks";
import { JobCard } from "./job-card";
import { JobFeedSkeleton } from "./skeletons";

/**
 * Client-side Jobs List Component using React Query
 * 
 * This is an example of using React Query for client-side data fetching.
 * Benefits:
 * - Automatic caching (30s stale time)
 * - No duplicate fetches
 * - Automatic background revalidation
 * - Loading and error states
 * - Less DB load
 * 
 * Usage:
 * ```tsx
 * <JobsListClient limit={10} />
 * ```
 */
interface JobsListClientProps {
  limit?: number;
}

export function JobsListClient({ limit = 6 }: JobsListClientProps) {
  const { data: jobs, isLoading, error } = useJobs({ limit });

  if (isLoading) {
    return <JobFeedSkeleton count={limit} />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Failed to load jobs. Please try again.</p>
      </div>
    );
  }

  if (!jobs || jobs.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        No jobs available at the moment. Check back soon!
      </div>
    );
  }

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
}
