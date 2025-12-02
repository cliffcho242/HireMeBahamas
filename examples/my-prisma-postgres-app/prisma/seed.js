const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function main() {
  console.log('Start seeding...');

  // Create users
  const user1 = await prisma.user.create({
    data: {
      email: 'alice@example.com',
      name: 'Alice Johnson',
      posts: {
        create: [
          {
            title: 'Getting Started with Prisma',
            content: 'Prisma makes database access easy and type-safe!',
            published: true,
          },
          {
            title: 'Draft Post',
            content: 'This is a draft post',
            published: false,
          },
        ],
      },
    },
  });

  const user2 = await prisma.user.create({
    data: {
      email: 'bob@example.com',
      name: 'Bob Smith',
      posts: {
        create: [
          {
            title: 'Welcome to HireMeBahamas',
            content: 'Find your dream job in the Bahamas!',
            published: true,
          },
        ],
      },
    },
  });

  console.log('Created users:', { user1, user2 });
  console.log('Seeding finished.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
