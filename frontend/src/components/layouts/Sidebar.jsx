import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home,
  Calculator,
  Calendar,
  Activity,
  ShoppingCart,
  Settings,
  BarChart3,
  Users,
  Package,
  CreditCard,
  Heart,
  Target,
  BookOpen,
  Zap,
  Crown
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../lib/api';

export const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      description: 'Visão geral da sua saúde',
    },
    {
      name: 'Calculadora IMC',
      href: '/tools/imc',
      icon: Calculator,
      description: 'Calcule seu índice de massa corporal',
    },
    {
      name: 'Diário Alimentar',
      href: '/tools/food-diary',
      icon: Calendar,
      description: 'Registre suas refeições',
    },
    {
      name: 'Exercícios',
      href: '/tools/exercises',
      icon: Activity,
      description: 'Acompanhe suas atividades físicas',
    },
    {
      name: 'Metas',
      href: '/tools/goals',
      icon: Target,
      description: 'Defina e acompanhe suas metas',
    },
    {
      name: 'Analytics',
      href: '/tools/analytics',
      icon: BarChart3,
      description: 'Análises detalhadas da sua saúde',
    },
  ];

  const storeNavigation = [
    {
      name: 'Produtos',
      href: '/store/products',
      icon: Package,
      description: 'Suplementos e produtos',
    },
    {
      name: 'Carrinho',
      href: '/store/cart',
      icon: ShoppingCart,
      description: 'Seus itens selecionados',
    },
    {
      name: 'Pedidos',
      href: '/store/orders',
      icon: CreditCard,
      description: 'Histórico de compras',
    },
  ];

  const adminNavigation = [
    {
      name: 'Usuários',
      href: '/admin/users',
      icon: Users,
      description: 'Gerenciar usuários',
    },
    {
      name: 'Produtos',
      href: '/admin/products',
      icon: Package,
      description: 'Gerenciar produtos',
    },
    {
      name: 'Analytics',
      href: '/admin/analytics',
      icon: BarChart3,
      description: 'Relatórios gerais',
    },
  ];

  const isActive = (href) => {
    return location.pathname === href || location.pathname.startsWith(href + '/');
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className={cn(
      "fixed left-0 top-16 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 z-40 transition-all duration-300",
      isCollapsed ? "w-16" : "w-64"
    )}>
      <div className="flex flex-col h-full">
        {/* Toggle Button */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="w-full flex items-center justify-center p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {isCollapsed ? (
              <Zap className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            ) : (
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {isCollapsed ? 'Expandir' : 'Recolher'}
              </span>
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-2">
          {/* Health Tools Section */}
          <div className="mb-6">
            {!isCollapsed && (
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Ferramentas de Saúde
              </h3>
            )}
            
            <ul className="space-y-1">
              {navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={cn(
                      "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors group",
                      isActive(item.href)
                        ? "bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                    )}
                    title={isCollapsed ? item.description : undefined}
                  >
                    <item.icon className={cn(
                      "h-5 w-5 mr-3",
                      isCollapsed && "mr-0"
                    )} />
                    {!isCollapsed && (
                      <span className="flex-1">{item.name}</span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Store Section */}
          <div className="mb-6">
            {!isCollapsed && (
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Loja
              </h3>
            )}
            
            <ul className="space-y-1">
              {storeNavigation.map((item) => (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={cn(
                      "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors group",
                      isActive(item.href)
                        ? "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                    )}
                    title={isCollapsed ? item.description : undefined}
                  >
                    <item.icon className={cn(
                      "h-5 w-5 mr-3",
                      isCollapsed && "mr-0"
                    )} />
                    {!isCollapsed && (
                      <span className="flex-1">{item.name}</span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Admin Section */}
          {isAdmin && (
            <div className="mb-6">
              {!isCollapsed && (
                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                  Administração
                </h3>
              )}
              
              <ul className="space-y-1">
                {adminNavigation.map((item) => (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={cn(
                        "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors group",
                        isActive(item.href)
                          ? "bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400"
                          : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                      )}
                      title={isCollapsed ? item.description : undefined}
                    >
                      <item.icon className={cn(
                        "h-5 w-5 mr-3",
                        isCollapsed && "mr-0"
                      )} />
                      {!isCollapsed && (
                        <span className="flex-1">{item.name}</span>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </nav>

        {/* Bottom Section */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <Link
            to="/settings"
            className={cn(
              "flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors",
              isActive('/settings') && "bg-gray-100 dark:bg-gray-800"
            )}
            title={isCollapsed ? "Configurações" : undefined}
          >
            <Settings className={cn(
              "h-5 w-5 mr-3",
              isCollapsed && "mr-0"
            )} />
            {!isCollapsed && <span>Configurações</span>}
          </Link>
        </div>
      </div>
    </div>
  );
};