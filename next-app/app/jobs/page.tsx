import { Suspense } from "react";
import Link from "next/link";
import { JobCard } from "@/components/job-card";
import { JobFeedSkeleton } from "@/components/skeletons";
import { getLatestJobs } from "@/lib/db";

// ISR: Revalidate every 30 seconds for fresh job listings
export const revalidate = 30;

export const metadata = {
  title: "Jobs - HireMeBahamas",
  description: "Browse the latest job opportunities in the Bahamas",
};

export default async function JobsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <section className="border-b border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Job Opportunities
              </h1>
              <p className="mt-2 text-slate-600 dark:text-slate-400">
                Discover amazing career opportunities in the Bahamas
              </p>
            </div>
            <Link
              href="/"
              className="text-sky-500 hover:text-sky-600 font-medium"
            >
              ← Back Home
            </Link>
          </div>
        </div>
      </section>

      {/* Jobs List */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <Suspense fallback={<JobFeedSkeleton count={12} />}>
            <JobsList />
          </Suspense>
        </div>
      </section>
    </main>
  );
}

async function JobsList() {
  const jobs = await getLatestJobs(50); // Get more jobs for the dedicated page

  if (!jobs.length) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-4">💼</div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
          No jobs available yet
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Check back soon for new opportunities!
        </p>
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
