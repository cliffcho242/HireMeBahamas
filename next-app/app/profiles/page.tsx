import { Suspense } from "react";
import Link from "next/link";
import { ProfileSkeleton } from "@/components/skeletons";

// ISR: Revalidate every 30 seconds for fresh profile data
export const revalidate = 30;

export const metadata = {
  title: "Profiles - HireMeBahamas",
  description: "Discover talented professionals in the Bahamas",
};

export default async function ProfilesPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <section className="border-b border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Professional Profiles
              </h1>
              <p className="mt-2 text-slate-600 dark:text-slate-400">
                Connect with talented professionals in the Bahamas
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

      {/* Profiles Grid */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <Suspense fallback={<ProfilesGridSkeleton />}>
            <ProfilesContent />
          </Suspense>
        </div>
      </section>
    </main>
  );
}

function ProfilesGridSkeleton() {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="card p-6">
          <ProfileSkeleton />
        </div>
      ))}
    </div>
  );
}

async function ProfilesContent() {
  // Placeholder for profiles content - will be populated with actual user data
  // For now, show a message
  return (
    <div className="text-center py-20">
      <div className="text-6xl mb-4">👥</div>
      <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
        Profiles Coming Soon
      </h2>
      <p className="text-slate-600 dark:text-slate-400 mb-8">
        We&apos;re building a directory of talented professionals!
      </p>
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <Link
          href="/jobs"
          className="inline-flex items-center gap-2 bg-sky-500 text-white font-semibold py-3 px-6 rounded-xl hover:bg-sky-600 transition-colors"
        >
          Browse Jobs
        </Link>
        <Link
          href="/register"
          className="inline-flex items-center gap-2 border-2 border-sky-500 text-sky-500 font-semibold py-3 px-6 rounded-xl hover:bg-sky-50 dark:hover:bg-sky-900/20 transition-colors"
        >
          Create Profile
        </Link>
      </div>
    </div>
  );
}
