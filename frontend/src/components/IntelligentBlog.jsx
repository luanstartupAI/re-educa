import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen,
  TrendingUp,
  Clock,
  User,
  Heart,
  MessageCircle,
  Share2,
  Bookmark,
  Search,
  Filter,
  Calendar,
  Tag,
  Eye,
  ThumbsUp,
  Instagram,
  Sparkles,
  Brain,
  Zap,
  Star,
  ChevronRight,
  Play,
  Pause,
  Volume2,
  VolumeX,
  MoreHorizontal,
  ExternalLink,
  Download,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  AnimatedGradient,
  FloatingElement,
  MagneticButton,
  MorphingCard,
  ParticleSystem,
  GlowingBorder,
  TypingAnimation,
  RippleEffect,
  StaggerContainer
} from '@/components/magic-ui';

// ================================
// BLOG INTELIGENTE COM IA
// ================================

const IntelligentBlog = () => {
  const [posts, setPosts] = useState([]);
  const [featuredPost, setFeaturedPost] = useState(null);
  const [categories, setCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  // Estados para funcionalidades avançadas
  const [readingMode, setReadingMode] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [bookmarkedPosts, setBookmarkedPosts] = useState([]);

  useEffect(() => {
    loadBlogData();
  }, []);

  const loadBlogData = async () => {
    setIsLoading(true);
    try {
      // Simular carregamento de dados (em produção viria da API)
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockPosts = [
        {
          id: 1,
          title: "10 Superalimentos que Transformarão sua Saúde em 2024",
          excerpt: "Descubra os alimentos mais poderosos da natureza e como incorporá-los na sua dieta diária para máxima vitalidade.",
          content: generateMockContent(),
          author: {
            name: "Dr. Ana Nutrição",
            avatar: "/api/placeholder/40/40",
            bio: "Nutricionista especializada em alimentação funcional"
          },
          category: "Nutrição",
          tags: ["superalimentos", "saúde", "nutrição", "bem-estar"],
          publishedAt: "2024-01-15T10:00:00Z",
          readTime: 8,
          views: 12847,
          likes: 892,
          comments: 156,
          featured: true,
          aiGenerated: true,
          instagramSource: "@dra.ana.nutricao",
          image: "/api/placeholder/800/400"
        },
        {
          id: 2,
          title: "Treino HIIT: 15 Minutos para Queimar Gordura",
          excerpt: "Um protocolo científico de alta intensidade que acelera seu metabolismo por até 24 horas após o exercício.",
          content: generateMockContent(),
          author: {
            name: "Coach Marcus Fit",
            avatar: "/api/placeholder/40/40",
            bio: "Personal trainer e especialista em HIIT"
          },
          category: "Fitness",
          tags: ["hiit", "treino", "queima gordura", "exercício"],
          publishedAt: "2024-01-14T15:30:00Z",
          readTime: 6,
          views: 8934,
          likes: 567,
          comments: 89,
          featured: false,
          aiGenerated: true,
          instagramSource: "@coach.marcus.fit",
          image: "/api/placeholder/600/300"
        },
        {
          id: 3,
          title: "Meditação Mindfulness: Guia Completo para Iniciantes",
          excerpt: "Aprenda técnicas simples de mindfulness que podem reduzir o estresse e aumentar sua qualidade de vida.",
          content: generateMockContent(),
          author: {
            name: "Mestre Zen Silva",
            avatar: "/api/placeholder/40/40",
            bio: "Instrutor de meditação e bem-estar mental"
          },
          category: "Bem-estar Mental",
          tags: ["meditação", "mindfulness", "estresse", "mental"],
          publishedAt: "2024-01-13T09:00:00Z",
          readTime: 12,
          views: 15623,
          likes: 1234,
          comments: 203,
          featured: false,
          aiGenerated: true,
          instagramSource: "@mestre.zen.silva",
          image: "/api/placeholder/600/300"
        }
      ];

      const mockCategories = [
        { id: 'all', name: 'Todos', count: mockPosts.length },
        { id: 'nutrition', name: 'Nutrição', count: 1 },
        { id: 'fitness', name: 'Fitness', count: 1 },
        { id: 'mental', name: 'Bem-estar Mental', count: 1 }
      ];

      setPosts(mockPosts);
      setFeaturedPost(mockPosts.find(post => post.featured));
      setCategories(mockCategories);
    } catch (error) {
      console.error('Erro ao carregar dados do blog:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateAIContent = async () => {
    setIsGenerating(true);
    try {
      // Simular geração de conteúdo com IA
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const newPost = {
        id: Date.now(),
        title: "Novo Artigo Gerado por IA",
        excerpt: "Conteúdo personalizado baseado nas últimas tendências do Instagram e pesquisas científicas.",
        content: generateMockContent(),
        author: {
          name: "IA Assistant",
          avatar: "/api/placeholder/40/40",
          bio: "Assistente de IA especializado em saúde"
        },
        category: "IA Generated",
        tags: ["ia", "personalizado", "tendências"],
        publishedAt: new Date().toISOString(),
        readTime: 5,
        views: 0,
        likes: 0,
        comments: 0,
        featured: false,
        aiGenerated: true,
        instagramSource: "Múltiplas fontes",
        image: "/api/placeholder/600/300"
      };

      setPosts(prev => [newPost, ...prev]);
    } catch (error) {
      console.error('Erro ao gerar conteúdo:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const filteredPosts = posts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || 
                           post.category.toLowerCase().includes(selectedCategory);
    return matchesSearch && matchesCategory;
  });

  if (isLoading) {
    return <BlogSkeleton />;
  }

  return (
    <AnimatedGradient className="min-h-screen">
      <ParticleSystem count={20} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header do Blog */}
        <BlogHeader 
          onGenerateContent={generateAIContent}
          isGenerating={isGenerating}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          categories={categories}
        />

        {/* Post em Destaque */}
        {featuredPost && (
          <FeaturedPost 
            post={featuredPost}
            onBookmark={(postId) => setBookmarkedPosts(prev => [...prev, postId])}
          />
        )}

        {/* Grid de Posts */}
        <PostGrid 
          posts={filteredPosts}
          onBookmark={(postId) => setBookmarkedPosts(prev => [...prev, postId])}
          bookmarkedPosts={bookmarkedPosts}
        />

        {/* Sidebar com Widgets */}
        <BlogSidebar />
      </div>
    </AnimatedGradient>
  );
};

// ================================
// COMPONENTES DO BLOG
// ================================

const BlogSkeleton = () => (
  <div className="min-h-screen bg-gray-50 animate-pulse">
    <div className="container mx-auto px-4 py-8">
      <div className="h-20 bg-gray-200 rounded-lg mb-8"></div>
      <div className="h-64 bg-gray-200 rounded-lg mb-8"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-80 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    </div>
  </div>
);

const BlogHeader = ({ 
  onGenerateContent, 
  isGenerating, 
  searchTerm, 
  setSearchTerm, 
  selectedCategory, 
  setSelectedCategory, 
  categories 
}) => (
  <StaggerContainer className="mb-12">
    <div className="text-center mb-8">
      <FloatingElement>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          <TypingAnimation text="Blog Inteligente RE-EDUCA" speed={50} />
        </h1>
      </FloatingElement>
      <p className="text-xl text-gray-600 max-w-3xl mx-auto">
        Conteúdo personalizado gerado por IA, baseado nas últimas tendências do Instagram 
        e pesquisas científicas em saúde e bem-estar.
      </p>
    </div>

    <MorphingCard className="p-6">
      <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
        <div className="flex flex-col sm:flex-row gap-4 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Buscar artigos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-48">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {categories.map(category => (
                <SelectItem key={category.id} value={category.id}>
                  {category.name} ({category.count})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex gap-2">
          <MagneticButton
            onClick={onGenerateContent}
            disabled={isGenerating}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          >
            {isGenerating ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Gerando...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Gerar com IA
              </>
            )}
          </MagneticButton>
          
          <Button variant="outline">
            <Instagram className="w-4 h-4 mr-2" />
            Conectar Instagram
          </Button>
        </div>
      </div>
    </MorphingCard>
  </StaggerContainer>
);

const FeaturedPost = ({ post, onBookmark }) => (
  <StaggerContainer className="mb-12">
    <MorphingCard className="overflow-hidden">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
        <div className="relative h-64 lg:h-auto">
          <img 
            src={post.image} 
            alt={post.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute top-4 left-4">
            <Badge className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white">
              <Star className="w-3 h-3 mr-1" />
              Destaque
            </Badge>
          </div>
          {post.aiGenerated && (
            <div className="absolute top-4 right-4">
              <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                <Brain className="w-3 h-3 mr-1" />
                IA
              </Badge>
            </div>
          )}
        </div>
        
        <div className="p-8">
          <div className="flex items-center gap-2 mb-4">
            <Badge variant="secondary">{post.category}</Badge>
            <span className="text-sm text-gray-500">•</span>
            <span className="text-sm text-gray-500">{post.readTime} min de leitura</span>
          </div>
          
          <h2 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-4 leading-tight">
            {post.title}
          </h2>
          
          <p className="text-gray-600 mb-6 text-lg leading-relaxed">
            {post.excerpt}
          </p>
          
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Avatar className="w-10 h-10">
                <AvatarImage src={post.author.avatar} alt={post.author.name} />
                <AvatarFallback>{post.author.name[0]}</AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium text-gray-900">{post.author.name}</p>
                <p className="text-sm text-gray-500">
                  {new Date(post.publishedAt).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>
            
            {post.instagramSource && (
              <div className="flex items-center gap-1 text-sm text-gray-500">
                <Instagram className="w-4 h-4" />
                {post.instagramSource}
              </div>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                {post.views.toLocaleString()}
              </span>
              <span className="flex items-center gap-1">
                <Heart className="w-4 h-4" />
                {post.likes}
              </span>
              <span className="flex items-center gap-1">
                <MessageCircle className="w-4 h-4" />
                {post.comments}
              </span>
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => onBookmark(post.id)}>
                <Bookmark className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">
                <Share2 className="w-4 h-4" />
              </Button>
              <MagneticButton size="sm">
                Ler Artigo
                <ChevronRight className="w-4 h-4 ml-1" />
              </MagneticButton>
            </div>
          </div>
        </div>
      </div>
    </MorphingCard>
  </StaggerContainer>
);

const PostGrid = ({ posts, onBookmark, bookmarkedPosts }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
    {posts.map((post, index) => (
      <FloatingElement key={post.id} delay={index * 0.1}>
        <PostCard 
          post={post} 
          onBookmark={onBookmark}
          isBookmarked={bookmarkedPosts.includes(post.id)}
        />
      </FloatingElement>
    ))}
  </div>
);

const PostCard = ({ post, onBookmark, isBookmarked }) => (
  <MorphingCard className="overflow-hidden h-full hover-lift">
    <div className="relative">
      <img 
        src={post.image} 
        alt={post.title}
        className="w-full h-48 object-cover"
      />
      <div className="absolute top-3 left-3">
        <Badge variant="secondary" className="bg-white/90 text-gray-700">
          {post.category}
        </Badge>
      </div>
      {post.aiGenerated && (
        <div className="absolute top-3 right-3">
          <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
            <Brain className="w-3 h-3 mr-1" />
            IA
          </Badge>
        </div>
      )}
    </div>
    
    <div className="p-6">
      <div className="flex items-center gap-2 mb-3">
        <Clock className="w-4 h-4 text-gray-400" />
        <span className="text-sm text-gray-500">{post.readTime} min</span>
        {post.instagramSource && (
          <>
            <span className="text-gray-300">•</span>
            <Instagram className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">Instagram</span>
          </>
        )}
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2 leading-tight">
        {post.title}
      </h3>
      
      <p className="text-gray-600 mb-4 line-clamp-3 text-sm leading-relaxed">
        {post.excerpt}
      </p>
      
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Avatar className="w-8 h-8">
            <AvatarImage src={post.author.avatar} alt={post.author.name} />
            <AvatarFallback className="text-xs">{post.author.name[0]}</AvatarFallback>
          </Avatar>
          <div>
            <p className="text-sm font-medium text-gray-900">{post.author.name}</p>
            <p className="text-xs text-gray-500">
              {new Date(post.publishedAt).toLocaleDateString('pt-BR')}
            </p>
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Heart className="w-3 h-3" />
            {post.likes}
          </span>
          <span className="flex items-center gap-1">
            <MessageCircle className="w-3 h-3" />
            {post.comments}
          </span>
        </div>
        
        <div className="flex gap-1">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => onBookmark(post.id)}
            className={isBookmarked ? 'text-yellow-600' : ''}
          >
            <Bookmark className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Share2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  </MorphingCard>
);

const BlogSidebar = () => (
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
    {/* Trending Topics */}
    <MorphingCard className="p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <TrendingUp className="w-5 h-5 text-green-500" />
        Trending Topics
      </h3>
      <div className="space-y-3">
        {['Jejum Intermitente', 'Treino Funcional', 'Mindfulness', 'Suplementação', 'Sono Reparador'].map((topic, index) => (
          <RippleEffect key={index} className="p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{topic}</span>
              <Badge variant="secondary" className="text-xs">#{index + 1}</Badge>
            </div>
          </RippleEffect>
        ))}
      </div>
    </MorphingCard>

    {/* Newsletter */}
    <MorphingCard className="p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Zap className="w-5 h-5 text-yellow-500" />
        Newsletter IA
      </h3>
      <p className="text-sm text-gray-600 mb-4">
        Receba conteúdo personalizado gerado por IA baseado no seu perfil de saúde.
      </p>
      <div className="space-y-3">
        <Input placeholder="Seu email" />
        <MagneticButton className="w-full">
          Inscrever-se
        </MagneticButton>
      </div>
    </MorphingCard>

    {/* Instagram Feed */}
    <MorphingCard className="p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Instagram className="w-5 h-5 text-pink-500" />
        Feed Instagram
      </h3>
      <div className="grid grid-cols-3 gap-2">
        {[...Array(9)].map((_, index) => (
          <div key={index} className="aspect-square bg-gray-200 rounded-lg overflow-hidden">
            <img 
              src={`/api/placeholder/100/100`} 
              alt={`Instagram post ${index + 1}`}
              className="w-full h-full object-cover hover:scale-110 transition-transform duration-300 cursor-pointer"
            />
          </div>
        ))}
      </div>
      <Button variant="outline" className="w-full mt-4">
        <ExternalLink className="w-4 h-4 mr-2" />
        Ver no Instagram
      </Button>
    </MorphingCard>
  </div>
);

// ================================
// FUNÇÕES AUXILIARES
// ================================

const generateMockContent = () => {
  return `
    <p>Este é um artigo gerado por inteligência artificial baseado nas últimas tendências e pesquisas científicas. O conteúdo é personalizado de acordo com as preferências e necessidades dos usuários.</p>
    
    <h2>Introdução</h2>
    <p>A saúde e o bem-estar são fundamentais para uma vida plena e produtiva. Neste artigo, exploramos as mais recentes descobertas e tendências que podem transformar sua jornada de saúde.</p>
    
    <h2>Principais Benefícios</h2>
    <ul>
      <li>Melhoria da qualidade de vida</li>
      <li>Aumento da energia e disposição</li>
      <li>Fortalecimento do sistema imunológico</li>
      <li>Redução do estresse e ansiedade</li>
    </ul>
    
    <h2>Como Implementar</h2>
    <p>A implementação dessas práticas deve ser gradual e consistente. Comece com pequenas mudanças e vá aumentando progressivamente a intensidade e frequência.</p>
    
    <h2>Conclusão</h2>
    <p>Investir em sua saúde é o melhor investimento que você pode fazer. Com as estratégias certas e consistência, você pode alcançar seus objetivos de bem-estar.</p>
  `;
};

export default IntelligentBlog;

