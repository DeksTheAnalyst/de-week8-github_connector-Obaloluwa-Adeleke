# main.py
"""
Demo script showing how to use the github_connector library.
"""
import os
from dotenv import load_dotenv
from github_connector import GitHubClient, ResourceNotFound, GitHubAPIError

# Load environment variables from .env file
load_dotenv()

def main():
    """Main demonstration function."""
    print("=" * 60)
    print("GitHub Connector Library Demo")
    print("=" * 60)
    
    # Initialize the client
    client = GitHubClient()
    
    # Example 1: Get repository details
    print("\n[Example 1] Fetching repository details...")
    try:
        repo_data = client.get_repo_details("torvalds", "linux")
        print(f"Repository: {repo_data['full_name']}")
        print(f"Description: {repo_data['description']}")
        print(f" Stars: {repo_data['stargazers_count']:,}")
        print(f" Forks: {repo_data['forks_count']:,}")
        print(f"Language: {repo_data['language']}")
    except ResourceNotFound:
        print(" Repository not found!")
    except GitHubAPIError as e:
        print(f"API Error: {e}")
    
    # Example 2: Get latest release
    print("\n[Example 2] Fetching latest release...")
    try:
        release_data = client.get_latest_release("python", "cpython")
        print(f"Latest Release: {release_data['tag_name']}")
        print(f"Name: {release_data['name']}")
        print(f"Published: {release_data['published_at']}")
        print(f"Author: {release_data['author']['login']}")
    except ResourceNotFound:
        print("No releases found!")
    except GitHubAPIError as e:
        print(f"API Error: {e}")
    
    # Example 3: Handling 404 errors
    print("\n[Example 3] Testing error handling (non-existent repo)...")
    try:
        client.get_repo_details("nonexistent-user-12345", "nonexistent-repo-67890")
    except ResourceNotFound:
        print(" ResourceNotFound exception caught correctly!")
    except GitHubAPIError as e:
        print(f"Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()