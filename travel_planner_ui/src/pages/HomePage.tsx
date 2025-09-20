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
      description: 'Advanced AI creates personalized itineraries based on your preferences',
      color: 'text-purple-500'
    },
    {
      icon: Zap,
      title: 'Real-time Updates',
      description: 'Get current weather, pricing, and availability information',
      color: 'text-yellow-500'
    },
    {
      icon: Shield,
      title: 'Budget Optimization',
      description: 'Smart budget validation and cost-saving recommendations',
      color: 'text-green-500'
    },
    {
      icon: Headphones,
      title: '24/7 Support',
      description: 'Round-the-clock assistance for all your travel needs',
      color: 'text-blue-500'
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
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-secondary/5">
        <div className="absolute inset-0 bg-grid-pattern opacity-5" />
        <div className="container mx-auto px-4 py-20 pb-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-4xl mx-auto"
          >
            {/* <Badge className="mb-6 text-sm px-4 py-2">
              <Sparkles className="h-4 w-4 mr-2" />
              Powered by Advanced AI
            </Badge>

            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Plan Your Perfect Trip with{' '}
              <span className="gradient-text">AI Intelligence</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Get personalized travel itineraries, smart budget planning, and real-time recommendations
              tailored to your preferences. Your dream vacation is just a few clicks away.
            </p> */}

            {/* <div className="flex flex-wrap justify-center gap-4 mb-12">
              {TRAVEL_THEMES.slice(0, 4).map((theme, index) => (
                <motion.div
                  key={theme.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 + index * 0.1, duration: 0.5 }}
                >
                  <Badge
                    className={`px-4 py-2 bg-gradient-to-r ${theme.gradient} text-white border-none`}
                  >
                    <span className="mr-2">{theme.icon}</span>
                    {theme.label}
                  </Badge>
                </motion.div>
              ))}
            </div> */}

            {/* Stats */}
            {/* <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: animateStats ? 1 : 0, y: animateStats ? 0 : 20 }}
                  transition={{ delay: 0.1 + index * 0.1, duration: 0.6 }}
                  className="text-center"
                >
                  <div className="flex items-center justify-center mb-2">
                    <stat.icon className="h-6 w-6 text-primary mr-2" />
                    <span className="text-2xl md:text-3xl font-bold text-foreground">
                      {stat.value}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                </motion.div>
              ))}
            </div> */}
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
        <section id="features" className="py-20 bg-secondary/30">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Why Choose TravelBuddy AI?
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
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
                  <Card className="h-full">
                    <CardContent className="p-6 text-center">
                      <feature.icon className={`h-12 w-12 mx-auto mb-4 ${feature.color}`} />
                      <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">
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
              <Card className="relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-secondary/10" />
                <CardContent className="relative p-12">
                  <Globe className="h-16 w-16 mx-auto mb-6 text-primary" />
                  <h2 className="text-2xl md:text-3xl font-bold mb-4">
                    Ready for Your Next Adventure?
                  </h2>
                  <p className="text-lg text-muted-foreground mb-8">
                    Join thousands of travelers who trust TravelBuddy AI for their perfect trips.
                    Start planning your dream vacation today!
                  </p>

                  <Button
                    size="xl"
                    variant="gradient"
                    onClick={() => {
                      document.getElementById('trip-planner')?.scrollIntoView({
                        behavior: 'smooth'
                      })
                    }}
                    className="group"
                  >
                    Start Planning Now
                    <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>

                  <div className="mt-8 flex items-center justify-center gap-6 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      <span>Free to use</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      <span>Instant results</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
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