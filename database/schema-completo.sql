-- =============================================
-- RE-EDUCA Store v2.0.0 - Schema Completo
-- Supabase PostgreSQL Database Schema
-- =============================================

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================
-- TABELA DE USUÁRIOS
-- =============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    subscription_plan VARCHAR(50) DEFAULT 'free' CHECK (subscription_plan IN ('free', 'basic', 'premium', 'enterprise')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Índices para performance
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Índices para otimização
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_subscription ON users(subscription_plan);
CREATE INDEX idx_users_active ON users(is_active);

-- =============================================
-- PERFIS ESTENDIDOS DOS USUÁRIOS
-- =============================================

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    birth_date DATE,
    gender VARCHAR(20) CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    height DECIMAL(5,2), -- em centímetros
    weight DECIMAL(5,2), -- em quilogramas
    activity_level VARCHAR(20) CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active')),
    health_goals TEXT[],
    medical_conditions TEXT[],
    allergies TEXT[],
    dietary_preferences TEXT[],
    timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo',
    language VARCHAR(10) DEFAULT 'pt-BR',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- =============================================
-- HISTÓRICO DE ATIVIDADES DOS USUÁRIOS
-- =============================================

CREATE TABLE user_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para analytics
    INDEX idx_activities_user_id (user_id),
    INDEX idx_activities_type (activity_type),
    INDEX idx_activities_timestamp (timestamp),
    INDEX idx_activities_details USING GIN (details)
);

-- =============================================
-- HISTÓRICO DE IMC
-- =============================================

CREATE TABLE imc_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    weight DECIMAL(5,2) NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    imc_value DECIMAL(4,2) NOT NULL,
    classification VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_imc_user_id (user_id),
    INDEX idx_imc_calculated_at (calculated_at)
);

-- =============================================
-- DIÁRIO ALIMENTAR
-- =============================================

CREATE TABLE food_diary_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    fdc_id INTEGER, -- ID do USDA Food Data Central
    description TEXT NOT NULL,
    quantity DECIMAL(8,3) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    meal_type VARCHAR(20) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')) NOT NULL,
    nutrients JSONB DEFAULT '{}',
    consumed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_food_diary_user_id (user_id),
    INDEX idx_food_diary_consumed_at (consumed_at),
    INDEX idx_food_diary_meal_type (meal_type),
    INDEX idx_food_diary_nutrients USING GIN (nutrients)
);

-- =============================================
-- PRODUTOS (PRÓPRIOS E AFILIADOS)
-- =============================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    type VARCHAR(20) CHECK (type IN ('own', 'affiliate')) NOT NULL,
    
    -- Dados do produto próprio
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'BRL',
    
    -- Dados do produto afiliado
    affiliate_platform VARCHAR(50) CHECK (affiliate_platform IN ('hotmart', 'kiwify', 'logs', 'braip')),
    affiliate_link TEXT,
    commission_rate DECIMAL(5,2),
    
    -- Metadados
    images TEXT[],
    tags TEXT[],
    features JSONB DEFAULT '{}',
    specifications JSONB DEFAULT '{}',
    
    -- Status e controle
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    stock_quantity INTEGER DEFAULT 0,
    digital_product BOOLEAN DEFAULT false,
    
    -- SEO
    slug VARCHAR(255) UNIQUE,
    meta_title VARCHAR(255),
    meta_description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_products_category (category),
    INDEX idx_products_type (type),
    INDEX idx_products_active (is_active),
    INDEX idx_products_featured (is_featured),
    INDEX idx_products_slug (slug),
    INDEX idx_products_tags USING GIN (tags),
    INDEX idx_products_features USING GIN (features)
);

-- =============================================
-- PEDIDOS E VENDAS
-- =============================================

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pending', 'processing', 'completed', 'cancelled', 'refunded')) DEFAULT 'pending',
    
    -- Valores
    subtotal DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    shipping DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'BRL',
    
    -- Dados do cliente
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    
    -- Endereço de entrega
    shipping_address JSONB,
    
    -- Pagamento
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) CHECK (payment_status IN ('pending', 'processing', 'completed', 'failed', 'refunded')) DEFAULT 'pending',
    payment_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_payment_status (payment_status),
    INDEX idx_orders_created_at (created_at),
    INDEX idx_orders_number (order_number)
);

