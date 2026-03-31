import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.core.config import settings
import json

class SpotifyService:
    @staticmethod
    def get_auth_manager():
        return SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private playlist-modify-public playlist-modify-private user-read-playback-state user-modify-playback-state",
            open_browser=False
        )

    @staticmethod
    def get_playlists(token_data, query="workout"):
        try:
            token_info = json.loads(token_data)
            sp = spotipy.Spotify(auth=token_info['access_token'])
            
            playlists = []
            
            # 1. Try fetching user's own playlists first
            print(f"DEBUG: Fetching personal playlists for query: {query}")
            user_playlists = sp.current_user_playlists(limit=50)
            
            for item in user_playlists['items']:
                # Simple keyword matching for relevance
                name = item['name'].lower()
                description = (item['description'] or '').lower()
                
                if query.lower() in name or query.lower() in description or not query:
                    playlists.append({
                        'id': item['id'],
                        'name': item['name'],
                        'description': item['description'],
                        'image': item['images'][0]['url'] if item['images'] else None,
                        'url': item['external_urls']['spotify'],
                        'uri': item['uri'],
                        'source': 'personal'
                    })
            
            # 2. If not enough personal playlists, fallback to public search
            if len(playlists) < 10:
                print(f"DEBUG: Found {len(playlists)} personal playlists, falling back to public search")
                search_results = sp.search(q=query, type='playlist', limit=20)
                
                existing_ids = {p['id'] for p in playlists}
                for item in search_results['playlists']['items']:
                    if item['id'] not in existing_ids:
                        playlists.append({
                            'id': item['id'],
                            'name': item['name'],
                            'description': item['description'],
                            'image': item['images'][0]['url'] if item['images'] else None,
                            'url': item['external_urls']['spotify'],
                            'uri': item['uri'],
                            'source': 'public'
                        })
                        if len(playlists) >= 15:
                            break
                            
            return playlists[:15]
        except Exception as e:
            print(f"DEBUG: Error fetching Spotify playlists: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

spotify_service = SpotifyService()
