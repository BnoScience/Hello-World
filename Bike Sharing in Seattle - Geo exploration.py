
# coding: utf-8

# # Base de dados de Compartilhamento de bicicletas em Seattle - USA
# 
# ### Dicionário dos dados: 
# 
# 
# 
#     ***Station dataset***
# 
#         station_id: station ID number
# 
#         name: name of station
# 
#         lat: station latitude
# 
#         long: station longitude
# 
#         install_date: date that station was placed in service
# 
#         install_dockcount: number of docks at each station on the installation date
# 
#         modification_date: date that station was modified, resulting in a change in location or dock count
# 
#         current_dockcount: number of docks at each station on 8/31/2016
# 
#         decommission_date: date that station was placed out of service
#  
#  
# 
#     Trip dataset
# 
#         trip_id: numeric ID of bike trip taken
# 
#         starttime: day and time trip started, in PST
# 
#         stoptime: day and time trip ended, in PST
# 
#         bikeid: ID attached to each bike
# 
#         tripduration: time of trip in seconds
# 
#         from_station_name: name of station where trip originated
# 
#         to_station_name: name of station where trip terminated
# 
#         from_station_id: ID of station where trip originated
# 
#         to_station_id: ID of station where trip terminated
# 
#         usertype: "Short-Term Pass Holder" is a rider who purchased a 24-Hour or 3-Day Pass; "Member" is a rider who purchased a Monthly or an Annual Membership
# 
#         gender: gender of rider
# 
#         birthyear: birth year of rider
# 
# 
# 
# Weather dataset contains daily weather information in the service area
# 

# In[1]:


# Importando as bibliotecas

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.parser import parse # Helps to format strins into date

get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


# importando o dataset de viagens

trip = pd.read_csv('trip.csv', error_bad_lines=False)

#importando o dataset de estações

station = pd.read_csv('station.csv',error_bad_lines=False)

# Importando o dataset de clima

weather = pd.read_csv('weather.csv',error_bad_lines=False)


# In[3]:


trip.head(10)


# In[4]:


trip.info()


# In[5]:


station.head()


# In[6]:


station.info()


# In[7]:


weather.head()


# In[8]:


weather.info()


# Lets explore this datasets. I will star with the trips dataset, but before i start the exploration, there are some things i should do first:
# 
# * Transform the time columns in time series (I chalenging myself, thats the first time i do this)
# * Join the lat e long in the trip dataset, this way i can do some geoanalysis

# # Data Manipulation on Trips Dataset

# In[9]:


trip.columns


# In[10]:


# lets drop the id columns that that are unnecessary

trip.drop(['trip_id','bikeid'], axis = 1,   inplace = True)


# In[11]:


trip.info()


# In[12]:


# Tranforming the starttime column

data = trip['starttime']


# In[13]:


dta = list(trip['starttime']) # transforma cada elemento da coluna startime em uma string
dta = pd.to_datetime(dta)  # Nor formato de string, cada elemento da lista é tranformado em data pelo pandas

trip['starttime'] = dta # Salvando as alterações na coluna


# In[14]:


# Confirmando se deu certo
trip.info()


# In[15]:


trip.starttime


# In[16]:


trip.head()


# In[17]:


# na verdade só precisamos da coluna starttime, uma vez que já temos a variável de duração da viagem

trip.drop(columns='stoptime', axis = 1, inplace=True)


# In[18]:


trip.info()


# Now should be a good ideia estimate the age of the users, as we have the birthyear

# In[19]:


trip.isnull().sum()


# In[20]:


trip.birthyear.describe()


# In[21]:


# Filling the null values, with values between 1969 and 1989

trip.birthyear.fillna(value = np.random.randint(1969,1989), inplace=True)
    


# In[22]:


trip.info()


# In[23]:


trip.birthyear.describe()


# In[24]:


ano = trip.starttime

def idade(ano):
    '''Essa função extrai o ano de cada elemento da coluna 'starttime' '''
    idade = []
    for i in ano.index:  # pegue cada elemento no índice da variável 'ano'
        a = str(ano[i])  # 'i' representa cada elemeto do índice da variável 'ano', por isso cada vez que 'for' identifica um 
        # número no índice ele joga dentro da variável 'a' que seleciona um item da variável 'ano' e transforma em string
        b = a.split('-')[0] # a variável 'b', armazena o resultado do método .split() aplicado sobre a variável 'a', em 
        # seguida, extraio o primeiro elemento do resultado de .split(), que é o ano
        c = pd.to_numeric(b)  # converte a string ano, para número
        

        idade.append(c.astype(int)) # armazena 'c' na lista 'idade', criada no início da função
    return idade


# In[25]:


# usando a função e armazenando o resultado em uma variável
idad = idade(ano)


# In[26]:


trip['idade'] = idad - trip.birthyear
trip['idade'] = trip['idade'].astype(int)


# In[27]:


trip.columns


# In[28]:


trip.head()


# In[29]:


# Preenchendo os valores ausentes da coluna sexo
trip.gender.value_counts()


# In[30]:


trip.gender.isnull().sum()


# In[31]:


