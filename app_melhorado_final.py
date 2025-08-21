import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from financial_analysis import FinancialAnalyzer
from cash_flow_analyzer import CashFlowAnalyzer
import io
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise de Precificação e Lucratividade",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .info-card {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Função para gerar relatório em PDF
def generate_report(analyzer, cvp_analysis, contribution_analysis):
    """Gera relatório em formato texto para download"""
    report = f"""
RELATÓRIO DE ANÁLISE FINANCEIRA - CAFETERIA
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*60}

RESUMO EXECUTIVO
{'='*60}
• Receita Total: R$ {cvp_analysis['total_revenue']:,.2f}
• Margem de Contribuição Total: R$ {cvp_analysis['total_contribution']:,.2f}
• Custos Fixos: R$ {cvp_analysis['fixed_costs']:,.2f}
• Lucro Líquido: R$ {cvp_analysis['net_profit']:,.2f}
• Margem de Contribuição (%): {cvp_analysis['contribution_margin_ratio']:.1f}%

ANÁLISE POR PRODUTO
{'='*60}
"""
    
    for _, product in contribution_analysis.iterrows():
        report += f"""
{product['name']}:
  - Preço: R$ {product['price']:.2f}
  - Custo Variável: R$ {product['cost']:.2f}
  - Margem de Contribuição: R$ {product['contribution_margin']:.2f} ({product['contribution_margin_percent']:.1f}%)
  - Quantidade Vendida: {product['quantity']} unidades
  - Contribuição Total: R$ {product['total_contribution']:.2f}
  - Participação na Receita: {product['revenue_participation']:.1f}%
  - Participação na Contribuição: {product['contribution_participation']:.1f}%
"""

    report += f"""

ANÁLISE CUSTO-VOLUME-LUCRO
{'='*60}
• Ponto de Equilíbrio (unidades): {cvp_analysis['breakeven_units']:,.0f}
• Ponto de Equilíbrio (receita): R$ {cvp_analysis['breakeven_revenue']:,.2f}
• Margem de Segurança (unidades): {cvp_analysis['safety_margin_units']:,.0f}
• Margem de Segurança (%): {cvp_analysis['safety_margin_percent']:.1f}%
• Alavancagem Operacional: {cvp_analysis['operating_leverage']:.2f}
• Razão Margem de Contribuição: {cvp_analysis['contribution_margin_ratio']:.1f}%

RECOMENDAÇÕES ESTRATÉGICAS
{'='*60}
"""
    
    optimization = analyzer.analyze_product_mix_optimization()
    
    report += "\nPRODUTOS COM MAIOR MARGEM:\n"
    for product in optimization['high_margin_products']:
        report += f"• {product['name']}: {product['contribution_margin_percent']:.1f}% de margem\n"
    
    report += "\nPRODUTOS COM MENOR MARGEM:\n"
    for product in optimization['low_margin_products']:
        report += f"• {product['name']}: {product['contribution_margin_percent']:.1f}% de margem\n"
    
    report += "\nMAIORES CONTRIBUIDORES:\n"
    for product in optimization['high_contribution_products']:
        report += f"• {product['name']}: R$ {product['total_contribution']:.2f}\n"
    
    report += f"""

CONCLUSÕES E PRÓXIMOS PASSOS
{'='*60}
1. Foque nos produtos de maior margem para aumentar lucratividade
2. Revise preços ou custos dos produtos de menor margem
3. Considere criar combos estratégicos
4. Monitore regularmente o ponto de equilíbrio
5. Analise oportunidades de aumento de volume nos produtos mais lucrativos

Relatório gerado automaticamente pelo Sistema de Análise de Precificação e Lucratividade
"""
    
    return report

