/**
 * =============================================================================
 * DRIZZLE ORM SCHEMA - VERCEL POSTGRES OPTIMIZED
 * =============================================================================
 *
 * Schema definitions for HireMeBahamas with:
 * - BTREE indexes for fast lookups
 * - GIN indexes for full-text search
 * - Optimized column types for Vercel Postgres
 *
 * =============================================================================
 */

import {
  pgTable,
  serial,
  varchar,
  text,
  boolean,
  integer,
  timestamp,
  real,
  index,
  uniqueIndex,
  pgEnum,
} from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

// =============================================================================
// ENUMS
// =============================================================================

export const notificationTypeEnum = pgEnum('notification_type', [
  'follow',
  'job_application',
  'job_post',
  'like',
  'comment',
  'mention',
  'message',
]);

export const jobStatusEnum = pgEnum('job_status', ['active', 'closed', 'draft', 'expired']);

export const budgetTypeEnum = pgEnum('budget_type', ['fixed', 'hourly']);

export const applicationStatusEnum = pgEnum('application_status', [
  'pending',
  'reviewed',
  'accepted',
  'rejected',
]);

// =============================================================================
// USERS TABLE
// =============================================================================

export const users = pgTable(
  'users',
  {
    id: serial('id').primaryKey(),
    email: varchar('email', { length: 255 }).notNull().unique(),
    hashedPassword: varchar('hashed_password', { length: 255 }),
    firstName: varchar('first_name', { length: 100 }).notNull(),
    lastName: varchar('last_name', { length: 100 }).notNull(),
    username: varchar('username', { length: 50 }).unique(),
    phone: varchar('phone', { length: 20 }),
    location: varchar('location', { length: 200 }),
    occupation: varchar('occupation', { length: 200 }),
    companyName: varchar('company_name', { length: 200 }),
    bio: text('bio'),
    skills: text('skills'),
    experience: text('experience'),
    education: text('education'),
    avatarUrl: varchar('avatar_url', { length: 500 }),
    isActive: boolean('is_active').default(true),
    isAdmin: boolean('is_admin').default(false),
    isAvailableForHire: boolean('is_available_for_hire').default(false),
    role: varchar('role', { length: 50 }).default('user'),
    oauthProvider: varchar('oauth_provider', { length: 50 }),
    oauthProviderId: varchar('oauth_provider_id', { length: 255 }),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }),
  },
  (table) => ({
    // BTREE indexes for fast lookups
    emailIdx: uniqueIndex('users_email_idx').on(table.email),
    usernameIdx: uniqueIndex('users_username_idx').on(table.username),
    isActiveIdx: index('users_is_active_idx').on(table.isActive),
    isAvailableForHireIdx: index('users_is_available_for_hire_idx').on(table.isAvailableForHire),
    createdAtIdx: index('users_created_at_idx').on(table.createdAt),
    locationIdx: index('users_location_idx').on(table.location),
  })
);

// =============================================================================
// JOBS TABLE
// =============================================================================

export const jobs = pgTable(
  'jobs',
  {
    id: serial('id').primaryKey(),
    title: varchar('title', { length: 200 }).notNull(),
    company: varchar('company', { length: 200 }).notNull(),
    description: text('description').notNull(),
    requirements: text('requirements'),
    benefits: text('benefits'),
    category: varchar('category', { length: 100 }).notNull(),
    jobType: varchar('job_type', { length: 50 }).notNull().default('full-time'),
    location: varchar('location', { length: 200 }).notNull(),
    salaryMin: integer('salary_min'),
    salaryMax: integer('salary_max'),
    budget: real('budget'),
    budgetType: varchar('budget_type', { length: 20 }).default('fixed'),
    isRemote: boolean('is_remote').default(false),
    skills: text('skills'),
    status: varchar('status', { length: 20 }).default('active'),
    employerId: integer('employer_id')
      .notNull()
      .references(() => users.id),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }),
  },
  (table) => ({
    // BTREE indexes for fast filtering
    statusIdx: index('jobs_status_idx').on(table.status),
    categoryIdx: index('jobs_category_idx').on(table.category),
    jobTypeIdx: index('jobs_job_type_idx').on(table.jobType),
    locationIdx: index('jobs_location_idx').on(table.location),
    isRemoteIdx: index('jobs_is_remote_idx').on(table.isRemote),
    employerIdIdx: index('jobs_employer_id_idx').on(table.employerId),
    createdAtIdx: index('jobs_created_at_idx').on(table.createdAt),
    salaryRangeIdx: index('jobs_salary_range_idx').on(table.salaryMin, table.salaryMax),
    // Composite index for common query patterns
    statusCreatedAtIdx: index('jobs_status_created_at_idx').on(table.status, table.createdAt),
    categoryStatusIdx: index('jobs_category_status_idx').on(table.category, table.status),
  })
);

