import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Moon, Sun, Menu, X, Plane, Github, Heart } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { cn } from '@/utils/cn'
import { HomePage } from '@/pages/HomePage'

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  // Handle dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  // Handle scroll for navbar styling
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const toggleDarkMode = () => {
    setDarkMode((prev: boolean) => !prev)
  }

  const navigation = [
    { name: 'Features', href: '#features' },
    { name: 'About', href: '#about' }
  ]

  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        {/* Navigation */}
        <motion.header
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          transition={{ duration: 0.6 }}
          className={cn(
            'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
            isScrolled
              ? 'bg-white/95 backdrop-blur-md border-b border-border shadow-md text-emt-navy'
              : 'bg-gradient-to-r from-emt-navy via-emt-blue-dark to-emt-blue text-white shadow-md'
          )}
        >
          <nav className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="flex items-center gap-3"
              >
                <div className={cn(
                  'w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg',
                  isScrolled
                    ? 'bg-gradient-to-br from-emt-blue-dark to-emt-blue'
                    : 'bg-white/15 border border-white/20'
                )}>
                  <Plane className={cn('h-5 w-5', isScrolled ? 'text-white' : 'text-white')} />
                </div>
                <div className="flex flex-col">
                  <h1
                    className={cn(
                      'text-lg font-semibold tracking-wide uppercase transition-colors',
                      isScrolled
                        ? 'text-emt-navy'
                        : 'text-white drop-shadow-[0_2px_8px_rgba(2,33,90,0.45)]'
                    )}
                  >
                    TravelBuddy
                  </h1>
                  <p
                    className={cn(
                      'text-xs font-medium transition-all',
                      isScrolled
                        ? 'text-emt-blue-dark/70'
                        : 'text-white/95 bg-white/15 rounded-full px-3 py-1 shadow-[0_2px_10px_rgba(2,33,90,0.35)]'
                    )}
                  >
                    Intelligent Trip Planning
                  </p>
                </div>
              </motion.div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-8">
                {navigation.map((item) => (
                  <motion.a
                    key={item.name}
                    href={item.href}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={(e) => {
                      e.preventDefault()
                      if (item.href === '#') {
                        window.scrollTo({ top: 0, behavior: 'smooth' })
                      } else {
                        const element = document.querySelector(item.href)
                        if (element) {
                          element.scrollIntoView({ behavior: 'smooth' })
                        }
                      }
                    }}
                    className={cn(
                      'text-sm font-medium transition-colors cursor-pointer tracking-wide',
                      isScrolled
                        ? 'text-emt-navy/80 hover:text-emt-blue-dark'
                        : 'text-white drop-shadow-[0_2px_6px_rgba(0,0,0,0.45)] hover:text-white'
                    )}
                  >
                    {item.name}
                  </motion.a>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                {/* Dark Mode Toggle */}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleDarkMode}
                  className={cn(
                    'hover:bg-white/15',
                    isScrolled
                      ? 'text-emt-blue-dark hover:bg-emt-sky'
                      : 'text-white drop-shadow-[0_2px_6px_rgba(0,0,0,0.45)]'
                  )}
                >
                  <AnimatePresence mode="wait">
                    {darkMode ? (
                      <motion.div
                        key="sun"
                        initial={{ rotate: -90, opacity: 0 }}
                        animate={{ rotate: 0, opacity: 1 }}
                        exit={{ rotate: 90, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Sun className="h-5 w-5" />
                      </motion.div>
                    ) : (
                      <motion.div
                        key="moon"
                        initial={{ rotate: 90, opacity: 0 }}
                        animate={{ rotate: 0, opacity: 1 }}
                        exit={{ rotate: -90, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Moon className="h-5 w-5" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </Button>

                {/* Mobile Menu Button */}
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                    'md:hidden hover:bg-white/15',
                    isScrolled
                      ? 'text-emt-blue-dark hover:bg-emt-sky'
                      : 'text-white drop-shadow-[0_2px_6px_rgba(0,0,0,0.45)]'
                  )}
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                  {mobileMenuOpen ? (
                    <X className="h-5 w-5" />
                  ) : (
                    <Menu className="h-5 w-5" />
                  )}
                </Button>
              </div>
            </div>

            {/* Mobile Navigation */}
            <AnimatePresence>
              {mobileMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className={cn(
                    'md:hidden mt-4 pt-4 border-t',
                    isScrolled
                      ? 'border-border text-emt-navy'
                      : 'border-white/30 text-white'
                  )}
                >
                  <div className="space-y-2">
                    {navigation.map((item) => (
                      <a
                        key={item.name}
                        href={item.href}
                    className={cn(
                      'block py-2 text-sm font-medium transition-colors cursor-pointer',
                      isScrolled
                        ? 'text-emt-navy/80 hover:text-emt-blue-dark'
                        : 'text-white drop-shadow-[0_2px_6px_rgba(0,0,0,0.45)] hover:text-white'
                    )}
                        onClick={(e) => {
                          e.preventDefault()
                          setMobileMenuOpen(false)
                          if (item.href === '#') {
                            window.scrollTo({ top: 0, behavior: 'smooth' })
                          } else {
                            const element = document.querySelector(item.href)
                            if (element) {
                              element.scrollIntoView({ behavior: 'smooth' })
                            }
                          }
                        }}
                      >
                        {item.name}
                      </a>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </nav>
        </motion.header>

        {/* Main Content */}
        <main className="pt-24 md:pt-28">
          <Routes>
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-emt-sky/60 bg-emt-sky dark:bg-emt-blue-dark/95 dark:border-emt-blue/40 transition-colors">
          <div className="container mx-auto px-4 py-12 text-emt-blue-dark/80 dark:text-white/80">
            <div className="flex flex-col md:flex-row items-center md:items-start justify-between gap-10 text-center md:text-left">
              <div className="flex flex-col items-center md:items-start gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-emt-blue-dark to-emt-blue rounded-2xl flex items-center justify-center shadow-lg shadow-emt-blue-dark/30">
                    <Plane className="h-5 w-5 text-white" />
                  </div>
                  <div className="text-left">
                    <span className="text-lg font-semibold text-emt-navy dark:text-white">TravelBuddy</span>
                    <p className="text-xs uppercase tracking-[0.35em] text-emt-blue-dark/70 dark:text-white/70 mt-1">AI TRAVEL SUITE</p>
                  </div>
                </div>
                <p className="text-sm text-emt-blue-dark/80 dark:text-white/80 max-w-md">
                  AI-powered planning with EaseMyTrip-inspired styling. Build flight itineraries, validate budgets, and discover personalized recommendations instantly.
                </p>
                <div className="flex items-center gap-3">
                  <Button
                    variant="outline"
                    size="icon"
                    className="border-emt-blue text-emt-blue hover:bg-emt-skyLight dark:border-white/60 dark:text-white dark:hover:bg-white/10"
                  >
                    <Github className="h-5 w-5" />
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-10 text-sm">
                <div>
                  <h3 className="font-semibold text-emt-navy dark:text-white mb-4">Explore</h3>
                  <ul className="space-y-2">
                    <li><a href="#trip-planner" className="hover:text-emt-blue-dark transition-colors dark:hover:text-white">Trip Planner</a></li>
                    <li><a href="#features" className="hover:text-emt-blue-dark transition-colors dark:hover:text-white">Features</a></li>
                    <li><a href="#about" className="hover:text-emt-blue-dark transition-colors dark:hover:text-white">Offers</a></li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-emt-navy dark:text-white mb-4">Support</h3>
                  <ul className="space-y-2">
                    <li><a href="mailto:support@travelbuddy.ai" className="hover:text-emt-blue-dark transition-colors dark:hover:text-white">Email Support</a></li>
                    <li><a href="#" className="hover:text-emt-blue-dark transition-colors dark:hover:text-white">FAQs</a></li>
                    <li><a href="#" className="hover:text-emt-blue-dark transition-colors dark:hover:text-white">Contact Sales</a></li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="border-t border-emt-sky/60 dark:border-white/10 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4 text-emt-blue-dark/70 dark:text-white/70 text-sm">
              <p>© 2025 TravelBuddy. All rights reserved.</p>
              <p className="flex items-center gap-1">
                Made with <Heart className="h-4 w-4 text-emt-orange" /> for travelers worldwide
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
