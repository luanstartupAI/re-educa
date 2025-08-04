import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CreditCard,
  Smartphone,
  Globe,
  Shield,
  CheckCircle,
  AlertCircle,
  Loader2,
  QrCode,
  Copy,
  Download,
  Receipt,
  ArrowLeft,
  Lock,
  Zap,
  Star,
  Gift,
  Percent,
  Clock,
  Users,
  TrendingUp,
  DollarSign,
  Euro,
  PoundSterling,
  Yen,
  Bitcoin,
  Banknote,
  Wallet,
  Building,
  MapPin,
  Mail,
  Phone,
  User,
  Calendar,
  Tag,
  Package,
  ShoppingCart,
  Heart,
  Share2,
  MessageCircle,
  Eye,
  ThumbsUp,
  Award,
  Crown,
  Sparkles,
  Rocket,
  Target,
  Gem,
  Flame,
  Lightning,
  Coins,
  CreditCard as CardIcon,
  Smartphone as PhoneIcon
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import {
  AnimatedGradient,
  FloatingElement,
  MagneticButton,
  MorphingCard,
  ParticleSystem,
  GlowingBorder,
  TypingAnimation,
  RippleEffect,
  StaggerContainer,
  PulsingDot,
  ShimmerEffect,
  CountingNumber,
  ProgressRing,
  WaveAnimation,
  GradientText,
  HolographicCard,
  NeuralNetwork,
  DataStream
} from '@/components/magic-ui';

// ================================
// SISTEMA DE PAGAMENTOS GLOBAL
// ================================