// =============================================================================
// MESSAGES TABLE
// =============================================================================

export const conversations = pgTable(
  'conversations',
  {
    id: serial('id').primaryKey(),
    participant1Id: integer('participant_1_id')
      .notNull()
      .references(() => users.id),
    participant2Id: integer('participant_2_id')
      .notNull()
      .references(() => users.id),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }),
  },
  (table) => ({
    participant1Idx: index('conversations_participant_1_idx').on(table.participant1Id),
    participant2Idx: index('conversations_participant_2_idx').on(table.participant2Id),
    participantsIdx: index('conversations_participants_idx').on(
      table.participant1Id,
      table.participant2Id
    ),
    updatedAtIdx: index('conversations_updated_at_idx').on(table.updatedAt),
  })
);

export const messages = pgTable(
  'messages',
  {
    id: serial('id').primaryKey(),
    conversationId: integer('conversation_id')
      .notNull()
      .references(() => conversations.id),
    senderId: integer('sender_id')
      .notNull()
      .references(() => users.id),
    receiverId: integer('receiver_id')
      .notNull()
      .references(() => users.id),
    content: text('content').notNull(),
    isRead: boolean('is_read').default(false),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    // BTREE indexes for message queries
    conversationIdIdx: index('messages_conversation_id_idx').on(table.conversationId),
    senderIdIdx: index('messages_sender_id_idx').on(table.senderId),
    receiverIdIdx: index('messages_receiver_id_idx').on(table.receiverId),
    isReadIdx: index('messages_is_read_idx').on(table.isRead),
    createdAtIdx: index('messages_created_at_idx').on(table.createdAt),
    // Composite index for unread messages
    receiverUnreadIdx: index('messages_receiver_unread_idx').on(table.receiverId, table.isRead),
    conversationCreatedIdx: index('messages_conversation_created_idx').on(
      table.conversationId,
      table.createdAt
    ),
  })
);

// =============================================================================
// JOB APPLICATIONS TABLE
// =============================================================================

export const jobApplications = pgTable(
  'job_applications',
  {
    id: serial('id').primaryKey(),
    jobId: integer('job_id')
      .notNull()
      .references(() => jobs.id),
    applicantId: integer('applicant_id')
      .notNull()
      .references(() => users.id),
    coverLetter: text('cover_letter'),
    proposedBudget: real('proposed_budget'),
    status: varchar('status', { length: 20 }).default('pending'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    jobIdIdx: index('job_applications_job_id_idx').on(table.jobId),
    applicantIdIdx: index('job_applications_applicant_id_idx').on(table.applicantId),
    statusIdx: index('job_applications_status_idx').on(table.status),
    jobApplicantIdx: uniqueIndex('job_applications_job_applicant_idx').on(
      table.jobId,
      table.applicantId
    ),
  })
);

// =============================================================================
// FOLLOWS TABLE
// =============================================================================

export const follows = pgTable(
  'follows',
  {
    id: serial('id').primaryKey(),
    followerId: integer('follower_id')
      .notNull()
      .references(() => users.id),
    followedId: integer('followed_id')
      .notNull()
      .references(() => users.id),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    followerIdx: index('follows_follower_id_idx').on(table.followerId),
    followedIdx: index('follows_followed_id_idx').on(table.followedId),
    uniqueFollowIdx: uniqueIndex('follows_unique_idx').on(table.followerId, table.followedId),
  })
);

// =============================================================================
// NOTIFICATIONS TABLE
// =============================================================================

export const notifications = pgTable(
  'notifications',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id),
    actorId: integer('actor_id').references(() => users.id),
    notificationType: notificationTypeEnum('notification_type').notNull(),
    content: text('content').notNull(),
    relatedId: integer('related_id'),
    isRead: boolean('is_read').default(false),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    userIdIdx: index('notifications_user_id_idx').on(table.userId),
    isReadIdx: index('notifications_is_read_idx').on(table.isRead),
    createdAtIdx: index('notifications_created_at_idx').on(table.createdAt),
    userUnreadIdx: index('notifications_user_unread_idx').on(table.userId, table.isRead),
    userCreatedIdx: index('notifications_user_created_idx').on(table.userId, table.createdAt),
  })
);

