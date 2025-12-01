import { NextRequest, NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { sql } from "@vercel/postgres";
import { z } from "zod";

// Serverless runtime for registration (needs more CPU for bcrypt)
export const runtime = "nodejs";

// Registration request schema
const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  role: z.enum(["job_seeker", "employer"]).default("job_seeker"),
});

export async function POST(request: NextRequest) {
  const startTime = Date.now();

  try {
    // Parse request body
    const body = await request.json();
    const result = registerSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          message: result.error.errors[0]?.message || "Invalid input",
          errors: result.error.errors,
        },
        { status: 400 }
      );
    }

    const { email, password, firstName, lastName, role } = result.data;
    const normalizedEmail = email.toLowerCase().trim();

    // Check if user already exists
    const { rows: existingUsers } = await sql`
      SELECT id FROM users WHERE email = ${normalizedEmail} LIMIT 1
    `;

    if (existingUsers.length > 0) {
      return NextResponse.json(
        {
          success: false,
          message: "An account with this email already exists",
        },
        { status: 409 }
      );
    }

    // Hash password (bcrypt with cost factor 12)
    const hashedPassword = await bcrypt.hash(password, 12);

    // Insert new user
    const { rows } = await sql`
      INSERT INTO users (
        email,
        hashed_password,
        first_name,
        last_name,
        role,
        is_admin,
        is_active,
        created_at,
        updated_at
      )
      VALUES (
        ${normalizedEmail},
        ${hashedPassword},
        ${firstName},
        ${lastName},
        ${role},
        false,
        true,
        NOW(),
        NOW()
      )
      RETURNING id, email, first_name, last_name, role, is_admin
    `;

    const user = rows[0];
    const duration = Date.now() - startTime;

    return NextResponse.json(
      {
        success: true,
        message: "Registration successful! Please log in.",
        user: {
          id: user.id,
          email: user.email,
          name: `${user.first_name} ${user.last_name}`,
          role: user.role,
        },
        performance: {
          durationMs: duration,
        },
      },
      {
        status: 201,
        headers: {
          "X-Response-Time": `${duration}ms`,
        },
      }
    );
  } catch (error) {
    console.error("Registration error:", error);
    return NextResponse.json(
      {
        success: false,
        message: "An error occurred during registration",
      },
      { status: 500 }
    );
  }
}

// Preflight for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
