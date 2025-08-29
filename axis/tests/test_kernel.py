"""
Basic tests for AXIS kernel functionality
"""
import pytest
from axis.src.core.kernel import Kernel

def test_kernel_init():
    """Test basic kernel initialization"""
    kernel = Kernel()
    assert not kernel.running
    assert kernel.watchdog_timer == 3

def test_kernel_start_stop():
    """Test kernel start/stop functionality"""
    kernel = Kernel()
    kernel.start()
    assert kernel.running
    
    kernel.stop()
    assert not kernel.running
