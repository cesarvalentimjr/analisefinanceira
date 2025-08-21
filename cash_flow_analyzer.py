import pandas as pd
import re
from datetime import datetime
from pdfminer.high_level import extract_text
import io

class CashFlowAnalyzer:
    def __init__(self):
        self.transactions = pd.DataFrame(columns=["Date", "Description", "Amount", "Type", "Category"])
        self.categories = {
            "inflow": {
                "Salário/Recebimento": ["salario", "pagamento", "recebimento", "deposito", "credito"],
                "Venda/Serviço": ["venda", "servico", "cliente", "pagto cliente"],
                "Outra Entrada": []
            },
            "outflow": {
                "Aluguel": ["aluguel", "arrendamento"],
                "Contas de Consumo": ["luz", "energia", "agua", "internet", "telefone", "gas"],
                "Fornecedores/Compras": ["fornecedor", "compra", "mercadoria", "insumo"],
                "Despesas com Pessoal": ["salario", "folha", "adiantamento"],
                "Impostos/Taxas": ["imposto", "taxa", "tributo", "irrf", "iss", "icms"],
                "Transporte": ["combustivel", "transporte", "uber", "99pop"],
                "Manutenção": ["manutencao", "reparo"],
                "Outra Saída": []
            }
        }

    def parse_pdf_statement(self, pdf_file_path: str):
        try:
            text = extract_text(pdf_file_path)
        except Exception as e:
            print(f"Erro ao extrair texto do PDF: {e}")
            return

        # Regex para capturar data, descrição e valor (considerando formato BRL e sinais)
        # Exemplo de linha: 01/01/2023 Descrição da Transação R$ 1.234,56 C
        # Exemplo de linha: 01/01/2023 Descrição da Transação R$ 1.234,56 D
        # Exemplo de linha: 01/01/2023 Descrição da Transação 1.234,56 C
        # Exemplo de linha: 01/01/2023 Descrição da Transação 1.234,56 D
        # Exemplo de linha: 01/01/2023 Descrição da Transação 1.234,56
        # Exemplo de linha: 01/01/2023 Descrição da Transação -1.234,56
        
        # Ajuste para o formato do extrato fornecido
        # O extrato fornecido tem o formato: Data Descrição Valor
        # Ex: 01/01/2025 SALÁRIO R$ 3.000,00
        # Ex: 05/01/2025 ALUGUEL R$ -1.500,00
        
        # Regex mais robusta para o formato do extrato fornecido
        # Captura a data (DD/MM/YYYY), a descrição (qualquer coisa até o valor) e o valor (com ou sem R$, com , para decimal e . para milhar, e opcionalmente sinal de -)
        # E também considera o formato de crédito/débito no final (C/D)
        
        # Tentativa 1: Formato DD/MM/YYYY Descrição R$ X.XXX,XX [C/D]
        # Tentativa 2: Formato DD/MM/YYYY Descrição X.XXX,XX [C/D]
        # Tentativa 3: Formato DD/MM/YYYY Descrição R$ -X.XXX,XX
        # Tentativa 4: Formato DD/MM/YYYY Descrição -X.XXX,XX
        
        # Ajuste para o extrato fornecido: 01/01/2025 SALÁRIO R$ 3.000,00
        #                                  05/01/2025 ALUGUEL R$ -1.500,00
        
        # Regex para o formato do extrato fornecido
        # Data (DD/MM/YYYY) - Descrição (qualquer coisa) - Valor (R$ opcional, sinal opcional, números com . e ,)
        pattern = re.compile(r'(\d{2}/\d{2}/\d{4})\s+([A-Z\s]+)\s+R\$\s*([\-]?\d{1,3}(?:\.\d{3})*,\d{2})')

        for line in text.split('\n'):
            match = pattern.search(line)
            if match:
                date_str, description, amount_str = match.groups()
                
                # Limpar a descrição de espaços extras
                description = description.strip()
                
                # Converter o valor para float
                # Remover o ponto de milhar e substituir a vírgula por ponto decimal
                amount_str = amount_str.replace('.', '').replace(',', '.')
                amount = float(amount_str)
                
                date = datetime.strptime(date_str, '%d/%m/%Y')
                
                transaction_type = 'Inflow' if amount >= 0 else 'Outflow'
                category = self._categorize_transaction(description, amount, transaction_type)
                
                self.transactions = pd.concat([
                    self.transactions,
                    pd.DataFrame([{
                        'Date': date,
                        'Description': description,
                        'Amount': amount,
                        'Type': transaction_type,
                        'Category': category
                    }])
                ], ignore_index=True)

    def _categorize_transaction(self, description: str, amount: float, transaction_type: str) -> str:
        description = description.lower()
        
        if transaction_type == "Inflow":
            for category, keywords in self.categories["inflow"].items():
                for keyword in keywords:
                    if keyword in description:
                        return category
            return "Outra Entrada"
        else:
            for category, keywords in self.categories["outflow"].items():
                for keyword in keywords:
                    if keyword in description:
                        return category
            return "Outra Saída"

    def get_monthly_summary(self) -> pd.DataFrame:
        if self.transactions.empty:
            return pd.DataFrame(columns=["Month", "Year", "Total Inflow", "Total Outflow", "Net Flow"])
        
        self.transactions["MonthYear"] = self.transactions["Date"].dt.to_period("M")
        
        monthly_summary = self.transactions.groupby("MonthYear").apply(self._calculate_monthly_metrics).reset_index()
        monthly_summary["Month"] = monthly_summary["MonthYear"].dt.month
        monthly_summary["Year"] = monthly_summary["MonthYear"].dt.year
        monthly_summary = monthly_summary[["Month", "Year", "Total Inflow", "Total Outflow", "Net Flow"]]
        return monthly_summary

    def _calculate_monthly_metrics(self, group):
        total_inflow = group[group["Type"] == "Inflow"]["Amount"].sum()
        total_outflow = group[group["Type"] == "Outflow"]["Amount"].sum()
        net_flow = total_inflow + total_outflow  # Outflows are already negative
        return pd.Series({
            "Total Inflow": total_inflow,
            "Total Outflow": total_outflow,
            "Net Flow": net_flow
        })

    def get_category_summary(self, transaction_type: str) -> pd.DataFrame:
        if self.transactions.empty:
            return pd.DataFrame(columns=["Category", "Total Amount"])
        
        filtered_transactions = self.transactions[self.transactions["Type"] == transaction_type]
        category_summary = filtered_transactions.groupby("Category")["Amount"].sum().reset_index()
        category_summary.columns = ["Category", "Total Amount"]
        return category_summary

    def get_all_transactions(self) -> pd.DataFrame:
        return self.transactions.copy()



