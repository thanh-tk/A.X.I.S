"""
Finite State Machine for managing AXIS workflow states
"""

class State:
    def enter(self):
        """Called when entering the state"""
        pass
    
    def exit(self):
        """Called when exiting the state"""
        pass
    
    def update(self):
        """Called periodically while in this state"""
        pass

class FSM:
    def __init__(self):
        self.current_state = None
        self.states = {}
        
    def add_state(self, name, state):
        """Add a state to the FSM"""
        self.states[name] = state
        
    def change_state(self, new_state):
        """Change to a new state"""
        if self.current_state:
            self.current_state.exit()
        
        self.current_state = self.states.get(new_state)
        if self.current_state:
            self.current_state.enter()
            
    def update(self):
        """Update the current state"""
        if self.current_state:
            self.current_state.update()