-- =============================================
-- ITENS DOS PEDIDOS
-- =============================================

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    
    -- Dados do produto no momento da compra
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    unit_price DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    total_price DECIMAL(10,2) NOT NULL,
    
    -- Dados específicos para afiliados
    affiliate_commission DECIMAL(10,2),
    affiliate_tracking_id VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_order_items_order_id (order_id),
    INDEX idx_order_items_product_id (product_id)
);

-- =============================================
-- ASSINATURAS E PLANOS
-- =============================================

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'expired', 'suspended')) DEFAULT 'active',
    
    -- Valores
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'BRL',
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'quarterly', 'yearly')) NOT NULL,
    
    -- Datas
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    
    -- Pagamento
    payment_method VARCHAR(50),
    payment_provider VARCHAR(50),
    external_subscription_id VARCHAR(255),
    
    -- Features do plano
    features JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_subscriptions_user_id (user_id),
    INDEX idx_subscriptions_status (status),
    INDEX idx_subscriptions_expires_at (expires_at)
);

-- =============================================
-- EXERCÍCIOS E ATIVIDADES FÍSICAS
-- =============================================

CREATE TABLE exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    muscle_groups TEXT[],
    equipment TEXT[],
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    instructions TEXT,
    tips TEXT,
    calories_per_minute DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_exercises_category (category),
    INDEX idx_exercises_difficulty (difficulty_level),
    INDEX idx_exercises_muscle_groups USING GIN (muscle_groups)
);

-- =============================================
-- REGISTRO DE EXERCÍCIOS DOS USUÁRIOS
-- =============================================

CREATE TABLE user_exercise_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    exercise_id UUID REFERENCES exercises(id) ON DELETE SET NULL,
    exercise_name VARCHAR(255) NOT NULL,
    duration_minutes INTEGER,
    sets INTEGER,
    reps INTEGER,
    weight_kg DECIMAL(5,2),
    distance_km DECIMAL(6,3),
    calories_burned INTEGER,
    notes TEXT,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_exercise_logs_user_id (user_id),
    INDEX idx_exercise_logs_exercise_id (exercise_id),
    INDEX idx_exercise_logs_performed_at (performed_at)
);

-- =============================================
-- METAS E OBJETIVOS
-- =============================================

CREATE TABLE user_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) CHECK (type IN ('weight_loss', 'weight_gain', 'muscle_gain', 'endurance', 'strength', 'general_health')) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_value DECIMAL(10,2),
    current_value DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(20),
    target_date DATE,
    status VARCHAR(20) CHECK (status IN ('active', 'completed', 'paused', 'cancelled')) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_goals_user_id (user_id),
    INDEX idx_goals_type (type),
    INDEX idx_goals_status (status),
    INDEX idx_goals_target_date (target_date)
);

-- =============================================
-- NOTIFICAÇÕES
-- =============================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_notifications_user_id (user_id),
    INDEX idx_notifications_type (type),
    INDEX idx_notifications_is_read (is_read),
    INDEX idx_notifications_scheduled_for (scheduled_for)
);

-- =============================================
-- CONFIGURAÇÕES DO SISTEMA
-- =============================================

CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_settings_key (key),
    INDEX idx_settings_public (is_public)
);

-- =============================================
-- LOGS DE AUDITORIA
-- =============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_action (action),
    INDEX idx_audit_logs_table_name (table_name),
    INDEX idx_audit_logs_created_at (created_at)
);

-- =============================================
-- TRIGGERS PARA UPDATED_AT
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger em todas as tabelas com updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_goals_updated_at BEFORE UPDATE ON user_goals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- POLÍTICAS RLS (ROW LEVEL SECURITY)
-- =============================================