# Usando o método fillna com o parâmetro 'ffill' para preencher os valores nulos com a observação válida 
gender = trip.gender.fillna(method='ffill')
trip.gender = gender
trip.gender.isnull().sum()


# In[32]:


trip.head()


# In[33]:


station.head()


# In[34]:


# Para fazer o merge, é necessário que ambos os dataframes, tenham pelo menos um coluna com o mesmo nome. 
# criando as colunas 'from_station_id' e 'to_station_id' no df station

station['from_station_id'] = station.station_id
station['to_station_id'] = station.station_id
station.head()


# In[35]:


# criando outro dataset, somente com a coluna 'from_station_id' e os dados de localização
from_station = station[['lat', 'long','from_station_id']]
from_station.head()


# In[36]:


# Incluindo a latitude e longitude das estações de partida em um novo dataset: trip2

trip2 = pd.merge(trip,from_station, on='from_station_id')


# In[37]:


trip2.info()


# In[38]:


# identificando as novas colunas como sendo os dados do local de partida
trip2.columns = ['starttime', 'tripduration', 'from_station_name',
       'to_station_name', 'from_station_id', 'to_station_id', 'usertype',
       'gender', 'birthyear', 'idade', 'from_lat', 'from_long']
trip2.columns


# In[39]:


# criando outro dataset, somente com a coluna 'to_station_id'
to_station = station[['lat', 'long','to_station_id']]
to_station.head()


# In[40]:


# Incluindo a latitude e longitude das estações de partida em um novo dataset: trip3

trip3 = pd.merge(trip2,to_station, on='to_station_id')


# In[41]:


trip3.columns


# In[42]:


# identificando as colunas dos dados de chegada
trip3.columns = ['starttime', 'tripduration', 'from_station_name',
       'to_station_name', 'from_station_id', 'to_station_id', 'usertype',
       'gender', 'birthyear', 'idade', 'from_lat', 'from_long', 'to_lat', 'to_long']


# In[43]:


trip3.head()


# In[44]:


trip3.info()


# ### Para o dataset ficar completo, precisamos incluir os dados de clima. 
# 
# Antes disso, é necessário me familiarizar com as variáveis do dataset 'weather'. Mas antes, vamos dar uma olhada onde ficam as estações de bike.

# In[45]:


# Folium é a biblioteca que permite plotagem com mapas, muito simples de usar

import folium


# In[46]:


station.columns


# In[47]:


mapa = folium.Map(location=[ 47.608013,  -122.335167], zoom_start=12) # Determinando o mapa de seattle usando os dados de latitude e longitude

lat = station['lat'].values # pegando os valores de latitude das estações do dataset station
long = station['long'].values # pegando os valores de latitude das estações do dataset station

for la, lo in zip(lat, long): # para cada valor em lat e long
    folium.Marker([la, lo]).add_to(mapa) # crie um marcador e coloque na variável mapa (que no caso é o mapa de Seattle)
mapa # Exiba o mapa


# In[48]:


trip3.from_station_name.value_counts().head(10)


# In[49]:


# Vamos ver no mapa as 10 estações mais populares

estacoes_mais_pop = pd.DataFrame(trip3.from_station_name.value_counts().head(10)) # Contando as 10 mais criando um novo df para poder passara 
# para o folium
station_2 = station[['name','lat', 'long' ]]
station_2.columns = ['from_station_name','lat', 'long']


# In[50]:


estacoes_mais_pop = estacoes_mais_pop.reset_index() # resetando o índice para ajustar o nome das colunas


# In[51]:


estacoes_mais_pop # repare que a coluna com o nome da estação está com o nome 'index'


# In[52]:


estacoes_mais_pop.columns = ['from_station_name','contagem'] # Corrigindo o problema, simplesmente renomeando as colunas


# In[53]:


estacoes_mais_pop


# In[54]:


estacoes_mais_pop = pd.merge(estacoes_mais_pop, station_2, on='from_station_name') # incluindo os dados de localização (lat e long)


# In[55]:


estacoes_mais_pop


# In[56]:


mapa2 = folium.Map(location=[47.608013,  -122.335167], zoom_start=13) # O mesmo processo anterior, mas precisamos criar um novo Mapa

lat = estacoes_mais_pop['lat'] 
long = estacoes_mais_pop['long'] 

# Dessa vez escrevi linha por linha, pois queria incluir o nome da estação no mapa. Não consegui achar um modo mais prático de fazer,
# por enquanto...

folium.Marker([47.614315, -122.354093],popup='Pier 69 / Alaskan Way & Clay St').add_to(mapa2)
folium.Marker([47.615330 ,-122.311752],popup='E Pine St & 16th Ave').add_to(mapa2)
folium.Marker([47.618418 ,-122.350964],popup='3rd Ave & Broad St ').add_to(mapa2)
folium.Marker([47.610185 ,-122.339641],popup='2nd Ave & Pine St').add_to(mapa2)
folium.Marker([47.613628 ,-122.337341],popup='Westlake Ave & 6th Ave').add_to(mapa2)
folium.Marker([47.622063 ,-122.321251],popup='E Harrison St & Broadway Ave E ').add_to(mapa2)
folium.Marker([47.615486 ,-122.318245],popup='Cal Anderson Park / 11th Ave & Pine St').add_to(mapa2)
folium.Marker([47.619859 ,-122.330304],popup='REI / Yale Ave N & John St ').add_to(mapa2)
folium.Marker([47.615829 ,-122.348564],popup='2nd Ave & Vine St').add_to(mapa2)
folium.Marker([47.620712 ,-122.312805],popup='15th Ave E & E Thomas St').add_to(mapa2)

