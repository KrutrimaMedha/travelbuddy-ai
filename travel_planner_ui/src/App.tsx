import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Moon, Sun, Menu, X, Plane, Github, Heart } from 'lucide-react'

import { Button } from '@/components/ui/Button'
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
    { name: 'Home', href: '#' },
    { name: 'Plan Trip', href: '#trip-planner' },
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
          className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
            isScrolled
              ? 'bg-background/95 backdrop-blur-md border-b border-border shadow-sm'
              : 'bg-transparent'
          }`}
        >
          <nav className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="flex items-center gap-3"
              >
                <div className="w-10 h-10 bg-gradient-to-r from-primary to-primary/80 rounded-lg flex items-center justify-center">
                  <Plane className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold gradient-text">TravelBuddy</h1>
                  <p className="text-xs text-muted-foreground">Intelligent Trip Planning</p>
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
                    className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
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
                  className="hover:bg-secondary"
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
                  className="md:hidden"
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
                  className="md:hidden mt-4 pt-4 border-t border-border"
                >
                  <div className="space-y-2">
                    {navigation.map((item) => (
                      <a
                        key={item.name}
                        href={item.href}
                        className="block py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
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
        <main className="pt-20">
          <Routes>
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-border bg-secondary/30">
          <div className="container mx-auto px-4 py-12">
            <div className="flex justify-center">
              {/* Brand */}
              <div className="flex flex-col items-center text-center">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-gradient-to-r from-primary to-primary/80 rounded-lg flex items-center justify-center">
                    <Plane className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-lg font-bold">TravelBuddy</span>
                </div>
                <p className="text-sm text-muted-foreground mb-4 max-w-md">
                  AI-powered travel planning that creates personalized itineraries, validates budgets,
                  and provides real-time recommendations for your perfect trip.
                </p>
                <div className="flex items-center gap-4">
                  <Button variant="ghost" size="icon">
                    <Github className="h-5 w-5" />
                  </Button>
                </div>
              </div>

              {/* Quick Links */}
              {/* <div>
                <h3 className="font-semibold mb-4">Quick Links</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="#" className="hover:text-foreground transition-colors">How it Works</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Features</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Pricing</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Support</a></li>
                </ul>
              </div> */}

              {/* Travel Themes */}
              {/* <div>
                <h3 className="font-semibold mb-4">Travel Themes</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="#" className="hover:text-foreground transition-colors">Adventure</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Cultural</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Devotional</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Nightlife</a></li>
                </ul>
              </div> */}
            </div>

            <div className="border-t border-border mt-12 pt-8 flex flex-col md:flex-row items-center justify-between">
              <p className="text-sm text-muted-foreground">
                © 2025
                 TravelBuddy. All rights reserved.
              </p>
              <p className="text-sm text-muted-foreground flex items-center gap-1 mt-4 md:mt-0">
                Made with <Heart className="h-4 w-4 text-red-500" /> for travelers worldwide
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App