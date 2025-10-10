# app/spotify/client.py
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self):
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.warning("Spotify credentials not found. Using mock client.")
                raise Exception("Spotify credentials not configured")
            
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id, 
                client_secret=client_secret
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            logger.info("Spotify authentication successful")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            raise

    def get_recommendations_by_emotion(self, emotion, limit=20):
        """
        Get music recommendations based on emotion with fallback to search
        """
        try:
            # Map emotions to Spotify parameters
            emotion_params = {
                'happy': {
                    'seed_genres': ['pop', 'dance', 'electronic'],
                    'target_danceability': 0.8,
                    'target_energy': 0.8,
                    'target_valence': 0.9,
                    'min_tempo': 120
                },
                'sad': {
                    'seed_genres': ['acoustic', 'sad', 'piano'],
                    'target_danceability': 0.3,
                    'target_energy': 0.3,
                    'target_valence': 0.2,
                    'max_tempo': 100
                },
                'angry': {
                    'seed_genres': ['rock', 'metal', 'hard-rock'],
                    'target_danceability': 0.6,
                    'target_energy': 0.9,
                    'target_valence': 0.3,
                    'min_tempo': 140
                },
                'surprise': {
                    'seed_genres': ['indie', 'alternative', 'experimental'],
                    'target_danceability': 0.7,
                    'target_energy': 0.7,
                    'target_valence': 0.7
                },
                'fear': {
                    'seed_genres': ['ambient', 'cinematic', 'soundtrack'],
                    'target_danceability': 0.2,
                    'target_energy': 0.3,
                    'target_valence': 0.3
                },
                'disgust': {
                    'seed_genres': ['industrial', 'experimental', 'noise'],
                    'target_danceability': 0.4,
                    'target_energy': 0.6,
                    'target_valence': 0.3
                },
                'neutral': {
                    'seed_genres': ['chill', 'ambient', 'indie'],
                    'target_danceability': 0.5,
                    'target_energy': 0.5,
                    'target_valence': 0.5
                }
            }
            
            params = emotion_params.get(emotion, emotion_params['neutral'])
            params['limit'] = limit
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.info(f"Getting Spotify recommendations for emotion: {emotion}")
            recommendations = self.sp.recommendations(**params)
            
            tracks = []
            for track in recommendations['tracks']:
                track_info = {
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
                }
                tracks.append(track_info)
            
            logger.info(f"Successfully retrieved {len(tracks)} tracks for emotion: {emotion}")
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting Spotify recommendations for emotion {emotion}: {e}")
            # Fallback to search based on emotion
            return self._get_fallback_tracks(emotion, limit)

    def _get_fallback_tracks(self, emotion, limit=20):
        """
        Fallback method using search when recommendations fail
        """
        try:
            emotion_keywords = {
                'happy': 'happy upbeat pop dance',
                'sad': 'sad acoustic emotional',
                'angry': 'angry rock metal aggressive',
                'surprise': 'surprising experimental indie',
                'fear': 'scary ambient cinematic',
                'disgust': 'industrial experimental noise',
                'neutral': 'chill ambient lo-fi'
            }
            
            query = emotion_keywords.get(emotion, 'chill')
            logger.info(f"Using fallback search for emotion: {emotion} with query: {query}")
            
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_info = {
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
                }
                tracks.append(track_info)
            
            logger.info(f"Fallback search returned {len(tracks)} tracks")
            return tracks
            
        except Exception as e:
            logger.error(f"Fallback search also failed: {e}")
            # Ultimate fallback - return mock data
            return self._get_mock_tracks(emotion, limit)

    def _get_mock_tracks(self, emotion, limit=20):
        """
        Ultimate fallback - return mock track data
        """
        mock_tracks = []
        for i in range(limit):
            mock_tracks.append({
                'name': f'{emotion.capitalize()} Song {i+1}',
                'artists': [f'{emotion.capitalize()} Artist'],
                'album': f'{emotion.capitalize()} Vibes',
                'preview_url': None,
                'external_url': 'https://open.spotify.com',
                'album_image': None
            })
        logger.info(f"Using mock data for emotion: {emotion}")
        return mock_tracks

    def search_tracks(self, query, limit=20):
        """
        Search for tracks directly
        """
        try:
            logger.info(f"Searching Spotify for: {query}")
            results = self.sp.search(q=query, type='track', limit=limit)
            
            tracks = []
            for track in results['tracks']['items']:
                track_info = {
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
                }
                tracks.append(track_info)
            
            logger.info(f"Search returned {len(tracks)} tracks")
            return tracks
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Return mock search results
            return self._get_mock_search_results(query, limit)

    def _get_mock_search_results(self, query, limit=20):
        """
        Mock search results when Spotify search fails
        """
        mock_tracks = []
        for i in range(min(limit, 10)):
            mock_tracks.append({
                'name': f'Search Result {i+1} for "{query}"',
                'artists': ['Various Artists'],
                'album': 'Search Results',
                'preview_url': None,
                'external_url': 'https://open.spotify.com',
                'album_image': None
            })
        return mock_tracks