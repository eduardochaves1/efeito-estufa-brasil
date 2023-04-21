import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Emissões de Gases de Efeito Estufa no Brasil (2000-2019)', page_icon='☁️', layout='wide')
st.write('''
<style>
  section.main > div {max-width:75em}
</style>
''', unsafe_allow_html=True)

class Page():
  def __init__(self):
    self.df = pd.read_parquet('./data/dataset_clean.parquet')
    self.emission_by_year = pd.read_parquet('./data/emission_by_year.parquet')

  def plot_graph(self, fig, type):
    if type == 'hist':
      fig.update_xaxes(categoryorder='total descending')

    return st.plotly_chart(fig, use_container_width=True)

  def plot_section(self, title, fig, tip=None, type=None):
    st.write('---')
    st.write(f'## {title}')
    if tip:
      st.info(tip, icon='ℹ️')
    self.plot_graph(fig, type=type)

  def view(self):
    st.write('# ☁️ Emissões de Gases de Efeito Estufa no Brasil (2000-2019)')
    st.dataframe(self.df.head(1_000), use_container_width=True)
    st.info('Todos os valores de emissão estão na escala de toneladas.', icon='ℹ️')

    self.plot_section('Emissão de Gases de Efeito Estufa (1970-2019)', px.line(self.emission_by_year))
    self.plot_section('Tipos de Emissão', px.histogram(self.df['tipo_emissao']), type='hist')
    self.plot_section('Estados com Mais Registros', px.histogram(self.df['sigla_uf']), type='hist',
      tip='NA: Não Alocado.')
    self.plot_section('Atividades Econômicas', px.histogram(self.df['atividade_economica']), type='hist')

Page().view()
