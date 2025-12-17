import { Suspense } from "react";
import Link from "next/link";
import { FeedSkeleton } from "@/components/skeletons";

// ISR: Revalidate every 30 seconds for fresh feed content
export const revalidate = 30;

export const metadata = {
  title: "Feed - HireMeBahamas",
  description: "Stay updated with the latest posts and updates from the HireMeBahamas community",
};

export default async function FeedPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <section className="border-b border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Community Feed
              </h1>
              <p className="mt-2 text-slate-600 dark:text-slate-400">
                Latest updates from the HireMeBahamas community
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

      {/* Feed Content */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <Suspense fallback={<FeedSkeleton count={5} />}>
            <FeedContent />
          </Suspense>
        </div>
      </section>
    </main>
  );
}

async function FeedContent() {
  // Placeholder for feed content - will be populated with actual posts
  // For now, show a message
  return (
    <div className="text-center py-20">
      <div className="text-6xl mb-4">🌴</div>
      <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
        Feed Coming Soon
      </h2>
      <p className="text-slate-600 dark:text-slate-400 mb-8">
        We&apos;re building an amazing community feed for you!
      </p>
      <Link
        href="/jobs"
        className="inline-flex items-center gap-2 bg-sky-500 text-white font-semibold py-3 px-6 rounded-xl hover:bg-sky-600 transition-colors"
      >
        Browse Jobs Instead
      </Link>
    </div>
  );
}
