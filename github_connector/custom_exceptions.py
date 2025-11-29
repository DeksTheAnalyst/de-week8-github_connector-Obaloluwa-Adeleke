# github_connector/custom_exceptions.py

class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    pass

class ResourceNotFound(GitHubAPIError):
    """Raised when a repository or resource is not found (404)."""
    pass

class RateLimitExceeded(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded (403/429)."""
    pass

class NetworkError(GitHubAPIError):
    """Raised when a network or connection error occurs."""
    pass

class AuthenticationError(GitHubAPIError):
    """Raised when authentication fails (401)."""
    pass