"""Additional PetKit integration Exceptions."""

from typing import Any

class PetKitBluetoothError(Exception):
    """Bluetooth issue from PetKit api."""

    def __init__(self, *args: Any) -> None:
        """Initialize the exception."""
        Exception.__init__(self, *args)