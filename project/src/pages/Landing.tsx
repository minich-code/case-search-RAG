import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Scale, 
  Search, 
  FileText, 
  BarChart3, 
  Zap, 
  Shield, 
  Clock, 
  CheckCircle,
  ArrowRight,
  Star
} from 'lucide-react'

export function Landing() {
  const features = [
    {
      icon: <Search className="h-6 w-6" />,
      title: 'Advanced Case Search',
      description: 'Powerful search across millions of legal cases with AI-powered relevance ranking.'
    },
    {
      icon: <FileText className="h-6 w-6" />,
      title: 'Case Analysis',
      description: 'Comprehensive case summaries, legal principles, and comparative analysis.'
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: 'Argument Generation',
      description: 'AI-assisted legal argument construction with supporting case citations.'
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: 'Real-time Research',
      description: 'Instant access to legal insights with our advanced query processing engine.'
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: 'Secure & Compliant',
      description: 'Enterprise-grade security with full compliance to legal industry standards.'
    },
    {
      icon: <Clock className="h-6 w-6" />,
      title: 'Time Efficient',
      description: 'Reduce research time by 70% with intelligent automation and insights.'
    }
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Senior Partner',
      firm: 'Chen & Associates',
      content: 'LegalResearch has transformed how we approach case analysis. The AI insights are incredibly accurate.',
      rating: 5
    },
    {
      name: 'Michael Rodriguez',
      role: 'Corporate Counsel',
      firm: 'TechCorp Legal',
      content: 'The search capabilities are unmatched. We find relevant cases in minutes, not hours.',
      rating: 5
    },
    {
      name: 'Jennifer Park',
      role: 'Associate',
      firm: 'Park Legal Group',
      content: 'Perfect for both junior and senior lawyers. The argument generation feature is a game-changer.',
      rating: 5
    }
  ]

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24">
        <div className="container mx-auto">
          <div className="mx-auto max-w-4xl text-center">
            <Badge variant="secondary" className="mb-4 text-xs sm:text-sm">
              Powered by Advanced AI
            </Badge>
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl lg:text-6xl">
              Revolutionize Your
              <span className="text-primary"> Legal Research</span>
            </h1>
            <p className="mt-4 text-lg text-muted-foreground sm:text-xl md:mt-6 lg:text-2xl">
              Advanced case analysis, intelligent search, and AI-powered insights 
              to accelerate your legal practice.
            </p>
            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" className="h-12 px-8 text-base" asChild>
                <Link to="/auth?mode=signup">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="h-12 px-8 text-base" asChild>
                <Link to="/app">
                  Try Demo
                </Link>
              </Button>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">
              No credit card required • 14-day free trial
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 sm:py-16 lg:py-24 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-2xl font-bold sm:text-3xl lg:text-4xl">
              Everything you need for legal research
            </h2>
            <p className="mt-4 text-muted-foreground">
              Comprehensive tools designed specifically for legal professionals.
            </p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <Card key={index} className="relative overflow-hidden">
                <CardHeader>
                  <div className="flex items-center space-x-2">
                    <div className="rounded-lg bg-primary/10 p-2 text-primary">
                      {feature.icon}
                    </div>
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-12 sm:py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-2xl font-bold sm:text-3xl lg:text-4xl">
              Trusted by legal professionals
            </h2>
            <p className="mt-4 text-muted-foreground">
              See what lawyers are saying about LegalResearch.
            </p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="relative">
                <CardHeader>
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-primary text-primary" />
                    ))}
                  </div>
                </CardHeader>
                <CardContent>
                  <blockquote className="text-sm">
                    "{testimonial.content}"
                  </blockquote>
                  <div className="mt-4">
                    <div className="font-semibold text-sm">{testimonial.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {testimonial.role}, {testimonial.firm}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 sm:py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-2xl font-bold sm:text-3xl lg:text-4xl">
              Ready to transform your practice?
            </h2>
            <p className="mt-4 text-lg opacity-90">
              Join thousands of legal professionals who trust LegalResearch.
            </p>
            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button 
                size="lg" 
                variant="secondary" 
                className="h-12 px-8 text-base"
                asChild
              >
                <Link to="/auth?mode=signup">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
            <div className="mt-6 flex items-center justify-center space-x-6 text-sm opacity-75">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>14-day free trial</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>No setup fees</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}