import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Music, ExternalLink, RefreshCw, Lock } from 'lucide-react'
import { spotifyAPI } from '../services/spotify'
import toast from 'react-hot-toast'
import useStore from '../store/useStore'

export default function SpotifyPlayer({ workoutFocus }) {
    const { user } = useStore()
    const [playlists, setPlaylists] = useState([])
    const [loading, setLoading] = useState(false)
    const [selectedPlaylist, setSelectedPlaylist] = useState(null)

    const fetchPlaylists = async () => {
        if (!user?.spotify_token_data) return
        setLoading(true)
        try {
            const { data } = await spotifyAPI.getPlaylists(workoutFocus || 'workout music')
            setPlaylists(data.playlists)
            if (data.playlists.length > 0) setSelectedPlaylist(data.playlists[0])
        } catch (err) {
            toast.error('Failed to load Spotify playlists')
        } finally {
            setLoading(false)
        }
    }

    const handleLinkSpotify = async () => {
        try {
            const { data } = await spotifyAPI.authorize()
            if (data.authorization_url) window.location.href = data.authorization_url
        } catch {
            toast.error('Failed to connect to Spotify')
        }
    }

    useEffect(() => {
        if (user?.spotify_token_data) fetchPlaylists()
    }, [user, workoutFocus])

    if (!user?.spotify_token_data) {
        return (
            <div className="glass-card p-6 text-center space-y-4">
                <div className="w-16 h-16 bg-[#1DB954]/10 rounded-full flex items-center justify-center mx-auto">
                    <Music className="text-[#1DB954]" size={32} />
                </div>
                <h3 className="text-xl font-bold text-main">Workout with Music</h3>
                <p className="text-muted text-sm">Connect your Spotify account to get personalized workout playlists directly in the app.</p>
                <button
                    onClick={handleLinkSpotify}
                    className="btn-primary bg-[#1DB954] hover:bg-[#1ed760] border-none flex items-center gap-2 mx-auto"
                >
                    <Music size={18} /> Connect Spotify
                </button>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-bold text-main flex items-center gap-2">
                    <Music className="text-[#1DB954]" size={20} /> Workout Playlists
                </h3>
                <button
                    onClick={fetchPlaylists}
                    disabled={loading}
                    className="p-2 hover:bg-white/5 rounded-lg text-muted transition-all"
                >
                    <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {playlists.length > 0 ? (
                    playlists.slice(0, 3).map((pl) => (
                        <button
                            key={pl.id}
                            onClick={() => setSelectedPlaylist(pl)}
                            className={`p-3 rounded-xl border transition-all text-left space-y-2 ${selectedPlaylist?.id === pl.id
                                ? 'border-[#1DB954] bg-[#1DB954]/5'
                                : 'border-white/10 hover:border-white/20 bg-white/5'
                                }`}
                        >
                            <img src={pl.image} alt={pl.name} className="w-full aspect-square rounded-lg object-cover shadow-lg" />
                            <p className="text-xs font-semibold text-main truncate">{pl.name}</p>
                        </button>
                    ))
                ) : (
                    <div className="col-span-full py-4 text-center">
                        <p className="text-muted text-sm italic">No workout playlists found. Try refreshing.</p>
                    </div>
                )}
            </div>

            {selectedPlaylist && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="relative rounded-2xl overflow-hidden bg-black/40 aspect-video sm:aspect-auto sm:h-[152px]"
                >
                    <iframe
                        src={`https://open.spotify.com/embed/playlist/${selectedPlaylist.id}?utm_source=generator&theme=0`}
                        width="100%"
                        height="152"
                        frameBorder="0"
                        allowFullScreen=""
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                        loading="lazy"
                    ></iframe>
                </motion.div>
            )}
        </div>
    )
}