const GlobalPaymentSystem = () => {
  const [currentStep, setCurrentStep] = useState('products');
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [paymentMethod, setPaymentMethod] = useState('');
  const [currency, setCurrency] = useState('BRL');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [userLocation, setUserLocation] = useState('BR');
  const [discountCode, setDiscountCode] = useState('');
  const [appliedDiscount, setAppliedDiscount] = useState(null);

  // Estados para checkout avançado
  const [customerData, setCustomerData] = useState({});
  const [billingAddress, setBillingAddress] = useState({});
  const [subscriptionPlan, setSubscriptionPlan] = useState(null);
  const [pixQrCode, setPixQrCode] = useState('');
  const [installments, setInstallments] = useState(1);

  useEffect(() => {
    detectUserLocation();
    loadProducts();
  }, []);

  const detectUserLocation = async () => {
    try {
      // Simular detecção de localização
      setUserLocation('BR');
      setCurrency('BRL');
    } catch (error) {
      console.error('Erro ao detectar localização:', error);
    }
  };

  const loadProducts = async () => {
    // Simular carregamento de produtos
    const mockProducts = [
      {
        id: 'basic_plan',
        name: 'Plano Básico RE-EDUCA',
        description: 'Acesso às ferramentas essenciais de saúde',
        price: 29.90,
        originalPrice: 49.90,
        currency: 'BRL',
        type: 'subscription',
        features: ['Calculadora IMC', 'Calendário Alimentar', 'Suporte básico'],
        popular: false,
        image: '/api/placeholder/300/200'
      },
      {
        id: 'premium_plan',
        name: 'Plano Premium RE-EDUCA',
        description: 'Experiência completa com IA personalizada',
        price: 59.90,
        originalPrice: 99.90,
        currency: 'BRL',
        type: 'subscription',
        features: ['Todas as ferramentas', 'IA personalizada', 'Blog exclusivo', 'Suporte prioritário'],
        popular: true,
        image: '/api/placeholder/300/200'
      },
      {
        id: 'enterprise_plan',
        name: 'Plano Enterprise',
        description: 'Solução completa para empresas',
        price: 199.90,
        originalPrice: 299.90,
        currency: 'BRL',
        type: 'subscription',
        features: ['Multi-usuários', 'Dashboard empresarial', 'API access', 'Suporte 24/7'],
        popular: false,
        image: '/api/placeholder/300/200'
      }
    ];

    setSelectedProducts(mockProducts);
  };

  const steps = [
    { id: 'products', title: 'Produtos', icon: Package },
    { id: 'customer', title: 'Dados', icon: User },
    { id: 'payment', title: 'Pagamento', icon: CreditCard },
    { id: 'confirmation', title: 'Confirmação', icon: CheckCircle }
  ];

  return (
    <AnimatedGradient className="min-h-screen">
      <ParticleSystem count={30} />
      <NeuralNetwork />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header do Sistema de Pagamentos */}
        <PaymentHeader 
          currentStep={currentStep}
          steps={steps}
          currency={currency}
          setCurrency={setCurrency}
          userLocation={userLocation}
        />

        {/* Conteúdo Principal */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Área Principal */}
          <div className="lg:col-span-2">
            <AnimatePresence mode="wait">
              {currentStep === 'products' && (
                <ProductSelection
                  products={selectedProducts}
                  onNext={() => setCurrentStep('customer')}
                  currency={currency}
                  discountCode={discountCode}
                  setDiscountCode={setDiscountCode}
                  appliedDiscount={appliedDiscount}
                  setAppliedDiscount={setAppliedDiscount}
                />
              )}
              
              {currentStep === 'customer' && (
                <CustomerDataForm
                  customerData={customerData}
                  setCustomerData={setCustomerData}
                  billingAddress={billingAddress}
                  setBillingAddress={setBillingAddress}
                  onNext={() => setCurrentStep('payment')}
                  onBack={() => setCurrentStep('products')}
                />
              )}
              
              {currentStep === 'payment' && (
                <PaymentMethodSelection
                  paymentMethod={paymentMethod}
                  setPaymentMethod={setPaymentMethod}
                  currency={currency}
                  userLocation={userLocation}
                  installments={installments}
                  setInstallments={setInstallments}
                  pixQrCode={pixQrCode}
                  setPixQrCode={setPixQrCode}
                  isProcessing={isProcessing}
                  setIsProcessing={setIsProcessing}
                  onNext={() => setCurrentStep('confirmation')}
                  onBack={() => setCurrentStep('customer')}
                />
              )}
              
              {currentStep === 'confirmation' && (
                <PaymentConfirmation
                  paymentStatus={paymentStatus}
                  selectedProducts={selectedProducts}
                  customerData={customerData}
                  paymentMethod={paymentMethod}
                  onRestart={() => setCurrentStep('products')}
                />
              )}
            </AnimatePresence>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <PaymentSidebar
              selectedProducts={selectedProducts}
              currency={currency}
              appliedDiscount={appliedDiscount}
              currentStep={currentStep}
            />
          </div>
        </div>
      </div>
    </AnimatedGradient>
  );
};

// ================================
// COMPONENTES DO SISTEMA
// ================================

