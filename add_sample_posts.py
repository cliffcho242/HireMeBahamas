#!/usr/bin/env python3
"""Add sample posts to the database"""

import sqlite3
import bcrypt

def add_sample_data():
    # Connect to database
    conn = sqlite3.connect('hirebahamas.db')
    cursor = conn.cursor()

    # Create sample users if they don't exist
    sample_users = [
        ('john@hirebahamas.com', 'John', 'Doe', 'freelancer'),
        ('sarah@hirebahamas.com', 'Sarah', 'Smith', 'employer'),
        ('mike@hirebahamas.com', 'Mike', 'Johnson', 'freelancer'),
        ('lisa@hirebahamas.com', 'Lisa', 'Brown', 'recruiter')
    ]

    for email, first_name, last_name, user_type in sample_users:
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name, user_type))
            print(f'Created user: {first_name} {last_name}')

    # Create sample posts
    sample_posts = [
        (1, 'Just finished an amazing web development project in Nassau! The Bahamas tech scene is growing fast. Looking for more opportunities! #BahamasTech #WebDev'),
        (2, 'Hiring React developers for our new e-commerce platform. Remote work available. DM for details! #HireBahamas #ReactJS'),
        (3, 'Completed my first freelance gig through HireBahamas. Such a great platform for connecting talent with opportunities in paradise! 🌴'),
        (4, 'Looking for talented graphic designers for branding projects. Nassau-based preferred but open to remote. #GraphicDesign #Bahamas'),
        (1, 'Beautiful day in Freeport! Working on some exciting mobile app projects. The Caribbean lifestyle really inspires creativity. ☀️'),
        (3, 'Just landed a new contract for mobile app development. Thanks to the HireBahamas community for the support! #MobileDev #Success'),
        (2, 'Our company is expanding and we need more talented developers. Join our team in Grand Bahama! Great benefits and work-life balance.'),
        (4, 'Excited to announce new job openings for marketing specialists. Perfect for those who love the island lifestyle! #Marketing #BahamasJobs')
    ]

    for user_id, content in sample_posts:
        cursor.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))
        print(f'Created post by user {user_id}')

    conn.commit()
    conn.close()
    print('Sample data created successfully!')

if __name__ == '__main__':
    add_sample_data()