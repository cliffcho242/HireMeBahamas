import hashlib
import random
import sqlite3
from datetime import datetime, timedelta


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Connect to database
conn = sqlite3.connect("hirebahamas.db")
cursor = conn.cursor()

# Sample users
users = [
    ("admin@hirebahamas.com", "admin123", "Admin", "User", "admin", "Nassau, Bahamas"),
    (
        "john@hirebahamas.com",
        "password123",
        "John",
        "Doe",
        "job_seeker",
        "Freeport, Bahamas",
    ),
    (
        "sarah@hirebahamas.com",
        "password123",
        "Sarah",
        "Wilson",
        "employer",
        "Nassau, Bahamas",
    ),
    (
        "mike@hirebahamas.com",
        "password123",
        "Mike",
        "Johnson",
        "job_seeker",
        "Nassau, Bahamas",
    ),
    (
        "emma@hirebahamas.com",
        "password123",
        "Emma",
        "Davis",
        "employer",
        "Freeport, Bahamas",
    ),
]

# Insert users
for email, password, first_name, last_name, user_type, location in users:
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (email, password_hash, first_name, last_name, user_type, location, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            email,
            hash_password(password),
            first_name,
            last_name,
            user_type,
            location,
            datetime.now(),
        ),
    )

# Sample posts
posts = [
    (
        "Just landed an amazing job at a tech company in Nassau! So excited for this new chapter. #CareerGoals #BahamasTech",
        2,
    ),
    (
        "Looking for talented developers to join our growing team. Great benefits, competitive salary, and beautiful office overlooking the ocean. DM me for details! 💼🌊",
        3,
    ),
    (
        "Coffee and coding - the perfect Monday morning combo. What's everyone working on this week? ☕💻",
        2,
    ),
    (
        "Excited to announce our new office in Freeport! We're hiring for multiple positions. Check out our careers page for more info. #JobOpening #Bahamas",
        5,
    ),
    (
        "Just finished an amazing networking event at the Bahamas International Business Centre. Met so many talented professionals! 🤝",
        4,
    ),
    (
        "Tips for job seekers: Always customize your resume for each application. It shows you care about the role and company. What are your best interview tips? 💡",
        3,
    ),
    (
        "Beautiful sunset from my office window today. Working in paradise doesn't get much better than this! 🌅🏢",
        2,
    ),
    (
        "We're expanding our marketing team! Looking for creative minds who love the Bahamas lifestyle. Remote work options available. 📈🏝️",
        5,
    ),
]

# Insert posts
for content, user_id in posts:
    created_at = datetime.now() - timedelta(
        days=random.randint(0, 7), hours=random.randint(0, 23)
    )
    cursor.execute(
        """
        INSERT INTO posts (content, user_id, created_at)
        VALUES (?, ?, ?)
    """,
        (content, user_id, created_at),
    )

# Add some likes
cursor.execute("SELECT id FROM posts")
post_ids = [row[0] for row in cursor.fetchall()]

for post_id in post_ids:
    # Random likes (1-5 per post)
    num_likes = random.randint(1, 5)
    for _ in range(num_likes):
        user_id = random.randint(1, 5)
        cursor.execute(
            """
            INSERT OR IGNORE INTO post_likes (post_id, user_id, created_at)
            VALUES (?, ?, ?)
        """,
            (post_id, user_id, datetime.now()),
        )

conn.commit()
conn.close()
print("Sample data seeded successfully!")
