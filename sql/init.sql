
CREATE DATABASE IF NOT EXISTS cryptobot_supreme;
USE cryptobot_supreme;

CREATE TABLE IF NOT EXISTS trades (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trade_id VARCHAR(100) UNIQUE NOT NULL,
    bot_name VARCHAR(50) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side ENUM('buy', 'sell') NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms DECIMAL(10,3),
    strategy VARCHAR(50),
    caso_uso INT,
    profit_loss DECIMAL(20,8) DEFAULT 0,
    fees DECIMAL(20,8) DEFAULT 0,
    status ENUM('pending', 'filled', 'cancelled', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_symbol (symbol),
    INDEX idx_bot_name (bot_name),
    INDEX idx_exchange (exchange),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS bot_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    bot_name VARCHAR(50) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    total_trades INT DEFAULT 0,
    winning_trades INT DEFAULT 0,
    losing_trades INT DEFAULT 0,
    total_pnl DECIMAL(20,8) DEFAULT 0,
    total_fees DECIMAL(20,8) DEFAULT 0,
    max_drawdown DECIMAL(10,4) DEFAULT 0,
    sharpe_ratio DECIMAL(10,4) DEFAULT 0,
    win_rate DECIMAL(5,4) DEFAULT 0,
    avg_trade_duration_minutes INT DEFAULT 0,
    last_trade_at TIMESTAMP NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_bot_exchange (bot_name, exchange),
    INDEX idx_bot_name (bot_name),
    INDEX idx_updated_at (updated_at)
);

CREATE TABLE IF NOT EXISTS system_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20,8) NOT NULL,
    metric_unit VARCHAR(20),
    component VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp),
    INDEX idx_component (component)
);

CREATE TABLE IF NOT EXISTS ai_model_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    prediction_accuracy DECIMAL(5,4),
    model_confidence DECIMAL(5,4),
    feature_importance JSON,
    training_date TIMESTAMP,
    last_prediction_at TIMESTAMP,
    predictions_count INT DEFAULT 0,
    correct_predictions INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_model_name (model_name),
    INDEX idx_updated_at (updated_at)
);

CREATE TABLE IF NOT EXISTS risk_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    portfolio_value DECIMAL(20,8),
    var_95 DECIMAL(10,6),
    var_99 DECIMAL(10,6),
    max_drawdown DECIMAL(10,6),
    sharpe_ratio DECIMAL(10,4),
    sortino_ratio DECIMAL(10,4),
    exposure_by_asset JSON,
    correlation_matrix JSON,
    risk_score DECIMAL(5,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_timestamp (timestamp)
);

