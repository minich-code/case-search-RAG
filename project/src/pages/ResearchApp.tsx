import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/hooks/use-toast'
import { 
  Send, 
  History, 
  Search, 
  FileText, 
  BookOpen, 
  Scale, 
  Clock,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Bookmark,
  Share2,
  Menu,
  Loader2
} from 'lucide-react'
import { supabase } from '@/lib/supabase'

interface ChatMessage {
  id: string
  query: string
  response: string
  citations: any[]
  timestamp: string
  tags: string[]
}

interface QueryResponse {
  final_answer: string
  citations: any[]
  error?: string
}

export function ResearchApp() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [selectedMessage, setSelectedMessage] = useState<ChatMessage | null>(null)

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory()
  }, [user])

  const loadChatHistory = async () => {
    if (!user) return

    try {
      const { data, error } = await supabase
        .from('chat_history')
        .select('*')
        .eq('user_id', user.id)
        .order('timestamp', { ascending: false })

      if (error) throw error
      setChatHistory(data || [])
      setMessages(data || [])
    } catch (error) {
      console.error('Error loading chat history:', error)
    }
  }

  const submitQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    setLoading(true)
    const currentQuery = query
    setQuery('')

    try {
      // Call FastAPI backend
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: currentQuery, 
          user_id: user?.id 
        }),
      })

      const data: QueryResponse = await response.json()

      if (data.error) {
        throw new Error(data.error)
      }

      // Create new message
      const newMessage: ChatMessage = {
        id: crypto.randomUUID(),
        query: currentQuery,
        response: data.final_answer,
        citations: data.citations || [],
        timestamp: new Date().toISOString(),
        tags: []
      }

      // Save to Supabase
      if (user) {
        const { error } = await supabase
          .from('chat_history')
          .insert({
            user_id: user.id,
            query: newMessage.query,
            response: newMessage.response,
            citations: newMessage.citations,
            tags: newMessage.tags,
            timestamp: newMessage.timestamp
          })

        if (error) {
          console.error('Error saving to database:', error)
        }
      }

      // Update local state
      setMessages(prev => [newMessage, ...prev])
      setChatHistory(prev => [newMessage, ...prev])

    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to process query',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: 'Copied',
      description: 'Response copied to clipboard',
    })
  }

  const saveMessage = async (messageId: string) => {
    // Implement bookmark functionality
    toast({
      title: 'Saved',
      description: 'Message saved to bookmarks',
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      {/* Desktop Sidebar - Chat History */}
      <div className="hidden lg:flex lg:w-80 lg:flex-col border-r">
        <div className="p-4 border-b">
          <h2 className="font-semibold flex items-center gap-2">
            <History className="h-5 w-5" />
            Chat History
          </h2>
        </div>
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-2">
            {chatHistory.map((message) => (
              <Card 
                key={message.id}
                className={`cursor-pointer transition-colors hover:bg-muted/50 ${
                  selectedMessage?.id === message.id ? 'bg-muted' : ''
                }`}
                onClick={() => setSelectedMessage(message)}
              >
                <CardHeader className="p-3">
                  <CardDescription className="text-xs flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDate(message.timestamp)}
                  </CardDescription>
                  <CardTitle className="text-sm line-clamp-2">
                    {message.query}
                  </CardTitle>
                </CardHeader>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {/* Mobile Header */}
        <div className="lg:hidden flex items-center justify-between p-4 border-b">
          <h1 className="font-semibold flex items-center gap-2">
            <Scale className="h-5 w-5" />
            Legal Research
          </h1>
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80">
              <SheetHeader>
                <SheetTitle className="flex items-center gap-2">
                  <History className="h-5 w-5" />
                  Chat History
                </SheetTitle>
              </SheetHeader>
              <ScrollArea className="mt-4 h-[calc(100vh-8rem)]">
                <div className="space-y-2">
                  {chatHistory.map((message) => (
                    <Card 
                      key={message.id}
                      className="cursor-pointer transition-colors hover:bg-muted/50"
                      onClick={() => setSelectedMessage(message)}
                    >
                      <CardHeader className="p-3">
                        <CardDescription className="text-xs flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDate(message.timestamp)}
                        </CardDescription>
                        <CardTitle className="text-sm line-clamp-2">
                          {message.query}
                        </CardTitle>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </SheetContent>
          </Sheet>
        </div>

        {/* Chat Messages */}
        <ScrollArea className="flex-1 p-4 md:p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.length === 0 && !loading && (
              <div className="text-center py-12">
                <Scale className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">
                  Welcome to Legal Research
                </h3>
                <p className="text-muted-foreground mb-6">
                  Ask questions about cases, legal principles, or get help with research
                </p>
                <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 max-w-2xl mx-auto">
                  {[
                    'Summarize Smith v. Jones case',
                    'Find cases about contract disputes',
                    'Explain tort law principles'
                  ].map((example, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      className="text-left h-auto p-3 text-sm"
                      onClick={() => setQuery(example)}
                    >
                      {example}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div key={message.id} className="space-y-4">
                {/* User Query */}
                <div className="flex justify-end">
                  <Card className="max-w-2xl bg-primary text-primary-foreground">
                    <CardContent className="p-4">
                      <p className="text-sm">{message.query}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* AI Response */}
                <div className="flex justify-start">
                  <Card className="max-w-3xl w-full">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Scale className="h-4 w-4" />
                          <span className="text-sm font-medium">Legal Research AI</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(message.response)}
                            className="h-8 w-8 p-0"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => saveMessage(message.id)}
                            className="h-8 w-8 p-0"
                          >
                            <Bookmark className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                          >
                            <Share2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="prose prose-sm max-w-none dark:prose-invert">
                        {message.response.split('\n').map((paragraph, pIndex) => (
                          <p key={pIndex} className="mb-3 last:mb-0">
                            {paragraph}
                          </p>
                        ))}
                      </div>

                      {/* Citations */}
                      {message.citations.length > 0 && (
                        <div className="space-y-2">
                          <Separator />
                          <div>
                            <h4 className="text-sm font-semibold mb-2 flex items-center gap-1">
                              <BookOpen className="h-4 w-4" />
                              Citations
                            </h4>
                            <div className="space-y-2">
                              {message.citations.map((citation, cIndex) => (
                                <Card key={cIndex} className="bg-muted/30">
                                  <CardContent className="p-3">
                                    <p className="text-sm font-medium">
                                      {citation.title || `Citation ${cIndex + 1}`}
                                    </p>
                                    {citation.citation && (
                                      <p className="text-xs text-muted-foreground mt-1">
                                        {citation.citation}
                                      </p>
                                    )}
                                  </CardContent>
                                </Card>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Feedback */}
                      <div className="flex items-center gap-2 pt-2">
                        <Button variant="ghost" size="sm" className="h-8 px-2">
                          <ThumbsUp className="h-3 w-3 mr-1" />
                          Helpful
                        </Button>
                        <Button variant="ghost" size="sm" className="h-8 px-2">
                          <ThumbsDown className="h-3 w-3 mr-1" />
                          Not helpful
                        </Button>
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {formatDate(message.timestamp)}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ))}

            {/* Loading State */}
            {loading && (
              <div className="flex justify-start">
                <Card className="max-w-3xl w-full">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Scale className="h-4 w-4" />
                      <span className="text-sm font-medium">Legal Research AI</span>
                      <Loader2 className="h-4 w-4 animate-spin ml-auto" />
                    </div>
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-4/5" />
                      <Skeleton className="h-4 w-3/4" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Query Input */}
        <div className="border-t p-4 md:p-6">
          <div className="max-w-4xl mx-auto">
            <form onSubmit={submitQuery} className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask about cases, legal principles, or research questions..."
                  className="pl-10 h-12 md:h-14 text-sm md:text-base"
                  disabled={loading}
                />
              </div>
              <Button 
                type="submit" 
                size="lg" 
                disabled={loading || !query.trim()}
                className="h-12 md:h-14 px-4 md:px-6"
              >
                {loading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </form>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              AI can make mistakes. Verify important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}