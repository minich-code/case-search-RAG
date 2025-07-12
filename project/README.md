# Legal Research App - Responsive AI-Powered Legal Research Platform

A comprehensive, fully responsive legal research web application built with React, TypeScript, Tailwind CSS, and Supabase. This application provides advanced case analysis, intelligent search, and AI-powered legal insights optimized for all devices.

## 🌟 Features

### Core Functionality
- **AI-Powered Legal Research**: Advanced case analysis and query processing
- **Intelligent Case Search**: Find relevant cases with AI-powered ranking
- **Argument Generation**: AI-assisted legal argument construction
- **Real-time Chat Interface**: ChatGPT-style interaction with legal AI
- **Citation Management**: Comprehensive legal citation tracking
- **Chat History**: Persistent conversation history with search

### Authentication & User Management
- **Email/Password Authentication**: Secure user registration and login
- **Google OAuth Integration**: One-click sign-in with Google
- **User Profile Management**: Complete user account management
- **Session Management**: Secure session handling with Supabase

### Responsive Design
- **Mobile-First Design**: Optimized for all devices (320px to 2560px+)
- **Touch-Friendly Interface**: Minimum 44px touch targets
- **Adaptive Navigation**: Hamburger menu on mobile, full nav on desktop
- **Responsive Typography**: Scales appropriately across screen sizes
- **Cross-Platform Compatibility**: Works on iOS, Android, and desktop browsers

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework with responsive design
- **Shadcn/ui** - High-quality component library
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icon library

### Backend & Database
- **Supabase** - Backend-as-a-Service
  - PostgreSQL database
  - Authentication & authorization
  - Real-time subscriptions
  - Row Level Security (RLS)
- **FastAPI Integration** - External API for query processing

### Development Tools
- **Vite** - Fast build tool and dev server
- **ESLint** - Code linting and formatting
- **PostCSS** - CSS processing with Autoprefixer

## 📱 Responsive Breakpoints

### Mobile (320px - 767px)
- Single-column layout
- Hamburger navigation menu
- Full-width search bar (min-height: 48px)
- Bottom sheet for chat history
- Touch-optimized controls

### Tablet (768px - 1023px)
- Two-column layouts where appropriate
- Condensed navigation bar
- Collapsible sidebar
- Optimized touch targets

### Desktop (1024px+)
- Three-column layouts
- Full navigation bar
- Persistent sidebar
- Hover states and micro-interactions

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Supabase account
- FastAPI backend running on `http://localhost:8000`

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd legal-research-app
```

2. **Install dependencies**
```bash
npm install
```

3. **Environment Setup**
Create a `.env.local` file in the root directory:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. **Start the development server**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## 🗄️ Database Schema

### Supabase Tables

#### Users Table
```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  plan TEXT DEFAULT 'free',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Chat History Table
```sql
CREATE TABLE chat_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  query TEXT NOT NULL,
  response TEXT NOT NULL,
  citations JSONB DEFAULT '[]',
  tags TEXT[] DEFAULT '{}',
  timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

#### Case Metadata Table
```sql
CREATE TABLE case_metadata (
  case_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  citation TEXT NOT NULL,
  summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔧 API Integration

### FastAPI Backend Integration
The app connects to a FastAPI backend for query processing:

**Endpoint**: `POST http://localhost:8000/api/query`

**Request Body**:
```json
{
  "query": "string",
  "user_id": "string"
}
```

**Response**:
```json
{
  "final_answer": "string",
  "citations": [],
  "error": "string"
}
```

## 📋 Component Architecture

### Layout Components
- **Header**: Responsive navigation with mobile menu
- **ThemeToggle**: Dark/light mode switcher
- **ProtectedRoute**: Authentication wrapper

### Page Components
- **Landing**: Marketing homepage with features
- **Auth**: Authentication with email/Google sign-in
- **Pricing**: Responsive pricing tiers
- **ResearchApp**: Main chat interface

### UI Components
- Built with Shadcn/ui for consistency
- Fully responsive and accessible
- Custom responsive utilities

## 🎨 Design System

### Colors
- **Primary**: Blue (#3B82F6) - Legal professional theme
- **Secondary**: Neutral grays for text and backgrounds
- **Accent**: Success, warning, and error states
- **Dark Mode**: Complete dark theme support

### Typography
- **Font Family**: Inter (system fallbacks)
- **Responsive Scaling**: 
  - Mobile: text-sm to text-base
  - Tablet: text-base to text-lg  
  - Desktop: text-lg to text-2xl

### Spacing
- **8px Grid System**: Consistent spacing scale
- **Responsive Margins**: p-4 (mobile) to p-8 (desktop)
- **Touch Targets**: Minimum 44px on mobile

## 🧪 Testing Strategy

### Responsive Testing Checklist
- [ ] iPhone SE (375px)
- [ ] iPhone 12/13 (390px)
- [ ] iPhone 12/13 Pro Max (428px)
- [ ] iPad (768px)
- [ ] iPad Pro (1024px)
- [ ] Desktop (1440px)
- [ ] Large Desktop (1920px+)

### Browser Testing
- [ ] Chrome (mobile/desktop)
- [ ] Safari (iOS/macOS)
- [ ] Firefox
- [ ] Edge

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel --prod
```

### Deploy to Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

## ⚡ Performance Optimizations

### Mobile Performance
- Lazy loading of components
- Optimized images with responsive srcsets
- Minimal JavaScript bundle size
- Service worker for caching (future enhancement)

### Desktop Performance
- Code splitting by route
- Tree shaking for unused code
- CSS purging in production
- CDN deployment for static assets

## 🔐 Security Features

### Authentication Security
- JWT token management
- Secure session storage
- Row Level Security (RLS) in Supabase
- OAuth integration with Google

### Data Protection
- Client-side validation
- Server-side authorization
- Encrypted data transmission
- GDPR compliance ready

## 📱 Mobile-Specific Features

### iOS Optimizations
- Safari viewport handling
- Touch callout prevention
- Smooth scrolling
- Home screen app icon support

### Android Optimizations
- Chrome viewport settings
- Material Design interactions
- Performance optimizations
- PWA capabilities (future)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Known Issues

- FastAPI backend must be running locally
- Supabase credentials need to be configured
- Some advanced features require subscription

## 🔮 Future Enhancements

- Progressive Web App (PWA) support
- Offline functionality
- Voice input for queries
- Advanced document upload
- Team collaboration features
- White-label solutions

## 📞 Support

For technical support or questions about the responsive design implementation, please open an issue in the GitHub repository.

---

**Built with ❤️ for legal professionals who demand excellence across all devices.**