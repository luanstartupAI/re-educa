# 📚 Documentação da API - RE-EDUCA Store

## 🔗 Base URL
```
http://localhost:5000/api
```

## 🔐 Autenticação
Todas as rotas protegidas requerem o header:
```
Authorization: Bearer <token>
```

## 📋 Endpoints

### 🔑 Autenticação

#### POST `/auth/register`
Registra novo usuário.

**Body:**
```json
{
  "name": "João Silva",
  "email": "joao@email.com",
  "password": "Senha123!",
  "password_confirmation": "Senha123!",
  "birth_date": "1990-01-01",
  "cpf": "12345678901",
  "phone": "11999999999"
}
```

**Response:**
```json
{
  "message": "Usuário registrado com sucesso",
  "user": {
    "id": "uuid",
    "name": "João Silva",
    "email": "joao@email.com",
    "subscription_type": "free"
  },
  "token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

#### POST `/auth/login`
Autentica usuário.

**Body:**
```json
{
  "email": "joao@email.com",
  "password": "Senha123!"
}
```

**Response:**
```json
{
  "message": "Login realizado com sucesso",
  "user": {
    "id": "uuid",
    "name": "João Silva",
    "email": "joao@email.com"
  },
  "token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

#### POST `/auth/refresh`
Renova token de acesso.

**Body:**
```json
{
  "refresh_token": "refresh_token"
}
```

#### POST `/auth/forgot-password`
Solicita reset de senha.

**Body:**
```json
{
  "email": "joao@email.com"
}
```

#### POST `/auth/reset-password`
Reseta senha com token.

**Body:**
```json
{
  "token": "reset_token",
  "new_password": "NovaSenha123!"
}
```

### 👤 Usuários

#### GET `/users/profile`
Retorna perfil do usuário atual.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "name": "João Silva",
    "email": "joao@email.com",
    "subscription_type": "free"
  }
}
```

#### PUT `/users/profile`
Atualiza perfil do usuário.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "name": "João Silva Santos",
  "birth_date": "1990-01-01",
  "phone": "11999999999"
}
```

#### POST `/users/change-password`
Altera senha do usuário.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "current_password": "Senha123!",
  "new_password": "NovaSenha123!"
}
```

#### GET `/users/subscription`
Retorna dados da assinatura.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "subscription": {
    "type": "free",
    "status": "active",
    "features": ["imc_calculator", "basic_food_diary"]
  }
}
```

### 🏥 Ferramentas de Saúde

#### POST `/health/imc/calculate`
Calcula IMC do usuário.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "weight": 70.5,
  "height": 1.75
}
```

**Response:**
```json
{
  "imc": 23.02,
  "classification": "Peso normal",
  "color": "#4ECDC4",
  "recommendations": [
    "Mantenha hábitos saudáveis",
    "Continue com exercícios regulares"
  ],
  "weight_range": {
    "min": 56.7,
    "max": 76.2
  }
}
```

#### GET `/health/imc/history`
Retorna histórico de cálculos de IMC.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: número da página (default: 1)
- `per_page`: itens por página (default: 20)

#### POST `/health/calories/calculate`
Calcula necessidade calórica.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "age": 30,
  "weight": 70.5,
  "height": 1.75,
  "gender": "male",
  "activity_level": "moderate"
}
```

**Response:**
```json
{
  "bmr": 1650,
  "daily_calories": 2557,
  "activity_multiplier": 1.55,
  "macros": {
    "protein": {
      "grams": 127.9,
      "calories": 511,
      "percentage": 20
    },
    "carbs": {
      "grams": 319.6,
      "calories": 1278,
      "percentage": 50
    },
    "fat": {
      "grams": 85.2,
      "calories": 767,
      "percentage": 30
    }
  }
}
```

#### GET `/health/nutrition/search`
Busca alimentos na API USDA.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `query`: termo de busca

**Response:**
```json
{
  "foods": [
    {
      "fdc_id": 123456,
      "name": "Arroz branco cozido",
      "brand": null,
      "category": "Grains",
      "nutrients": [...]
    }
  ]
}
```

