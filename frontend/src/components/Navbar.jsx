import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sun, Moon, User, LogOut, LayoutDashboard, Dumbbell, Apple, TrendingUp, MessageCircle, Calendar as CalendarIcon } from 'lucide-react'
import useStore from '../store/useStore'

const navLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/workout', label: 'Workouts', icon: Dumbbell },
    { to: '/nutrition', label: 'Nutrition', icon: Apple },
    { to: '/calendar', label: 'Schedule', icon: CalendarIcon },
    { to: '/progress', label: 'Progress', icon: TrendingUp },
    { to: '/ai-coach', label: 'AI Coach', icon: MessageCircle },
]

export default function Navbar() {
    const location = useLocation()
    const navigate = useNavigate()
    const { user, theme, toggleTheme, logout, toggleChatOpen } = useStore()

    const handleLogout = () => {
        logout()
        navigate('/')
    }

    return (
        <motion.nav
            initial={{ y: -60, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="sticky top-0 z-50 w-full glass border-b border-brand-border"
        >
            <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
                {/* Logo */}
                <Link to="/dashboard" className="flex items-center gap-2">
                    <div className="w-9 h-9 rounded-xl icon-purple flex items-center justify-center text-white font-bold text-lg">
                        ✦
                    </div>
                    <span className="text-xl font-bold gradient-text">ArogyaMitra</span>
                </Link>

                {/* Nav Links */}
                <div className="hidden md:flex items-center gap-1">
                    {navLinks.map(({ to, label, icon: Icon }) => (
                        <Link
                            key={to}
                            to={to === '/ai-coach' ? '#' : to}
                            onClick={to === '/ai-coach' ? (e) => { e.preventDefault(); toggleChatOpen() } : undefined}
                            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${location.pathname === to ? 'nav-active' : 'text-muted hover:text-main hover:bg-white/5'
                                }`}
                        >
                            <Icon size={16} />
                            {label}
                        </Link>
                    ))}
                </div>

                {/* Right Side */}
                <div className="flex items-center gap-3">
                    {/* Theme Toggle */}
                    <button
                        onClick={toggleTheme}
                        className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-muted hover:text-main transition-all"
                    >
                        {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                    </button>

                    {/* User */}
                    <Link to="/profile" className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-purple-500/30 transition-all">
                        <User size={16} className="text-muted" />
                        <span className="text-sm text-main font-medium">{user?.username || 'User'}</span>
                    </Link>

                    {/* Logout */}
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-muted hover:text-red-400 hover:bg-red-500/10 transition-all"
                    >
                        <LogOut size={16} />
                        <span className="hidden sm:inline">Logout</span>
                    </button>
                </div>
            </div>
        </motion.nav>
    )
}
