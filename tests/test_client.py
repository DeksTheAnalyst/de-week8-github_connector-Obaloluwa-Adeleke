# tests/test_client.py
"""
Unit tests for GitHubClient using mocked responses.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from github_connector import GitHubClient, ResourceNotFound, RateLimitExceeded, GitHubAPIError


@pytest.fixture
def client():
    """Fixture to create a GitHubClient instance."""
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'fake_token_for_testing'}):
        return GitHubClient()


class TestGitHubClient:
    """Test suite for GitHubClient."""
    
    def test_initialization_with_token(self):
        """Test that client initializes correctly with a token."""
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
            client = GitHubClient()
            assert client.token == 'test_token'
    
    def test_initialization_without_token(self):
        """Test that client initializes without token (with warning)."""
        with patch.dict('os.environ', {}, clear=True):
            client = GitHubClient()
            assert client.token is None
    
    def test_get_headers_with_token(self, client):
        """Test that headers include authorization when token exists."""
        headers = client._get_headers()
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer fake_token_for_testing'
        assert headers['Accept'] == 'application/vnd.github+json'
    
    @patch('github_connector.client.requests.request')
    def test_get_repo_details_success(self, mock_request, client):
        """Test successful repository details retrieval."""
        # Mock a successful 200 response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test-repo',
            'full_name': 'owner/test-repo',
            'description': 'A test repository',
            'stargazers_count': 100,
            'forks_count': 50
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = client.get_repo_details('owner', 'test-repo')
        
        # Assertions
        assert result['name'] == 'test-repo'
        assert result['stargazers_count'] == 100
        mock_request.assert_called_once()
    
    @patch('github_connector.client.requests.request')
    def test_get_repo_details_not_found(self, mock_request, client):
        """Test that 404 raises ResourceNotFound exception."""
        # Mock a 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        # Should raise ResourceNotFound
        with pytest.raises(ResourceNotFound):
            client.get_repo_details('nonexistent', 'repo')
    
    @patch('github_connector.client.requests.request')
    def test_get_latest_release_success(self, mock_request, client):
        """Test successful latest release retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tag_name': 'v1.0.0',
            'name': 'Release 1.0.0',
            'published_at': '2024-01-01T00:00:00Z'
        }
        mock_request.return_value = mock_response
        
        result = client.get_latest_release('owner', 'repo')
        
        assert result['tag_name'] == 'v1.0.0'
        assert result['name'] == 'Release 1.0.0'
    
    @patch('github_connector.client.requests.request')
    @patch('github_connector.client.time.sleep')  # Mock sleep to speed up test
    def test_retry_logic_with_rate_limit(self, mock_sleep, mock_request, client):
        """Test that client retries on rate limit and eventually succeeds."""
        # Mock sequence: 429, 429, 200 (rate limit twice, then success)
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'success': True}
        
        mock_request.side_effect = [mock_response_429, mock_response_429, mock_response_200]
        
        # Should eventually succeed after retries
        result = client.get_repo_details('owner', 'repo')
        
        assert result['success'] is True
        assert mock_request.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep twice before third attempt
    
    @patch('github_connector.client.requests.request')
    @patch('github_connector.client.time.sleep')
    def test_retry_exhaustion(self, mock_sleep, mock_request, client):
        """Test that RateLimitExceeded is raised after max retries."""
        # Mock all attempts returning 429
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        # Should raise RateLimitExceeded after 3 attempts
        with pytest.raises(RateLimitExceeded):
            client.get_repo_details('owner', 'repo')
        
        assert mock_request.call_count == 3
    
    @patch('github_connector.client.requests.request')
    def test_other_http_errors(self, mock_request, client):
        """Test that other HTTP errors raise GitHubAPIError."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_request.return_value = mock_response
        
        with pytest.raises(GitHubAPIError):
            client.get_repo_details('owner', 'repo')