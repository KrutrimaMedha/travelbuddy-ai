/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Sparkles, 
  ArrowRight, Globe,
  CheckCircle2, Zap, Shield, Headphones
} from 'lucide-react'
import { toast } from 'sonner'

import { TripPlanningForm } from '@/components/forms/TripPlanningForm'
import { TripResultsDisplay } from '@/components/results/TripResultsDisplay'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { FullPageLoader } from '@/components/ui/LoadingSpinner'

import { useTripPlanner } from '@/hooks/useTripPlanner'
// import { TRAVEL_THEMES } from '@/utils/constants'
import type { TripRequest } from '@/types'

export function HomePage() {
  const [showResults, setShowResults] = useState(false)
  const [, setAnimateStats] = useState(false)

  const {
    planTrip,
    tripPlan,
    isPlanning,
    loadingState,
    saveTrip,
    resetTripPlan
  } = useTripPlanner()

  // Animate stats on component mount
  useEffect(() => {
    const timer = setTimeout(() => setAnimateStats(true), 500)
    return () => clearTimeout(timer)
  }, [])

  // Show results when trip plan is received
  useEffect(() => {
    if (tripPlan && tripPlan.status === 'success') {
      setShowResults(true)
      // Smooth scroll to results
      setTimeout(() => {
        const resultsElement = document.getElementById('trip-results')
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    }
  }, [tripPlan])

  const handleTripPlan = (request: TripRequest) => {
    planTrip(request)
    toast.success('Trip planning started!')
  }

  const handleSaveTrip = (trip: any) => {
    saveTrip(trip)
  }

  const handleShareTrip = (trip: any) => {
    if (navigator.share) {
      navigator.share({
        title: `${trip.trip_overview.source} to ${trip.trip_overview.destination} Trip Plan`,
        text: `Check out this amazing ${trip.trip_overview.theme} trip plan!`,
        url: window.location.href,
      })
    } else {
      navigator.clipboard.writeText(window.location.href)
      toast.success('Trip link copied to clipboard!')
    }
  }

  const handlePlanNewTrip = () => {
    setShowResults(false)
    resetTripPlan()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Stats for the hero section
  // const stats = [
  //   { label: 'Happy Travelers', value: '10,000+', icon: Users },
  //   { label: 'Destinations', value: '500+', icon: MapPin },
  //   { label: 'Success Rate', value: '98%', icon: TrendingUp },
  //   { label: 'Average Rating', value: '4.9/5', icon: Star },
  // ]

  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered Planning',
      description: 'Advanced AI creates personalized itineraries based on your preferences'
    },
    {
      icon: Zap,
      title: 'Real-time Updates',
      description: 'Get current weather, pricing, and availability information'
    },
    {
      icon: Shield,
      title: 'Budget Optimization',
      description: 'Smart budget validation and cost-saving recommendations'
    },
    {
      icon: Headphones,
      title: '24/7 Support',
      description: 'Round-the-clock assistance for all your travel needs'
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Full Page Loader */}
      {isPlanning && (
        <FullPageLoader
          message={loadingState.message}
          progress={loadingState.progress}
        />
      )}

      {/* Hero Section */}
      <section className="relative overflow-hidden text-white emt-hero-gradient">
        <div className="absolute inset-0">
          <div className="absolute -top-32 -left-24 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute top-12 right-10 h-48 w-48 rounded-full bg-white/20 blur-2xl" />
          <div className="absolute inset-0 hidden md:block pointer-events-none opacity-10 bg-[radial-gradient(circle_at_1px_1px,rgba(255,255,255,0.45)_1px,transparent_0)] bg-[size:36px_36px]" />
        </div>
        <div className="container mx-auto px-4 py-24 pb-16 relative">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="max-w-5xl mx-auto text-center"
          >
            <Badge
              variant="outline"
              className="mb-6 inline-flex items-center gap-2 border-white/40 bg-white/10 text-white uppercase tracking-[0.3em] text-[11px] px-5 py-2"
            >
              <Sparkles className="h-4 w-4" />
              PREMIUM TRAVEL DEALS
            </Badge>

            <h1 className="text-4xl md:text-6xl font-semibold leading-tight">
              Fly Smarter with{' '}
              <span className="text-white">EaseMyTrip-inspired Planning</span>
            </h1>

            <p className="text-lg md:text-xl text-white/85 mt-6 mb-12 max-w-3xl mx-auto">
              Unlock AI-personalized itineraries, budget-friendly fares, and round-the-clock assistance.
              Experience the signature EaseMyTrip look and feel with intelligent travel automation.
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              <Button
                size="xl"
                variant="gradient"
                className="group shadow-xl shadow-emt-blue-dark/40 ring-1 ring-white/20"
                onClick={() => {
                  document.getElementById('trip-planner')?.scrollIntoView({
                    behavior: 'smooth'
                  })
                }}
              >
                Start Your Flight Search
                <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                size="xl"
                variant="accent"
                className="bg-white text-emt-navy hover:bg-white/90"
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              >
                View Live Offers
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Planning Form Section */}
      <section id="trip-planner" className="pt-10 pb-20">
        <div className="container mx-auto px-4">
          {!showResults ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <TripPlanningForm
                onSubmit={handleTripPlan}
                isLoading={isPlanning}
              />
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              <div className="text-center">
                <Button
                  onClick={handlePlanNewTrip}
                  variant="outline"
                  className="mb-8"
                >
                  <ArrowRight className="h-4 w-4 mr-2 rotate-180" />
                  Plan Another Trip
                </Button>
              </div>
            </motion.div>
          )}
        </div>
      </section>

      {/* Results Section */}
      {showResults && (
        <section id="trip-results" className="pb-20">
          <div className="container mx-auto px-4">
            <TripResultsDisplay
              tripData={tripPlan || null}
              isLoading={isPlanning}
              onSaveTrip={handleSaveTrip}
              onShareTrip={handleShareTrip}
            />
          </div>
        </section>
      )}
    
      {/* Features Section */}
      {!showResults && (
        <section id="features" className="py-20 emt-section-soft">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-emt-navy mb-4">
                Why Choose TravelBuddy AI?
              </h2>
              <p className="text-lg text-emt-blue-dark/80 max-w-2xl mx-auto">
                Experience the future of travel planning with our cutting-edge AI technology
                and comprehensive travel services.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.6 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -5 }}
                >
                  <Card className="h-full border-none bg-white/95">
                    <CardContent className="p-8 text-center space-y-4">
                      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emt-sky">
                        <feature.icon className={`h-9 w-9 text-emt-blue`} />
                      </div>
                      <h3 className="text-lg font-semibold text-emt-navy">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground/90">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA Section */}
      {!showResults && (
        <section id="about" className="py-20">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center max-w-3xl mx-auto"
            >
              <Card className="relative overflow-hidden border-none bg-gradient-to-r from-emt-blue-dark via-emt-blue to-emt-blue-light text-white shadow-2xl">
                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.6),transparent_55%)]" />
                <CardContent className="relative p-12 space-y-6">
                  <Globe className="h-16 w-16 mx-auto mb-4 text-white drop-shadow-lg" />
                  <h2 className="text-2xl md:text-3xl font-semibold">
                    Ready for Your Next Adventure?
                  </h2>
                  <p className="text-lg text-white/85 max-w-2xl mx-auto">
                    Join thousands of travelers who trust TravelBuddy AI for EaseMyTrip-inspired planning.
                    Start building your itinerary with transparent pricing and lightning-fast results.
                  </p>

                  <div className="flex flex-wrap justify-center gap-4">
                    <Button
                      size="xl"
                      variant="accent"
                      className="group shadow-xl shadow-black/20"
                      onClick={() => {
                        document.getElementById('trip-planner')?.scrollIntoView({
                          behavior: 'smooth'
                        })
                      }}
                    >
                      Start Planning Now
                      <ArrowRight className="h-5 w-5 ml-2 transition-transform group-hover:translate-x-1" />
                    </Button>
                    <Button
                      size="xl"
                      variant="ghost"
                      className="border-white/60 text-white hover:bg-white/10"
                      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    >
                      Explore Offers
                    </Button>
                  </div>

                  <div className="mt-6 flex flex-wrap items-center justify-center gap-6 text-sm text-white/80">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-white" />
                      <span>Free to use</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-white" />
                      <span>Instant results</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-white" />
                      <span>AI-powered</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </section>
      )}
    </div>
  )
}
