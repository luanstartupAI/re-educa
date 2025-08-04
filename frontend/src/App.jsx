import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { 
  Heart, 
  Calculator, 
  Calendar, 
  Scale, 
  ShoppingCart, 
  User, 
  Menu, 
  X, 
  Shield, 
  Zap, 
  Target,
  TrendingUp,
  Award,
  Bell,
  Search,
  Filter,
  Star,
  ChevronRight,
  Activity,
  Apple,
  Dumbbell,
  Moon,
  Sun
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import AIAssistantPopup from '@/components/AIAssistantPopup.jsx'
import './App.css'

// Componente de Header com navegação
function Header({ isDark, toggleTheme }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-background/80 border-b border-border">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-lg flex items-center justify-center">
              <Heart className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-green-600">RE-EDUCA</h1>
              <p className="text-xs text-muted-foreground">Store</p>
            </div>
          </Link>

          {/* Navigation Desktop */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/tools" className="text-foreground hover:text-green-600 transition-colors">
              Ferramentas
            </Link>
            <Link to="/store" className="text-foreground hover:text-green-600 transition-colors">
              Loja
            </Link>
            <Link to="/plans" className="text-foreground hover:text-green-600 transition-colors">
              Planos
            </Link>
            <Link to="/about" className="text-foreground hover:text-green-600 transition-colors">
              Sobre
            </Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="hidden md:flex"
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>
            
            <Button variant="ghost" size="icon" className="hidden md:flex">
              <Search className="w-5 h-5" />
            </Button>
            
            <Button variant="ghost" size="icon" className="relative">
              <ShoppingCart className="w-5 h-5" />
              <Badge className="absolute -top-2 -right-2 w-5 h-5 p-0 flex items-center justify-center text-xs bg-orange-500">
                3
              </Badge>
            </Button>

            {isLoggedIn ? (
              <Button variant="ghost" size="icon">
                <User className="w-5 h-5" />
              </Button>
            ) : (
              <div className="hidden md:flex space-x-2">
                <Button variant="outline" size="sm">
                  Entrar
                </Button>
                <Button className="bg-green-600 hover:bg-green-700 text-white" size="sm">
                  Cadastrar
                </Button>
              </div>
            )}

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-border pt-4">
            <nav className="flex flex-col space-y-4">
              <Link to="/tools" className="text-foreground hover:text-green-600 transition-colors">
                Ferramentas
              </Link>
              <Link to="/store" className="text-foreground hover:text-green-600 transition-colors">
                Loja
              </Link>
              <Link to="/plans" className="text-foreground hover:text-green-600 transition-colors">
                Planos
              </Link>
              <Link to="/about" className="text-foreground hover:text-green-600 transition-colors">
                Sobre
              </Link>
              <div className="flex space-x-2 pt-4">
                <Button variant="outline" size="sm" className="flex-1">
                  Entrar
                </Button>
                <Button className="bg-green-600 hover:bg-green-700 text-white flex-1" size="sm">
                  Cadastrar
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}

// Componente Hero Section
function HeroSection() {
  return (
    <section className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-blue-50 opacity-50"></div>
      <div className="container mx-auto px-4 relative">
        <div className="max-w-4xl mx-auto text-center">
          <Badge className="mb-6 bg-green-100 text-green-700 border-green-200">
            🚀 Nova Plataforma de Saúde Inteligente
          </Badge>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-foreground">
            Transforme sua <span className="text-green-600">saúde</span> com 
            <br />inteligência artificial
          </h1>
          
          <p className="text-lg md:text-xl lg:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Ferramentas inteligentes, produtos curados e acompanhamento personalizado 
            para sua jornada de bem-estar. Tudo em uma plataforma segura e fácil de usar.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button className="bg-green-600 hover:bg-green-700 text-white text-lg px-8 py-4">
              Começar Gratuitamente
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
            <Button variant="outline" className="text-lg px-8 py-4">
              Ver Demonstração
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">50k+</div>
              <div className="text-sm text-muted-foreground">Usuários Ativos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">98%</div>
              <div className="text-sm text-muted-foreground">Satisfação</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">1M+</div>
              <div className="text-sm text-muted-foreground">Refeições Registradas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">24/7</div>
              <div className="text-sm text-muted-foreground">Suporte IA</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// Componente de Ferramentas
function ToolsSection() {
  const tools = [
    {
      icon: Calculator,
      title: "Calculadora IMC",
      description: "Calcule e acompanhe seu IMC com histórico inteligente",
      color: "text-green-600",
      bgColor: "bg-green-100",
      features: ["Histórico completo", "Gráficos de progresso", "Metas personalizadas"]
    },
    {
      icon: Calendar,
      title: "Calendário Alimentar",
      description: "Registre refeições com dados nutricionais precisos",
      color: "text-blue-600",
      bgColor: "bg-blue-100",
      features: ["API USDA integrada", "Análise nutricional", "Recomendações IA"]
    },
    {
      icon: Scale,
      title: "Balança de Alimentos",
      description: "Análise nutricional completa de qualquer alimento",
      color: "text-orange-600",
      bgColor: "bg-orange-100",
      features: ["Reconhecimento visual", "Dados precisos", "Comparações"]
    },
    {
      icon: Activity,
      title: "Monitor de Atividades",
      description: "Acompanhe exercícios e atividades físicas",
      color: "text-purple-600",
      bgColor: "bg-purple-100",
      features: ["Integração wearables", "Metas automáticas", "Relatórios detalhados"]
    }
  ]

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-blue-100 text-blue-700 border-blue-200">
            🛠️ Ferramentas Inteligentes
          </Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Tudo que você precisa para sua <span className="text-green-600">saúde</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Ferramentas avançadas com inteligência artificial para monitorar, 
            analisar e otimizar sua jornada de saúde e bem-estar.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {tools.map((tool, index) => (
            <Card key={index} className="bg-card border border-border rounded-lg shadow-sm hover:shadow-md hover:scale-105 transition-all duration-300 group">
              <CardHeader className="text-center">
                <div className={`w-16 h-16 ${tool.bgColor} rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform`}>
                  <tool.icon className={`w-8 h-8 ${tool.color}`} />
                </div>
                <CardTitle className="text-lg">{tool.title}</CardTitle>
                <CardDescription>{tool.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {tool.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center text-sm text-muted-foreground">
                      <div className="w-1.5 h-1.5 bg-green-600 rounded-full mr-2"></div>
                      {feature}
                    </li>
                  ))}
                </ul>
                <Button className="w-full mt-4 bg-secondary hover:bg-secondary/80 text-secondary-foreground">
                  Usar Ferramenta
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

// Componente de Features
function FeaturesSection() {
  const features = [
    {
      icon: Shield,
      title: "Segurança Total",
      description: "Seus dados de saúde protegidos com criptografia de ponta e compliance LGPD completo."
    },
    {
      icon: Zap,
      title: "IA Personalizada",
      description: "Assistente virtual especializado que aprende com seus hábitos e oferece recomendações únicas."
    },
    {
      icon: Target,
      title: "Metas Inteligentes",
      description: "Objetivos adaptativos baseados em seu progresso e perfil de saúde individual."
    },
    {
      icon: TrendingUp,
      title: "Análise Preditiva",
      description: "Identifique tendências e receba alertas preventivos para manter sua saúde em dia."
    },
    {
      icon: Award,
      title: "Gamificação",
      description: "Sistema de recompensas e conquistas que torna sua jornada de saúde mais motivadora."
    },
    {
      icon: Bell,
      title: "Notificações Smart",
      description: "Lembretes inteligentes no momento certo para maximizar seus resultados."
    }
  ]

  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-orange-100 text-orange-700 border-orange-200">
            ✨ Recursos Avançados
          </Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Tecnologia de <span className="text-green-600">ponta</span> para sua saúde
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Recursos inovadores que fazem a diferença na sua jornada de bem-estar, 
            com a segurança e confiabilidade que você merece.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <feature.icon className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Componente de Dashboard Preview
function DashboardPreview() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-purple-100 text-purple-700 border-purple-200">
            📊 Dashboard Inteligente
          </Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Acompanhe seu <span className="text-green-600">progresso</span> em tempo real
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Dashboard personalizado com métricas importantes, insights de IA e 
            visualizações que tornam seus dados de saúde fáceis de entender.
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="bg-card border border-border rounded-lg shadow-sm p-8">
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 text-center space-y-2">
                <Activity className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <div className="text-3xl font-bold text-green-600">24.8</div>
                <div className="text-sm text-muted-foreground font-medium">IMC Atual</div>
                <Progress value={75} className="mt-2" />
              </div>
              <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 text-center space-y-2">
                <Apple className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <div className="text-3xl font-bold text-blue-600">1,847</div>
                <div className="text-sm text-muted-foreground font-medium">Calorias Hoje</div>
                <Progress value={60} className="mt-2" />
              </div>
              <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 text-center space-y-2">
                <Dumbbell className="w-8 h-8 text-orange-600 mx-auto mb-2" />
                <div className="text-3xl font-bold text-orange-600">4/5</div>
                <div className="text-sm text-muted-foreground font-medium">Treinos Semana</div>
                <Progress value={80} className="mt-2" />
              </div>
            </div>

            <div className="text-center">
              <p className="text-muted-foreground mb-4">
                Seus dados são analisados por IA para gerar insights personalizados
              </p>
              <Button className="bg-green-600 hover:bg-green-700 text-white">
                Ver Dashboard Completo
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </section>
  )
}

// Componente de CTA
function CTASection() {
  return (
    <section className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-blue-50 opacity-50"></div>
      <div className="container mx-auto px-4 relative">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Pronto para transformar sua <span className="text-green-600">saúde</span>?
          </h2>
          <p className="text-lg md:text-xl lg:text-2xl text-muted-foreground mb-8">
            Junte-se a milhares de pessoas que já estão vivendo de forma mais saudável 
            com nossa plataforma inteligente. Comece gratuitamente hoje mesmo.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button className="bg-green-600 hover:bg-green-700 text-white text-lg px-8 py-4">
              Começar Gratuitamente
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
            <Button variant="outline" className="text-lg px-8 py-4">
              Falar com Especialista
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            ✅ Sem cartão de crédito • ✅ Cancelamento gratuito • ✅ Suporte 24/7
          </p>
        </div>
      </div>
    </section>
  )
}

// Componente de Footer
function Footer() {
  return (
    <footer className="bg-gray-100 border-t border-border py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-500 rounded-lg flex items-center justify-center">
                <Heart className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-green-600">RE-EDUCA</h3>
                <p className="text-xs text-muted-foreground">Store</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              Transformando vidas através da tecnologia e saúde inteligente.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Ferramentas</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/tools/imc" className="hover:text-green-600 transition-colors">Calculadora IMC</Link></li>
              <li><Link to="/tools/calendar" className="hover:text-green-600 transition-colors">Calendário Alimentar</Link></li>
              <li><Link to="/tools/scale" className="hover:text-green-600 transition-colors">Balança de Alimentos</Link></li>
              <li><Link to="/tools/activity" className="hover:text-green-600 transition-colors">Monitor Atividades</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Empresa</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/about" className="hover:text-green-600 transition-colors">Sobre Nós</Link></li>
              <li><Link to="/privacy" className="hover:text-green-600 transition-colors">Privacidade</Link></li>
              <li><Link to="/terms" className="hover:text-green-600 transition-colors">Termos de Uso</Link></li>
              <li><Link to="/contact" className="hover:text-green-600 transition-colors">Contato</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Suporte</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/help" className="hover:text-green-600 transition-colors">Central de Ajuda</Link></li>
              <li><Link to="/docs" className="hover:text-green-600 transition-colors">Documentação</Link></li>
              <li><Link to="/api" className="hover:text-green-600 transition-colors">API</Link></li>
              <li><Link to="/status" className="hover:text-green-600 transition-colors">Status</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-border mt-8 pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2025 RE-EDUCA Store. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  )
}

// Componente principal da aplicação
function App() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    // Detectar preferência do sistema
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setIsDark(prefersDark)
    
    // Aplicar tema
    if (prefersDark) {
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        <Header isDark={isDark} toggleTheme={toggleTheme} />
        
        <Routes>
          <Route path="/" element={
            <main className="animate-fade-in">
              <HeroSection />
              <ToolsSection />
              <FeaturesSection />
              <DashboardPreview />
              <CTASection />
            </main>
          } />
          <Route path="/tools" element={<div className="py-20 text-center">Ferramentas em desenvolvimento...</div>} />
          <Route path="/store" element={<div className="py-20 text-center">Loja em desenvolvimento...</div>} />
          <Route path="/plans" element={<div className="py-20 text-center">Planos em desenvolvimento...</div>} />
          <Route path="/about" element={<div className="py-20 text-center">Sobre em desenvolvimento...</div>} />
        </Routes>
        
        <Footer />
        
        {/* Assistente IA Popup */}
        <AIAssistantPopup />
      </div>
    </Router>
  )
}

export default App