-- Habilitar RLS em tabelas sensíveis
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE imc_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_diary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_exercise_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Políticas para usuários (podem ver apenas seus próprios dados)
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own user_profiles" ON user_profiles FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own activities" ON user_activities FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view own imc_history" ON imc_history FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own food_diary" ON food_diary_entries FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own orders" ON orders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view own subscriptions" ON subscriptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view own exercise_logs" ON user_exercise_logs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own goals" ON user_goals FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own notifications" ON notifications FOR ALL USING (auth.uid() = user_id);

-- Políticas para administradores
CREATE POLICY "Admins can view all users" ON users FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE id = auth.uid() AND role = 'admin'
    )
);

-- =============================================
-- DADOS INICIAIS
-- =============================================

-- Configurações do sistema
INSERT INTO system_settings (key, value, description, is_public) VALUES
('app_name', '"RE-EDUCA Store"', 'Nome da aplicação', true),
('app_version', '"2.0.0"', 'Versão da aplicação', true),
('maintenance_mode', 'false', 'Modo de manutenção', false),
('max_file_upload_size', '10485760', 'Tamanho máximo de upload em bytes (10MB)', false),
('default_subscription_plan', '"free"', 'Plano padrão para novos usuários', false),
('email_verification_required', 'false', 'Verificação de email obrigatória', false);

-- Exercícios básicos
INSERT INTO exercises (name, category, muscle_groups, equipment, difficulty_level, instructions, calories_per_minute) VALUES
('Caminhada', 'Cardio', ARRAY['pernas', 'core'], ARRAY[], 'beginner', 'Caminhe em ritmo moderado por 30-60 minutos', 5.0),
('Corrida', 'Cardio', ARRAY['pernas', 'core'], ARRAY[], 'intermediate', 'Corra em ritmo constante, mantendo boa postura', 12.0),
('Flexão de braço', 'Força', ARRAY['peito', 'triceps', 'ombros'], ARRAY[], 'beginner', 'Mantenha o corpo reto, desça até o peito quase tocar o chão', 8.0),
('Agachamento', 'Força', ARRAY['pernas', 'glúteos'], ARRAY[], 'beginner', 'Desça como se fosse sentar, mantenha os joelhos alinhados', 6.0),
('Prancha', 'Core', ARRAY['core', 'ombros'], ARRAY[], 'beginner', 'Mantenha o corpo reto em posição de prancha', 4.0);

-- =============================================
-- VIEWS ÚTEIS
-- =============================================

-- View para estatísticas de usuários
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.name,
    u.email,
    u.subscription_plan,
    COUNT(DISTINCT fd.id) as food_entries_count,
    COUNT(DISTINCT el.id) as exercise_logs_count,
    COUNT(DISTINCT imc.id) as imc_records_count,
    MAX(u.last_login) as last_activity
FROM users u
LEFT JOIN food_diary_entries fd ON u.id = fd.user_id
LEFT JOIN user_exercise_logs el ON u.id = el.user_id
LEFT JOIN imc_history imc ON u.id = imc.user_id
GROUP BY u.id, u.name, u.email, u.subscription_plan;

-- View para dashboard de vendas
CREATE VIEW sales_dashboard AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as orders_count,
    SUM(total) as total_revenue,
    AVG(total) as average_order_value,
    COUNT(DISTINCT user_id) as unique_customers
FROM orders 
WHERE status = 'completed'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;

-- =============================================
-- COMENTÁRIOS FINAIS
-- =============================================

COMMENT ON DATABASE postgres IS 'RE-EDUCA Store v2.0.0 - Plataforma completa de saúde e bem-estar';
COMMENT ON TABLE users IS 'Usuários da plataforma com autenticação e perfis';
COMMENT ON TABLE products IS 'Produtos próprios e de afiliados (Hotmart, Kiwify, Logs, Braip)';
COMMENT ON TABLE food_diary_entries IS 'Diário alimentar com integração USDA Food Data Central';
COMMENT ON TABLE imc_history IS 'Histórico de cálculos de IMC dos usuários';
COMMENT ON TABLE user_exercise_logs IS 'Registro de exercícios e atividades físicas';
COMMENT ON TABLE orders IS 'Pedidos e vendas da plataforma';
COMMENT ON TABLE subscriptions IS 'Assinaturas e planos dos usuários';

-- Fim do schema

