import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { CheckCircle, Star, Zap, Crown, Building2 } from 'lucide-react'

export function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false)

  const plans = [
    {
      name: 'Starter',
      description: 'Perfect for solo practitioners and small firms',
      icon: <Star className="h-6 w-6" />,
      price: {
        monthly: 49,
        annual: 39
      },
      features: [
        '100 queries per month',
        'Basic case search',
        'Case summaries',
        'Email support',
        '7-day history',
        'Basic citations'
      ],
      popular: false,
      cta: 'Start Free Trial'
    },
    {
      name: 'Professional',
      description: 'Ideal for growing practices and teams',
      icon: <Zap className="h-6 w-6" />,
      price: {
        monthly: 149,
        annual: 119
      },
      features: [
        '500 queries per month',
        'Advanced case search',
        'Detailed case analysis',
        'Argument generation',
        'Priority support',
        '30-day history',
        'Advanced citations',
        'Team collaboration',
        'API access'
      ],
      popular: true,
      cta: 'Start Free Trial'
    },
    {
      name: 'Enterprise',
      description: 'For large firms and organizations',
      icon: <Building2 className="h-6 w-6" />,
      price: {
        monthly: 399,
        annual: 319
      },
      features: [
        'Unlimited queries',
        'Premium case search',
        'AI-powered insights',
        'Custom integrations',
        'Dedicated support',
        'Unlimited history',
        'White-label options',
        'Advanced analytics',
        'SSO integration',
        'Custom training'
      ],
      popular: false,
      cta: 'Contact Sales'
    }
  ]

  const faqs = [
    {
      question: 'What is included in the free trial?',
      answer: 'The 14-day free trial includes full access to all features of your chosen plan, with no restrictions.'
    },
    {
      question: 'Can I change my plan later?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect at the next billing cycle.'
    },
    {
      question: 'Is there a setup fee?',
      answer: 'No, there are no setup fees or hidden costs. You only pay the monthly or annual subscription fee.'
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, PayPal, and can arrange bank transfers for Enterprise plans.'
    },
    {
      question: 'Is my data secure?',
      answer: 'Yes, we use enterprise-grade security measures and comply with all relevant legal industry standards.'
    },
    {
      question: 'Do you offer custom plans?',
      answer: 'Yes, we can create custom plans for large organizations with specific requirements. Contact our sales team.'
    }
  ]

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="container mx-auto">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            Choose Your Plan
          </h1>
          <p className="mt-4 text-lg text-muted-foreground sm:text-xl">
            Select the perfect plan for your legal practice. All plans include our core features.
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-3 mt-8">
            <Label htmlFor="billing-toggle" className="text-sm">Monthly</Label>
            <Switch
              id="billing-toggle"
              checked={isAnnual}
              onCheckedChange={setIsAnnual}
            />
            <Label htmlFor="billing-toggle" className="text-sm">
              Annual
              <Badge variant="secondary" className="ml-2 text-xs">
                Save 20%
              </Badge>
            </Label>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid gap-6 md:gap-8 lg:grid-cols-3 max-w-6xl mx-auto mb-16">
          {plans.map((plan, index) => (
            <Card 
              key={plan.name} 
              className={`relative ${
                plan.popular 
                  ? 'border-primary shadow-lg scale-105 lg:scale-110' 
                  : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="px-3 py-1">
                    <Crown className="h-3 w-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}
              
              <CardHeader className="text-center pb-2">
                <div className="flex items-center justify-center mb-4">
                  <div className="rounded-lg bg-primary/10 p-3 text-primary">
                    {plan.icon}
                  </div>
                </div>
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <CardDescription className="text-sm px-2">
                  {plan.description}
                </CardDescription>
                <div className="mt-6">
                  <span className="text-3xl font-bold">
                    ${isAnnual ? plan.price.annual : plan.price.monthly}
                  </span>
                  <span className="text-muted-foreground ml-1">
                    /month {isAnnual && <span className="text-xs">(billed annually)</span>}
                  </span>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                {plan.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className="flex items-start space-x-3">
                    <CheckCircle className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </CardContent>
              
              <CardFooter>
                <Button 
                  className="w-full h-11" 
                  variant={plan.popular ? 'default' : 'outline'}
                  asChild
                >
                  <Link to={plan.name === 'Enterprise' ? '/contact' : '/auth?mode=signup'}>
                    {plan.cta}
                  </Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Features Comparison */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-2xl font-bold text-center mb-8">
            All plans include
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              'Case law database access',
              'AI-powered search',
              'Legal citations',
              'Mobile access',
              'Data export',
              'Regular updates'
            ].map((feature, index) => (
              <div key={index} className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-primary" />
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">{faq.question}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-16">
          <h2 className="text-2xl font-bold mb-4">
            Still have questions?
          </h2>
          <p className="text-muted-foreground mb-6">
            Our team is here to help you choose the right plan for your needs.
          </p>
          <Button size="lg" variant="outline" asChild>
            <Link to="/contact">Contact Sales</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}