mapa2


# In[57]:


# Avaliando o dataset sobre o clima
weather.head(10)


# In[58]:


# Avaliando o dataset trip3, lembrando que este dataset contém os dados de localização
trip3.head()


# In[59]:


data_str = list(trip3.starttime) # Criando uma nova coluna de data, com o mesmo formato de data do dataset sobre o clima
# isso vai permitir adicionar os dados climáticos no trip.


# In[60]:


data_str


# In[61]:


data_str = [datetime.strftime(x, '%Y-%m-%d') for x in data_str] # Formatando a coluna usando datetime


# In[62]:


data_str[:5]


# In[63]:


trip3['Date'] = data_str # Adicionando a coluna


# In[64]:


type(weather.Date)


# In[65]:


trip3.head() # Confirmando a coluna


# In[66]:


trip3.Date.dtypes


# In[67]:


weather.Date.dtypes


# In[68]:


# usando o mesmo método usado na coluna starttime do dataset trip isso é necessário pois as colunas Date de trip3 e weather
# estão salvas com tipos de dados diferentes

dt = list(weather['Date']) # transforma cada elemento da coluna Date em uma string
dt = pd.to_datetime(dt)  # Nor formato de string, cada elemento da lista é tranformado em data pelo pandas

weather['Date'] = dt # Salvando as alterações na coluna


# In[69]:


weather.head()


# In[70]:


trip3.Date = pd.to_datetime(trip3.Date)


# In[71]:


trip4 = pd.merge(weather,trip3, on = 'Date')


# In[72]:


trip4.info()


# In[73]:


trip4.head()


# Now we have a huge dataset with 35 colunas with data about use, weather and localization. But there are some null values. Lets work on it ! 

# ### Mean_Temperature_F

# In[74]:


# We have 110 null values in this colunm
trip4.Mean_Temperature_F.isnull().sum()


# In[75]:


trip4.Mean_Temperature_F.describe()


# In[76]:


# Vamos preencher os dados ausentes com o valor da média, mais ou menos o desvio padrão
trip4.Mean_Temperature_F = trip4.Mean_Temperature_F.fillna(value = np.random.randint(48,68))


# In[77]:


trip4.Mean_Temperature_F.describe()


# In[78]:


trip4.Mean_Temperature_F.isnull().sum()


# In[79]:


trip4.isnull().sum()


# ### Max_Gust_Speed_MPH

# In[80]:


trip4.Max_Gust_Speed_MPH.describe()


# this column should be numeric, but has to many null values and i dont know what it means. sou, we gonna drop it.

# In[81]:


trip4.drop(columns='Max_Gust_Speed_MPH', axis=1, inplace=True)


# In[82]:


trip4.isnull().sum()


# ### Events
# 
# I think this information is very important, but has too many NaN values, that must be days that dont ocurried any event

# In[83]:


trip4.Events.describe()


# In[84]:


trip4.Events.value_counts()


# In[85]:


events = trip4.Events


# In[86]:


events.replace('Rain , Thunderstorm', 'Rain-Thunderstorm', inplace = True)
events.replace('Rain , Snow', 'Rain-Snow', inplace = True)
events.replace('Fog , Rain', 'Rain-Snow', inplace = True)
events.value_counts()


# In[87]:


events.fillna(value='No-Event', inplace=True)


# In[88]:


events.isnull().sum()


# In[89]:


events.value_counts()


# In[90]:


trip4.info()


# Lets choose the columns we are interested in

# In[91]:


columns_to_drop = ['Max_Temperature_F','Min_TemperatureF', 'Max_Dew_Point_F', 'MeanDew_Point_F', 'Min_Dewpoint_F',
                   'Max_Humidity', 'Min_Humidity','Max_Sea_Level_Pressure_In', 'Min_Sea_Level_Pressure_In', 'Max_Visibility_Miles',
                   'Min_Visibility_Miles', 'Max_Wind_Speed_MPH']                 


# In[92]:


# converting the trip duration from seconds to minutes
trip4.tripduration = trip4.tripduration / 60


# In[93]:


trip5 = trip4.drop(columns= columns_to_drop, axis=1)


# In[94]:


trip5.columns


# In[95]:


trip5.head()


# In[96]:


trip5.describe()


# ### Now we gona work on the date vals. 
# 
# My goal is:
#  * separete the date into new columns: Year, month, day and hour
#  * from the hour column create a new feature that identifies the time of the day: Morning, evening and night, so we can understand the time of the day that people most uses the bike
#  * from the month column extract the year station: Summer, winter, 
#  * create days of the week
#  
# I think this changes can give us a real understanding about the use patterns
