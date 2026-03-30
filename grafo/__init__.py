"""
Lazy exports for the `grafo` package.

Avoid importing heavy optional dependencies (for example geopy/supabase)
at package import time.
"""

__all__ = [
    "geocode_orders",
    "get_santiago_graph",
    "calculate_routing_for_day",
    "execute_vrp_pipeline",
]


def geocode_orders(*args, **kwargs):
    from .geocoder import geocode_orders as _geocode_orders

    return _geocode_orders(*args, **kwargs)


def get_santiago_graph(*args, **kwargs):
    from .network_builder import get_santiago_graph as _get_santiago_graph

    return _get_santiago_graph(*args, **kwargs)


def calculate_routing_for_day(*args, **kwargs):
    from .routing import calculate_routing_for_day as _calculate_routing_for_day

    return _calculate_routing_for_day(*args, **kwargs)


def execute_vrp_pipeline(*args, **kwargs):
    from .main import execute_vrp_pipeline as _execute_vrp_pipeline

    return _execute_vrp_pipeline(*args, **kwargs)
