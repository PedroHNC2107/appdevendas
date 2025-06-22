import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

# Conexão com o banco de dados SQLite
conn = sqlite3.connect("pedidos.db")
cursor = conn.cursor()

# Criação da tabela (se não existir)
cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente TEXT,
    valor_da_compra TEXT,
    produto TEXT,
    quantidade_cartelas INTEGER,
    quantidade_unidades INTEGER,
    meio_pagamento TEXT,
    data TEXT
)
""")
conn.commit()

st.title("Cadastro de Pedidos")

# Formulário para novo pedido
with st.form("form_pedido"):
    nome = st.text_input("Nome do Cliente")
    valor = st.text_input("Valor da compra")
    produto = st.text_input("Produto Comprado")
    cartelas = st.number_input("Quantidade de Cartelas", min_value=0, step=1)
    unidades = st.number_input("Quantidade de Unidades", min_value=0, step=1)
    pagamento = st.selectbox("Meio de Pagamento", ["Dinheiro", "Pix", "Cartão", "Outros"])
    enviado = st.form_submit_button("Salvar Pedido")

    if enviado:
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO pedidos (nome_cliente, valor_da_compra, produto, quantidade_cartelas, quantidade_unidades, meio_pagamento, data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, valor, produto, cartelas, unidades, pagamento, data))
        conn.commit()
        st.success("Pedido salvo com sucesso!")

        # Atualizar o DataFrame e sobrescrever o Excel
        df_atualizado = pd.read_sql_query("SELECT * FROM pedidos", conn)
        df_atualizado.to_excel("pedidos_exportados.xlsx", index=False)

# Mostrar os pedidos cadastrados
st.subheader("Pedidos Registrados")
df = pd.read_sql_query("SELECT * FROM pedidos", conn)
st.dataframe(df)

# Exportar para Excel com botão de download
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Pedidos')
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(df)

st.download_button(
    label="📥 Baixar como Excel",
    data=excel_data,
    file_name='pedidos_exportados.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

st.info("O arquivo Excel é atualizado automaticamente a cada novo pedido. Você também pode baixá-lo manualmente acima.")
