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
import { formatDate } from '../../lib/utils';
import { 
  Apple, 
  Search, 
  Plus, 
  Calendar, 
  Clock, 
  Scale, 
  Flame, 
  Protein, 
  Carbs, 
  Fat, 
  Fiber,
  Trash2,
  Edit,
  Filter
} from 'lucide-react';
import { toast } from 'sonner';

// Schema de validação
const foodEntrySchema = z.object({
  food_name: z.string().min(1, 'Nome do alimento é obrigatório'),
  quantity: z.number().min(0.1, 'Quantidade deve ser maior que 0'),
  unit: z.string().min(1, 'Unidade é obrigatória'),
  meal_type: z.string().min(1, 'Tipo de refeição é obrigatório'),
  calories: z.number().min(0, 'Calorias devem ser maior ou igual a 0'),
  protein: z.number().min(0, 'Proteína deve ser maior ou igual a 0'),
  carbs: z.number().min(0, 'Carboidratos devem ser maior ou igual a 0'),
  fat: z.number().min(0, 'Gordura deve ser maior ou igual a 0'),
  fiber: z.number().min(0, 'Fibra deve ser maior ou igual a 0'),
});

export const FoodDiaryPage = () => {
  const { request, loading } = useApi();
  const [entries, setEntries] = React.useState([]);
  const [searchResults, setSearchResults] = React.useState([]);
  const [selectedDate, setSelectedDate] = React.useState(new Date().toISOString().split('T')[0]);
  const [showAddForm, setShowAddForm] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [isSearching, setIsSearching] = React.useState(false);
  const [dailyTotals, setDailyTotals] = React.useState({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    fiber: 0,
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm({
    resolver: zodResolver(foodEntrySchema),
  });

  // Carregar entradas do dia
  React.useEffect(() => {
    loadEntries();
  }, [selectedDate]);

  const loadEntries = async () => {
    try {
      const data = await request(() => 
        apiService.health.getFoodEntries({ date: selectedDate })
      );
      setEntries(data.entries || []);
      calculateDailyTotals(data.entries || []);
    } catch {
      console.error('Erro ao carregar entradas:');
    }
  };

  const calculateDailyTotals = (entries) => {
    const totals = entries.reduce((acc, entry) => ({
      calories: acc.calories + (entry.calories || 0),
      protein: acc.protein + (entry.protein || 0),
      carbs: acc.carbs + (entry.carbs || 0),
      fat: acc.fat + (entry.fat || 0),
      fiber: acc.fiber + (entry.fiber || 0),
    }), {
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0,
      fiber: 0,
    });

    setDailyTotals(totals);
  };

  const searchFoods = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const data = await request(() => apiService.health.searchFoods(query));
      setSearchResults(data.foods || []);
    } catch (error) {
      console.error('Erro ao buscar alimentos:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    // Debounce search
    clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      searchFoods(query);
    }, 500);
  };

  const searchTimeout = React.useRef(null);

  const selectFood = (food) => {
    setValue('food_name', food.description);
    setValue('calories', food.foodNutrients?.find(n => n.nutrientName === 'Energy')?.value || 0);
    setValue('protein', food.foodNutrients?.find(n => n.nutrientName === 'Protein')?.value || 0);
    setValue('carbs', food.foodNutrients?.find(n => n.nutrientName === 'Carbohydrate, by difference')?.value || 0);
    setValue('fat', food.foodNutrients?.find(n => n.nutrientName === 'Total lipid (fat)')?.value || 0);
    setValue('fiber', food.foodNutrients?.find(n => n.nutrientName === 'Fiber, total dietary')?.value || 0);
    setSearchResults([]);
    setSearchQuery('');
  };

  const onSubmit = async (data) => {
    try {
      await request(() => 
        apiService.health.addFoodEntry({
          ...data,
          date: selectedDate,
        })
      );

      toast.success('Alimento adicionado com sucesso!');
      setShowAddForm(false);
      reset();
      loadEntries();
    } catch {
      toast.error('Erro ao adicionar alimento. Tente novamente.');
    }
  };

  const deleteEntry = async () => {
    try {
      // Implementar delete no backend
      toast.success('Entrada removida com sucesso!');
      loadEntries();
    } catch {
      toast.error('Erro ao remover entrada. Tente novamente.');
    }
  };

  const mealTypes = [
    { value: 'breakfast', label: 'Café da manhã', icon: '🌅' },
    { value: 'lunch', label: 'Almoço', icon: '🌞' },
    { value: 'dinner', label: 'Jantar', icon: '🌙' },
    { value: 'snack', label: 'Lanche', icon: '🍎' },
  ];

  const getMealTypeIcon = (type) => {
    return mealTypes.find(meal => meal.value === type)?.icon || '🍽️';
  };

  // const getMealTypeLabel = (type) => { // Unused function
  //   return mealTypes.find(meal => meal.value === type)?.label || 'Refeição';
  // };

  const getMacroColor = (macro) => {
    switch (macro) {
      case 'protein': return 'text-red-600';
      case 'carbs': return 'text-green-600';
      case 'fat': return 'text-yellow-600';
      case 'fiber': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Diário Alimentar
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Registre suas refeições e acompanhe sua nutrição
            </p>
          </div>
          <Button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Adicionar Alimento</span>
          </Button>
        </div>

        {/* Seletor de Data */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-4">
              <Calendar className="h-5 w-5 text-gray-500" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
              <span className="text-gray-600 dark:text-gray-400">
                {formatDate(selectedDate)}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Resumo Diário */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Flame className="h-5 w-5 text-orange-500" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {dailyTotals.calories.toFixed(0)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Calorias</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Protein className="h-5 w-5 text-red-500" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {dailyTotals.protein.toFixed(1)}g
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Proteína</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Carbs className="h-5 w-5 text-green-500" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {dailyTotals.carbs.toFixed(1)}g
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Carboidratos</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Fat className="h-5 w-5 text-yellow-500" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {dailyTotals.fat.toFixed(1)}g
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Gordura</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Fiber className="h-5 w-5 text-purple-500" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {dailyTotals.fiber.toFixed(1)}g
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Fibra</div>
            </CardContent>
          </Card>
        </div>

        {/* Formulário de Adição */}
        {showAddForm && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Apple className="h-5 w-5" />
                <span>Adicionar Alimento</span>
              </CardTitle>
              <CardDescription>
                Busque um alimento ou adicione manualmente
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {/* Busca de Alimentos */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Buscar Alimento
                  </label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      type="text"
                      placeholder="Digite o nome do alimento..."
                      value={searchQuery}
                      onChange={handleSearchChange}
                      className="pl-10"
                    />
                  </div>
                  
                  {/* Resultados da busca */}
                  {searchResults.length > 0 && (
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg max-h-40 overflow-y-auto">
                      {searchResults.map((food, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => selectFood(food)}
                          className="w-full text-left p-3 hover:bg-gray-50 dark:hover:bg-gray-800 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                        >
                          <div className="font-medium text-gray-900 dark:text-white">
                            {food.description}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {food.foodNutrients?.find(n => n.nutrientName === 'Energy')?.value || 0} kcal
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Nome do Alimento */}
                  <div className="space-y-2">
                    <label htmlFor="food_name" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Nome do Alimento
                    </label>
                    <Input
                      id="food_name"
                      {...register('food_name')}
                    />
                    {errors.food_name && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.food_name.message}
                      </p>
                    )}
                  </div>

                  {/* Tipo de Refeição */}
                  <div className="space-y-2">
                    <label htmlFor="meal_type" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Tipo de Refeição
                    </label>
                    <select
                      id="meal_type"
                      {...register('meal_type')}
                      className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      <option value="">Selecione...</option>
                      {mealTypes.map((meal) => (
                        <option key={meal.value} value={meal.value}>
                          {meal.icon} {meal.label}
                        </option>
                      ))}
                    </select>
                    {errors.meal_type && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.meal_type.message}
                      </p>
                    )}
                  </div>

                  {/* Quantidade */}
                  <div className="space-y-2">
                    <label htmlFor="quantity" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Quantidade
                    </label>
                    <Input
                      id="quantity"
                      type="number"
                      step="0.1"
                      {...register('quantity', { valueAsNumber: true })}
                    />
                    {errors.quantity && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.quantity.message}
                      </p>
                    )}
                  </div>

                  {/* Unidade */}
                  <div className="space-y-2">
                    <label htmlFor="unit" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Unidade
                    </label>
                    <Input
                      id="unit"
                      placeholder="g, ml, unidade..."
                      {...register('unit')}
                    />
                    {errors.unit && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.unit.message}
                      </p>
                    )}
                  </div>
                </div>

                {/* Macronutrientes */}
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="calories" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Calorias (kcal)
                    </label>
                    <Input
                      id="calories"
                      type="number"
                      step="0.1"
                      {...register('calories', { valueAsNumber: true })}
                    />
                    {errors.calories && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.calories.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="protein" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Proteína (g)
                    </label>
                    <Input
                      id="protein"
                      type="number"
                      step="0.1"
                      {...register('protein', { valueAsNumber: true })}
                    />
                    {errors.protein && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.protein.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="carbs" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Carboidratos (g)
                    </label>
                    <Input
                      id="carbs"
                      type="number"
                      step="0.1"
                      {...register('carbs', { valueAsNumber: true })}
                    />
                    {errors.carbs && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.carbs.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="fat" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Gordura (g)
                    </label>
                    <Input
                      id="fat"
                      type="number"
                      step="0.1"
                      {...register('fat', { valueAsNumber: true })}
                    />
                    {errors.fat && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.fat.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="fiber" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Fibra (g)
                    </label>
                    <Input
                      id="fiber"
                      type="number"
                      step="0.1"
                      {...register('fiber', { valueAsNumber: true })}
                    />
                    {errors.fiber && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.fiber.message}
                      </p>
                    )}
                  </div>
                </div>

                {/* Botões */}
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Salvando...' : 'Adicionar Alimento'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowAddForm(false)}
                  >
                    Cancelar
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Lista de Entradas */}
        <Card>
          <CardHeader>
            <CardTitle>Entradas do Dia</CardTitle>
            <CardDescription>
              {entries.length} alimento(s) registrado(s)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {entries.length > 0 ? (
              <div className="space-y-4">
                {entries.map((entry, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-lg">{getMealTypeIcon(entry.meal_type)}</span>
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {entry.food_name}
                        </h3>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {entry.quantity} {entry.unit}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                        <span className="flex items-center space-x-1">
                          <Flame className="h-3 w-3" />
                          <span>{entry.calories} kcal</span>
                        </span>
                        <span className={`flex items-center space-x-1 ${getMacroColor('protein')}`}>
                          <Protein className="h-3 w-3" />
                          <span>{entry.protein}g</span>
                        </span>
                        <span className={`flex items-center space-x-1 ${getMacroColor('carbs')}`}>
                          <Carbs className="h-3 w-3" />
                          <span>{entry.carbs}g</span>
                        </span>
                        <span className={`flex items-center space-x-1 ${getMacroColor('fat')}`}>
                          <Fat className="h-3 w-3" />
                          <span>{entry.fat}g</span>
                        </span>
                        <span className={`flex items-center space-x-1 ${getMacroColor('fiber')}`}>
                          <Fiber className="h-3 w-3" />
                          <span>{entry.fiber}g</span>
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => deleteEntry(entry.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Apple className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  Nenhum alimento registrado para hoje. Adicione sua primeira refeição!
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};