// =============================================================================
// POSTS TABLE
// =============================================================================

export const posts = pgTable(
  'posts',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id),
    content: text('content').notNull(),
    imageUrl: varchar('image_url', { length: 500 }),
    videoUrl: varchar('video_url', { length: 500 }),
    postType: varchar('post_type', { length: 50 }).default('text'),
    relatedJobId: integer('related_job_id').references(() => jobs.id),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }),
  },
  (table) => ({
    userIdIdx: index('posts_user_id_idx').on(table.userId),
    postTypeIdx: index('posts_post_type_idx').on(table.postType),
    createdAtIdx: index('posts_created_at_idx').on(table.createdAt),
    relatedJobIdx: index('posts_related_job_idx').on(table.relatedJobId),
  })
);

// =============================================================================
// POST LIKES TABLE
// =============================================================================

export const postLikes = pgTable(
  'post_likes',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id),
    postId: integer('post_id')
      .notNull()
      .references(() => posts.id),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    userIdIdx: index('post_likes_user_id_idx').on(table.userId),
    postIdIdx: index('post_likes_post_id_idx').on(table.postId),
    uniqueLikeIdx: uniqueIndex('post_likes_unique_idx').on(table.userId, table.postId),
  })
);

// =============================================================================
// POST COMMENTS TABLE
// =============================================================================

export const postComments = pgTable(
  'post_comments',
  {
    id: serial('id').primaryKey(),
    postId: integer('post_id')
      .notNull()
      .references(() => posts.id),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id),
    content: text('content').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }),
  },
  (table) => ({
    postIdIdx: index('post_comments_post_id_idx').on(table.postId),
    userIdIdx: index('post_comments_user_id_idx').on(table.userId),
    createdAtIdx: index('post_comments_created_at_idx').on(table.createdAt),
    postCreatedIdx: index('post_comments_post_created_idx').on(table.postId, table.createdAt),
  })
);

// =============================================================================
// REVIEWS TABLE
// =============================================================================

export const reviews = pgTable(
  'reviews',
  {
    id: serial('id').primaryKey(),
    jobId: integer('job_id')
      .notNull()
      .references(() => jobs.id),
    reviewerId: integer('reviewer_id')
      .notNull()
      .references(() => users.id),
    revieweeId: integer('reviewee_id')
      .notNull()
      .references(() => users.id),
    rating: integer('rating').notNull(),
    comment: text('comment'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    jobIdIdx: index('reviews_job_id_idx').on(table.jobId),
    reviewerIdx: index('reviews_reviewer_id_idx').on(table.reviewerId),
    revieweeIdx: index('reviews_reviewee_id_idx').on(table.revieweeId),
    ratingIdx: index('reviews_rating_idx').on(table.rating),
  })
);

// =============================================================================
// PROFILE PICTURES TABLE
// =============================================================================

export const profilePictures = pgTable(
  'profile_pictures',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id),
    fileUrl: varchar('file_url', { length: 500 }).notNull(),
    filename: varchar('filename', { length: 255 }).notNull(),
    fileSize: integer('file_size').notNull(),
    isCurrent: boolean('is_current').default(false),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    userIdIdx: index('profile_pictures_user_id_idx').on(table.userId),
    isCurrentIdx: index('profile_pictures_is_current_idx').on(table.isCurrent),
    userCurrentIdx: index('profile_pictures_user_current_idx').on(table.userId, table.isCurrent),
  })
);

// =============================================================================
// UPLOADED FILES TABLE
// =============================================================================

export const uploadedFiles = pgTable(
  'uploaded_files',
  {
    id: serial('id').primaryKey(),
    userId: integer('user_id')
      .notNull()
      .references(() => users.id),
    filename: varchar('filename', { length: 255 }).notNull(),
    fileType: varchar('file_type', { length: 50 }).notNull(),
    fileSize: integer('file_size').notNull(),
    fileUrl: varchar('file_url', { length: 500 }).notNull(),
    uploadType: varchar('upload_type', { length: 50 }).notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    userIdIdx: index('uploaded_files_user_id_idx').on(table.userId),
    uploadTypeIdx: index('uploaded_files_upload_type_idx').on(table.uploadType),
  })
);