# Função para gerar relatório de fluxo de caixa
def generate_cash_flow_report(analyzer):
    report = f"""
RELATÓRIO DE ANÁLISE DE FLUXO DE CAIXA
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*60}

RESUMO MENSAL
{'='*60}
"""
    monthly_summary = analyzer.get_monthly_summary()
    for _, row in monthly_summary.iterrows():
        report += f"Mês/Ano: {row['Month']}/{row['Year']}\n"
        report += f"  - Entradas: R$ {row['Total Inflow']:.2f}\n"
        report += f"  - Saídas: R$ {row['Total Outflow']:.2f}\n"
        report += f"  - Saldo: R$ {row['Net Flow']:.2f}\n\n"

    report += f"""
DETALHAMENTO DE ENTRADAS POR CATEGORIA
{'='*60}
"""
    inflow_categories = analyzer.get_category_summary("Inflow")
    for _, row in inflow_categories.iterrows():
        report += f"- {row['Category']}: R$ {row['Total Amount']:.2f}\n"

    report += f"""

DETALHAMENTO DE SAÍDAS POR CATEGORIA
{'='*60}
"""
    outflow_categories = analyzer.get_category_summary("Outflow")
    for _, row in outflow_categories.iterrows():
        report += f"- {row['Category']}: R$ {row['Total Amount']:.2f}\n"

    report += f"""

TRANSAÇÕES INDIVIDUAIS
{'='*60}
"""
    all_transactions = analyzer.get_all_transactions()
    for _, row in all_transactions.iterrows():
        report += f"{row['Date'].strftime('%d/%m/%Y')} - {row['Description']} - R$ {row['Amount']:.2f} ({row['Category']})\n"

    return report

# Título principal
st.title("☕ Análise de Precificação e Lucratividade da Cafeteria")
st.markdown("**Sistema completo para otimização de lucratividade e análise de combos**")
st.markdown("---")

# Sidebar para entrada de dados
st.sidebar.header("📊 Configurações e Dados de Entrada")

# Seção para upload de planilha
st.sidebar.subheader("📁 Upload de Dados")

# Upload de arquivo
uploaded_file = st.sidebar.file_uploader(
    "Faça upload da planilha com dados dos produtos",
    type=['xlsx', 'xls', 'csv'],
    help="Use a planilha template baixada acima"
)

# Campo para alíquota do SIMPLES
st.sidebar.subheader("💸 Tributação SIMPLES")
tax_rate = st.sidebar.number_input(
    "% Alíquota Efetiva (SIMPLES)",
    min_value=0.0, max_value=30.0, value=0.0, step=0.1,
    help="Percentual efetivo de tributação sobre a receita"
)

# Seção para dados de produtos
st.sidebar.subheader("🍰 Dados dos Produtos")

# Opção para carregar dados de exemplo
if st.sidebar.button("📋 Carregar Dados de Exemplo"):
    st.session_state.example_data = True

# Processar dados do upload ou usar entrada manual
product_data = []
use_uploaded_data = False

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:
            df_upload = pd.read_excel(uploaded_file)
        
        # Verificar se as colunas necessárias existem
        required_columns = ['Nome do Produto', 'Preço de Venda (R$)', 'Custo Variável (R$)', 'Quantidade Vendida (mês)']
        if all(col in df_upload.columns for col in required_columns):
            for _, row in df_upload.iterrows():
                product_data.append({
                    "name": row['Nome do Produto'],
                    "price": float(row['Preço de Venda (R$)']),
                    "cost": float(row['Custo Variável (R$)']),
                    "quantity": int(row['Quantidade Vendida (mês)'])
                })
            use_uploaded_data = True
            st.sidebar.success(f"✅ Planilha carregada com {len(product_data)} produtos!")
        else:
            st.sidebar.error("❌ Planilha não possui as colunas necessárias. Use o template fornecido.")
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao processar planilha: {str(e)}")

