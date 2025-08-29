#!/usr/bin/env python3
"""
Simple CLI tool to monitor Elite Dangerous journal events
"""
import asyncio
import logging
from pathlib import Path

from axis.src.input import JournalReader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_event(event: dict):
    """Print formatted journal events"""
    event_type = event.get('event', 'Unknown')
    timestamp = event.get('timestamp', 'No time')
    print(f"\n[{timestamp}] {event_type}")
    
    # Print other event details
    for key, value in event.items():
        if key not in ['event', 'timestamp']:
            print(f"  {key}: {value}")

async def main():
    """Main entry point"""
    print("AXIS Journal Monitor")
    print("------------------")
    
    # Create and start journal reader
    reader = JournalReader(print_event)
    print(f"Monitoring journal directory: {reader.journal_path}")
    
    try:
        await reader.start()
    except KeyboardInterrupt:
        print("\nStopping journal monitor...")
        reader.stop()

if __name__ == '__main__':
    asyncio.run(main())
