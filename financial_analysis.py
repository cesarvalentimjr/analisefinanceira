"""
Módulo de análise financeira para cafeteria
Contém funções para cálculos de margem de contribuição, ponto de equilíbrio,
margem de segurança, alavancagem operacional e análise custo-volume-lucro.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

class FinancialAnalyzer:
    """Classe para análise financeira de produtos de cafeteria"""
    
    def __init__(self, products_data: List[Dict], fixed_costs: float, tax_rate: float = 0.0):
        """
        Inicializa o analisador financeiro
        
        Args:
            products_data: Lista de dicionários com dados dos produtos
            fixed_costs: Custos fixos totais
        """
        self.products_data = products_data
        self.fixed_costs = fixed_costs
        self.tax_rate = tax_rate
        self.df = pd.DataFrame(products_data)
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calcula métricas básicas para cada produto"""
        if len(self.df) > 0:
            self.df['contribution_margin'] = self.df['price'] - self.df['cost']
            # Calcular imposto sobre receita
            self.df['tax'] = self.df['price'] * (self.tax_rate / 100)
            self.df['total_tax'] = self.df['tax'] * self.df['quantity']
            # Ajustar margem de contribuição considerando impostos
            self.df['contribution_margin'] = self.df['price'] - self.df['cost'] - self.df['tax']
            self.df['contribution_margin_percent'] = (
                (self.df['contribution_margin'] / self.df['price']) * 100
            ).fillna(0)
            self.df['total_revenue'] = self.df['price'] * self.df['quantity']
            self.df['total_variable_cost'] = (self.df['cost'] + self.df['tax']) * self.df['quantity']
            self.df['total_contribution'] = self.df['contribution_margin'] * self.df['quantity']
    
    def get_contribution_margin_analysis(self) -> pd.DataFrame:
        """
        Retorna análise detalhada da margem de contribuição por produto
        
        Returns:
            DataFrame com análise de margem de contribuição
        """
        if len(self.df) == 0:
            return pd.DataFrame()
        
        analysis_df = self.df.copy()
        analysis_df['contribution_rank'] = analysis_df['contribution_margin_percent'].rank(ascending=False)
        analysis_df['revenue_participation'] = (
            analysis_df['total_revenue'] / analysis_df['total_revenue'].sum() * 100
        )
        analysis_df['contribution_participation'] = (
            analysis_df['total_contribution'] / analysis_df['total_contribution'].sum() * 100
        )
        
        return analysis_df
    
    def calculate_breakeven_analysis(self) -> Dict:
        """
        Calcula análise de ponto de equilíbrio
        
        Returns:
            Dicionário com métricas de ponto de equilíbrio
        """
        if len(self.df) == 0:
            return {}
        
        total_contribution = self.df['total_contribution'].sum()
        total_quantity = self.df['quantity'].sum()
        total_revenue = self.df['total_revenue'].sum()
        
        # Margem de contribuição média ponderada
        weighted_avg_contribution_margin = total_contribution / total_quantity if total_quantity > 0 else 0
        
        # Preço médio ponderado
        weighted_avg_price = total_revenue / total_quantity if total_quantity > 0 else 0
        
        # Ponto de equilíbrio em unidades
        breakeven_units = self.fixed_costs / weighted_avg_contribution_margin if weighted_avg_contribution_margin > 0 else 0
        
        # Ponto de equilíbrio em receita
        breakeven_revenue = breakeven_units * weighted_avg_price
        
        # Margem de segurança
        safety_margin_units = total_quantity - breakeven_units
        safety_margin_percent = (safety_margin_units / total_quantity * 100) if total_quantity > 0 else 0
        safety_margin_revenue = total_revenue - breakeven_revenue
        
        return {
            'breakeven_units': breakeven_units,
            'breakeven_revenue': breakeven_revenue,
            'safety_margin_units': safety_margin_units,
            'safety_margin_percent': safety_margin_percent,
            'safety_margin_revenue': safety_margin_revenue,
            'weighted_avg_contribution_margin': weighted_avg_contribution_margin,
            'weighted_avg_price': weighted_avg_price
        }
    
    def calculate_operating_leverage(self) -> float:
        """
        Calcula alavancagem operacional
        
        Returns:
            Valor da alavancagem operacional
        """
        if len(self.df) == 0:
            return 0
        
        total_contribution = self.df['total_contribution'].sum()
        net_profit = total_contribution - self.fixed_costs
        
        if net_profit == 0:
            return float('inf')
        
        return total_contribution / net_profit
    
    def get_cost_volume_profit_analysis(self) -> Dict:
        """
        Análise completa custo-volume-lucro
        
        Returns:
            Dicionário com análise CVP completa
        """
        if len(self.df) == 0:
            return {}
        
        total_revenue = self.df['total_revenue'].sum()
        total_variable_cost = self.df['total_variable_cost'].sum()
        total_contribution = self.df['total_contribution'].sum()
        net_profit = total_contribution - self.fixed_costs
        
        # Razão da margem de contribuição
        contribution_margin_ratio = (total_contribution / total_revenue * 100) if total_revenue > 0 else 0
        
        # Razão de custos variáveis
        variable_cost_ratio = (total_variable_cost / total_revenue * 100) if total_revenue > 0 else 0
        
        breakeven_analysis = self.calculate_breakeven_analysis()
        operating_leverage = self.calculate_operating_leverage()
        
        return {
            'total_revenue': total_revenue,
            'total_variable_cost': total_variable_cost,
            'total_contribution': total_contribution,
            'fixed_costs': self.fixed_costs,
            'net_profit': net_profit,
            'contribution_margin_ratio': contribution_margin_ratio,
            'variable_cost_ratio': variable_cost_ratio,
            'operating_leverage': operating_leverage,
            **breakeven_analysis
        }
    
    def simulate_price_changes(self, product_name: str, new_price: float) -> Dict:
        """
        Simula mudança de preço em um produto
        
        Args:
            product_name: Nome do produto
            new_price: Novo preço do produto
            
        Returns:
            Dicionário com análise do impacto da mudança
        """
        if len(self.df) == 0:
            return {}
        
        product_idx = self.df[self.df['name'] == product_name].index
        if len(product_idx) == 0:
            return {'error': 'Produto não encontrado'}
        
        # Estado atual
        current_analysis = self.get_cost_volume_profit_analysis()
        
        # Simular mudança
        df_sim = self.df.copy()
        df_sim.loc[product_idx, 'price'] = new_price
        df_sim.loc[product_idx, 'contribution_margin'] = new_price - df_sim.loc[product_idx, 'cost']
        df_sim.loc[product_idx, 'contribution_margin_percent'] = (
            (df_sim.loc[product_idx, 'contribution_margin'] / new_price) * 100
        )
        df_sim.loc[product_idx, 'total_revenue'] = new_price * df_sim.loc[product_idx, 'quantity']
        df_sim.loc[product_idx, 'total_contribution'] = (
            df_sim.loc[product_idx, 'contribution_margin'] * df_sim.loc[product_idx, 'quantity']
        )
        
        # Recalcular métricas
        sim_analyzer = FinancialAnalyzer(df_sim.to_dict('records'), self.fixed_costs)
        new_analysis = sim_analyzer.get_cost_volume_profit_analysis()
        
        return {
            'current_profit': current_analysis.get('net_profit', 0),
            'new_profit': new_analysis.get('net_profit', 0),
            'profit_change': new_analysis.get('net_profit', 0) - current_analysis.get('net_profit', 0),
            'current_contribution_ratio': current_analysis.get('contribution_margin_ratio', 0),
            'new_contribution_ratio': new_analysis.get('contribution_margin_ratio', 0)
        }
    
    def analyze_product_mix_optimization(self) -> Dict:
        """
        Analisa otimização do mix de produtos
        
        Returns:
            Dicionário com recomendações de otimização
        """
        if len(self.df) == 0:
            return {}
        
        df_analysis = self.get_contribution_margin_analysis()
        
        # Produtos com maior margem
        high_margin_products = df_analysis.nlargest(3, 'contribution_margin_percent')
        
        # Produtos com menor margem
        low_margin_products = df_analysis.nsmallest(3, 'contribution_margin_percent')
        
        # Produtos com maior contribuição total
        high_contribution_products = df_analysis.nlargest(3, 'total_contribution')
        
        return {
            'high_margin_products': high_margin_products[['name', 'contribution_margin_percent', 'total_contribution']].to_dict('records'),
            'low_margin_products': low_margin_products[['name', 'contribution_margin_percent', 'total_contribution']].to_dict('records'),
            'high_contribution_products': high_contribution_products[['name', 'contribution_margin_percent', 'total_contribution']].to_dict('records')
        }
    
    def calculate_combo_analysis(self, product_names: List[str], discount_percent: float) -> Dict:
        """
        Analisa viabilidade de combo de produtos
        
        Args:
            product_names: Lista de nomes dos produtos no combo
            discount_percent: Percentual de desconto do combo
            
        Returns:
            Dicionário com análise do combo
        """
        if len(self.df) == 0:
            return {}
        
        combo_products = self.df[self.df['name'].isin(product_names)]
        
        if len(combo_products) == 0:
            return {'error': 'Nenhum produto encontrado'}
        
        # Cálculos do combo
        combo_original_price = combo_products['price'].sum()
        combo_discounted_price = combo_original_price * (1 - discount_percent / 100)
        combo_total_cost = combo_products['cost'].sum()
        combo_margin = combo_discounted_price - combo_total_cost
        combo_margin_percent = (combo_margin / combo_discounted_price * 100) if combo_discounted_price > 0 else 0
        
        # Margem média dos produtos individuais
        avg_individual_margin = combo_products['contribution_margin_percent'].mean()
        
        return {
            'products': product_names,
            'original_price': combo_original_price,
            'discounted_price': combo_discounted_price,
            'total_cost': combo_total_cost,
            'combo_margin': combo_margin,
            'combo_margin_percent': combo_margin_percent,
            'avg_individual_margin_percent': avg_individual_margin,
            'margin_impact': combo_margin_percent - avg_individual_margin,
            'discount_applied': discount_percent,
            'viability': 'Viável' if combo_margin_percent > 15 else 'Revisar' if combo_margin_percent > 5 else 'Não recomendado'
        }



