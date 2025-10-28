#!/usr/bin/env python3
"""
HireMe Availability Automation Manager
Automatically manages user availability for HireMe feature with robust error handling
"""

import logging
import os
import random
import sqlite3
import sys
import time
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    filename="hireme_automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class HireMeAutomation:
    def __init__(self, db_path="hirebahamas.db", interval_minutes=5):
        self.db_path = db_path
        self.interval_seconds = interval_minutes * 60
        self.running = True

        # Ensure log file exists
        if not os.path.exists("hireme_automation.log"):
            open("hireme_automation.log", "w").close()

        logging.info("HireMe Automation Manager initialized")
        print("🚀 HireMe Availability Automation Manager Started")
        print(f"📊 Update interval: {interval_minutes} minutes")
        print(f"📁 Database: {db_path}")
        print(f"📝 Log file: hireme_automation.log")
        print("-" * 50)

    def check_database_connection(self):
        """Check if database is accessible"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False

    def update_user_availability(self):
        """Update user availability with random status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all users
            cursor.execute("SELECT id, email, first_name, last_name FROM users")
            users = cursor.fetchall()

            if not users:
                logging.warning("No users found in database")
                print("⚠️  No users found in database")
                return

            updated_count = 0
            available_count = 0

            print(f"\n🔄 Updating availability for {len(users)} users...")

            for user in users:
                user_id, email, first_name, last_name = user

                # 70% chance of being available (more realistic)
                available = random.choice([True, True, True, False, True, True, True])

                cursor.execute(
                    "UPDATE users SET is_available_for_hire = ? WHERE id = ?",
                    (available, user_id),
                )

                status = "AVAILABLE" if available else "NOT AVAILABLE"
                status_icon = "✅" if available else "❌"

                print(f"  {status_icon} {first_name} {last_name} ({email}): {status}")

                if available:
                    available_count += 1

                updated_count += 1

            conn.commit()
            conn.close()

            logging.info(
                f"Updated {updated_count} users, {available_count} now available"
            )
            print(
                f"\n✅ Updated {updated_count} users - {available_count} now available for hire"
            )

        except Exception as e:
            logging.error(f"Error updating availability: {e}")
            print(f"❌ Error updating availability: {e}")

    def run_automation(self):
        """Main automation loop"""
        cycle_count = 0

        while self.running:
            cycle_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")

            print(f"\n🔄 Cycle #{cycle_count} - {current_time}")
            logging.info(f"Starting automation cycle #{cycle_count}")

            # Check database connection
            if not self.check_database_connection():
                print("❌ Database connection failed - waiting...")
                time.sleep(30)  # Wait 30 seconds before retry
                continue

            # Update availability
            self.update_user_availability()

            # Log completion
            next_update = datetime.now() + timedelta(seconds=self.interval_seconds)
            next_time = next_update.strftime("%H:%M:%S")
            print(f"⏰ Next update at {next_time}")
            logging.info(
                f"Cycle #{cycle_count} completed, next update in {self.interval_seconds//60} minutes"
            )

            # Wait for next cycle
            time.sleep(self.interval_seconds)

    def stop(self):
        """Stop the automation"""
        self.running = False
        logging.info("HireMe Automation stopped")
        print("\n🛑 HireMe Automation stopped")


def main():
    """Main entry point"""
    print("🎯 HireMe Availability Automation Manager")
    print("=" * 50)

    # Check if database exists
    if not os.path.exists("hirebahamas.db"):
        print("❌ Database file 'hirebahamas.db' not found!")
        print("   Please run the backend first to create the database.")
        sys.exit(1)

    # Create automation manager
    automation = HireMeAutomation(interval_minutes=5)

    try:
        # Run initial update
        print("\n🚀 Running initial availability update...")
        automation.update_user_availability()

        # Start automation loop
        automation.run_automation()

    except KeyboardInterrupt:
        print("\n⏹️  Received interrupt signal...")
        automation.stop()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        automation.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
