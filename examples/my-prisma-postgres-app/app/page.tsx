import { prisma } from '@/lib/prisma';

export default async function Home() {
  const users = await prisma.user.findMany({
    include: {
      posts: true,
    },
  });

  const postCount = await prisma.post.count();

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">My Prisma Postgres App</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Database Stats</h2>
          <p className="text-gray-700">
            Total Users: <span className="font-bold">{users.length}</span>
          </p>
          <p className="text-gray-700">
            Total Posts: <span className="font-bold">{postCount}</span>
          </p>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-semibold">Users</h2>
          {users.map((user) => (
            <div key={user.id} className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-2">{user.name}</h3>
              <p className="text-gray-600 mb-4">{user.email}</p>
              
              {user.posts.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold text-lg mb-2">Posts:</h4>
                  <ul className="space-y-2">
                    {user.posts.map((post) => (
                      <li key={post.id} className="pl-4 border-l-2 border-blue-500">
                        <p className="font-medium">{post.title}</p>
                        {post.content && (
                          <p className="text-gray-600 text-sm">{post.content}</p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          {post.published ? '✅ Published' : '📝 Draft'}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>

        {users.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              No users found. Run <code className="bg-gray-100 px-2 py-1 rounded">npx prisma db seed</code> to populate the database.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
