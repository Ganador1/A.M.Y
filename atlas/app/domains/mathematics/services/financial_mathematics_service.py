"""
Servicio de Matemáticas Financieras para AXIOM Mathematics
Proporciona modelos matemáticos avanzados para finanzas cuantitativas,
análisis de riesgo, pricing de derivados y optimización de portafolios.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats, optimize, linalg
from scipy.special import ndtr  # Normal CDF
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from app.exceptions.domain.mathematics import MathematicsError
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class ModelType(Enum):
    BLACK_SCHOLES = "black_scholes"
    BINOMIAL = "binomial"
    MONTE_CARLO = "monte_carlo"
    HESTON = "heston"
    JUMP_DIFFUSION = "jump_diffusion"

class RiskMeasure(Enum):
    VAR = "value_at_risk"
    CVAR = "conditional_var"
    EXPECTED_SHORTFALL = "expected_shortfall"
    MAXIMUM_DRAWDOWN = "maximum_drawdown"

@dataclass
class OptionParameters:
    """Parámetros para pricing de opciones"""
    spot_price: float
    strike_price: float
    time_to_expiry: float
    risk_free_rate: float
    volatility: float
    dividend_yield: float = 0.0
    option_type: OptionType = OptionType.CALL

@dataclass
class OptionResult:
    """Resultado del pricing de opciones"""
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: Optional[float] = None

@dataclass
class PortfolioMetrics:
    """Métricas de portafolio"""
    expected_return: float
    volatility: float
    sharpe_ratio: float
    var_95: float
    cvar_95: float
    maximum_drawdown: float
    calmar_ratio: float

@dataclass
class RiskAnalysisResult:
    """Resultado de análisis de riesgo"""
    var_estimates: Dict[str, float]
    stress_test_results: Dict[str, float]
    correlation_matrix: np.ndarray
    risk_contributions: Dict[str, float]

class FinancialMathematicsService:
    """
    Servicio de Matemáticas Financieras
    
    Proporciona:
    - Pricing de opciones y derivados
    - Modelos de volatilidad estocástica
    - Análisis de riesgo (VaR, CVaR)
    - Optimización de portafolios
    - Modelos de tasas de interés
    - Análisis de crédito
    - Backtesting de estrategias
    - Simulación Monte Carlo financiera
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trading_days_per_year = 252
        self.risk_free_proxies = {
            'USD': 0.02,  # 2% default risk-free rate
            'EUR': 0.01,
            'GBP': 0.015,
            'JPY': 0.005
        }
    
    # === PRICING DE OPCIONES ===
    
    def black_scholes_option_price(self, params: OptionParameters) -> OptionResult:
        """
        Pricing de opciones usando modelo Black-Scholes
        
        Args:
            params: Parámetros de la opción
        
        Returns:
            OptionResult con precio y griegas
        """
        try:
            S = params.spot_price
            K = params.strike_price
            T = params.time_to_expiry
            r = params.risk_free_rate
            sigma = params.volatility
            q = params.dividend_yield
            
            # Calcular d1 y d2
            d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            
            # Pricing
            if params.option_type == OptionType.CALL:
                price = S*np.exp(-q*T)*ndtr(d1) - K*np.exp(-r*T)*ndtr(d2)
            else:  # PUT
                price = K*np.exp(-r*T)*ndtr(-d2) - S*np.exp(-q*T)*ndtr(-d1)
            
            # Griegas
            delta = self._calculate_delta(S, K, T, r, sigma, q, params.option_type, d1)
            gamma = self._calculate_gamma(S, T, sigma, q, d1)
            theta = self._calculate_theta(S, K, T, r, sigma, q, params.option_type, d1, d2)
            vega = self._calculate_vega(S, T, sigma, q, d1)
            rho = self._calculate_rho(K, T, r, params.option_type, d2)
            
            return OptionResult(
                price=price,
                delta=delta,
                gamma=gamma,
                theta=theta,
                vega=vega,
                rho=rho
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en pricing Black-Scholes: {e}")
            raise
    
    def _calculate_delta(self, S: float, K: float, T: float, r: float, 
                        sigma: float, q: float, option_type: OptionType, d1: float) -> float:
        """Calcular Delta"""
        if option_type == OptionType.CALL:
            return np.exp(-q*T) * ndtr(d1)
        else:
            return -np.exp(-q*T) * ndtr(-d1)
    
    def _calculate_gamma(self, S: float, T: float, sigma: float, q: float, d1: float) -> float:
        """Calcular Gamma"""
        return np.exp(-q*T) * stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    def _calculate_theta(self, S: float, K: float, T: float, r: float, 
                        sigma: float, q: float, option_type: OptionType, 
                        d1: float, d2: float) -> float:
        """Calcular Theta"""
        term1 = -S * np.exp(-q*T) * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        
        if option_type == OptionType.CALL:
            term2 = q * S * np.exp(-q*T) * ndtr(d1)
            term3 = -r * K * np.exp(-r*T) * ndtr(d2)
        else:
            term2 = -q * S * np.exp(-q*T) * ndtr(-d1)
            term3 = r * K * np.exp(-r*T) * ndtr(-d2)
        
        return term1 + term2 + term3
    
    def _calculate_vega(self, S: float, T: float, sigma: float, q: float, d1: float) -> float:
        """Calcular Vega"""
        return S * np.exp(-q*T) * stats.norm.pdf(d1) * np.sqrt(T)
    
    def _calculate_rho(self, K: float, T: float, r: float, option_type: OptionType, d2: float) -> float:
        """Calcular Rho"""
        if option_type == OptionType.CALL:
            return K * T * np.exp(-r*T) * ndtr(d2)
        else:
            return -K * T * np.exp(-r*T) * ndtr(-d2)
    
    def binomial_option_price(self, params: OptionParameters, n_steps: int = 100) -> OptionResult:
        """
        Pricing de opciones usando modelo binomial
        
        Args:
            params: Parámetros de la opción
            n_steps: Número de pasos en el árbol binomial
        
        Returns:
            OptionResult con precio y griegas aproximadas
        """
        try:
            S = params.spot_price
            K = params.strike_price
            T = params.time_to_expiry
            r = params.risk_free_rate
            sigma = params.volatility
            q = params.dividend_yield
            
            # Parámetros del modelo binomial
            dt = T / n_steps
            u = np.exp(sigma * np.sqrt(dt))  # Factor de subida
            d = 1 / u  # Factor de bajada
            p = (np.exp((r - q) * dt) - d) / (u - d)  # Probabilidad neutral al riesgo
            
            # Inicializar árbol de precios
            price_tree = np.zeros((n_steps + 1, n_steps + 1))
            
            # Precios finales
            for j in range(n_steps + 1):
                price_tree[n_steps, j] = S * (u ** j) * (d ** (n_steps - j))
            
            # Valores de la opción en vencimiento
            option_tree = np.zeros((n_steps + 1, n_steps + 1))
            for j in range(n_steps + 1):
                if params.option_type == OptionType.CALL:
                    option_tree[n_steps, j] = max(0, price_tree[n_steps, j] - K)
                else:
                    option_tree[n_steps, j] = max(0, K - price_tree[n_steps, j])
            
            # Backward induction
            for i in range(n_steps - 1, -1, -1):
                for j in range(i + 1):
                    price_tree[i, j] = S * (u ** j) * (d ** (i - j))
                    option_tree[i, j] = np.exp(-r * dt) * (
                        p * option_tree[i + 1, j + 1] + (1 - p) * option_tree[i + 1, j]
                    )
            
            price = option_tree[0, 0]
            
            # Aproximar griegas usando diferencias finitas
            delta = (option_tree[1, 1] - option_tree[1, 0]) / (price_tree[1, 1] - price_tree[1, 0])
            
            # Gamma aproximado
            if n_steps >= 2:
                gamma_up = (option_tree[2, 2] - option_tree[2, 1]) / (price_tree[2, 2] - price_tree[2, 1])
                gamma_down = (option_tree[2, 1] - option_tree[2, 0]) / (price_tree[2, 1] - price_tree[2, 0])
                gamma = (gamma_up - gamma_down) / (0.5 * (price_tree[2, 2] - price_tree[2, 0]))
            else:
                gamma = 0.0
            
            # Theta aproximado
            if n_steps >= 2:
                theta = (option_tree[2, 1] - option_tree[0, 0]) / (2 * dt)
            else:
                theta = 0.0
            
            return OptionResult(
                price=price,
                delta=delta,
                gamma=gamma,
                theta=theta,
                vega=0.0,  # Requiere recalcular con volatilidad perturbada
                rho=0.0    # Requiere recalcular con tasa perturbada
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en pricing binomial: {e}")
            raise
    
    def monte_carlo_option_price(self, params: OptionParameters, 
                               n_simulations: int = 100000) -> OptionResult:
        """
        Pricing de opciones usando simulación Monte Carlo
        
        Args:
            params: Parámetros de la opción
            n_simulations: Número de simulaciones
        
        Returns:
            OptionResult con precio y error estándar
        """
        try:
            S = params.spot_price
            K = params.strike_price
            T = params.time_to_expiry
            r = params.risk_free_rate
            sigma = params.volatility
            q = params.dividend_yield
            
            # Generar trayectorias de precios
            np.random.seed(42)  # Para reproducibilidad
            Z = np.random.standard_normal(n_simulations)
            
            # Precio final usando modelo geométrico browniano
            ST = S * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
            
            # Payoffs
            if params.option_type == OptionType.CALL:
                payoffs = np.maximum(ST - K, 0)
            else:
                payoffs = np.maximum(K - ST, 0)
            
            # Precio descontado
            price = np.exp(-r * T) * np.mean(payoffs)
            standard_error = np.exp(-r * T) * np.std(payoffs) / np.sqrt(n_simulations)
            
            # Aproximar Delta usando diferencias finitas
            dS = 0.01 * S
            ST_up = (S + dS) * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
            ST_down = (S - dS) * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
            
            if params.option_type == OptionType.CALL:
                payoffs_up = np.maximum(ST_up - K, 0)
                payoffs_down = np.maximum(ST_down - K, 0)
            else:
                payoffs_up = np.maximum(K - ST_up, 0)
                payoffs_down = np.maximum(K - ST_down, 0)
            
            price_up = np.exp(-r * T) * np.mean(payoffs_up)
            price_down = np.exp(-r * T) * np.mean(payoffs_down)
            delta = (price_up - price_down) / (2 * dS)
            
            return OptionResult(
                price=price,
                delta=delta,
                gamma=0.0,  # Requiere más cálculos
                theta=0.0,  # Requiere más cálculos
                vega=0.0,   # Requiere más cálculos
                rho=0.0     # Requiere más cálculos
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en pricing Monte Carlo: {e}")
            raise
    
    # === ANÁLISIS DE RIESGO ===
    
    def calculate_var(self, returns: np.ndarray, confidence_level: float = 0.95,
                     method: str = "historical") -> Dict[str, float]:
        """
        Calcular Value at Risk (VaR)
        
        Args:
            returns: Serie de retornos
            confidence_level: Nivel de confianza
            method: Método de cálculo ("historical", "parametric", "monte_carlo")
        
        Returns:
            Diccionario con estimaciones de VaR
        """
        try:
            alpha = 1 - confidence_level
            
            results = {}
            
            if method == "historical":
                # VaR histórico
                var_historical = np.percentile(returns, alpha * 100)
                results["historical_var"] = var_historical
            
            elif method == "parametric":
                # VaR paramétrico (asumiendo distribución normal)
                mean_return = np.mean(returns)
                std_return = np.std(returns)
                var_parametric = mean_return + stats.norm.ppf(alpha) * std_return
                results["parametric_var"] = var_parametric
            
            elif method == "monte_carlo":
                # VaR Monte Carlo
                n_simulations = 10000
                np.random.seed(42)
                
                # Ajustar distribución t-Student para colas pesadas
                df, loc, scale = stats.t.fit(returns)
                simulated_returns = stats.t.rvs(df, loc, scale, size=n_simulations)
                var_monte_carlo = np.percentile(simulated_returns, alpha * 100)
                results["monte_carlo_var"] = var_monte_carlo
            
            else:
                # Calcular todos los métodos
                results.update(self.calculate_var(returns, confidence_level, "historical"))
                results.update(self.calculate_var(returns, confidence_level, "parametric"))
                results.update(self.calculate_var(returns, confidence_level, "monte_carlo"))
            
            return results
            
        except MathematicsError as e:
            self.logger.error(f"Error en cálculo de VaR: {e}")
            raise
    
    def calculate_cvar(self, returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """
        Calcular Conditional Value at Risk (CVaR) o Expected Shortfall
        
        Args:
            returns: Serie de retornos
            confidence_level: Nivel de confianza
        
        Returns:
            CVaR estimado
        """
        try:
            alpha = 1 - confidence_level
            var = np.percentile(returns, alpha * 100)
            
            # CVaR es la media de los retornos por debajo del VaR
            tail_returns = returns[returns <= var]
            cvar = np.mean(tail_returns) if len(tail_returns) > 0 else var
            
            return cvar
            
        except MathematicsError as e:
            self.logger.error(f"Error en cálculo de CVaR: {e}")
            raise
    
    def portfolio_risk_analysis(self, returns_matrix: np.ndarray, 
                              weights: np.ndarray) -> RiskAnalysisResult:
        """
        Análisis completo de riesgo de portafolio
        
        Args:
            returns_matrix: Matriz de retornos (activos x tiempo)
            weights: Pesos del portafolio
        
        Returns:
            RiskAnalysisResult con análisis completo
        """
        try:
            # Retornos del portafolio
            portfolio_returns = np.dot(returns_matrix.T, weights)
            
            # VaR estimates
            var_estimates = self.calculate_var(portfolio_returns, method="all")
            
            # Matriz de correlación
            correlation_matrix = np.corrcoef(returns_matrix)
            
            # Contribuciones al riesgo
            cov_matrix = np.cov(returns_matrix)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            marginal_contributions = np.dot(cov_matrix, weights) / np.sqrt(portfolio_variance)
            risk_contributions = weights * marginal_contributions
            risk_contributions_dict = {f"Asset_{i}": contrib for i, contrib in enumerate(risk_contributions)}
            
            # Stress testing
            stress_scenarios = {
                "market_crash": -0.20,  # Caída del 20%
                "volatility_spike": 2.0,  # Duplicar volatilidad
                "correlation_increase": 0.8  # Correlaciones altas
            }
            
            stress_results = {}
            for scenario, shock in stress_scenarios.items():
                if scenario == "market_crash":
                    stressed_returns = portfolio_returns + shock
                    stress_results[scenario] = self.calculate_var(stressed_returns)["historical_var"]
                elif scenario == "volatility_spike":
                    stressed_returns = portfolio_returns * shock
                    stress_results[scenario] = self.calculate_var(stressed_returns)["historical_var"]
                else:
                    # Scenario más complejo requiere más implementación
                    stress_results[scenario] = var_estimates.get("historical_var", 0) * 1.5
            
            return RiskAnalysisResult(
                var_estimates=var_estimates,
                stress_test_results=stress_results,
                correlation_matrix=correlation_matrix,
                risk_contributions=risk_contributions_dict
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en análisis de riesgo de portafolio: {e}")
            raise
    
    # === OPTIMIZACIÓN DE PORTAFOLIOS ===
    
    def mean_variance_optimization(self, expected_returns: np.ndarray, 
                                 cov_matrix: np.ndarray,
                                 risk_aversion: float = 1.0,
                                 constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimización de portafolio usando teoría de Markowitz
        
        Args:
            expected_returns: Retornos esperados de los activos
            cov_matrix: Matriz de covarianza
            risk_aversion: Parámetro de aversión al riesgo
            constraints: Restricciones adicionales
        
        Returns:
            Diccionario con pesos óptimos y métricas
        """
        try:
            n_assets = len(expected_returns)
            
            # Función objetivo: maximizar utilidad (retorno - penalización por riesgo)
            def objective(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
                return -(portfolio_return - 0.5 * risk_aversion * portfolio_variance)
            
            # Restricciones
            constraints_list = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Suma de pesos = 1
            ]
            
            # Restricciones adicionales
            if constraints:
                if 'long_only' in constraints and constraints['long_only']:
                    bounds = [(0, 1) for _ in range(n_assets)]
                else:
                    bounds = [(-1, 1) for _ in range(n_assets)]
                
                if 'max_weight' in constraints:
                    max_weight = constraints['max_weight']
                    bounds = [(0, max_weight) for _ in range(n_assets)]
            else:
                bounds = [(0, 1) for _ in range(n_assets)]
            
            # Optimización
            initial_weights = np.ones(n_assets) / n_assets
            result = optimize.minimize(
                objective, initial_weights, method='SLSQP',
                bounds=bounds, constraints=constraints_list
            )
            
            optimal_weights = result.x
            
            # Calcular métricas del portafolio óptimo
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_variance = np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Sharpe ratio (asumiendo tasa libre de riesgo = 0)
            sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
            
            return {
                'optimal_weights': optimal_weights,
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'optimization_success': result.success,
                'optimization_message': result.message
            }
            
        except MathematicsError as e:
            self.logger.error(f"Error en optimización de portafolio: {e}")
            raise
    
    def efficient_frontier(self, expected_returns: np.ndarray, 
                          cov_matrix: np.ndarray,
                          n_portfolios: int = 100) -> Dict[str, np.ndarray]:
        """
        Calcular la frontera eficiente de Markowitz
        
        Args:
            expected_returns: Retornos esperados
            cov_matrix: Matriz de covarianza
            n_portfolios: Número de portafolios en la frontera
        
        Returns:
            Diccionario con retornos y volatilidades de la frontera
        """
        try:
            n_assets = len(expected_returns)
            
            # Rango de retornos objetivo
            min_return = np.min(expected_returns)
            max_return = np.max(expected_returns)
            target_returns = np.linspace(min_return, max_return, n_portfolios)
            
            efficient_portfolios = []
            
            for target_return in target_returns:
                # Minimizar varianza sujeto a retorno objetivo
                def objective(weights):
                    return np.dot(weights.T, np.dot(cov_matrix, weights))
                
                constraints = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Suma = 1
                    {'type': 'eq', 'fun': lambda x: np.dot(x, expected_returns) - target_return}  # Retorno objetivo
                ]
                
                bounds = [(0, 1) for _ in range(n_assets)]
                initial_weights = np.ones(n_assets) / n_assets
                
                result = optimize.minimize(
                    objective, initial_weights, method='SLSQP',
                    bounds=bounds, constraints=constraints
                )
                
                if result.success:
                    weights = result.x
                    portfolio_return = np.dot(weights, expected_returns)
                    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
                    portfolio_volatility = np.sqrt(portfolio_variance)
                    
                    efficient_portfolios.append({
                        'weights': weights,
                        'return': portfolio_return,
                        'volatility': portfolio_volatility
                    })
            
            # Extraer arrays para plotting
            returns_array = np.array([p['return'] for p in efficient_portfolios])
            volatilities_array = np.array([p['volatility'] for p in efficient_portfolios])
            weights_array = np.array([p['weights'] for p in efficient_portfolios])
            
            return {
                'returns': returns_array,
                'volatilities': volatilities_array,
                'weights': weights_array,
                'portfolios': efficient_portfolios
            }
            
        except MathematicsError as e:
            self.logger.error(f"Error en cálculo de frontera eficiente: {e}")
            raise
    
    # === MODELOS DE TASAS DE INTERÉS ===
    
    def vasicek_model(self, r0: float, kappa: float, theta: float, 
                     sigma: float, T: float, n_steps: int = 1000) -> Dict[str, Any]:
        """
        Modelo de Vasicek para tasas de interés
        
        Args:
            r0: Tasa inicial
            kappa: Velocidad de reversión a la media
            theta: Tasa de largo plazo
            sigma: Volatilidad
            T: Tiempo total
            n_steps: Número de pasos
        
        Returns:
            Diccionario con simulación de tasas
        """
        try:
            dt = T / n_steps
            rates = np.zeros(n_steps + 1)
            rates[0] = r0
            
            np.random.seed(42)
            dW = np.random.normal(0, np.sqrt(dt), n_steps)
            
            for i in range(n_steps):
                dr = kappa * (theta - rates[i]) * dt + sigma * dW[i]
                rates[i + 1] = rates[i] + dr
            
            # Calcular precios de bonos
            times = np.linspace(0, T, n_steps + 1)
            bond_prices = self._vasicek_bond_price(rates, times, kappa, theta, sigma, T)
            
            return {
                'times': times,
                'rates': rates,
                'bond_prices': bond_prices,
                'mean_rate': np.mean(rates),
                'rate_volatility': np.std(rates)
            }
            
        except MathematicsError as e:
            self.logger.error(f"Error en modelo de Vasicek: {e}")
            raise
    
    def _vasicek_bond_price(self, rates: np.ndarray, times: np.ndarray,
                           kappa: float, theta: float, sigma: float, T: float) -> np.ndarray:
        """Calcular precios de bonos bajo modelo de Vasicek"""
        bond_prices = np.zeros_like(rates)
        
        for i, (r, t) in enumerate(zip(rates, times)):
            tau = T - t
            if tau > 0:
                B = (1 - np.exp(-kappa * tau)) / kappa
                A = np.exp((theta - sigma**2 / (2 * kappa**2)) * (B - tau) - 
                          sigma**2 * B**2 / (4 * kappa))
                bond_prices[i] = A * np.exp(-B * r)
            else:
                bond_prices[i] = 1.0  # Precio al vencimiento
        
        return bond_prices
    
    # === BACKTESTING ===
    
    def backtest_strategy(self, returns: np.ndarray, signals: np.ndarray,
                         transaction_costs: float = 0.001) -> Dict[str, Any]:
        """
        Backtesting de estrategia de trading
        
        Args:
            returns: Retornos del activo
            signals: Señales de trading (-1, 0, 1)
            transaction_costs: Costos de transacción
        
        Returns:
            Diccionario con métricas de performance
        """
        try:
            # Calcular retornos de la estrategia
            strategy_returns = signals[:-1] * returns[1:]  # Desfase para evitar look-ahead bias
            
            # Aplicar costos de transacción
            position_changes = np.diff(np.concatenate([[0], signals[:-1]]))
            transaction_costs_series = np.abs(position_changes) * transaction_costs
            net_returns = strategy_returns - transaction_costs_series
            
            # Calcular métricas
            cumulative_returns = np.cumprod(1 + net_returns)
            total_return = cumulative_returns[-1] - 1
            
            # Volatilidad anualizada
            volatility = np.std(net_returns) * np.sqrt(self.trading_days_per_year)
            
            # Sharpe ratio
            sharpe_ratio = np.mean(net_returns) / np.std(net_returns) * np.sqrt(self.trading_days_per_year)
            
            # Maximum drawdown
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdowns)
            
            # Calmar ratio
            calmar_ratio = (total_return / len(net_returns) * self.trading_days_per_year) / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Win rate
            winning_trades = np.sum(net_returns > 0)
            total_trades = np.sum(np.abs(position_changes) > 0)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            return {
                'total_return': total_return,
                'annualized_return': total_return / len(net_returns) * self.trading_days_per_year,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'calmar_ratio': calmar_ratio,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'cumulative_returns': cumulative_returns,
                'strategy_returns': net_returns
            }
            
        except MathematicsError as e:
            self.logger.error(f"Error en backtesting: {e}")
            raise
    
    # === UTILIDADES ===
    
    def implied_volatility(self, market_price: float, params: OptionParameters,
                          initial_guess: float = 0.2) -> float:
        """
        Calcular volatilidad implícita usando método de Newton-Raphson
        
        Args:
            market_price: Precio de mercado de la opción
            params: Parámetros de la opción
            initial_guess: Estimación inicial de volatilidad
        
        Returns:
            Volatilidad implícita
        """
        try:
            def objective(vol):
                params_copy = OptionParameters(
                    spot_price=params.spot_price,
                    strike_price=params.strike_price,
                    time_to_expiry=params.time_to_expiry,
                    risk_free_rate=params.risk_free_rate,
                    volatility=vol,
                    dividend_yield=params.dividend_yield,
                    option_type=params.option_type
                )
                theoretical_price = self.black_scholes_option_price(params_copy).price
                return theoretical_price - market_price
            
            # Usar método de Brent para encontrar la raíz
            result = optimize.brentq(objective, 0.001, 5.0)
            return result
            
        except MathematicsError as e:
            self.logger.error(f"Error en cálculo de volatilidad implícita: {e}")
            return initial_guess
    
    def calculate_portfolio_metrics(self, returns: np.ndarray) -> PortfolioMetrics:
        """
        Calcular métricas completas de portafolio
        
        Args:
            returns: Serie de retornos del portafolio
        
        Returns:
            PortfolioMetrics con todas las métricas
        """
        try:
            # Retorno esperado anualizado
            expected_return = np.mean(returns) * self.trading_days_per_year
            
            # Volatilidad anualizada
            volatility = np.std(returns) * np.sqrt(self.trading_days_per_year)
            
            # Sharpe ratio
            sharpe_ratio = expected_return / volatility if volatility > 0 else 0
            
            # VaR y CVaR
            var_95 = self.calculate_var(returns, 0.95)["historical_var"]
            cvar_95 = self.calculate_cvar(returns, 0.95)
            
            # Maximum drawdown
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            maximum_drawdown = np.min(drawdowns)
            
            # Calmar ratio
            calmar_ratio = expected_return / abs(maximum_drawdown) if maximum_drawdown != 0 else 0
            
            return PortfolioMetrics(
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                var_95=var_95,
                cvar_95=cvar_95,
                maximum_drawdown=maximum_drawdown,
                calmar_ratio=calmar_ratio
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en cálculo de métricas de portafolio: {e}")
            raise