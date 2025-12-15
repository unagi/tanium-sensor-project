"""Foo sensor package exposing per-OS single-file implementations."""

from . import linux, mac, win

__all__ = ["win", "mac", "linux"]
