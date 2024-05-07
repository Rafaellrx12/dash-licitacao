import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3


conexao = sqlite3.connect('db.sqlite3')


def consultar_sql(query):
    return pd.read_sql(query, conexao)

st.set_page_config(layout="wide")



df_licitacao = consultar_sql("SELECT * FROM licitacao_licitacao")
df_categoria = consultar_sql("SELECT * FROM licitacao_categoria")
df_departamento = consultar_sql("SELECT * FROM licitacao_departamento")


df_licitacao['data_demanda'] = pd.to_datetime(df_licitacao['data_demanda'])

legenda_situaçao = {"AN": "Análise", "CO": "Concluido", "NG" : "Negado"}
df_licitacao["situacao"] = df_licitacao["situacao"].map(legenda_situaçao)

filtro_ano = st.sidebar.selectbox("Selecione o ano", sorted(df_licitacao['data_demanda'].dt.year.unique()))
df_licitacao_filtrado = df_licitacao[df_licitacao['data_demanda'].dt.year == filtro_ano]


valor_total_departamento = df_licitacao_filtrado.groupby('departamento_id')['custo'].apply(lambda x: (x * df_licitacao_filtrado.loc[x.index, 'quantidade']).sum()).reset_index(name='total_custo')
valor_total_categoria = df_licitacao_filtrado.groupby('categoria_id')['custo'].apply(lambda x: (x * df_licitacao_filtrado.loc[x.index, 'quantidade']).sum()).reset_index(name='total_custo')


quantidade_por_situacao = df_licitacao_filtrado['situacao'].value_counts().reset_index()
quantidade_por_situacao.columns = ['Situacao', 'Quantidade']


conexao.close()


with st.container():
    fig_departamento = px.bar(valor_total_departamento.merge(df_departamento, how='left', left_on='departamento_id', right_on='id'), x='nome', y='total_custo', title="Valor Total de Cada Departamento")
    fig_departamento.update_xaxes(title_text='Departamento')
    fig_departamento.update_yaxes(title_text='Valor Total')
    st.plotly_chart(fig_departamento, use_container_width=True)


with st.container():
    fig_categoria = px.bar(valor_total_categoria.merge(df_categoria, how='left', left_on='categoria_id', right_on='id'), x='nome', y='total_custo', title="Valor Total de Cada Categoria")
    fig_categoria.update_xaxes(title_text='Categoria')
    fig_categoria.update_yaxes(title_text='Valor Total')
    st.plotly_chart(fig_categoria, use_container_width=True)


with st.container():
    fig_situacao = px.pie(quantidade_por_situacao, names='Situacao', values='Quantidade', title='Distribuição das Situações')
    fig_situacao.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_situacao, use_container_width=True)
