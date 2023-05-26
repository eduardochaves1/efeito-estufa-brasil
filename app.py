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
def plot_graph(fig, type=None):
  if type == 'hist':
    fig.update_xaxes(categoryorder='total descending')
  return st.plotly_chart(fig, use_container_width=True)

class Page():
  def __init__(self):
    self.emission_per_year = pd.read_parquet('./data/emission_per_year.parquet')
    self.df = pd.read_parquet('./data/dataset_clean.parquet')
    self.emission_per_uf = self.get_grouped_data(self.df, 'sigla_uf')
    self.emission_per_emission_type = self.get_grouped_data(self.df, 'tipo_emissao')
    self.emission_per_gas = self.get_grouped_data(self.df, 'gas').head(10)
    self.emission_per_eco_activity = self.get_grouped_data(self.df, 'atividade_economica')
    self.df_nivel_1 = self.get_grouped_data(self.df, 'nivel_1')
    self.df_nivel_2 = self.get_grouped_data(self.df, 'nivel_2')
    self.df_nivel_3 = self.get_grouped_data(self.df, 'nivel_3')
    self.df_nivel_4 = self.get_grouped_data(self.df, 'nivel_4')
    self.df_nivel_5 = self.get_grouped_data(self.df, 'nivel_5')
    self.df_nivel_6 = self.get_grouped_data(self.df, 'nivel_6')

    activity_dict = {
    "AGROPEC": "Agricultura",
    "PEC": "Pecuária",
    "AGR": "Agropecuária",
    "MET": "Metalurgia",
    "CIM": "Construção",
    "TRAN_CARGA": "Transporte de Carga",
    "TRAN_PASS": "Transporte de Passageiros",
    "ENE_ELET": "Energia Elétrica",
    "COM": "Comercial",
    "PUB": "Público",
    "RES": "Residencial",
    "PROD_COMB": "Produção de Combustível",
    "SANEAMENTO": "Saneamento",
    'Outra_IND': 'Outra Indústria',
    'HFC': 'Hidrofluorcarbonetos',
    }
    for key, value in activity_dict.items():
      self.emission_per_eco_activity = self.emission_per_eco_activity.rename(index={key: value})

    with open('data/Brasil.json', 'r') as file:
      self.geojson = json.loads(file.read())

    for feature in self.geojson['features']:
      feature['id'] = feature['properties']['UF']


  def get_grouped_data(self, df, groupby: str, sum: str='emissao', drop: str='ano'):
    return df.groupby(groupby, sort=False).sum(sum).drop(drop, axis=1).squeeze().sort_values(ascending=False)


  def plot_section(self, title, fig, type=None, tip=None, text=None):
    st.write('---')
    st.write(f'## {title}')
    if text:
      st.write(text)
    if tip:
      st.info(tip, icon='ℹ️')
    plot_graph(fig, type=type)


  def getStatesSection(self):
    st.write('---')
    st.write('## Emissões por Estado (2000-2019)')
    st.write('Os gráficos abaixo (Mapa, barras) apresentam o índice de emissão de gases de efeito estufa em diferentes estados do Brasil.')
    state_map, state_bar = st.tabs(['Mapa', 'Barras'])
    with state_map:
      plot_graph(px.choropleth_mapbox(
        locations = self.emission_per_uf.index,
        color = self.emission_per_uf.values,
        geojson = self.geojson,
        mapbox_style = "carto-positron",
        color_continuous_scale='RdBu_r',
        range_color=(self.emission_per_uf.iloc[0], self.emission_per_uf.iloc[-1]), # min & max values from emission_per_uf
        center={'lat': -15.793889, 'lon': -47.882778}, # brazil
        zoom=2.5,
        height=500))
    with state_bar:
      st.info('NA: Não Alocado.', icon='ℹ️')
      plot_graph(px.bar(x=self.emission_per_uf.index, y=self.emission_per_uf.values))


  def view(self):
    st.write('# ☁️ Emissões de Gases de Efeito Estufa no Brasil (2000-2019)')
    st.write('- Projeto no GitHub [neste link](https://github.com/eduardochaves1/efeito-estufa-brasil).')

    st.write('Os gráficos a seguir foram criados com base em um conjunto de dados de 20 anos de emissões de gases de efeito estufa (GEE) no Brasil (2000-2019), fornecendo mais de 1 milhão de registros para os setores de Agricultura, Energia, Indústria, Resíduos e Mudança do Uso da Terra em escala nacional. e níveis subnacionais. foi desenvolvido pelo Observatório do Clima, uma iniciativa da sociedade civil brasileira, com base nas diretrizes do IPCC e nos Inventários Nacionais Brasileiros incorporados a fatores e processos de emissão específicos do país.')

    st.dataframe(self.df.head(1_000), use_container_width=True)

    st.info('**OBS 1:** Todos os valores de emissão estão na escala de toneladas (t).', icon='ℹ️')
    st.info('**OBS 2:** Originalmente o dataset veio com registros desde 1970 (3.2 Mi de registros), porém filtramos os dados a partir de 2000 (1.2 Mi de registros) por questões de economia de performance e tempo. Por este motivo, a maior parte dos dados apresentados nesta página são entre 2000-2019.', icon='ℹ️')

    self.plot_section('Emissão de Gases de Efeito Estufa (1970-2019)', px.line(self.emission_per_year),
                      text='Apresentação da evolução no índice de emissão de Gases de Efeito Estufa (GEE) ao longo do tempo. Esse índice mede a quantidade de gases que são liberados na atmosfera e que contribuem para o aquecimento global. Quanto maior o índice, maior é a quantidade de GEE emitida.')
    self.plot_section('Emissão vs Remoção (2000-2019)', px.bar(x=self.emission_per_emission_type.index, y=self.emission_per_emission_type.values),
                      text='Índice de diferentes registros sobre GEE, podendo ser emissão ou remoção.')
    self.getStatesSection()
    self.plot_section('Atividades Econômicas (2000-2019)', px.bar(x=self.emission_per_eco_activity.index, y=self.emission_per_eco_activity.values),
                      text='Apontamento do índice de emissão de GEE nas atividades mais presentes no Brasil.')
    self.plot_section('Top 10 Gases com Maiores Emissões (2000-2019)', px.bar(x=self.emission_per_gas.index, y=self.emission_per_gas.values),
                      text='Demonstração dos 10 gases causadores do efeito estufa com maiores índices de emissão.')


    st.write('## Níveis Categórios de Emissão (2000-2019)')

    (self.tab_nivel_1, self.tab_nivel_2, self.tab_nivel_3,
    self.tab_nivel_4, self.tab_nivel_5, self.tab_nivel_6) = st.tabs(['Nível 1', 'Nível 2', 'Nível 3', 'Nível 4', 'Nível 5', 'Nível 6'])

    for level in range(1, 7):
        data = getattr(self, f'df_nivel_{level}')
        feature_tab = getattr(self, f'tab_nivel_{level}')
        with feature_tab:
            if level in [4,5,6]:
                plot_graph(px.bar(x=data.index, y=data.values))
            else:
                plot_graph(px.pie(names=data.index, values=data.values))

Page().view()
