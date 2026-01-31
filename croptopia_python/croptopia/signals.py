"""
Signal System - Replaces Godot's signal/connect pattern
Enables loose coupling between all systems via observer pattern
"""

from typing import Callable, Dict, List, Any


class SignalEmitter:
    """
    Base class that provides Godot-like signal capabilities to any class.
    
    Usage:
        class MySystem(SignalEmitter):
            def __init__(self):
                super().__init__()
        
        obj = MySystem()
        obj.on_signal("event_name", callback_function)
        obj.emit_signal("event_name", arg1, arg2)
    """
    
    def __init__(self):
        """Initialize signal handler dictionary"""
        self._signal_handlers: Dict[str, List[Callable]] = {}
    
    def on_signal(self, signal_name: str, callback: Callable) -> None:
        """
        Connect a callback to a signal (replaces Godot's .connect())
        
        Args:
            signal_name: Name of the signal to connect to
            callback: Function to call when signal is emitted
        """
        if signal_name not in self._signal_handlers:
            self._signal_handlers[signal_name] = []
        
        self._signal_handlers[signal_name].append(callback)
    
    def disconnect_signal(self, signal_name: str, callback: Callable) -> None:
        """
        Disconnect a callback from a signal
        
        Args:
            signal_name: Name of the signal
            callback: Function to disconnect
        """
        if signal_name in self._signal_handlers:
            if callback in self._signal_handlers[signal_name]:
                self._signal_handlers[signal_name].remove(callback)
    
    def emit_signal(self, signal_name: str, *args, **kwargs) -> None:
        """
        Fire a signal to all connected handlers (replaces Godot's .emit_signal())
        
        Args:
            signal_name: Name of the signal to emit
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        if signal_name in self._signal_handlers:
            for callback in self._signal_handlers[signal_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in signal handler for '{signal_name}': {e}")
    
    def has_signal(self, signal_name: str) -> bool:
        """Check if a signal has any connected handlers"""
        return signal_name in self._signal_handlers and len(self._signal_handlers[signal_name]) > 0
    
    def clear_signals(self, signal_name: str = None) -> None:
        """
        Clear all handlers for a signal (or all signals if signal_name is None)
        
        Args:
            signal_name: Specific signal to clear, or None for all
        """
        if signal_name:
            if signal_name in self._signal_handlers:
                self._signal_handlers[signal_name].clear()
        else:
            self._signal_handlers.clear()


class EventBus(SignalEmitter):
    """
    Global event bus for system-wide signals that don't belong to specific objects.
    
    Usage:
        event_bus = EventBus()
        event_bus.on_signal("game_paused", on_pause_handler)
        event_bus.emit_signal("game_paused", pause_reason="user_input")
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - ensure only one EventBus exists"""
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize singleton instance only once"""
        if self.__initialized:
            return
        super().__init__()
        self.__initialized = True
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Global event bus instance
event_bus = EventBus.get_instance()
