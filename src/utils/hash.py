"""
Utilidades de hashing para detectar cambios en PDFs.
"""

import hashlib


def calculate_pdf_hash(content: bytes) -> str:
    """
    Calcula el hash SHA-256 del contenido binario de un PDF.

    Se usa para detectar si un PDF ha cambiado desde la última vez
    que se procesó.

    Args:
        content: Contenido binario del PDF

    Returns:
        Hash SHA-256 en formato hexadecimal
    """
    return hashlib.sha256(content).hexdigest()


def calculate_message_hash(message: str) -> str:
    """
    Calcula hash de un mensaje para evitar notificaciones duplicadas.

    Args:
        message: Contenido del mensaje

    Returns:
        Hash SHA-256 del mensaje
    """
    return hashlib.sha256(message.encode("utf-8")).hexdigest()
