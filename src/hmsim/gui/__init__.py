"""HM Simulator GUI Module."""

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False
    Gtk = None

__all__ = ['Gtk', 'GTK_AVAILABLE']
