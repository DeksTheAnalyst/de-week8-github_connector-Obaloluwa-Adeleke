# github_connector/__init__.py
"""
GitHub Connector - A resilient client library for the GitHub API.
"""
from .client import GitHubClient
from .custom_exceptions import (
    GitHubAPIError,
    ResourceNotFound,
    RateLimitExceeded,
    NetworkError,
    AuthenticationError
)

__all__ = [
    'GitHubClient',
    'GitHubAPIError',
    'ResourceNotFound',
    'RateLimitExceeded',
    'NetworkError',
    'AuthenticationError'
]

__version__ = '0.1.0'