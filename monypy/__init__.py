from .doc import Doc
from .exceptions import DocumentDoesNotExistError, DocumentInitDataError
from .manager import Manager

__version__ = '1.0.2'

__all__ = (
    'Doc',
    'Manager',
    'DocumentInitDataError',
    'DocumentDoesNotExistError',
)