# Se não há upload válido, usar entrada manual
if not use_uploaded_data:
    # Inicializar com dados de exemplo se solicitado
    if st.session_state.get('example_data', False):
        example_products = [
            {"name": "Café Expresso", "price": 4.50, "cost": 1.20, "quantity": 300},
            {"name": "Cappuccino", "price": 6.00, "cost": 2.00, "quantity": 200},
            {"name": "Croissant", "price": 8.00, "cost": 3.50, "quantity": 150},
            {"name": "Pão de Açúcar", "price": 5.50, "cost": 2.20, "quantity": 180},
            {"name": "Sanduíche Natural", "price": 12.00, "cost": 6.00, "quantity": 100},
            {"name": "Suco Natural", "price": 7.00, "cost": 2.50, "quantity": 120}
        ]
        num_products = len(example_products)
        st.session_state.example_data = False
    else:
        example_products = []
        num_products = st.sidebar.number_input("Quantos produtos você deseja analisar?", min_value=1, max_value=20, value=3, step=1)

    # Coletar dados dos produtos
    for i in range(int(num_products)):
        with st.sidebar.expander(f"Produto {i+1}", expanded=i < 3):
            if example_products and i < len(example_products):
                default_name = example_products[i]["name"]
                default_price = example_products[i]["price"]
                default_cost = example_products[i]["cost"]
                default_quantity = example_products[i]["quantity"]
            else:
                default_name = f"Produto {i+1}"
                default_price = 10.0
                default_cost = 5.0
                default_quantity = 100
            
            name = st.text_input(f"Nome do Produto", value=default_name, key=f"name_{i}")
            price = st.number_input(f"Preço de Venda (R$)", min_value=0.0, value=default_price, format="%.2f", key=f"price_{i}")
            cost = st.number_input(f"Custo Variável (R$)", min_value=0.0, value=default_cost, format="%.2f", key=f"cost_{i}")
            quantity = st.number_input(f"Quantidade Vendida (mês)", min_value=0, value=default_quantity, step=1, key=f"quantity_{i}")
            
            product_data.append({
                "name": name, 
                "price": price, 
                "cost": cost, 
                "quantity": quantity
            })

# Seção para custos fixos
st.sidebar.subheader("🏢 Custos Fixos")
fixed_costs = st.sidebar.number_input("Custos Fixos Totais (R$/mês)", min_value=0.0, value=8000.0, format="%.2f")

# Inicializar analisador financeiro
if product_data:
    analyzer = FinancialAnalyzer(product_data, fixed_costs, tax_rate)
    cvp_analysis = analyzer.get_cost_volume_profit_analysis()
    contribution_analysis = analyzer.get_contribution_margin_analysis()

