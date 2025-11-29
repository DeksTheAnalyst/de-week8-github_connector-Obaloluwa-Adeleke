# GitHub Connector

A Python library for fetching GitHub repository data with automatic retry logic and rate limit handling.

## Overview

This library provides a simple interface to:
- Get repository details (stars, forks, description, etc.)
- Get latest release information
- Handle rate limits automatically with exponential backoff
- Log all requests and errors

## Project Structure
```
github_connector_project/
├── github_connector/
│   ├── __init__.py
│   ├── client.py              # Main GitHubClient class
│   └── custom_exceptions.py   # Custom exceptions
├── tests/
│   ├── __init__.py
│   └── test_client.py         # Unit tests
├── main.py                     # Demo script
├── pyproject.toml             # Poetry dependencies
├── .env                        # Your GitHub token (create this)
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Install Poetry
```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 2. Install Dependencies
```bash
cd github_connector_project
poetry install
```

### 3. Get GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select `public_repo` scope
4. Copy the token

### 4. Create `.env` File
Create a `.env` file in the project root:
```
GITHUB_TOKEN=your_token_here
```

### 5. Run the Demo
```bash
poetry run python main.py
```

### 6. Run Tests
```bash
poetry run pytest
```

## Usage
```python
from github_connector import GitHubClient, ResourceNotFound

# Initialize client
client = GitHubClient()

# Get repository details
try:
    repo = client.get_repo_details("torvalds", "linux")
    print(f"Stars: {repo['stargazers_count']:,}")
    print(f"Forks: {repo['forks_count']:,}")
except ResourceNotFound:
    print("Repository not found!")

# Get latest release
try:
    release = client.get_latest_release("microsoft", "vscode")
    print(f"Latest: {release['tag_name']}")
except ResourceNotFound:
    print("No releases found!")
```

## Error Handling

The library uses custom exceptions:

| Exception | When It's Raised |
|-----------|------------------|
| `ResourceNotFound` | Repository or release doesn't exist (404) |
| `RateLimitExceeded` | Too many requests after retries (403/429) |
| `AuthenticationError` | Invalid token (401) |
| `NetworkError` | Connection problems |
| `GitHubAPIError` | Other API errors |

**Example:**
```python
from github_connector import GitHubClient, RateLimitExceeded, GitHubAPIError

client = GitHubClient()

try:
    repo = client.get_repo_details("owner", "repo")
except ResourceNotFound:
    print("Not found")
except RateLimitExceeded:
    print("Too many requests")
except GitHubAPIError as e:
    print(f"Error: {e}")
```

## Rate Limiting

- **Without token**: 60 requests/hour
- **With token**: 5,000 requests/hour
- **Automatic retries**: 3 attempts with exponential backoff (1s, 2s, 4s)

## Logging

The library logs:
- **INFO**: All requests and successes
- **WARNING**: Rate limits and retries
- **ERROR**: Failures and exceptions

## Troubleshooting

**"GITHUB_TOKEN not found" warning**
- Create `.env` file with your token

**"Rate limit exceeded"**
- Add a GitHub token to `.env`
- Wait before making more requests

**"ResourceNotFound" for valid repo**
- Check spelling (case-sensitive)
- For `get_latest_release()`, repo must have releases (not just tags)

**Tests failing**
- Run `poetry install` to install dependencies
- Run tests with `poetry run pytest`

## API Reference

### `GitHubClient()`
Initializes the client. Loads token from `GITHUB_TOKEN` environment variable.

### `get_repo_details(owner: str, repo: str) -> dict`
Returns repository info (name, description, stars, forks, language, etc.)

### `get_latest_release(owner: str, repo: str) -> dict`
Returns latest release info (tag_name, name, published_at, body, etc.)

## Requirements Met

Class-based interface with `GitHubClient`  
Token authentication via environment variables  
Rate limit detection and retry with exponential backoff  
Custom exception handling  
Comprehensive logging (INFO/WARNING/ERROR)  
Type hints and docstrings  
Poetry dependency management  
Unit tests with mocked responses  

Packaged by Obaloluwa Adeleke
