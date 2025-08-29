"""
Elite Dangerous Journal reader using EliteAPI
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class JournalReader:
    def __init__(self, callback: Callable[[dict], None], journal_path: Optional[Path] = None):
        """
        Initialize Journal reader
        
        Args:
            callback: Function to call with each event
            journal_path: Path to journal directory (optional, uses default if not specified)
        """
        self.callback = callback
        self.journal_path = journal_path or self._get_default_journal_path()
        self.running = False
        self._current_file = None
        
    def _get_default_journal_path(self) -> Path:
        """Get the default Elite Dangerous journal path"""
        # Default paths for different platforms
        if Path('/home').exists():  # Linux
            return Path.home() / '.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous'
        else:  # Windows
            return Path.home() / 'Saved Games/Frontier Developments/Elite Dangerous'
    
    async def start(self):
        """Start monitoring journal files"""
        self.running = True
        while self.running:
            try:
                # Find latest journal file
                journal_files = sorted(self.journal_path.glob('Journal.*.log'))
                if not journal_files:
                    logger.warning(f"No journal files found in {self.journal_path}")
                    await asyncio.sleep(1)
                    continue
                
                latest_file = journal_files[-1]
                
                # If this is a new file, start from beginning
                if self._current_file != latest_file:
                    self._current_file = latest_file
                    file_pos = 0
                    logger.info(f"Monitoring new journal file: {latest_file}")
                
                # Read new events
                with open(latest_file, 'r') as f:
                    f.seek(file_pos)
                    for line in f:
                        try:
                            event = json.loads(line)
                            self.callback(event)
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse journal entry: {line}")
                    file_pos = f.tell()
                
                await asyncio.sleep(0.1)  # Small delay between reads
                
            except Exception as e:
                logger.error(f"Error reading journal: {e}")
                await asyncio.sleep(1)
    
    def stop(self):
        """Stop monitoring journal files"""
        self.running = False
