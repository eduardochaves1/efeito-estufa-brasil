import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title='Emissões de Gases de Efeito Estufa no Brasil (2000-2019)', page_icon='☁️', layout='wide')
st.write('''
<style>
  section.main > div {max-width:75em}
</style>
''', unsafe_allow_html=True)

@st.cache_resource
def plot_graph(fig, type):
  if type == 'hist':
    fig.update_xaxes(categoryorder='total descending')
  return st.plotly_chart(fig, use_container_width=True)
class Page():
  def __init__(self):
    self.df = pd.read_parquet('./data/dataset_clean.parquet')
    self.emission_by_year = pd.read_parquet('./data/emission_by_year.parquet')

    with open('data/Brasil.json', 'r') as file:
      self.geojson = json.loads(file.read())

    for feature in self.geojson['features']:
      feature['id'] = feature['properties']['UF']

  def plot_section(self, title, fig, tip=None, type=None):
    st.write('---')
    st.write(f'## {title}')
    if tip:
      st.info(tip, icon='ℹ️')
    plot_graph(fig, type=type)

  def view(self):
    st.write('# ☁️ Emissões de Gases de Efeito Estufa no Brasil (2000-2019)')
    st.dataframe(self.df.head(1_000), use_container_width=True)
    st.info('**OBS 1:** Todos os valores de emissão estão na escala de toneladas.', icon='ℹ️')
    st.info('**OBS 2:** A grande maior parte dos gráficos representam dados de 2000 até 2019 apenas, por questões de economia de performance e tempo.', icon='ℹ️')

    self.plot_section('Emissão de Gases de Efeito Estufa (1970-2019)', px.line(self.emission_by_year))
    self.plot_section('Tipos de Emissão (2000-2019)', px.bar(self.df['tipo_emissao'].value_counts()))
    self.plot_section('Emissões por Estado (2000-2019)', px.choropleth_mapbox(
      self.df,
      locations = 'sigla_uf',
      color = 'emissao',
      geojson = self.geojson,
      mapbox_style = "carto-positron",
      range_color=(0, 250_000),
      center={'lat': -15.793889, 'lon': -47.882778},
      zoom=2.5,
      height=500))
    self.plot_section('Estados com Mais Registros (2000-2019)', px.bar(self.df['sigla_uf'].value_counts()),
      tip='NA: Não Alocado.')
    self.plot_section('Atividades Econômicas (2000-2019)', px.bar(self.df['atividade_economica'].value_counts()))
    self.plot_section('Top 10 Gases com Maiores Emissões (2000-2019)', px.bar(self.df['gas'].value_counts().head(10)))

Page().view()
