#!/usr/bin/env python3
"""
Initialize SQLite database for job tracking.

Usage:
  python3 init_db.py [--db-path /path/to/jobs.db]

Creates the 'jobs' table with proper schema and indexes.
If the database already exists, it will not be overwritten.
"""

import sqlite3
import os
import sys
import argparse
from datetime import datetime


def create_tables(cursor):
    """Create the jobs table and indexes."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            salary TEXT,
            link TEXT,
            platform TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            post_time TEXT,
            recruiter_active TEXT,
            match_score INTEGER,
            match_reason TEXT,
            notes TEXT,
            UNIQUE(company, title)
        )
    ''')

    # Indexes for common queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_seen ON jobs(last_seen)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON jobs(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_score ON jobs(match_score)')


def main():
    parser = argparse.ArgumentParser(description='Initialize job hunting database')
    parser.add_argument(
        '--db-path',
        default='jobs.db',
        help='Path to the SQLite database file (default: jobs.db)'
    )
    args = parser.parse_args()

    db_dir = os.path.dirname(os.path.abspath(args.db_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(args.db_path)
    cursor = conn.cursor()
    create_tables(cursor)
    conn.commit()

    # Verify
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    if cursor.fetchone():
        print(f"✅ Database initialized successfully: {args.db_path}")
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        print(f"\n📊 Table schema (jobs):")
        for col in columns:
            print(f"  - {col[1]:20s} {col[2]:10s} {'NOT NULL' if col[3] else 'NULL':>10s}")
    else:
        print("❌ Failed to create table")
        sys.exit(1)

    conn.close()


if __name__ == '__main__':
    main()
