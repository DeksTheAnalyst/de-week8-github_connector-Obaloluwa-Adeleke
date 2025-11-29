# github_connector/client.py
import os
import logging
import requests
import time
from typing import Dict, Any, Optional
from .custom_exceptions import (
    GitHubAPIError, 
    ResourceNotFound, 
    RateLimitExceeded,
    NetworkError,
    AuthenticationError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitHubClient:
    """A resilient client for interacting with the GitHub API."""
    
    BASE_URL = "https://api.github.com"
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1  # seconds

    def __init__(self) -> None:
        """
        Initializes the client, loading the API key from environment variables.
        
        Raises:
            AuthenticationError: If GITHUB_TOKEN is not set in environment.
        """
        self.token = os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            logger.warning("GITHUB_TOKEN not found. API requests will have lower rate limits.")
            # Note: We could raise AuthenticationError here, but the spec says
            # "raise a clear error OR log a warning (and proceed with lower rate limits)"
            # I'm choosing to warn and proceed. Adjust if you prefer strict error.
        else:
            logger.info("GitHubClient initialized with authentication token.")

    def _get_headers(self) -> Dict[str, str]:
        """
        Constructs the headers for API requests.
        
        Returns:
            Dictionary containing necessary headers including authorization if token exists.
        """
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        return headers
    def _make_request(self, method: str, endpoint: str) -> Dict[str, Any]:
        """
        Makes an API request with automatic retries for rate limits.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., '/repos/owner/repo')
            
        Returns:
            JSON response as a dictionary
            
        Raises:
            ResourceNotFound: If resource returns 404
            RateLimitExceeded: If rate limit persists after retries
            AuthenticationError: If authentication fails (401)
            NetworkError: If network/connection issues occur
            GitHubAPIError: For other API errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                response = requests.request(method, url, headers=headers, timeout=10)
                
                # Handle different status codes
                if response.status_code == 200:
                    logger.info(f"Request successful: {url}")
                    return response.json()
                
                elif response.status_code == 404:
                    logger.error(f"Resource not found: {url}")
                    raise ResourceNotFound(f"Resource not found at {endpoint}")
                
                elif response.status_code == 401:
                    logger.error(f"Authentication failed for {url}")
                    raise AuthenticationError("Invalid or missing GitHub token")
                
                elif response.status_code in [403, 429]:
                    # Rate limit hit
                    if attempt < self.MAX_RETRIES - 1:
                        backoff_time = self.INITIAL_BACKOFF * (2 ** attempt)
                        logger.warning(
                            f"Rate limit hit (status {response.status_code}). "
                            f"Retrying in {backoff_time}s..."
                        )
                        time.sleep(backoff_time)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {self.MAX_RETRIES} attempts")
                        raise RateLimitExceeded(
                            f"Rate limit exceeded after {self.MAX_RETRIES} retries"
                        )
                
                else:
                    # Other HTTP errors
                    logger.error(f"API error {response.status_code}: {response.text}")
                    raise GitHubAPIError(
                        f"GitHub API error {response.status_code}: {response.text}"
                    )
                    
            except requests.exceptions.Timeout:
                logger.error(f"Request timeout for {url}")
                raise NetworkError(f"Request timeout for {endpoint}")
            
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error for {url}: {str(e)}")
                raise NetworkError(f"Connection error: {str(e)}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for {url}: {str(e)}")
                raise NetworkError(f"Request failed: {str(e)}")
        
        # Should never reach here, but just in case
        raise GitHubAPIError("Request failed after all retries")
    def get_repo_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetches details for a specific repository.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            
        Returns:
            Dictionary containing repository details (name, description, stars, forks, etc.)
            
        Raises:
            ResourceNotFound: If repository doesn't exist
            GitHubAPIError: For other API errors
        """
        endpoint = f"/repos/{owner}/{repo}"
        return self._make_request("GET", endpoint)
    
    def get_latest_release(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetches details about the latest release of a repository.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            
        Returns:
            Dictionary containing latest release details (tag, name, body, etc.)
            
        Raises:
            ResourceNotFound: If repository or release doesn't exist
            GitHubAPIError: For other API errors
        """
        endpoint = f"/repos/{owner}/{repo}/releases/latest"
        return self._make_request("GET", endpoint)