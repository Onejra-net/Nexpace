"""
PDF document loading.

Responsible for:
- Reading PDF files from disk
- Providing raw document bytes to the PDF viewer
"""

from pathlib import Path


class PdfDocumentLoader:
    """
    Handle PDF document reading from the filesystem.
    """

    @staticmethod
    def read_bytes(path):
        """
        Read a PDF file and return its raw binary content.
        """

        return Path(path).read_bytes()
