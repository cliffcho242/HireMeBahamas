import { Suspense } from "react";
import Link from "next/link";
import { JobFeedSkeleton } from "@/components/skeletons";
import { JobCard } from "@/components/job-card";
import { getLatestJobs } from "@/lib/db";

// Revalidate every 30 seconds for fresh content (ISR)
export const revalidate = 30;

export default async function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 py-20 sm:px-6 lg:px-8">
        <div className="absolute inset-0 bg-gradient-to-br from-sky-400/20 via-transparent to-amber-400/20" />
        <div className="relative mx-auto max-w-7xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-6xl lg:text-7xl">
            Find Your Dream Job in{" "}
            <span className="bg-gradient-to-r from-sky-400 to-sky-600 bg-clip-text text-transparent">
              The Bahamas
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
            The fastest job platform in the Caribbean. Connect with top employers,
            find amazing opportunities, and build your career in paradise.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link href="/jobs" className="btn-primary">
              Browse Jobs
            </Link>
            <Link href="/register" className="btn-secondary bg-slate-900 dark:bg-white dark:text-slate-900">
              Get Started
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="border-y border-slate-200 bg-white/50 py-12 dark:border-slate-700 dark:bg-slate-800/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-sky-500">1000+</div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Active Jobs
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-sky-500">500+</div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Companies
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-sky-500">10K+</div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Job Seekers
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-sky-500">&lt;120ms</div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Login Speed
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Latest Jobs Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              Latest Opportunities
            </h2>
            <Link
              href="/jobs"
              className="text-sky-500 hover:text-sky-600 font-medium"
            >
              View All →
            </Link>
          </div>
          <Suspense fallback={<JobFeedSkeleton count={6} />}>
            <JobFeed />
          </Suspense>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-sky-500 to-sky-600 py-16 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            Ready to start your journey?
          </h2>
          <p className="mt-4 text-lg text-sky-100">
            Join thousands of job seekers and employers in the Bahamas.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto bg-white text-sky-600 font-semibold py-3 px-8 rounded-xl hover:bg-sky-50 transition-all shadow-lg"
            >
              Create Free Account
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto border-2 border-white text-white font-semibold py-3 px-8 rounded-xl hover:bg-white/10 transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white font-semibold mb-4">For Job Seekers</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/jobs" className="hover:text-white">Browse Jobs</Link></li>
                <li><Link href="/register" className="hover:text-white">Create Profile</Link></li>
                <li><Link href="/hireme" className="hover:text-white">Get Hired</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">For Employers</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/post-job" className="hover:text-white">Post a Job</Link></li>
                <li><Link href="/pricing" className="hover:text-white">Pricing</Link></li>
                <li><Link href="/hireme" className="hover:text-white">Find Talent</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/about" className="hover:text-white">About Us</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contact</Link></li>
                <li><Link href="/blog" className="hover:text-white">Blog</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-white">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-white">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-slate-800 text-center text-sm">
            <p>© {new Date().getFullYear()} HireMeBahamas. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}

async function JobFeed() {
  const jobs = await getLatestJobs(6);

  if (!jobs.length) {
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
