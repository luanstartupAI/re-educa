import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { DashboardLayout } from '../../components/layouts/PageLayout';
import { useApi } from '../../lib/api';
import { apiService } from '../../lib/api';
import { calculateIMC, classifyIMC, formatWeight, formatHeight } from '../../lib/utils';
import { Calculator, TrendingUp, TrendingDown, Target, Info, Save, History } from 'lucide-react';
import { toast } from 'sonner';

// Schema de validação
const imcSchema = z.object({
  weight: z.number().min(20, 'Peso deve ser pelo menos 20kg').max(300, 'Peso deve ser no máximo 300kg'),
  height: z.number().min(0.5, 'Altura deve ser pelo menos 0.5m').max(3, 'Altura deve ser no máximo 3m'),
});

export const IMCCalculatorPage = () => {
  const { request, loading } = useApi();
  const [imcResult, setImcResult] = React.useState(null);
  const [history, setHistory] = React.useState([]);
  const [showHistory, setShowHistory] = React.useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(imcSchema),
  });

  const watchedWeight = watch('weight');
  const watchedHeight = watch('height');

  // Calcular IMC em tempo real
  React.useEffect(() => {
    if (watchedWeight && watchedHeight && watchedWeight > 0 && watchedHeight > 0) {
      const imc = calculateIMC(watchedWeight, watchedHeight);
      if (imc) {
        const classification = classifyIMC(imc);
        setImcResult({
          imc: imc.toFixed(1),
          classification: classification.classification,
          color: classification.color,
        });
      }
    } else {
      setImcResult(null);
    }
  }, [watchedWeight, watchedHeight]);

  // Carregar histórico
  React.useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await request(() => apiService.health.getIMCHistory());
      setHistory(data.history || []);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    }
  };

  const onSubmit = async (data) => {
    try {
      const imc = calculateIMC(data.weight, data.height);
      const classification = classifyIMC(imc);

      const result = await request(() => 
        apiService.health.calculateIMC({
          weight: data.weight,
          height: data.height,
          imc: imc,
          classification: classification.classification,
        })
      );

      toast.success('IMC calculado e salvo com sucesso!');
      loadHistory(); // Recarregar histórico
      reset();
    } catch (error) {
      toast.error('Erro ao salvar IMC. Tente novamente.');
    }
  };

  const getImcColor = (imc) => {
    if (imc < 18.5) return 'text-blue-600';
    if (imc < 25) return 'text-green-600';
    if (imc < 30) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getImcBgColor = (imc) => {
    if (imc < 18.5) return 'bg-blue-50 dark:bg-blue-900/20';
    if (imc < 25) return 'bg-green-50 dark:bg-green-900/20';
    if (imc < 30) return 'bg-yellow-50 dark:bg-yellow-900/20';
    return 'bg-red-50 dark:bg-red-900/20';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Calculadora IMC
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Calcule seu Índice de Massa Corporal e acompanhe seu progresso
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center space-x-2"
          >
            <History className="h-4 w-4" />
            <span>{showHistory ? 'Ocultar' : 'Ver'} Histórico</span>
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Calculadora */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calculator className="h-5 w-5" />
                <span>Calcular IMC</span>
              </CardTitle>
              <CardDescription>
                Digite seu peso e altura para calcular seu IMC
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {/* Peso */}
                <div className="space-y-2">
                  <label htmlFor="weight" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Peso (kg)
                  </label>
                  <Input
                    id="weight"
                    type="number"
                    step="0.1"
                    placeholder="Ex: 70.5"
                    {...register('weight', { valueAsNumber: true })}
                  />
                  {errors.weight && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.weight.message}
                    </p>
                  )}
                </div>

                {/* Altura */}
                <div className="space-y-2">
                  <label htmlFor="height" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Altura (m)
                  </label>
                  <Input
                    id="height"
                    type="number"
                    step="0.01"
                    placeholder="Ex: 1.75"
                    {...register('height', { valueAsNumber: true })}
                  />
                  {errors.height && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.height.message}
                    </p>
                  )}
                </div>

                {/* Resultado em tempo real */}
                {imcResult && (
                  <div className={`p-4 rounded-lg border ${getImcBgColor(parseFloat(imcResult.imc))}`}>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                        {imcResult.imc}
                      </div>
                      <div className={`text-lg font-medium ${getImcColor(parseFloat(imcResult.imc))}`}>
                        {imcResult.classification}
                      </div>
                    </div>
                  </div>
                )}

                {/* Botão calcular */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading || !imcResult}
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Salvando...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Save className="h-4 w-4" />
                      <span>Calcular e Salvar</span>
                    </div>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Informações sobre IMC */}
          <div className="space-y-6">
            {/* Classificação IMC */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="h-5 w-5" />
                  <span>Classificação IMC</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <span className="font-medium">Abaixo do peso</span>
                    <span className="text-blue-600 font-bold">&lt; 18.5</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <span className="font-medium">Peso normal</span>
                    <span className="text-green-600 font-bold">18.5 - 24.9</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <span className="font-medium">Sobrepeso</span>
                    <span className="text-yellow-600 font-bold">25.0 - 29.9</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <span className="font-medium">Obesidade</span>
                    <span className="text-red-600 font-bold">&gt;= 30.0</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Dicas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Info className="h-5 w-5" />
                  <span>Dicas Importantes</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p>O IMC é uma ferramenta de triagem, não um diagnóstico definitivo.</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p>Consulte um profissional de saúde para avaliação completa.</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p>Atletas podem ter IMC elevado devido à massa muscular.</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p>Idosos podem ter IMC diferente devido à perda de massa muscular.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Histórico */}
        {showHistory && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Histórico de IMC</span>
              </CardTitle>
              <CardDescription>
                Acompanhe sua evolução ao longo do tempo
              </CardDescription>
            </CardHeader>
            <CardContent>
              {history.length > 0 ? (
                <div className="space-y-3">
                  {history.map((entry, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`p-2 rounded-lg ${getImcBgColor(entry.imc)}`}>
                          <span className={`font-bold ${getImcColor(entry.imc)}`}>
                            {entry.imc}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {entry.classification}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {formatWeight(entry.weight)} • {formatHeight(entry.height)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {new Date(entry.created_at).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <TrendingDown className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">
                    Nenhum registro encontrado. Calcule seu IMC para começar!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
};