# RE-EDUCA Store Frontend

Frontend moderno para a plataforma RE-EDUCA Store, desenvolvido com React, Vite e Tailwind CSS.

## 🚀 Tecnologias

- **React 19** - Biblioteca JavaScript para interfaces
- **Vite** - Build tool e dev server
- **Tailwind CSS** - Framework CSS utilitário
- **React Router DOM** - Roteamento
- **React Hook Form** - Gerenciamento de formulários
- **Zod** - Validação de schemas
- **Radix UI** - Componentes acessíveis
- **Lucide React** - Ícones
- **Sonner** - Notificações toast
- **Next Themes** - Gerenciamento de tema claro/escuro
- **Axios** - Cliente HTTP
- **Framer Motion** - Animações

## 🎨 Design System

### Paleta de Cores (macOS-inspired)

- **Primária**: Azul (#3b82f6)
- **Secundária**: Verde (#22c55e)
- **Sucesso**: Verde (#22c55e)
- **Aviso**: Amarelo (#f59e0b)
- **Erro**: Vermelho (#ef4444)
- **Neutra**: Cinza (#737373)

### Tema Claro/Escuro

O sistema suporta automaticamente:
- Tema claro (padrão)
- Tema escuro
- Detecção automática do sistema

## 📁 Estrutura do Projeto

```
src/
├── components/
│   ├── layouts/          # Layouts da aplicação
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   ├── Sidebar.jsx
│   │   └── PageLayout.jsx
│   └── ui/              # Componentes base
│       ├── button.jsx
│       ├── input.jsx
│       ├── card.jsx
│       ├── loading.jsx
│       └── error.jsx
├── lib/                 # Utilitários e configurações
│   ├── api.js          # Configuração da API
│   ├── colors.js       # Paleta de cores
│   ├── theme.js        # Sistema de tema
│   └── utils.js        # Funções utilitárias
├── pages/              # Páginas da aplicação
│   └── auth/
│       ├── LoginPage.jsx
│       └── RegisterPage.jsx
└── App.jsx             # Componente principal
```

## 🛠️ Funcionalidades Implementadas

### ✅ Concluído

1. **Design System Completo**
   - Paleta de cores moderna inspirada no macOS
   - Sistema de tema claro/escuro
   - Componentes base (Button, Input, Card)
   - Layouts responsivos

2. **Sistema de Autenticação**
   - Página de login moderna
   - Página de registro com validações
   - Integração com backend
   - Proteção de rotas

3. **Integração com Backend**
   - Configuração completa do Axios
   - Interceptors para autenticação
   - Refresh token automático
   - Tratamento de erros centralizado

4. **Componentes de UI**
   - Loading spinners
   - Tratamento de erros
   - Notificações toast
   - Formulários com validação

5. **Layouts Responsivos**
   - Header com navegação
   - Footer completo
   - Sidebar colapsível
   - Layouts específicos (Auth, Dashboard, Content)

### 🚧 Em Desenvolvimento

1. **Páginas de Ferramentas de Saúde**
   - Calculadora IMC
   - Diário alimentar
   - Monitor de exercícios
   - Analytics e gráficos

2. **Loja Virtual**
   - Catálogo de produtos
   - Carrinho de compras
   - Sistema de pagamento
   - Histórico de pedidos

3. **Dashboard Completo**
   - Métricas de saúde
   - Gráficos interativos
   - Metas e progresso
   - Recomendações personalizadas

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+
- npm ou pnpm

### Instalação

```bash
# Instalar dependências
npm install

# Executar em modo desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# API Configuration
VITE_API_URL=http://localhost:5000/api

# App Configuration
VITE_APP_NAME=RE-EDUCA Store
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_AI_FEATURES=true
VITE_ENABLE_AR_FEATURES=false
VITE_ENABLE_IOT_FEATURES=false
VITE_ENABLE_BLOCKCHAIN_FEATURES=false
```

## 🎯 Próximos Passos

1. **Implementar páginas de ferramentas de saúde**
2. **Criar sistema de loja virtual**
3. **Desenvolver dashboard completo**
4. **Adicionar testes unitários e E2E**
5. **Implementar PWA features**
6. **Otimizar performance**

## 📱 Responsividade

O frontend é totalmente responsivo e funciona em:
- 📱 Mobile (320px+)
- 📱 Tablet (768px+)
- 💻 Desktop (1024px+)
- 🖥️ Large screens (1440px+)

## 🎨 Customização

### Cores

Edite `src/lib/colors.js` para personalizar a paleta:

```javascript
export const colors = {
  primary: {
    500: '#3b82f6', // Sua cor primária
  },
  // ... outras cores
};
```

### Tema

Configure o tema em `src/lib/theme.js`:

```javascript
export const theme = {
  config: {
    defaultTheme: 'system', // 'light', 'dark', 'system'
  },
  // ... configurações
};
```

## 🔧 Scripts Disponíveis

- `npm run dev` - Servidor de desenvolvimento
- `npm run build` - Build para produção
- `npm run preview` - Preview do build
- `npm run lint` - Linting do código

## 📄 Licença

Este projeto faz parte da plataforma RE-EDUCA Store.

---

**Desenvolvido com ❤️ para transformar vidas através da educação em saúde**