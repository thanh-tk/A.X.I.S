"""
Sample hello world skill for AXIS
"""

def on_load():
    """Called when the skill is loaded"""
    return {
        "name": "Hello",
        "version": "0.1.0",
        "triggers": ["Docked"],
        "permissions": ["navigation"]
    }

def on_event(event):
    """Handle incoming events"""
    if event["event"] == "Docked":
        print(f"Hello! Docked at {event.get('StationName', 'unknown station')}")
