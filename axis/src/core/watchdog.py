"""
Watchdog timer for safety monitoring
"""
import time
import threading

class Watchdog:
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self._timer = None
        self._last_pet = 0
        
    def start(self):
        """Start the watchdog timer"""
        self._last_pet = time.time()
        self._start_timer()
        
    def stop(self):
        """Stop the watchdog timer"""
        if self._timer:
            self._timer.cancel()
            
    def pet(self):
        """Reset the watchdog timer"""
        self._last_pet = time.time()
        
    def _start_timer(self):
        """Internal method to start/restart the timer"""
        if self._timer:
            self._timer.cancel()
            
        self._timer = threading.Timer(self.timeout, self._on_timeout)
        self._timer.start()
        
    def _on_timeout(self):
        """Called when watchdog times out"""
        elapsed = time.time() - self._last_pet
        if elapsed >= self.timeout:
            self.callback()  # Execute timeout callback