// =============================================================================
// RELATIONS
// =============================================================================

export const usersRelations = relations(users, ({ many }) => ({
  jobsPosted: many(jobs),
  applications: many(jobApplications),
  sentMessages: many(messages, { relationName: 'sentMessages' }),
  receivedMessages: many(messages, { relationName: 'receivedMessages' }),
  following: many(follows, { relationName: 'following' }),
  followers: many(follows, { relationName: 'followers' }),
  posts: many(posts),
  notifications: many(notifications),
  reviewsGiven: many(reviews, { relationName: 'reviewsGiven' }),
  reviewsReceived: many(reviews, { relationName: 'reviewsReceived' }),
}));

export const jobsRelations = relations(jobs, ({ one, many }) => ({
  employer: one(users, {
    fields: [jobs.employerId],
    references: [users.id],
  }),
  applications: many(jobApplications),
}));

export const jobApplicationsRelations = relations(jobApplications, ({ one }) => ({
  job: one(jobs, {
    fields: [jobApplications.jobId],
    references: [jobs.id],
  }),
  applicant: one(users, {
    fields: [jobApplications.applicantId],
    references: [users.id],
  }),
}));

export const conversationsRelations = relations(conversations, ({ one, many }) => ({
  participant1: one(users, {
    fields: [conversations.participant1Id],
    references: [users.id],
    relationName: 'participant1',
  }),
  participant2: one(users, {
    fields: [conversations.participant2Id],
    references: [users.id],
    relationName: 'participant2',
  }),
  messages: many(messages),
}));

export const messagesRelations = relations(messages, ({ one }) => ({
  conversation: one(conversations, {
    fields: [messages.conversationId],
    references: [conversations.id],
  }),
  sender: one(users, {
    fields: [messages.senderId],
    references: [users.id],
    relationName: 'sentMessages',
  }),
  receiver: one(users, {
    fields: [messages.receiverId],
    references: [users.id],
    relationName: 'receivedMessages',
  }),
}));

export const followsRelations = relations(follows, ({ one }) => ({
  follower: one(users, {
    fields: [follows.followerId],
    references: [users.id],
    relationName: 'following',
  }),
  followed: one(users, {
    fields: [follows.followedId],
    references: [users.id],
    relationName: 'followers',
  }),
}));

export const notificationsRelations = relations(notifications, ({ one }) => ({
  user: one(users, {
    fields: [notifications.userId],
    references: [users.id],
  }),
  actor: one(users, {
    fields: [notifications.actorId],
    references: [users.id],
  }),
}));

export const postsRelations = relations(posts, ({ one, many }) => ({
  user: one(users, {
    fields: [posts.userId],
    references: [users.id],
  }),
  relatedJob: one(jobs, {
    fields: [posts.relatedJobId],
    references: [jobs.id],
  }),
  likes: many(postLikes),
  comments: many(postComments),
}));

export const postLikesRelations = relations(postLikes, ({ one }) => ({
  user: one(users, {
    fields: [postLikes.userId],
    references: [users.id],
  }),
  post: one(posts, {
    fields: [postLikes.postId],
    references: [posts.id],
  }),
}));

export const postCommentsRelations = relations(postComments, ({ one }) => ({
  post: one(posts, {
    fields: [postComments.postId],
    references: [posts.id],
  }),
  user: one(users, {
    fields: [postComments.userId],
    references: [users.id],
  }),
}));

export const reviewsRelations = relations(reviews, ({ one }) => ({
  job: one(jobs, {
    fields: [reviews.jobId],
    references: [jobs.id],
  }),
  reviewer: one(users, {
    fields: [reviews.reviewerId],
    references: [users.id],
    relationName: 'reviewsGiven',
  }),
  reviewee: one(users, {
    fields: [reviews.revieweeId],
    references: [users.id],
    relationName: 'reviewsReceived',
  }),
}));

export const profilePicturesRelations = relations(profilePictures, ({ one }) => ({
  user: one(users, {
    fields: [profilePictures.userId],
    references: [users.id],
  }),
}));

export const uploadedFilesRelations = relations(uploadedFiles, ({ one }) => ({
  user: one(users, {
    fields: [uploadedFiles.userId],
    references: [users.id],
  }),
}));
