import api from './api'

export const spotifyAPI = {
    authorize: () => api.get('/spotify/authorize'),
    getPlaylists: (query) => api.get(`/spotify/playlists`, { params: { query } }),
}
