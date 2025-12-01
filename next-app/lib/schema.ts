import { pgTable, serial, varchar, text, boolean, timestamp, integer, jsonb } from "drizzle-orm/pg-core";

// Users table
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  email: varchar("email", { length: 255 }).unique().notNull(),
  hashedPassword: varchar("hashed_password", { length: 255 }).notNull(),
  firstName: varchar("first_name", { length: 100 }).notNull(),
  lastName: varchar("last_name", { length: 100 }).notNull(),
  role: varchar("role", { length: 50 }).default("job_seeker").notNull(),
  isAdmin: boolean("is_admin").default(false).notNull(),
  isActive: boolean("is_active").default(true).notNull(),
  bio: text("bio"),
  location: varchar("location", { length: 255 }),
  phone: varchar("phone", { length: 50 }),
  profilePicture: varchar("profile_picture", { length: 500 }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Jobs table
export const jobs = pgTable("jobs", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  company: varchar("company", { length: 255 }).notNull(),
  location: varchar("location", { length: 255 }).notNull(),
  jobType: varchar("job_type", { length: 50 }).notNull(),
  salaryMin: integer("salary_min"),
  salaryMax: integer("salary_max"),
  description: text("description").notNull(),
  requirements: jsonb("requirements"),
  isActive: boolean("is_active").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Posts table (social feed)
export const posts = pgTable("posts", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id).notNull(),
  content: text("content").notNull(),
  imageUrl: varchar("image_url", { length: 500 }),
  likes: integer("likes").default(0).notNull(),
  isActive: boolean("is_active").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Messages table
export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  senderId: integer("sender_id").references(() => users.id).notNull(),
  receiverId: integer("receiver_id").references(() => users.id).notNull(),
  content: text("content").notNull(),
  isRead: boolean("is_read").default(false).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Notifications table
export const notifications = pgTable("notifications", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id).notNull(),
  type: varchar("type", { length: 50 }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  message: text("message").notNull(),
  data: jsonb("data"),
  isRead: boolean("is_read").default(false).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Push subscriptions table
export const pushSubscriptions = pgTable("push_subscriptions", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id).notNull(),
  endpoint: varchar("endpoint", { length: 500 }).notNull(),
  p256dh: varchar("p256dh", { length: 255 }).notNull(),
  auth: varchar("auth", { length: 255 }).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Job applications table
export const applications = pgTable("applications", {
  id: serial("id").primaryKey(),
  jobId: integer("job_id").references(() => jobs.id).notNull(),
  userId: integer("user_id").references(() => users.id).notNull(),
  coverLetter: text("cover_letter"),
  resumeUrl: varchar("resume_url", { length: 500 }),
  status: varchar("status", { length: 50 }).default("pending").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Reviews table
export const reviews = pgTable("reviews", {
  id: serial("id").primaryKey(),
  reviewerId: integer("reviewer_id").references(() => users.id).notNull(),
  revieweeId: integer("reviewee_id").references(() => users.id).notNull(),
  rating: integer("rating").notNull(),
  comment: text("comment"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Export types
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type Job = typeof jobs.$inferSelect;
export type NewJob = typeof jobs.$inferInsert;
export type Post = typeof posts.$inferSelect;
export type NewPost = typeof posts.$inferInsert;
export type Message = typeof messages.$inferSelect;
export type NewMessage = typeof messages.$inferInsert;
export type Notification = typeof notifications.$inferSelect;
export type NewNotification = typeof notifications.$inferInsert;
export type PushSubscription = typeof pushSubscriptions.$inferSelect;
export type NewPushSubscription = typeof pushSubscriptions.$inferInsert;
export type Application = typeof applications.$inferSelect;
export type NewApplication = typeof applications.$inferInsert;
export type Review = typeof reviews.$inferSelect;
export type NewReview = typeof reviews.$inferInsert;
