import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { DashboardLayout } from '../../components/layouts/PageLayout';
import { useApi } from '../../lib/api';
import { apiService } from '../../lib/api';
import { formatCurrency, formatDate, formatPercentage } from '../../lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  ShoppingCart, 
  DollarSign,
  Activity,
  Target,
  Award,
  Calendar,
  Clock,
  BarChart3,
  PieChart,
  LineChart,
  ArrowUp,
  ArrowDown,
  Eye,
  Download,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import {
  LineChart as RechartsLineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

export const DashboardPage = () => {
  const { request, loading } = useApi();
  const [dashboardData, setDashboardData] = React.useState({
    metrics: {},
    charts: {},
    recentActivity: [],
    healthData: {}
  });
  const [selectedPeriod, setSelectedPeriod] = React.useState('week');
  const [isRefreshing, setIsRefreshing] = React.useState(false);

  // Carregar dados do dashboard
  React.useEffect(() => {
    loadDashboardData();
  }, [selectedPeriod]);

  const loadDashboardData = async () => {
    try {
      const data = await request(() => 
        apiService.admin.getDashboard({ period: selectedPeriod })
      );
      setDashboardData(data);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      toast.error('Erro ao carregar dados do dashboard. Tente novamente.');
    }
  };

  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      await loadDashboardData();
      toast.success('Dados atualizados com sucesso!');
    } catch (error) {
      toast.error('Erro ao atualizar dados.');
    } finally {
      setIsRefreshing(false);
    }
  };

  // Dados mockados para demonstração
  const mockMetrics = {
    totalUsers: 1247,
    activeUsers: 892,
    totalRevenue: 45678.90,
    totalOrders: 234,
    conversionRate: 3.2,
    averageOrderValue: 195.20
  };

  const mockSalesData = [
    { name: 'Jan', sales: 4000, orders: 240 },
    { name: 'Fev', sales: 3000, orders: 139 },
    { name: 'Mar', sales: 2000, orders: 980 },
    { name: 'Abr', sales: 2780, orders: 390 },
    { name: 'Mai', sales: 1890, orders: 480 },
    { name: 'Jun', sales: 2390, orders: 380 },
    { name: 'Jul', sales: 3490, orders: 430 }
  ];

  const mockHealthData = [
    { name: 'IMC', value: 24.5, target: 22.0, unit: '' },
    { name: 'Peso', value: 70.5, target: 68.0, unit: 'kg' },
    { name: 'Calorias', value: 1850, target: 2000, unit: 'kcal' },
    { name: 'Proteína', value: 85, target: 90, unit: 'g' },
    { name: 'Carboidratos', value: 220, target: 250, unit: 'g' },
    { name: 'Gordura', value: 65, target: 70, unit: 'g' }
  ];

  const mockCategoryData = [
    { name: 'Suplementos', value: 35, color: '#8884d8' },
    { name: 'Equipamentos', value: 25, color: '#82ca9d' },
    { name: 'Vestuário', value: 20, color: '#ffc658' },
    { name: 'Acessórios', value: 15, color: '#ff7300' },
    { name: 'Outros', value: 5, color: '#8dd1e1' }
  ];

  const mockActivityData = [
    { time: '09:00', activity: 'Login no sistema', user: 'João Silva' },
    { time: '09:15', activity: 'Compra realizada', user: 'Maria Santos' },
    { time: '10:30', activity: 'IMC calculado', user: 'Pedro Costa' },
    { time: '11:45', activity: 'Produto avaliado', user: 'Ana Oliveira' },
    { time: '14:20', activity: 'Diário alimentar atualizado', user: 'Carlos Lima' },
    { time: '16:10', activity: 'Meta atingida', user: 'Lucia Ferreira' }
  ];

  const getMetricCard = (title, value, change, icon, color) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {title}
            </p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {value}
            </p>
            <div className="flex items-center space-x-1 mt-2">
              {change > 0 ? (
                <ArrowUp className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowDown className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm font-medium ${
                change > 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                {Math.abs(change)}%
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                vs mês anterior
              </span>
            </div>
          </div>
          <div className={`p-3 rounded-lg ${color}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const getHealthProgressCard = (data) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Target className="h-5 w-5" />
          <span>Metas de Saúde</span>
        </CardTitle>
        <CardDescription>
          Acompanhe seu progresso em relação às metas
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((item, index) => {
            const progress = (item.value / item.target) * 100;
            const isOverTarget = item.value > item.target;
            
            return (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {item.name}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {item.value}{item.unit} / {item.target}{item.unit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      isOverTarget ? 'bg-red-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(progress, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Visão geral da plataforma e métricas de saúde
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="week">Última Semana</option>
              <option value="month">Último Mês</option>
              <option value="quarter">Último Trimestre</option>
              <option value="year">Último Ano</option>
            </select>
            
            <Button
              variant="outline"
              onClick={refreshData}
              disabled={isRefreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>
          </div>
        </div>

        {/* Métricas Principais */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {getMetricCard(
            'Total de Usuários',
            mockMetrics.totalUsers.toLocaleString(),
            12.5,
            <Users className="h-6 w-6 text-blue-500" />,
            'bg-blue-50 dark:bg-blue-900/20'
          )}
          
          {getMetricCard(
            'Receita Total',
            formatCurrency(mockMetrics.totalRevenue),
            8.2,
            <DollarSign className="h-6 w-6 text-green-500" />,
            'bg-green-50 dark:bg-green-900/20'
          )}
          
          {getMetricCard(
            'Pedidos',
            mockMetrics.totalOrders,
            -2.1,
            <ShoppingCart className="h-6 w-6 text-orange-500" />,
            'bg-orange-50 dark:bg-orange-900/20'
          )}
          
          {getMetricCard(
            'Taxa de Conversão',
            `${mockMetrics.conversionRate}%`,
            5.3,
            <TrendingUp className="h-6 w-6 text-purple-500" />,
            'bg-purple-50 dark:bg-purple-900/20'
          )}
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico de Vendas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <LineChart className="h-5 w-5" />
                <span>Vendas e Pedidos</span>
              </CardTitle>
              <CardDescription>
                Evolução das vendas e pedidos ao longo do tempo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsLineChart data={mockSalesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="sales" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="Vendas (R$)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="orders" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="Pedidos"
                  />
                </RechartsLineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Gráfico de Categorias */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <PieChart className="h-5 w-5" />
                <span>Vendas por Categoria</span>
              </CardTitle>
              <CardDescription>
                Distribuição das vendas por categoria de produto
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={mockCategoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {mockCategoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Gráficos de Saúde */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Radar Chart de Saúde */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Perfil de Saúde</span>
              </CardTitle>
              <CardDescription>
                Análise completa do seu perfil de saúde
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={mockHealthData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="name" />
                  <PolarRadiusAxis />
                  <Radar
                    name="Atual"
                    dataKey="value"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                  />
                  <Radar
                    name="Meta"
                    dataKey="target"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.3}
                  />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Progresso das Metas */}
          {getHealthProgressCard(mockHealthData)}
        </div>

        {/* Atividade Recente */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Atividade Recente</span>
            </CardTitle>
            <CardDescription>
              Últimas atividades dos usuários na plataforma
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockActivityData.map((activity, index) => (
                <div key={index} className="flex items-center space-x-4 p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                      <Activity className="h-4 w-4 text-blue-600" />
                    </div>
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {activity.activity}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      por {activity.user}
                    </p>
                  </div>
                  
                  <div className="flex-shrink-0">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {activity.time}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Ações Rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="cursor-pointer hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6 text-center">
              <BarChart3 className="h-8 w-8 text-blue-500 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Relatórios Detalhados
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Acesse relatórios completos e análises avançadas
              </p>
              <Button variant="outline" className="w-full">
                <Eye className="h-4 w-4 mr-2" />
                Ver Relatórios
              </Button>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6 text-center">
              <Download className="h-8 w-8 text-green-500 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Exportar Dados
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Exporte relatórios em PDF, Excel ou CSV
              </p>
              <Button variant="outline" className="w-full">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6 text-center">
              <Award className="h-8 w-8 text-yellow-500 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Metas e Conquistas
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Acompanhe suas metas e conquistas
              </p>
              <Button variant="outline" className="w-full">
                <Target className="h-4 w-4 mr-2" />
                Ver Metas
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};