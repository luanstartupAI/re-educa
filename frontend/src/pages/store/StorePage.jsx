import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { DashboardLayout } from '../../components/layouts/PageLayout';
import { useApi } from '../../lib/api';
import { apiService } from '../../lib/api';
import { formatCurrency, formatPercentage } from '../../lib/utils';
import { 
  Search, 
  Filter, 
  Grid, 
  List, 
  Star, 
  ShoppingCart, 
  Heart, 
  Eye,
  TrendingUp,
  Tag,
  Package,
  Truck,
  Shield,
  Award
} from 'lucide-react';
import { toast } from 'sonner';

export const StorePage = () => {
  const { request, loading } = useApi();
  const [products, setProducts] = React.useState([]);
  const [categories, setCategories] = React.useState([]);
  const [featuredProducts, setFeaturedProducts] = React.useState([]);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState('');
  const [viewMode, setViewMode] = React.useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = React.useState('name');
  // const [priceRange] = React.useState({ min: 0, max: 1000 }); // Unused variable
  const [showFilters, setShowFilters] = React.useState(false);

  // Carregar dados iniciais
  React.useEffect(() => {
    loadStoreData();
  }, []);

  const loadStoreData = async () => {
    try {
      const [productsData, categoriesData, featuredData] = await Promise.all([
        request(() => apiService.products.getAll()),
        request(() => apiService.products.getCategories()),
        request(() => apiService.products.getFeatured()),
      ]);

      setProducts(productsData.products || []);
      setCategories(categoriesData.categories || []);
      setFeaturedProducts(featuredData.products || []);
    } catch {
      console.error('Erro ao carregar dados da loja:');
      toast.error('Erro ao carregar produtos. Tente novamente.');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadStoreData();
      return;
    }

    try {
      const data = await request(() => 
        apiService.products.search({ query: searchQuery })
      );
      setProducts(data.products || []);
    } catch {
      console.error('Erro na busca:');
      toast.error('Erro ao buscar produtos. Tente novamente.');
    }
  };

  const handleCategoryFilter = async (categoryId) => {
    setSelectedCategory(categoryId);
    
    if (!categoryId) {
      loadStoreData();
      return;
    }

    try {
      const data = await request(() => 
        apiService.products.getByCategory(categoryId)
      );
      setProducts(data.products || []);
    } catch {
      console.error('Erro ao filtrar por categoria:');
      toast.error('Erro ao filtrar produtos. Tente novamente.');
    }
  };

  const handleSort = (sortType) => {
    setSortBy(sortType);
    const sortedProducts = [...products].sort((a, b) => {
      switch (sortType) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'price_asc':
          return a.price - b.price;
        case 'price_desc':
          return b.price - a.price;
        case 'rating':
          return b.rating - a.rating;
        case 'newest':
          return new Date(b.created_at) - new Date(a.created_at);
        default:
          return 0;
      }
    });
    setProducts(sortedProducts);
  };

  const addToCart = async (productId) => {
    try {
      await request(() => apiService.orders.addToCart({ product_id: productId, quantity: 1 }));
      toast.success('Produto adicionado ao carrinho!');
    } catch {
      toast.error('Erro ao adicionar ao carrinho. Tente novamente.');
    }
  };

  const toggleWishlist = async () => {
    try {
      // Implementar toggle de wishlist
      toast.success('Produto adicionado aos favoritos!');
    } catch {
      toast.error('Erro ao adicionar aos favoritos. Tente novamente.');
    }
  };

  const getProductCard = (product) => (
    <Card key={product.id} className="group hover:shadow-lg transition-all duration-300">
      <div className="relative">
        <img
          src={product.image_url || '/placeholder-product.jpg'}
          alt={product.name}
          className="w-full h-48 object-cover rounded-t-lg group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-2 right-2 flex space-x-1">
          <Button
            size="sm"
            variant="secondary"
            className="h-8 w-8 p-0 bg-white/90 hover:bg-white"
            onClick={() => toggleWishlist(product.id)}
          >
            <Heart className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="secondary"
            className="h-8 w-8 p-0 bg-white/90 hover:bg-white"
          >
            <Eye className="h-4 w-4" />
          </Button>
        </div>
        {product.discount_percentage > 0 && (
          <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-md text-sm font-medium">
            -{formatPercentage(product.discount_percentage)}
          </div>
        )}
      </div>
      
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-gray-900 dark:text-white line-clamp-2">
            {product.name}
          </h3>
        </div>
        
        <div className="flex items-center space-x-2 mb-3">
          <div className="flex items-center">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`h-4 w-4 ${
                  i < Math.floor(product.rating)
                    ? 'text-yellow-400 fill-current'
                    : 'text-gray-300'
                }`}
              />
            ))}
          </div>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            ({product.review_count})
          </span>
        </div>
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            {product.discount_percentage > 0 ? (
              <>
                <span className="text-lg font-bold text-gray-900 dark:text-white">
                  {formatCurrency(product.discounted_price)}
                </span>
                <span className="text-sm text-gray-500 line-through">
                  {formatCurrency(product.price)}
                </span>
              </>
            ) : (
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {formatCurrency(product.price)}
              </span>
            )}
          </div>
        </div>
        
        <Button
          onClick={() => addToCart(product.id)}
          className="w-full"
          disabled={loading}
        >
          <ShoppingCart className="h-4 w-4 mr-2" />
          Adicionar ao Carrinho
        </Button>
      </CardContent>
    </Card>
  );

  const getProductListItem = (product) => (
    <Card key={product.id} className="flex hover:shadow-lg transition-all duration-300">
      <div className="relative w-32 h-32 flex-shrink-0">
        <img
          src={product.image_url || '/placeholder-product.jpg'}
          alt={product.name}
          className="w-full h-full object-cover rounded-l-lg"
        />
        {product.discount_percentage > 0 && (
          <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-md text-xs font-medium">
            -{formatPercentage(product.discount_percentage)}
          </div>
        )}
      </div>
      
      <div className="flex-1 p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              {product.name}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
              {product.description}
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`h-4 w-4 ${
                    i < Math.floor(product.rating)
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  }`}
                />
              ))}
              <span className="text-sm text-gray-500 dark:text-gray-400 ml-1">
                ({product.review_count})
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {product.discount_percentage > 0 ? (
                <>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {formatCurrency(product.discounted_price)}
                  </span>
                  <span className="text-sm text-gray-500 line-through">
                    {formatCurrency(product.price)}
                  </span>
                </>
              ) : (
                <span className="text-lg font-bold text-gray-900 dark:text-white">
                  {formatCurrency(product.price)}
                </span>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => toggleWishlist(product.id)}
            >
              <Heart className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              onClick={() => addToCart(product.id)}
              disabled={loading}
            >
              <ShoppingCart className="h-4 w-4 mr-2" />
              Adicionar
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Loja Virtual
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Descubra produtos incríveis para sua saúde e bem-estar
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            >
              {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid className="h-4 w-4" />}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Busca e Filtros */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Busca */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Buscar produtos..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Categorias */}
              <div className="flex-shrink-0">
                <select
                  value={selectedCategory}
                  onChange={(e) => handleCategoryFilter(e.target.value)}
                  className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="">Todas as Categorias</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Ordenação */}
              <div className="flex-shrink-0">
                <select
                  value={sortBy}
                  onChange={(e) => handleSort(e.target.value)}
                  className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="name">Nome A-Z</option>
                  <option value="price_asc">Menor Preço</option>
                  <option value="price_desc">Maior Preço</option>
                  <option value="rating">Melhor Avaliados</option>
                  <option value="newest">Mais Recentes</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Produtos em Destaque */}
        {featuredProducts.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-orange-500" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Produtos em Destaque
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {featuredProducts.slice(0, 4).map((product) => getProductCard(product))}
            </div>
          </div>
        )}

        {/* Lista de Produtos */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Todos os Produtos ({products.length})
            </h2>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded-t-lg"></div>
                  <CardContent className="p-4">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-4 w-3/4"></div>
                    <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : products.length > 0 ? (
            <div className={viewMode === 'grid' 
              ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
              : "space-y-4"
            }>
              {products.map((product) => 
                viewMode === 'grid' 
                  ? getProductCard(product)
                  : getProductListItem(product)
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Nenhum produto encontrado
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Tente ajustar os filtros ou buscar por outros termos.
                </p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Benefícios da Loja */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <Truck className="h-8 w-8 text-blue-500 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900 dark:text-white">Entrega Rápida</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Em até 24h</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Shield className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900 dark:text-white">Garantia</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">30 dias</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Award className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900 dark:text-white">Qualidade</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Certificada</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Tag className="h-8 w-8 text-purple-500 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900 dark:text-white">Descontos</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Exclusivos</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};