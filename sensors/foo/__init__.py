"""Foo sensor package exposing per-OS single-file implementations."""
from . import win, mac, linux

__all__ = ["win", "mac", "linux"]
