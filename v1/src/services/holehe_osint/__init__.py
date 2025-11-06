"""
IRIS v6.0 - Holehe OSINT Module
Email verification and OSINT using holehe
"""

from .service import HoleheService, HoleheException, HoleheNotInstalledException
from .models import (
    HoleheResult,
    EmailCheckRequest,
    EmailCheckResponse,
    EmailProfile,
    ServiceCategory,
    AvailableModule,
    BulkEmailCheckRequest,
    BulkEmailCheckResponse
)

__all__ = [
    'HoleheService',
    'HoleheException',
    'HoleheNotInstalledException',
    'HoleheResult',
    'EmailCheckRequest',
    'EmailCheckResponse',
    'EmailProfile',
    'ServiceCategory',
    'AvailableModule',
    'BulkEmailCheckRequest',
    'BulkEmailCheckResponse'
]

__version__ = '1.0.0'
