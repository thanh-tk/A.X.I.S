"""
AXIS Kernel - Core system coordinator
Handles state management and coordinates between input, planning, and output layers
"""

class Kernel:
    def __init__(self):
        self.running = False
        self.watchdog_timer = 3  # seconds
        self._skills = {}

    def start(self):
        """Initialize and start the AXIS kernel"""
        self.running = True
        # TODO: Initialize components
        # - Load skills
        # - Start watchdog
        # - Initialize FSM
        
    def stop(self):
        """Gracefully shutdown the kernel"""
        self.running = False
        # TODO: Cleanup resources

    def load_skills(self):
        """Load skills from the skills directory"""
        pass  # TODO: Implement skill loading

    def handle_event(self, event):
        """Process incoming events from Elite Dangerous"""
        pass  # TODO: Implement event handling
