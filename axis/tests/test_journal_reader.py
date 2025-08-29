"""
Tests for Elite Dangerous journal reader
"""
import asyncio
import json
from pathlib import Path
import pytest
from axis.src.input import JournalReader

@pytest.fixture
def temp_journal(tmp_path):
    """Create a temporary journal file for testing"""
    journal_path = tmp_path / "Journal.test.log"
    return journal_path

@pytest.fixture
def sample_events():
    """Sample journal events for testing"""
    return [
        {"timestamp": "2025-08-29T10:00:00Z", "event": "Startup", "game_version": "4.0.0.1234"},
        {"timestamp": "2025-08-29T10:01:00Z", "event": "Location", "StarSystem": "Sol"},
        {"timestamp": "2025-08-29T10:02:00Z", "event": "FSDJump", "StarSystem": "Alpha Centauri"}
    ]

@pytest.mark.asyncio
async def test_journal_reader(temp_journal, sample_events):
    """Test basic journal reading functionality"""
    received_events = []
    
    def callback(event):
        received_events.append(event)
    
    # Create reader with test path
    reader = JournalReader(callback, journal_path=temp_journal.parent)
    
    # Write test events to journal
    with open(temp_journal, 'w') as f:
        for event in sample_events:
            f.write(json.dumps(event) + '\n')
    
    # Start reader in background
    read_task = asyncio.create_task(reader.start())
    
    # Wait briefly for events to be processed
    await asyncio.sleep(0.5)
    
    # Stop reader
    reader.stop()
    await read_task
    
    # Verify received events
    assert len(received_events) == len(sample_events)
    for expected, received in zip(sample_events, received_events):
        assert received == expected