# Seção principal de resultados
if product_data and not contribution_analysis.empty:
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Receita Total", f"R$ {cvp_analysis['total_revenue']:,.2f}")
    
    with col2:
        # Margem de contribuição com percentual
        contribution_percent = cvp_analysis['contribution_margin_ratio']
        st.metric("📈 Margem de Contribuição", 
                 f"R$ {cvp_analysis['total_contribution']:,.2f}",
                 delta=f"{contribution_percent:.1f}%")
    
    with col3:
        st.metric("🏢 Custos Fixos", f"R$ {cvp_analysis['fixed_costs']:,.2f}")
    
    with col4:
        profit_percent = (cvp_analysis['net_profit']/cvp_analysis['total_revenue']*100) if cvp_analysis['total_revenue'] > 0 else 0
        st.metric("💵 Lucro Líquido", 
                 f"R$ {cvp_analysis['net_profit']:,.2f}",
                 delta=f"{profit_percent:.1f}%")

    st.markdown("---")

    # Análise por produto
    st.subheader("📊 Análise Detalhada por Produto")
    
    # Tabela de análise
    display_df = contribution_analysis[['name', 'price', 'cost', 'contribution_margin', 'contribution_margin_percent', 
                                      'quantity', 'total_contribution', 'revenue_participation', 'contribution_participation']].copy()
    display_df.columns = ['Produto', 'Preço (R$)', 'Custo Var. (R$)', 'Margem Contr. (R$)', 'Margem Contr. (%)', 
                         'Qtd Vendida', 'Contr. Total (R$)', 'Part. Receita (%)', 'Part. Contribuição (%)']
    
    # Formatação da tabela
    st.dataframe(
        display_df.style.format({
            'Preço (R$)': 'R$ {:.2f}',
            'Custo Var. (R$)': 'R$ {:.2f}',
            'Margem Contr. (R$)': 'R$ {:.2f}',
            'Margem Contr. (%)': '{:.1f}%',
            'Contr. Total (R$)': 'R$ {:.2f}',
            'Part. Receita (%)': '{:.1f}%',
            'Part. Contribuição (%)': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    # Gráficos de análise
    col1, col2 = st.columns(2)
    
    with col1:
        fig_margin = px.bar(contribution_analysis, x='name', y='contribution_margin_percent', 
                           title='Margem de Contribuição por Produto (%)',
                           labels={'contribution_margin_percent': 'Margem (%)', 'name': 'Produto'},
                           color='contribution_margin_percent',
                           color_continuous_scale='RdYlGn')
        fig_margin.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_margin, use_container_width=True)
    
    with col2:
        fig_contribution = px.pie(contribution_analysis, values='total_contribution', names='name', 
                                 title='Participação na Margem de Contribuição Total')
        st.plotly_chart(fig_contribution, use_container_width=True)

    st.markdown("---")

    # Análise de ponto de equilíbrio com legendas e alertas
    st.subheader("⚖️ Análise Custo-Volume-Lucro")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎯 Ponto de Equilíbrio**")
        st.metric("Unidades", f"{cvp_analysis['breakeven_units']:,.0f}")
        st.metric("Receita", f"R$ {cvp_analysis['breakeven_revenue']:,.2f}")
        
        # Legenda do ponto de equilíbrio
        current_units = sum([p["quantity"] for p in product_data])
        if current_units > cvp_analysis['breakeven_units']:
            st.markdown('<div class="success-card">✅ <strong>Situação:</strong> Acima do ponto de equilíbrio</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-card">⚠️ <strong>Situação:</strong> Abaixo do ponto de equilíbrio</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**🛡️ Margem de Segurança**")
        st.metric("Unidades", f"{cvp_analysis['safety_margin_units']:,.0f}")
        st.metric("Percentual", f"{cvp_analysis['safety_margin_percent']:.1f}%")
        
        # Legenda da margem de segurança
        if cvp_analysis['safety_margin_percent'] > 30:
            st.markdown('<div class="success-card">✅ <strong>Risco:</strong> Baixo - Margem confortável</div>', unsafe_allow_html=True)
        elif cvp_analysis['safety_margin_percent'] > 15:
            st.markdown('<div class="warning-card">⚠️ <strong>Risco:</strong> Moderado - Atenção necessária</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-card">🚨 <strong>Risco:</strong> Alto - Situação crítica</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("**⚡ Alavancagem Operacional**")
        leverage_value = cvp_analysis['operating_leverage']
        leverage_display = f"{leverage_value:.2f}" if leverage_value != float('inf') else "∞"
        st.metric("Alavancagem", leverage_display)
        st.metric("Razão Margem Contr.", f"{cvp_analysis['contribution_margin_ratio']:.1f}%")
        
        # Legenda da alavancagem operacional
        if leverage_value < 2:
            st.markdown('<div class="success-card">✅ <strong>Sensibilidade:</strong> Baixa - Estável</div>', unsafe_allow_html=True)
        elif leverage_value < 5:
            st.markdown('<div class="warning-card">⚠️ <strong>Sensibilidade:</strong> Moderada</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-card">🚨 <strong>Sensibilidade:</strong> Alta - Volátil</div>', unsafe_allow_html=True)

    # Seção de Análise de Fluxo de Caixa
    st.markdown("---")
    st.subheader("💰 Análise de Fluxo de Caixa")
    st.markdown("**Faça upload de extratos bancários em PDF para análise de fluxo de caixa.**")

    uploaded_pdf = st.file_uploader("Subir extrato bancário (PDF)", type=["pdf"])

    if uploaded_pdf is not None:
        st.info("Processando o extrato bancário...")
        
        cash_flow_analyzer = CashFlowAnalyzer()
        # Salvar o arquivo PDF temporariamente para que o pdfminer.six possa lê-lo
        with open("temp_extrato.pdf", "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        cash_flow_analyzer.parse_pdf_statement("temp_extrato.pdf")
        
        st.success("✅ Extrato processado com sucesso!")
        
        # Verificar se há transações processadas
        all_transactions_df = cash_flow_analyzer.get_all_transactions()
        
        if not all_transactions_df.empty:
            st.subheader("📈 Sumário Mensal de Fluxo de Caixa")
            monthly_summary_df = cash_flow_analyzer.get_monthly_summary()
            st.dataframe(monthly_summary_df.style.format({
                'Total Inflow': 'R$ {:.2f}',
                'Total Outflow': 'R$ {:.2f}',
                'Net Flow': 'R$ {:.2f}'
            }), use_container_width=True)
            
            # Gráficos de fluxo de caixa
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Entradas por Categoria")
                inflow_category_df = cash_flow_analyzer.get_category_summary("Inflow")
                if not inflow_category_df.empty:
                    fig_inflow = px.pie(inflow_category_df, values='Total Amount', names='Category', 
                                       title='Distribuição das Entradas')
                    st.plotly_chart(fig_inflow, use_container_width=True)
                    st.dataframe(inflow_category_df.style.format({
                        'Total Amount': 'R$ {:.2f}'
                    }), use_container_width=True)
                else:
                    st.info("Nenhuma entrada encontrada no período.")
            
            with col2:
                st.subheader("📊 Saídas por Categoria")
                outflow_category_df = cash_flow_analyzer.get_category_summary("Outflow")
                if not outflow_category_df.empty:
                    fig_outflow = px.pie(outflow_category_df, values='Total Amount', names='Category', 
                                        title='Distribuição das Saídas')
                    st.plotly_chart(fig_outflow, use_container_width=True)
                    st.dataframe(outflow_category_df.style.format({
                        'Total Amount': 'R$ {:.2f}'
                    }), use_container_width=True)
                else:
                    st.info("Nenhuma saída encontrada no período.")
            
            st.subheader("📋 Todas as Transações")
            st.dataframe(all_transactions_df.style.format({
                'Amount': 'R$ {:.2f}'
            }), use_container_width=True)
            
            # Botão para download do relatório de fluxo de caixa
            if st.button("📊 Gerar Relatório de Fluxo de Caixa", use_container_width=True):
                cash_flow_report_content = generate_cash_flow_report(cash_flow_analyzer)
                cash_flow_report_bytes = cash_flow_report_content.encode('utf-8')
                st.download_button(
                    label="📥 Baixar Relatório de Fluxo de Caixa (TXT)",
                    data=cash_flow_report_bytes,
                    file_name=f"relatorio_fluxo_caixa_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                st.success("✅ Relatório de Fluxo de Caixa gerado com sucesso! Clique no botão acima para baixar.")
        else:
            st.warning("⚠️ Nenhuma transação foi encontrada no PDF. Verifique o formato do extrato.")

    else:
        st.info("Por favor, suba um arquivo PDF para analisar o fluxo de caixa.")

    # Seção de download do relatório
    st.markdown("---")
    st.subheader("📄 Download do Relatório de Análise")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📊 Gerar Relatório Completo", use_container_width=True):
            report_content = generate_report(analyzer, cvp_analysis, contribution_analysis)
            
            # Criar arquivo para download
            report_bytes = report_content.encode('utf-8')
            
            st.download_button(
                label="📥 Baixar Relatório (TXT)",
                data=report_bytes,
                file_name=f"relatorio_analise_cafeteria_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.success("✅ Relatório gerado com sucesso! Clique no botão acima para baixar.")

# Footer
st.markdown("---")
st.markdown("**💡 Desenvolvido para otimização de lucratividade de cafeterias** ☕")
st.markdown("*Use as análises para tomar decisões estratégicas baseadas em dados!*")

