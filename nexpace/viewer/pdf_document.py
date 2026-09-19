from pathlib import Path



class PdfDocumentLoader:
    """Load PDF documents from disk."""

    @staticmethod
    def read_bytes(path):
        """Read a PDF file and return its raw bytes."""
        
        return Path(path).read_bytes()