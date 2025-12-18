#!/usr/bin/env python3
"""
Demonstration of SIGTERM Context Filter

This script demonstrates how the logging filter adds helpful context
to SIGTERM messages in production logs.
"""

import logging
import sys
from io import StringIO


def demo_sigterm_filter():
    """Demonstrate the SIGTERM context filter in action."""
    
    # Load the gunicorn config from the script's directory
    import importlib.util
    import os
    
    # Get the directory containing this demo script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "gunicorn.conf.py")
    
    spec = importlib.util.spec_from_file_location(
        "gunicorn_conf", 
        config_path
    )
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    
    print("="*80)
    print("SIGTERM Context Filter - Live Demonstration")
    print("="*80)
    print()
    
    # Create a logger with our filter
    logger = logging.getLogger('demo.gunicorn.error')
    logger.setLevel(logging.ERROR)
    
    # Create handler with the SIGTERM filter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.ERROR)
    
    # Apply the filter
    sigterm_filter = config.SIGTERMContextFilter()
    handler.addFilter(sigterm_filter)
    
    # Format like Gunicorn
    formatter = logging.Formatter(
        '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    print("EXAMPLE 1: SIGTERM message (NORMAL during deployments)")
    print("-" * 80)
    logger.error("Worker (pid:57) was sent SIGTERM!")
    print()
    
    print()
    print("EXAMPLE 2: Regular worker message (no context added)")
    print("-" * 80)
    regular_logger = logging.getLogger('demo.regular')
    regular_logger.setLevel(logging.INFO)
    regular_handler = logging.StreamHandler(sys.stdout)
    regular_handler.setFormatter(formatter)
    regular_logger.addHandler(regular_handler)
    regular_logger.info("Worker booting with pid: 12345")
    print()
    
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print("What you just saw:")
    print()
    print("1. SIGTERM messages now include helpful context")
    print("   • Explains this is normal during deployments")
    print("   • Provides troubleshooting guidance")
    print("   • Reduces false alarms and confusion")
    print()
    print("2. Regular log messages remain unchanged")
    print("   • Filter only activates for SIGTERM messages")
    print("   • Zero impact on normal logging")
    print()
    print("This will appear in your production logs automatically!")
    print()


if __name__ == "__main__":
    demo_sigterm_filter()