CREATE TABLE IF NOT EXISTS exchange_status (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    exchange_name VARCHAR(50) NOT NULL,
    status ENUM('online', 'offline', 'maintenance', 'degraded') DEFAULT 'online',
    latency_ms DECIMAL(10,3),
    last_successful_request TIMESTAMP,
    error_rate DECIMAL(5,4) DEFAULT 0,
    api_calls_count INT DEFAULT 0,
    api_calls_limit INT,
    rate_limit_remaining INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_exchange (exchange_name),
    INDEX idx_status (status),
    INDEX idx_updated_at (updated_at)
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    alert_type ENUM('performance', 'risk', 'system', 'trading') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    component VARCHAR(100),
    metric_name VARCHAR(100),
    threshold_value DECIMAL(20,8),
    current_value DECIMAL(20,8),
    status ENUM('active', 'resolved', 'acknowledged') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    
    INDEX idx_alert_type (alert_type),
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

INSERT INTO bot_performance (bot_name, exchange, active) VALUES
('arbitragem', 'binance', TRUE),
('arbitragem', 'coinbase', TRUE),
('grid', 'binance', TRUE),
('momentum', 'binance', TRUE),
('scalping', 'binance', TRUE),
('mean_reversion', 'binance', TRUE),
('swing', 'binance', TRUE)
ON DUPLICATE KEY UPDATE active = VALUES(active);

INSERT INTO exchange_status (exchange_name, status, api_calls_limit) VALUES
('binance', 'online', 1200),
('coinbase', 'online', 10000),
('kraken', 'online', 900),
('ftx', 'offline', 0)
ON DUPLICATE KEY UPDATE 
    status = VALUES(status),
    api_calls_limit = VALUES(api_calls_limit);

CREATE OR REPLACE VIEW daily_performance AS
SELECT 
    DATE(timestamp) as trade_date,
    bot_name,
    exchange,
    COUNT(*) as total_trades,
    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(profit_loss) as daily_pnl,
    AVG(execution_time_ms) as avg_execution_time,
    MIN(timestamp) as first_trade,
    MAX(timestamp) as last_trade
FROM trades 
WHERE timestamp >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
GROUP BY DATE(timestamp), bot_name, exchange
ORDER BY trade_date DESC, daily_pnl DESC;

CREATE OR REPLACE VIEW current_portfolio AS
SELECT 
    SUBSTRING_INDEX(symbol, '/', 1) as base_asset,
    SUBSTRING_INDEX(symbol, '/', -1) as quote_asset,
    SUM(CASE WHEN side = 'buy' THEN amount ELSE -amount END) as net_position,
    COUNT(*) as total_trades,
    SUM(profit_loss) as total_pnl,
    MAX(timestamp) as last_trade_time
FROM trades 
WHERE status = 'filled'
GROUP BY base_asset, quote_asset
HAVING ABS(net_position) > 0.00001
ORDER BY ABS(net_position) DESC;

DELIMITER //

CREATE PROCEDURE UpdateBotPerformance(
    IN p_bot_name VARCHAR(50),
    IN p_exchange VARCHAR(50)
)
BEGIN
    DECLARE v_total_trades INT DEFAULT 0;
    DECLARE v_winning_trades INT DEFAULT 0;
    DECLARE v_total_pnl DECIMAL(20,8) DEFAULT 0;
    DECLARE v_total_fees DECIMAL(20,8) DEFAULT 0;
    DECLARE v_last_trade TIMESTAMP;
    
    SELECT 
        COUNT(*),
        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END),
        SUM(profit_loss),
        SUM(fees),
        MAX(timestamp)
    INTO v_total_trades, v_winning_trades, v_total_pnl, v_total_fees, v_last_trade
    FROM trades 
    WHERE bot_name = p_bot_name AND exchange = p_exchange AND status = 'filled';
    
    INSERT INTO bot_performance (
        bot_name, exchange, total_trades, winning_trades, 
        losing_trades, total_pnl, total_fees, last_trade_at,
        win_rate, updated_at
    ) VALUES (
        p_bot_name, p_exchange, v_total_trades, v_winning_trades,
        v_total_trades - v_winning_trades, v_total_pnl, v_total_fees, v_last_trade,
        CASE WHEN v_total_trades > 0 THEN v_winning_trades / v_total_trades ELSE 0 END,
        CURRENT_TIMESTAMP
    )
    ON DUPLICATE KEY UPDATE
        total_trades = v_total_trades,
        winning_trades = v_winning_trades,
        losing_trades = v_total_trades - v_winning_trades,
        total_pnl = v_total_pnl,
        total_fees = v_total_fees,
        last_trade_at = v_last_trade,
        win_rate = CASE WHEN v_total_trades > 0 THEN v_winning_trades / v_total_trades ELSE 0 END,
        updated_at = CURRENT_TIMESTAMP;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER after_trade_insert 
AFTER INSERT ON trades
FOR EACH ROW
BEGIN
    IF NEW.status = 'filled' THEN
        CALL UpdateBotPerformance(NEW.bot_name, NEW.exchange);
    END IF;
END //

CREATE TRIGGER after_trade_update
AFTER UPDATE ON trades
FOR EACH ROW
BEGIN
    IF NEW.status = 'filled' AND OLD.status != 'filled' THEN
        CALL UpdateBotPerformance(NEW.bot_name, NEW.exchange);
    END IF;
END //

DELIMITER ;



COMMIT;