const PaymentHeader = ({ currentStep, steps, currency, setCurrency, userLocation }) => (
  <StaggerContainer className="mb-12">
    <div className="text-center mb-8">
      <FloatingElement>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          <GradientText>Sistema de Pagamentos Global</GradientText>
        </h1>
      </FloatingElement>
      <p className="text-xl text-gray-600 max-w-3xl mx-auto">
        Pagamentos seguros em múltiplas moedas com PIX, Stripe e tecnologia de ponta
      </p>
    </div>

    {/* Progress Steps */}
    <HolographicCard className="p-6">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = step.id === currentStep;
          const isCompleted = steps.findIndex(s => s.id === currentStep) > index;
          
          return (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center">
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all duration-300
                  ${isActive ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white scale-110' : 
                    isCompleted ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'}
                `}>
                  {isCompleted ? <CheckCircle className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
                </div>
                <span className={`text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-500'}`}>
                  {step.title}
                </span>
              </div>
              
              {index < steps.length - 1 && (
                <div className={`
                  flex-1 h-1 mx-4 rounded-full transition-all duration-300
                  ${isCompleted ? 'bg-green-500' : 'bg-gray-200'}
                `} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </HolographicCard>

    {/* Currency Selector */}
    <div className="flex justify-center mt-6">
      <MorphingCard className="p-4">
        <div className="flex items-center gap-4">
          <Globe className="w-5 h-5 text-blue-500" />
          <span className="text-sm font-medium">Moeda:</span>
          <Select value={currency} onValueChange={setCurrency}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="BRL">🇧🇷 BRL</SelectItem>
              <SelectItem value="USD">🇺🇸 USD</SelectItem>
              <SelectItem value="EUR">🇪🇺 EUR</SelectItem>
              <SelectItem value="GBP">🇬🇧 GBP</SelectItem>
              <SelectItem value="JPY">🇯🇵 JPY</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </MorphingCard>
    </div>
  </StaggerContainer>
);

const ProductSelection = ({ 
  products, 
  onNext, 
  currency, 
  discountCode, 
  setDiscountCode, 
  appliedDiscount, 
  setAppliedDiscount 
}) => {
  const [selectedPlan, setSelectedPlan] = useState(null);

  const applyDiscount = () => {
    // Simular aplicação de desconto
    if (discountCode.toLowerCase() === 'welcome20') {
      setAppliedDiscount({
        code: 'WELCOME20',
        type: 'percentage',
        value: 20,
        description: '20% de desconto para novos usuários'
      });
    } else if (discountCode.toLowerCase() === 'save50') {
      setAppliedDiscount({
        code: 'SAVE50',
        type: 'fixed',
        value: 50,
        description: 'R$ 50 de desconto'
      });
    } else {
      setAppliedDiscount(null);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8"
    >
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Escolha seu Plano</h2>
        <p className="text-gray-600">Selecione o plano ideal para suas necessidades de saúde e bem-estar</p>
      </div>

      {/* Planos */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {products.map((product, index) => (
          <FloatingElement key={product.id} delay={index * 0.1}>
            <PlanCard
              product={product}
              currency={currency}
              isSelected={selectedPlan?.id === product.id}
              onSelect={setSelectedPlan}
              appliedDiscount={appliedDiscount}
            />
          </FloatingElement>
        ))}
      </div>

      {/* Código de Desconto */}
      <MorphingCard className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Gift className="w-5 h-5 text-green-500" />
          Código de Desconto
        </h3>
        <div className="flex gap-3">
          <Input
            placeholder="Digite seu código"
            value={discountCode}
            onChange={(e) => setDiscountCode(e.target.value)}
            className="flex-1"
          />
          <MagneticButton onClick={applyDiscount} variant="outline">
            Aplicar
          </MagneticButton>
        </div>
        
        {appliedDiscount && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg"
          >
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="w-4 h-4" />
              <span className="font-medium">{appliedDiscount.description}</span>
            </div>
          </motion.div>
        )}
      </MorphingCard>

      {/* Botão Continuar */}
      <div className="flex justify-end">
        <MagneticButton
          onClick={onNext}
          disabled={!selectedPlan}
          className="px-8 py-3"
        >
          Continuar
          <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
        </MagneticButton>
      </div>
    </motion.div>
  );
};

const PlanCard = ({ product, currency, isSelected, onSelect, appliedDiscount }) => {
  const formatPrice = (price) => {
    const currencySymbols = {
      BRL: 'R$',
      USD: '$',
      EUR: '€',
      GBP: '£',
      JPY: '¥'
    };
    
    let finalPrice = price;
    if (appliedDiscount) {
      if (appliedDiscount.type === 'percentage') {
        finalPrice = price * (1 - appliedDiscount.value / 100);
      } else {
        finalPrice = Math.max(0, price - appliedDiscount.value);
      }
    }
    
    return `${currencySymbols[currency]} ${finalPrice.toFixed(2)}`;
  };

  return (
    <HolographicCard 
      className={`relative overflow-hidden cursor-pointer transition-all duration-300 ${
        isSelected ? 'ring-2 ring-blue-500 scale-105' : 'hover:scale-102'
      } ${product.popular ? 'border-2 border-yellow-400' : ''}`}
      onClick={() => onSelect(product)}
    >
      {product.popular && (
        <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-center py-2 text-sm font-medium">
          <Star className="w-4 h-4 inline mr-1" />
          Mais Popular
        </div>
      )}
      
      <div className={`p-6 ${product.popular ? 'pt-12' : ''}`}>
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-2">{product.name}</h3>
          <p className="text-gray-600 text-sm mb-4">{product.description}</p>
          
          <div className="space-y-2">
            {product.originalPrice > product.price && (
              <div className="text-sm text-gray-500 line-through">
                {formatPrice(product.originalPrice)}
              </div>
            )}
            <div className="text-3xl font-bold text-gray-900">
              {formatPrice(product.price)}
              <span className="text-sm font-normal text-gray-500">/mês</span>
            </div>
            {appliedDiscount && (
              <div className="text-sm text-green-600 font-medium">
                Desconto aplicado!
              </div>
            )}
          </div>
        </div>

        <div className="space-y-3 mb-6">
          {product.features.map((feature, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
              <span>{feature}</span>
            </div>
          ))}
        </div>

        <MagneticButton 
          className={`w-full ${isSelected ? 'bg-blue-600' : ''}`}
          variant={isSelected ? 'default' : 'outline'}
        >
          {isSelected ? 'Selecionado' : 'Selecionar Plano'}
        </MagneticButton>
      </div>
    </HolographicCard>
  );
};

const PaymentSidebar = ({ selectedProducts, currency, appliedDiscount, currentStep }) => {
  const calculateTotal = () => {
    let total = selectedProducts.reduce((sum, product) => sum + product.price, 0);
    
    if (appliedDiscount) {
      if (appliedDiscount.type === 'percentage') {
        total = total * (1 - appliedDiscount.value / 100);
      } else {
        total = Math.max(0, total - appliedDiscount.value);
      }
    }
    
    return total;
  };

  return (
    <div className="space-y-6">
      {/* Resumo do Pedido */}
      <HolographicCard className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <ShoppingCart className="w-5 h-5 text-blue-500" />
          Resumo do Pedido
        </h3>
        
        <div className="space-y-4">
          {selectedProducts.map(product => (
            <div key={product.id} className="flex justify-between items-start">
              <div className="flex-1">
                <p className="font-medium text-sm">{product.name}</p>
                <p className="text-xs text-gray-500">{product.description}</p>
              </div>
              <p className="font-medium">R$ {product.price.toFixed(2)}</p>
            </div>
          ))}
          
          {appliedDiscount && (
            <div className="flex justify-between items-center text-green-600">
              <span className="text-sm">Desconto ({appliedDiscount.code})</span>
              <span className="font-medium">
                -{appliedDiscount.type === 'percentage' ? `${appliedDiscount.value}%` : `R$ ${appliedDiscount.value}`}
              </span>
            </div>
          )}
          
          <Separator />
          
          <div className="flex justify-between items-center text-lg font-bold">
            <span>Total</span>
            <span>R$ {calculateTotal().toFixed(2)}</span>
          </div>
        </div>
      </HolographicCard>

      {/* Segurança */}
      <MorphingCard className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-green-500" />
          Segurança Garantida
        </h3>
        
        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-green-500" />
            <span>Criptografia SSL 256-bit</span>
          </div>
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-green-500" />
            <span>Certificado PCI DSS</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Dados protegidos LGPD</span>
          </div>
        </div>
      </MorphingCard>

      {/* Suporte */}
      <MorphingCard className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-blue-500" />
          Precisa de Ajuda?
        </h3>
        
        <div className="space-y-3">
          <Button variant="outline" className="w-full justify-start">
            <MessageCircle className="w-4 h-4 mr-2" />
            Chat ao Vivo
          </Button>
          <Button variant="outline" className="w-full justify-start">
            <Phone className="w-4 h-4 mr-2" />
            (11) 9999-9999
          </Button>
          <Button variant="outline" className="w-full justify-start">
            <Mail className="w-4 h-4 mr-2" />
            suporte@re-educa.com
          </Button>
        </div>
      </MorphingCard>
    </div>
  );
};

export default GlobalPaymentSystem;