#### POST `/health/food-diary/entries`
Adiciona entrada no diário alimentar.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "food_name": "Arroz branco",
  "quantity": 100,
  "unit": "g",
  "calories": 130,
  "protein": 2.7,
  "carbs": 28,
  "fat": 0.3,
  "meal_type": "lunch"
}
```

#### GET `/health/food-diary/entries`
Retorna entradas do diário alimentar.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `date`: data específica (YYYY-MM-DD)
- `page`: número da página
- `per_page`: itens por página

#### POST `/health/exercise/entries`
Adiciona entrada de exercício.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "exercise_name": "Corrida",
  "duration": 30,
  "intensity": "moderate",
  "calories_burned": 300,
  "exercise_type": "cardio"
}
```

#### GET `/health/analytics/summary`
Retorna analytics de saúde (Premium).

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `period`: período em dias (default: 30)

### 🛒 Produtos

#### GET `/products`
Retorna lista de produtos.

**Query Parameters:**
- `page`: número da página
- `per_page`: itens por página
- `category`: categoria do produto
- `search`: termo de busca

**Response:**
```json
{
  "products": [
    {
      "id": "uuid",
      "name": "Suplemento de Proteína",
      "description": "Proteína de alta qualidade",
      "price": 89.90,
      "category": "supplements",
      "images": ["url1", "url2"]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### GET `/products/{product_id}`
Retorna detalhes de um produto.

#### GET `/products/categories`
Retorna categorias de produtos.

#### GET `/products/featured`
Retorna produtos em destaque.

#### GET `/products/recommendations`
Retorna produtos recomendados (requer autenticação).

### 📦 Pedidos

#### GET `/orders`
Retorna pedidos do usuário.

**Headers:** `Authorization: Bearer <token>`

#### POST `/orders`
Cria novo pedido.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "products": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "price": 89.90
    }
  ],
  "shipping_address": {
    "street": "Rua das Flores, 123",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01234-567"
  },
  "payment_method": "credit_card"
}
```

#### GET `/orders/{order_id}`
Retorna detalhes de um pedido.

**Headers:** `Authorization: Bearer <token>`

#### POST `/orders/{order_id}/cancel`
Cancela um pedido.

**Headers:** `Authorization: Bearer <token>`

### 💳 Pagamentos

#### POST `/payments/create-payment-intent`
Cria intent de pagamento.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "amount": 8990,
  "currency": "brl"
}
```

#### POST `/payments/subscription/create`
Cria assinatura.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "plan": "premium",
  "amount": 2990
}
```

#### POST `/payments/subscription/cancel`
Cancela assinatura.

**Headers:** `Authorization: Bearer <token>`

### 👨‍💼 Administrativo

#### GET `/admin/users`
Retorna todos os usuários (Admin).

**Headers:** `Authorization: Bearer <token>`

#### GET `/admin/analytics`
Retorna analytics gerais (Admin).

**Headers:** `Authorization: Bearer <token>`

#### GET `/admin/orders`
Retorna todos os pedidos (Admin).

**Headers:** `Authorization: Bearer <token>`

## 🚨 Códigos de Erro

### 400 - Bad Request
```json
{
  "error": "Dados inválidos",
  "details": [
    {
      "field": "email",
      "message": "Email inválido"
    }
  ]
}
```

### 401 - Unauthorized
```json
{
  "error": "Token de acesso inválido ou expirado"
}
```

### 403 - Forbidden
```json
{
  "error": "Acesso negado. Privilégios de administrador requeridos."
}
```

### 404 - Not Found
```json
{
  "error": "Recurso não encontrado"
}
```

### 429 - Too Many Requests
```json
{
  "error": "Limite de requisições excedido",
  "retry_after": 60
}
```

### 500 - Internal Server Error
```json
{
  "error": "Erro interno do servidor"
}
```

## 📝 Notas Importantes

1. **Rate Limiting**: A API implementa rate limiting para proteger contra abuso
2. **Validação**: Todos os dados são validados rigorosamente
3. **Logs**: Todas as ações são logadas para auditoria
4. **Segurança**: JWT tokens com refresh automático
5. **Paginação**: Todas as listas são paginadas
6. **CORS**: Configurado para desenvolvimento local

## 🔧 Configuração para Frontend

### Variáveis de Ambiente
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WS_URL=ws://localhost:5000/ws
```

### Headers Padrão
```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
};
```

### Interceptor para Refresh Token
```javascript
// Implementar interceptor para renovar token automaticamente
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response.status === 401) {
      // Renovar token
      return refreshToken().then(() => {
        return axios.request(error.config);
      });
    }
    return Promise.reject(error);
  }
);
```