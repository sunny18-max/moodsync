#!/usr/bin/env python3
"""
Test script for Spotify API integration
"""

import sys
import os
import time

# Add the parent directory to Python path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.spotify.client import SpotifyClient
    from config.settings import settings
except ImportError as e:
    print(f"Import error: {e}")
    print("Current Python path:")
    for path in sys.path:
        print(f"  {path}")
    sys.exit(1)

def test_spotify_authentication():
    """Test Spotify API authentication"""
    print("Testing Spotify Authentication...")
    
    try:
        client = SpotifyClient()
        print("✓ Spotify client initialized successfully")
        
        # Test if we can make API calls
        genres = client.get_available_genres()
        if genres and len(genres) > 0:
            print(f"✓ Retrieved {len(genres)} available genres")
            print(f"  Sample genres: {genres[:5]}")
        else:
            print("⚠️  No genres retrieved")
            
        return client
        
    except Exception as e:
        print(f"❌ Spotify authentication failed: {e}")
        return None

def test_emotion_recommendations(client):
    """Test music recommendations for different emotions"""
    print("\nTesting Emotion-Based Recommendations...")
    
    test_emotions = ['happy', 'sad', 'angry', 'surprise', 'neutral']
    
    for emotion in test_emotions:
        try:
            start_time = time.time()
            tracks = client.get_recommendations_by_emotion(emotion, limit=5)
            end_time = time.time()
            
            if tracks:
                print(f"✓ Emotion '{emotion}': {len(tracks)} tracks found ({end_time - start_time:.2f}s)")
                
                # Show first track as sample
                if tracks:
                    first_track = tracks[0]
                    print(f"  Sample: '{first_track['name']}' by {', '.join(first_track['artists'])}")
            else:
                print(f"⚠️  Emotion '{emotion}': No tracks found")
                
        except Exception as e:
            print(f"❌ Emotion '{emotion}' recommendation failed: {e}")

def test_music_search(client):
    """Test music search functionality"""
    print("\nTesting Music Search...")
    
    test_queries = [
        "pop music",
        "rock classics", 
        "jazz",
        "electronic"
    ]
    
    for query in test_queries:
        try:
            tracks = client.search_tracks(query, limit=3)
            if tracks:
                print(f"✓ Search '{query}': {len(tracks)} tracks found")
                if tracks:
                    print(f"  First result: '{tracks[0]['name']}'")
            else:
                print(f"⚠️  Search '{query}': No results")
                
        except Exception as e:
            print(f"❌ Search '{query}' failed: {e}")

def run_all_spotify_tests():
    """Run all Spotify integration tests"""
    print("=" * 60)
    print("SPOTIFY INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Check if credentials are set
    if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
        print("❌ Spotify credentials not set in environment variables")
        print("   Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file")
        return
    
    print(f"Spotify Client ID: {settings.SPOTIFY_CLIENT_ID[:10]}...")
    print(f"Spotify Client Secret: {settings.SPOTIFY_CLIENT_SECRET[:10]}...")
    
    client = test_spotify_authentication()
    
    if client:
        test_emotion_recommendations(client)
        test_music_search(client)
    
    print("\n" + "=" * 60)
    print("SPOTIFY TEST SUMMARY: Check for any ❌ or ⚠️  above")
    print("=" * 60)

if __name__ == '__main__':
    run_all_spotify_tests()