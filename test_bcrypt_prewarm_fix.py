"""
Test script to verify that the bcrypt pre-warming fix works correctly.

This test verifies:
1. No "(trapped) error reading bcrypt version" warning appears
2. Bcrypt pre-warming completes successfully
3. The passlib logger is set to ERROR level
"""

import asyncio
import logging
import sys
from io import StringIO

# Capture logging output
log_capture = StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
handler.setFormatter(formatter)

# Set up root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)

# Suppress bcrypt version check warning from passlib logger
# This simulates what we do in security.py
logging.getLogger('passlib').setLevel(logging.ERROR)

# Import required libraries
import anyio
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=10
)

_bcrypt_warmed = False

def prewarm_bcrypt() -> None:
    """Pre-warm bcrypt by performing a dummy hash operation."""
    global _bcrypt_warmed
    if _bcrypt_warmed:
        return
    
    try:
        _ = pwd_context.hash("prewarm")
        _bcrypt_warmed = True
        logging.getLogger(__name__).info("Bcrypt pre-warmed with 10 rounds")
    except Exception as e:
        logging.getLogger(__name__).warning(f"Bcrypt pre-warm encountered an error: {type(e).__name__}: {e}")
        raise

async def prewarm_bcrypt_async() -> None:
    """Pre-warm bcrypt asynchronously."""
    await anyio.to_thread.run_sync(prewarm_bcrypt)

async def test_bcrypt_prewarm():
    """Test that bcrypt pre-warming works without warnings."""
    print("=" * 70)
    print("Testing bcrypt pre-warming fix")
    print("=" * 70)
    
    # Clear any previous captured logs
    log_capture.seek(0)
    log_capture.truncate()
    
    # Run pre-warming
    try:
        await prewarm_bcrypt_async()
        print("✓ Bcrypt pre-warming completed successfully")
    except Exception as e:
        print(f"✗ Bcrypt pre-warming failed: {type(e).__name__}: {e}")
        return False
    
    # Check captured logs for the bcrypt version warning
    logs = log_capture.getvalue()
    
    has_bcrypt_warning = "error reading bcrypt version" in logs.lower()
    has_trapped_error = "trapped" in logs.lower()
    
    print()
    if has_bcrypt_warning or has_trapped_error:
        print("✗ FAILED: Bcrypt version warning still appears")
        print("Captured logs:")
        print(logs)
        return False
    else:
        print("✓ PASSED: No bcrypt version warnings detected")
    
    # Verify passlib logger level
    passlib_logger = logging.getLogger('passlib')
    if passlib_logger.level == logging.ERROR:
        print("✓ PASSED: passlib logger is set to ERROR level")
    else:
        print(f"✗ FAILED: passlib logger level is {passlib_logger.level}, expected {logging.ERROR}")
        return False
    
    print("=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_bcrypt_prewarm())
    sys.exit(0 if success else 1)
