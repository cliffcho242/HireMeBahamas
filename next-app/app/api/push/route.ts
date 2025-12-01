import { NextRequest, NextResponse } from "next/server";
import { sql } from "@vercel/postgres";
import { verifyAuth } from "@/lib/auth";

// Serverless runtime for push
export const runtime = "nodejs";

/**
 * POST /api/push/subscribe
 * Subscribe to push notifications
 */
export async function POST(request: NextRequest) {
  try {
    // Verify authentication
    const auth = await verifyAuth(request);
    if (!auth.success) {
      return NextResponse.json(
        { success: false, message: auth.message },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { endpoint, keys } = body;

    if (!endpoint || !keys?.p256dh || !keys?.auth) {
      return NextResponse.json(
        { success: false, message: "Invalid subscription data" },
        { status: 400 }
      );
    }

    // Check if subscription already exists
    const { rows: existing } = await sql`
      SELECT id FROM push_subscriptions 
      WHERE user_id = ${auth.userId} AND endpoint = ${endpoint}
    `;

    if (existing.length > 0) {
      // Update existing subscription
      await sql`
        UPDATE push_subscriptions 
        SET p256dh = ${keys.p256dh}, auth = ${keys.auth}, updated_at = NOW()
        WHERE user_id = ${auth.userId} AND endpoint = ${endpoint}
      `;
    } else {
      // Insert new subscription
      await sql`
        INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, created_at)
        VALUES (${auth.userId}, ${endpoint}, ${keys.p256dh}, ${keys.auth}, NOW())
      `;
    }

    return NextResponse.json({
      success: true,
      message: "Push subscription saved",
    });
  } catch (error) {
    console.error("Push subscribe error:", error);
    return NextResponse.json(
      { success: false, message: "Failed to save subscription" },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/push/subscribe
 * Unsubscribe from push notifications
 */
export async function DELETE(request: NextRequest) {
  try {
    const auth = await verifyAuth(request);
    if (!auth.success) {
      return NextResponse.json(
        { success: false, message: auth.message },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { endpoint } = body;

    if (!endpoint) {
      return NextResponse.json(
        { success: false, message: "Endpoint required" },
        { status: 400 }
      );
    }

    await sql`
      DELETE FROM push_subscriptions 
      WHERE user_id = ${auth.userId} AND endpoint = ${endpoint}
    `;

    return NextResponse.json({
      success: true,
      message: "Unsubscribed from push notifications",
    });
  } catch (error) {
    console.error("Push unsubscribe error:", error);
    return NextResponse.json(
      { success: false, message: "Failed to unsubscribe" },
      { status: 500 }
    );
  }
}
