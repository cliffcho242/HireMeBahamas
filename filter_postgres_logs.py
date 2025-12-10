#!/usr/bin/env python3
"""
PostgreSQL Log Filter and Categorizer
======================================

This script filters and properly categorizes PostgreSQL log messages,
correcting the issue where Railway's managed PostgreSQL logs informational
messages with "error" level.

Usage:
    # Filter logs from stdin
    cat logs.json | python filter_postgres_logs.py
    
    # Filter logs from a file
    python filter_postgres_logs.py < logs.json
    
    # Filter and suppress benign messages
    python filter_postgres_logs.py --suppress-benign < logs.json
    
    # Show statistics
    python filter_postgres_logs.py --stats < logs.json
"""

import argparse
import json
import re
import sys
from typing import Dict, Optional


# PostgreSQL informational messages that are safe to ignore or downgrade
BENIGN_PATTERNS = [
    r"database system is ready to accept connections",
    r"database system was shut down at",
    r"database system is shut down",
    r"checkpoint starting:",
    r"checkpoint complete:",
    r"autovacuum launcher started",
    r"autovacuum launcher shutting down",
    r"received smart shutdown request",
    r"received fast shutdown request",
    r"shutting down",
    r"starting.*PostgreSQL",
    r"listening on",
    r"LOG:\s+duration:",  # Query duration logs
    r"LOG:\s+statement:",  # Statement logs
]

# Compile patterns for efficiency
BENIGN_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in BENIGN_PATTERNS]


def is_benign_message(message: str) -> bool:
    """
    Check if a PostgreSQL message is benign (informational, not an error).
    
    Args:
        message: The log message to check
        
    Returns:
        True if the message is benign, False otherwise
    """
    for pattern in BENIGN_REGEX:
        if pattern.search(message):
            return True
    return False


def extract_postgres_log_level(message: str) -> Optional[str]:
    """
    Extract the actual PostgreSQL log level from a message.
    
    PostgreSQL log format: "timestamp [pid] LEVEL: message"
    Example: "2025-12-10 02:55:37.131 UTC [6] LOG:  database system is ready"
    
    Args:
        message: The log message
        
    Returns:
        The PostgreSQL log level (LOG, WARNING, ERROR, FATAL, PANIC) or None
    """
    # Match PostgreSQL log format: [pid] LEVEL: message
    match = re.search(r'\[\d+\]\s+(LOG|WARNING|ERROR|FATAL|PANIC):', message)
    if match:
        return match.group(1)
    return None


def correct_log_level(message: str, current_level: str) -> str:
    """
    Correct the log level based on PostgreSQL's actual log level.
    
    Args:
        message: The log message
        current_level: The current (possibly incorrect) log level
        
    Returns:
        The corrected log level
    """
    postgres_level = extract_postgres_log_level(message)
    
    if not postgres_level:
        # No PostgreSQL level found, keep current
        return current_level
    
    # Map PostgreSQL levels to standard log levels
    level_mapping = {
        'LOG': 'info',
        'WARNING': 'warning',
        'ERROR': 'error',
        'FATAL': 'error',
        'PANIC': 'error',
    }
    
    return level_mapping.get(postgres_level, current_level)


def process_log_entry(entry: Dict, suppress_benign: bool = False, 
                     correct_levels: bool = True) -> Optional[Dict]:
    """
    Process a single log entry.
    
    Args:
        entry: The log entry dictionary
        suppress_benign: If True, return None for benign messages
        correct_levels: If True, correct log levels
        
    Returns:
        Processed log entry or None if suppressed
    """
    message = entry.get('message', '')
    
    # Check if benign
    if is_benign_message(message):
        if suppress_benign:
            return None
        
        # Mark as benign in attributes
        if 'attributes' not in entry:
            entry['attributes'] = {}
        entry['attributes']['benign'] = True
    
    # Correct log level if needed
    if correct_levels and 'attributes' in entry and 'level' in entry['attributes']:
        current_level = entry['attributes']['level']
        corrected_level = correct_log_level(message, current_level)
        
        if corrected_level != current_level:
            entry['attributes']['original_level'] = current_level
            entry['attributes']['level'] = corrected_level
    
    return entry


def main():
    """Main entry point."""
    epilog_text = """
Examples:
    # Filter logs from stdin
    cat logs.json | python filter_postgres_logs.py
    
    # Filter logs from a file
    python filter_postgres_logs.py < logs.json
    
    # Filter and suppress benign messages
    python filter_postgres_logs.py --suppress-benign < logs.json
    
    # Show statistics
    python filter_postgres_logs.py --stats < logs.json
"""
    parser = argparse.ArgumentParser(
        description='Filter and categorize PostgreSQL logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_text
    )
    parser.add_argument(
        '--suppress-benign',
        action='store_true',
        help='Suppress benign informational messages'
    )
    parser.add_argument(
        '--no-correct-levels',
        action='store_true',
        help='Do not correct log levels'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics instead of filtered logs'
    )
    
    args = parser.parse_args()
    
    stats = {
        'total': 0,
        'benign': 0,
        'corrected': 0,
        'errors': 0,
        'warnings': 0,
        'info': 0,
    }
    
    # Process input line by line
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            # Try to parse as JSON
            entry = json.loads(line)
            stats['total'] += 1
            
            # Process the entry
            processed = process_log_entry(
                entry,
                suppress_benign=args.suppress_benign,
                correct_levels=not args.no_correct_levels
            )
            
            # Update statistics
            if processed:
                if processed.get('attributes', {}).get('benign'):
                    stats['benign'] += 1
                
                if 'original_level' in processed.get('attributes', {}):
                    stats['corrected'] += 1
                
                level = processed.get('attributes', {}).get('level', '').lower()
                if level == 'error':
                    stats['errors'] += 1
                elif level == 'warning':
                    stats['warnings'] += 1
                elif level == 'info':
                    stats['info'] += 1
                
                # Output processed entry
                if not args.stats:
                    print(json.dumps(processed))
            else:
                # Entry was suppressed
                stats['benign'] += 1
        
        except json.JSONDecodeError:
            # Not JSON, just echo the line
            if not args.stats:
                print(line)
        except Exception as e:
            print(f"Error processing line: {e}", file=sys.stderr)
            if not args.stats:
                print(line)
    
    # Print statistics if requested
    if args.stats:
        print("\nPostgreSQL Log Statistics", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print(f"Total entries:        {stats['total']}", file=sys.stderr)
        print(f"Benign messages:      {stats['benign']}", file=sys.stderr)
        print(f"Corrected levels:     {stats['corrected']}", file=sys.stderr)
        print(f"Errors:              {stats['errors']}", file=sys.stderr)
        print(f"Warnings:            {stats['warnings']}", file=sys.stderr)
        print(f"Info:                {stats['info']}", file=sys.stderr)
        print("=" * 50, file=sys.stderr)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
