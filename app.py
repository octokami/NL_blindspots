from dash import Dash, dcc, html, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
# whilst your local machine's webserver doesn't need this, Heroku's linux webserver (i.e. dyno) does. I.e. This is your HTTP server
import gunicorn
from whitenoise import WhiteNoise  # for serving static files on Heroku
from sklearn.preprocessing import MinMaxScaler

# Data
filename = 'with_coordinates'
data_path = 'data/'

with_coordinates = pd.read_pickle(data_path + filename + '.pkl', compression='bz2')
df = with_coordinates.copy()
neighbourhoods = df['neighbourhood'].unique()
municipalities = df['municipality'].unique()
municipalities = np.append(municipalities, 'Netherlands')

# Instantiate dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Reference the underlying flask app (Used by gunicorn webserver in Heroku production deployment)
server = app.server

# Enable Whitenoise for serving static files from Heroku (the /static folder is seen as root by Heroku)
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='homepage')
])

### Index page ###


index_page = html.Div([
    html.H1('Blind Spot Map for Dutch playgrounds, parks and sports facilities'),
    dcc.Link('Go to the Blind Spot Map', href='/map'),
    html.Br(),
    dcc.Link('Go to the Neighbourhood Charts', href='/chart'),
    dcc.Markdown('''
**Blind Spot formulas:**
* Playground demand = (% of children <15) + (Households with children) + (amount of births) - (cars per household) + (% rental homes)
* Sport demand = - (age) - (Households with children) - (% female) + (%singles) + (education level) + (%unemployed) + (town size)
* Park demand = - (age) + (Households with children) + (% female) + (%singles) + (education level)

**Methodology**

For each attribute present in the demand formula:

1. If the neighbourhood has a higher value of the attribute than the quantile of the whole dataset demand is added by 1

    1.1. Quantile default is 0.5, which is the median

2. If more weight for a certain attribute is wished, they can be manually inputed

    2.1. By default all attributes have the same weight

3. If a neighbourhood already has at least one facility of that type within the 'Minimum distance to facilities', the demand is zero

4. The Minimum demand value sets what is the minimum value that should be seen on the map

**References**
* Playground

article:https://sitelines.com/articles/2017/11/playground-planning-101-location-location-location/ 
Creating a playground for the children of the community to enjoy is best if you pick a location that can serve the most kids. A good rule of thumb is to select a site that is within walking distance to the greatest number of families. Choose a site that is close to:


Highly populated neighborhoods
Schools
Entertainment facilities
Libraries
Trails and outdoor hotspots
https://www.miracle-recreation.com/blog/ultimate-guide-planning-your-playground/?lang=can#space-considerations-when-planning-playground 
Knowing who the playground is intended for will help you decide what type of equipment to install. Children play differently and are at various levels of development at different ages. For instance, a playground designed for a 5-year-old won’t appeal to a 12-year-old, and might not be the appropriate size for them. Likewise, toddlers and younger children will have difficulty using playground equipment designed for 5- or 7-year-olds.
https://www.jstor.org/stable/pdf/44659555.pdf 
The children's playground, for boys and girls under twelve, with sand pits, baby hammocks, etc., and a woman teacher in charge. 
Special facilities depending upon local opportunities, such as swimming

Based on the above literature, I propose the following variables to build a demand model on:
Children under 15 years old, data on cbs website: https://opendata.cbs.nl/?dl=57C47#/CBS/nl/dataset/85039NED/table 
Amount of families with children: https://opendata.cbs.nl/?dl=57C47#/CBS/nl/dataset/85039NED/table 
Birth total:
https://opendata.cbs.nl/?dl=57C47#/CBS/nl/dataset/85039NED/table 
Household income: (no source on this in CBS)
https://frw.studenttheses.ub.rug.nl/3781/1/BaPo_thesis_finalversion_DavidSnippe.pdf low income implies more use of parks
Cars per household
Percentage rental homes

* Sports facilities

Dutch study that uses Age, gender, level of education, employment(binary), children living at home (binary), Neighbourhood safety and Neighbourhood Socio-economic status
Article: Do objective neighbourhood characteristics relate to residents’ preferences for certain sports locations? A cross-sectional study using a discrete choice modelling approach https://www.researchgate.net/publication/321738962_Do_objective_neighbourhood_characteristics_relate_to_residents%27_preferences_for_certain_sports_locations_A_cross-sectional_study_using_a_discrete_choice_modelling_approach

Economic and demographic factors: (age, ethnicity, education, and health)
Decrease of participation with increasing age, for men even stronger than for women—men more likely to participate in sport—women have different preferences regarding the type of sport—married people participate less in sport than singles—ethnic minorities participate less in sports than whites— negative effect of poor health—positive impact of household income and education—unemployed participate more in sports

Article: Investigating the Economic and Demographic Determinants of Sporting Participation in England
https://www.jstor.org/stable/3559931

Positive effect of income—employed persons less likely to participate in sport—negative effect of age—positive effect of educational level—females less likely to participate than males—Blacks and Hispanics less likely to participate than Whites.
Article: Economic Determinants of Participation in Physical Activity and Sport
https://ideas.repec.org/p/spe/wpaper/0613.html

Lera-López and Rapún-Gárate:
Women are less likely to participate in sport than men—positive influence of age—education is positively related to the frequency of sport participation—income level has no influence on sport participation—being employed is negatively related to the frequency of sport participation.

Hovemann and Wicker:
European model: age, relationship, Having children and occupation have a negative effect—education years and town size have a significant positive influence.
https://www.researchgate.net/publication/346161866_Sports_facilities%27_location_and_participation_in_sports_among_working_adults


About age:
3–18: Higher demand of Swimming pools
19–28: higher demand of Gymnasia, sports fields and public playgrounds and fitness centers
65 and older: higher demand of Swimming pools and forest area
being responsible for housekeeping and undertaking voluntary work reduces the likelihood of participating in sport (Downward and Riordan)
Article: Promoting Sport for All to Age-specific Target Groups: the Impact of Sport Infrastructure
https://www.tandfonline.com/doi/full/10.1080/16184740802571377?casa_token=GkmAWu2tlVMAAAAA%3AXA_HhWxXLq6WHOIGeiwet7sb2w-J-Um7mKDXMDpCDNQR0LT6BAUfBkX5eI_Fdlwb8pyiNb2Y4f8VmA
Article: Socio-economic patterns of sport demand and ageing
https://link.springer.com/article/10.1007/s11556-010-0066-5


* Parks

Paper: https://www.sciencedirect.com/science/article/pii/S1353829210000316

This meta study investigates all the important factors and features amongst different sample groups that influence the attractiveness of parks. A few features were deemed most important across multiple studies: Condition, accessibility, aesthetics, and safety. 

Interestingly, women have more appreciation for parks & greenery close to home. The paper states that parks provide opportunities to socialize in safe and supportive social environments appeared to be important, notably for women and girls. This finding is also supported by other papers, such as: https://www.sciencedirect.com/science/article/pii/S2213078020300463?casa_token=dRnI7X6FR6IAAAAA:HFTd0DnnXG_uOe82bvKIt1t8PH2IXJ_GD5j1KlmmQz2Sl9b15CLhJw5PZgmyUCW7qKrVZOatRZ4#bib42
As is the case among adults reported elsewhere, quantitative evidence suggests that parks also support both physical activity behavior and socializing among children. In addition to the home and local streets, parks are a popular setting for physical activity among children. However, children do not always visit the closest park and may be willing to travel further to use certain parks with desired features or facilities.

From these findings we conclude the following contributors to increasing or decreasing the demand value of park and nature: Areas with high relative frequency of families with children have higher demand for parks & nature (+), female (+)

Paper: https://www.sciencedirect.com/science/article/pii/S2213078020300463?casa_token=dRnI7X6FR6IAAAAA:HFTd0DnnXG_uOe82bvKIt1t8PH2IXJ_GD5j1KlmmQz2Sl9b15CLhJw5PZgmyUCW7qKrVZOatRZ4#bib42

This paper looked more deeply into demographic variables, such as age, income, and education. 

The study indicated income, educational background and occupation of the respondents have a statistically significant association (P < 0.05) with the frequency of park visit. The low-income group and those who had primary and below primary education were infrequent park users in the study area. Regarding marital status, the highest percentage of park users in the study area were single group (64.6%).
Old age and very low-income age group from 16 to 25 was the largest park user whereas above 55 years was the lowest park user. The study found that the rate of participation in park utilization decreases with an increase of age.me groups were identified as the least and infrequent park users in the study area. 

From these findings we conclude the following contributors to increasing or decreasing the demand value of park and nature: female (+), as income increases, demand increases (+), as education increases, demand increases (+), as age increases, demand decreases (-), single (+)

Paper: https://www.sciencedirect.com/science/article/pii/S0169204600000396?casa_token=3GZAKKq19BkAAAAA:7qwqXqlObueRrpBB5sVkwoJ0ApDKdIub03Mk0RxnTEdJxCuL37fRL-phagwz-RSDHGNVPoTm-iA

The paper investigates what factors influence the frequency to which a park is used by its inhabitants. The frequency of the park usage can highlight what factors contribute to the placement of a successful park. The most relevant findings of this paper to our case are the following: 

The frequency to which people visit a park greatly decreases when the distance to the park from their home is larger than 1000m, while there is little difference in frequency for distances ranging from 500-1000. People who live less than 500 meter from the park are the most frequent users overall. It is hypothesized that the provision of parks within 500 m of a given resident would meet most residents' requirements on park use. Under these ideal conditions, the average park use frequency is as high as 9.9 times per month. When the distance to the nearest park is 500–1000 m or 1000+ m, the visitation frequency drops to 6.9 and 4.1 times per month, much lower than the frequency of visits under ideal conditions.

From these findings we conclude the following contributors to increasing or decreasing the demand value of park and nature: Residents that meet the earlier described criteria, and live further than 1000m from a park, might have increased demand for parks & nature. 

**Datasets:**
* Centraal Bureau voor de Statistiek, subject to the [Creative Commons Naamsvermelding (CC BY 4.0)](https://www.cbs.nl/nl-nl/over-ons/website/copyright)
* Open Street Map, licensed under the [Open Data Commons Open Database License (ODbL)](https://www.openstreetmap.org/copyright) by the OpenStreetMap Foundation (OSMF)

### Built with ![Image](heart.png) in Python using [Dash](https://plotly.com/dash/)"""'''),
])

### Page 1 ###
page_1_header = html.H1('Blind Spot Map')

page_1_body = html.Div([
        # Map
        html.Div([
            html.B('Municipality', style={'font-size': '18px'}),
            dcc.Dropdown(municipalities, value='Netherlands', id='dropdown_province'),
            dcc.RadioItems(id='radio', options=['Playgrounds', 'Sports Facilities', 'Parks & Nature'],
                           value='Playgrounds',
                           inline=True, inputStyle={"margin-left": "20px"}),
            dcc.Graph(id='map'),
        ], style={'width': '65%', 'float': 'left', 'display': 'inline-block'}),

        # Manual inputs
        html.Div([
            html.Div([
                html.Div([
                    html.B('Minimum Demand Value', style={'font-size': '16px'}),
                    dcc.Slider(min=0, max=1, value=0.7, id='slider_threshold'),
                ], style={'width': '48%', 'float': 'left'}),
                html.Div([
                    html.B('Minimum distance to facilities (Km)', style={'font-size': '16px', 'text-align': 'right'}),
                    dcc.Input(value=1, type='number', id='input_distance'),
                ], style={'width': '48%', 'float': 'right'})
            ], className='row'),

            html.Br(),

            html.Div([
                html.H2('Quantile'),
                html.Label('Citizens quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='citizens_quantile'),
                html.Label('Females quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='females_quantile'),
                html.Label('A 00 14 quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='a_00_14_quantile'),
                html.Label('A 45 64 quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='a_45_64_quantile'),
                html.Label('Births quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='births_quantile'),
                html.Label('Households with children quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='households_with_children_quantile'),
                html.Label('Singles quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='singles_quantile'),
                html.Label('Rental quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='rental_quantile'),
                html.Label('Working quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='working_quantile'),
                html.Label('Low edu quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='low_edu_quantile'),
                html.Label('High edu quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='high_edu_quantile'),
                html.Label('Cars quantile'),
                dcc.Slider(min=0, max=1, value=0.5, id='cars_quantile'),
            ], className='row', style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),

            html.Div([
                html.H2('Weight'),
                html.Label('Citizens weight'),
                dcc.Input(value=1, type='number', id='citizens_weight'),
                html.Label('Females weight'),
                dcc.Input(value=1, type='number', id='females_weight'),
                html.Label('A 00 14 weight'),
                dcc.Input(value=1, type='number', id='a_00_14_weight'),
                html.Label('A 45 64 weight'),
                dcc.Input(value=1, type='number', id='a_45_64_weight'),
                html.Label('Births weight'),
                dcc.Input(value=1, type='number', id='births_weight'),
                html.Label('Households with children weight'),
                dcc.Input(value=1, type='number', id='households_with_children_weight'),
                html.Label('Single weight'),
                dcc.Input(value=1, type='number', id='singles_weight'),
                html.Label('Rental weight'),
                dcc.Input(value=1, type='number', id='rental_weight'),
                html.Label('Working weight'),
                dcc.Input(value=1, type='number', id='working_weight'),
                html.Label('Low edu weight'),
                dcc.Input(value=1, type='number', id='low_edu_weight'),
                html.Label('High edu weight'),
                dcc.Input(value=1, type='number', id='high_edu_weight'),
                html.Label('Cars weight'),
                dcc.Input(value=1, type='number', id='cars_weight'),
            ], className='row', style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),

            html.Br(),
            html.Hr(),

            html.Div([
                html.A(html.Button('Reset values'), href='/map', style={'width': '50%', 'float': 'left'}),
                html.Button('Download', id='button_download', n_clicks=0, style={'width': '50%', 'float': 'right'}),
                dcc.Download(id="download-dataframe-xlsx"),
            ]),

        ], className='row', style={'width': '25%', 'float': 'right', 'display': 'inline-block'}),

    ], className='row')

# Footer
page_1_footer = html.Div([
        html.Br(),
        dcc.Link('Go to Neighbourhood charts', href='/chart'),
        html.Br(),
        dcc.Link('Go back to the homepage', href='/'),

        # Down Table
        html.Div([
            dbc.Container(id='tbl_out')
        ], className='row'),
    ])

page_1_layout = html.Div([page_1_header, page_1_body, page_1_footer])

@app.callback(
    Output("map", "figure"),
    Output('tbl_out', 'children'),
    Input("radio", "value"),
    Input('dropdown_province', 'value'),
    Input('slider_threshold', 'value'),
    Input('input_distance', 'value'),
    # 12 weights
    Input('citizens_weight', 'value'),
    Input('females_weight', 'value'),
    Input('a_00_14_weight', 'value'),
    Input('a_45_64_weight', 'value'),
    Input('births_weight', 'value'),
    Input('households_with_children_weight', 'value'),
    Input('singles_weight', 'value'),
    Input('rental_weight', 'value'),
    Input('working_weight', 'value'),
    Input('low_edu_weight', 'value'),
    Input('high_edu_weight', 'value'),
    Input('cars_weight', 'value'),
    # 12 Quantiles
    Input('citizens_quantile', 'value'),
    Input('females_quantile', 'value'),
    Input('a_00_14_quantile', 'value'),
    Input('a_45_64_quantile', 'value'),
    Input('births_quantile', 'value'),
    Input('households_with_children_quantile', 'value'),
    Input('singles_quantile', 'value'),
    Input('rental_quantile', 'value'),
    Input('working_quantile', 'value'),
    Input('low_edu_quantile', 'value'),
    Input('high_edu_quantile', 'value'),
    Input('cars_quantile', 'value'),
)
def update_map(radio_input, municipality, slider_threshold, input_distance,
               citizens_weight, females_weight, a_00_14_weight, a_45_64_weight, births_weight,
               households_with_children_weight,
               singles_weight, rental_weight, working_weight, low_edu_weight, high_edu_weight, cars_weight,

               citizens_quantile, females_quantile, a_00_14_quantile, a_45_64_quantile, births_quantile,
               households_with_children_quantile,
               singles_quantile, rental_quantile, working_quantile, low_edu_quantile, high_edu_quantile, cars_quantile):
    df = with_coordinates.copy()

    # Table
    if municipality != 'Netherlands':
        zoom = 11
        df = df[df['municipality'] == municipality]
        df_table = df.loc[:, ['neighbourhood', 'citizens', 'females', 'a_00_14', 'a_15_24', 'a_25_44', 'a_45_64',
                              'births', 'households_with_children', 'not_married', 'rental_perc', 'percentage_working',
                              'low_edu', 'mid_edu', 'high_edu', 'cars_per_household',
                              'play_demand', 'sport_demand', 'park_demand', 'sport_distance', 'play_distance',
                              'park_distance']]
        if (radio_input == "Playgrounds"):
            df_table.sort_values(by='play_demand', ascending=False, inplace=True)
        if (radio_input == "Parks & Nature"):
            df_table.sort_values(by='park_demand', ascending=False, inplace=True)
        if (radio_input == "Sports Facilities"):
            df_table.sort_values(by='sport_demand', ascending=False, inplace=True)

        table_out = [dbc.Label(municipality),
                     dash_table.DataTable(df_table.to_dict('records'), [{"name": i, "id": i} for i in df_table.columns],
                                          id='tbl')]

    if municipality == 'Netherlands':
        clickData = None
        zoom = 7
        table_out = []

    # Weights and Quantiles

    # Children under 15
    if (a_00_14_weight != 1 or a_00_14_quantile != 0.5):
        df['demand_a_00_14'] = df['a_00_14'] \
            .apply(lambda x: a_00_14_weight * 1 if (x > df['a_00_14'].quantile(a_00_14_quantile)) else 0)
    # + 45 < Age < 64
    if (a_45_64_weight != 1 or a_45_64_quantile != 0.5):
        df['demand_a_45_64'] = df['a_45_64'] \
            .apply(lambda x: a_45_64_weight * 1 if (x > df['a_45_64'].quantile(a_45_64_quantile)) else 0)
    # Households with children
    if (households_with_children_weight != 1 or households_with_children_quantile != 0.5):
        df['demand_households_with_children'] = df['households_with_children'] \
            .apply(lambda x: households_with_children_weight * 1 if (
                x > df['households_with_children'].quantile(households_with_children_quantile)) else 0)
    # cars per household
    if (cars_weight != 1 or cars_quantile != 0.5):
        df['demand_cars'] = df['cars_per_household'] \
            .apply(lambda x: cars_weight * 1 if (x > df['cars_per_household'].quantile(cars_quantile)) else 0)
    # births
    if (births_weight != 1 or births_quantile != 0.5):
        df['demand_births'] = df['births'] \
            .apply(lambda x: births_weight * 1 if (x > df['births'].quantile(births_quantile)) else 0)
    # rental homes
    if (rental_weight != 1 or rental_quantile != 0.5):
        df['demand_rental'] = df['rental_perc'] \
            .apply(lambda x: rental_weight * 1 if (x > df['rental_perc'].quantile(rental_quantile)) else 0)
    # %female
    if (females_weight != 1 or females_quantile != 0.5):
        df['demand_females'] = df['females'] \
            .apply(lambda x: females_weight * 1 if (x > df['females'].quantile(females_quantile)) else 0)
    # %singles
    if (singles_weight != 1 or singles_quantile != 0.5):
        df['demand_singles'] = df['not_married'] \
            .apply(lambda x: singles_weight * 1 if (x > df['not_married'].quantile(singles_quantile)) else 0)
    # + education level
    if (low_edu_weight != 1 or low_edu_quantile != 0.5):
        df['demand_low_edu'] = df['low_edu'] \
            .apply(lambda x: low_edu_weight * 1 if (x > df['low_edu'].quantile(low_edu_quantile)) else 0)
    if (high_edu_weight != 1 or high_edu_quantile != 0.5):
        df['demand_high_edu'] = df['high_edu'] \
            .apply(lambda x: high_edu_weight * 1 if (x > df['high_edu'].quantile(high_edu_quantile)) else 0)
    # + %unemployed
    if (working_weight != 1 or working_quantile != 0.5):
        df['demand_percentage_working'] = df['percentage_working'] \
            .apply(lambda x: working_weight * 1 if (x > df['percentage_working'].quantile(working_quantile)) else 0)
    # + town size
    if (citizens_weight != 1 or citizens_quantile != 0.5):
        df['demand_citizens'] = df['citizens'] \
            .apply(lambda x: citizens_weight * 1 if (x > df['citizens'].quantile(citizens_quantile)) else 0)

    # Calculating demands
    if (radio_input == "Playgrounds"):
        # Calculating demand
        df['play_demand'] = df['demand_a_00_14'] \
                            + df['demand_households_with_children'] \
                            + df['demand_cars'] \
                            + df['demand_births'] \
                            + df['demand_rental']
        df['play_demand'] = MinMaxScaler().fit_transform(np.array(df['play_demand']).reshape(-1, 1))
        df['play_demand'] = df['play_demand'].apply(lambda x: round(x, 3))

        # Adding distance calculations
        for index, row in df.iterrows():
            if (row['play_distance'] <= input_distance):
                df.loc[index, 'play_demand'] = 0.0

                # Filtering Demand threshold
        df = df[df['play_demand'] >= slider_threshold]

        # Map config: Steven's psychophysical law
        hover_data = ["play_demand", "play_distance"]
        size = df['play_demand'].apply(lambda x: x ** (1 / 0.7))


    elif (radio_input == "Parks & Nature"):
        # Calculating demand
        df['park_demand'] = df['demand_households_with_children'] \
                            - df['demand_low_edu'] \
                            + df['demand_high_edu'] \
                            + df['demand_a_00_14'] \
                            - df['demand_a_45_64'] \
                            + df['demand_females'] \
                            + df['demand_singles']
        df['park_demand'] = MinMaxScaler().fit_transform(np.array(df['park_demand']).reshape(-1, 1))
        df['park_demand'] = df['park_demand'].apply(lambda x: round(x, 3))

        # Adding distance calculations
        for index, row in df.iterrows():
            if (row['park_distance'] <= input_distance):
                df.loc[index, 'park_demand'] = 0.0

        # Filtering Demand threshold
        df = df[df['park_demand'] > slider_threshold]

        # Map config
        hover_data = ["park_demand", "park_demand"]
        size = df['park_demand'].apply(lambda x: x ** (1 / 0.7))

    if (radio_input == "Sports Facilities"):
        # Calculating demand
        df['sport_demand'] = df['demand_a_00_14'] \
                             - df['demand_a_45_64'] \
                             - df['demand_females'] \
                             + df['demand_singles'] \
                             - df['demand_households_with_children'] \
                             - df['demand_low_edu'] \
                             + df['demand_high_edu'] \
                             - df['demand_percentage_working'] \
                             + df['demand_citizens']
        df['sport_demand'] = MinMaxScaler().fit_transform(np.array(df['sport_demand']).reshape(-1, 1))
        df['sport_demand'] = df['sport_demand'].apply(lambda x: round(x, 3))

        # Adding distance calculations
        for index, row in df.iterrows():
            if (row['sport_distance'] <= input_distance):
                df.loc[index, 'sport_demand'] = 0.0

        # Filtering Demand threshold
        df = df[df['sport_demand'] > slider_threshold]

        # Map config
        hover_data = ["sport_demand", "sport_demand"]
        size = df['sport_demand'].apply(lambda x: x ** (1 / 0.7))

    # Map
    hover_name = 'neighbourhood'
    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", mapbox_style="open-street-map", height=900,
                            opacity=0.9, color_continuous_scale=plotly.colors.sequential.Purp,
                            color=size, size=size, zoom=zoom, hover_name=hover_name, hover_data=hover_data)
    fig.update_layout(clickmode='event+select')

    return fig, table_out


# Click on map
@app.callback(
    Output('dropdown_province', 'value'),
    Input('map', 'clickData'))
def display_click_data(clickData):
    neighbourhood_df = df[['neighbourhood', 'municipality']]
    if clickData != None:
        neighbourhood = dict(clickData['points'][0])['hovertext']
        municipality = list(neighbourhood_df[neighbourhood_df['neighbourhood'] == neighbourhood]['municipality'])[0]
    else:
        municipality = 'Netherlands'
    return municipality


# Download button
@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("button_download", "n_clicks"),
    State('tbl', 'data'),
    State('tbl', 'columns'),
    State('dropdown_province', 'value'),
    prevent_initial_call=True,
)
def download(n_clicks, rows, columns, name):
    to_download = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    return dcc.send_data_frame(to_download.to_excel, "Regio: " + name + " blindspots.xlsx", sheet_name="Blindspots")


### Page 2 ###

page_2_layout = html.Div([
    html.H1('Neighbourhood demographics'),
    html.Div([
        html.B('Neighbourhood', style={'font-size': '18px'}),
        dcc.Dropdown(neighbourhoods, value='Kanaleneiland', id='dropdown_province'),
        dcc.Graph(id='chart_age'),
        dcc.Graph(id='chart_education'),
    ], className='row'),

    html.Div([
        html.Br(),
        dcc.Link('Go to the Blind Spot Map', href='/map'),
        html.Br(),
        dcc.Link('Go back to the homepage', href='/')
    ], className='row'),
])


@app.callback(Output('chart_age', 'figure'),
              Output('chart_education', 'figure'),
              Input('dropdown_province', 'value'),
              )
def make_charts(neighbourhood):
    ### Age ###
    aggregations = {
        'citizens': 'sum',
        'a_00_14': 'sum',
        'a_15_24': 'sum',
        'a_25_44': 'sum',
        'a_45_64': 'sum'
    }

    # Data
    df = with_coordinates.copy()
    # Neighbourhood
    df = df.loc[:, ['neighbourhood', 'municipality', 'citizens', 'a_00_14', 'a_15_24', 'a_25_44', 'a_45_64']]
    # Municipality
    df_municipalities = df.groupby(['municipality'], as_index=False).agg(aggregations)

    # Country
    df_NL = df_municipalities.agg(aggregations)
    columns = df_NL.to_frame().index
    df_NL = pd.DataFrame([list(df_municipalities.agg(aggregations))], columns=columns)
    df_NL.index = ['NL']

    municipality = list(df.loc[df['neighbourhood'] == neighbourhood, 'municipality'])[0]
    df_neighbourhood = df.loc[df['neighbourhood'] == neighbourhood]
    df_neighbourhood = df_neighbourhood.drop(columns=['municipality'])
    df_neighbourhood.set_index('neighbourhood', inplace=True)
    df_municipality = df_municipalities.loc[df_municipalities['municipality'] == municipality]
    df_municipality.set_index('municipality', inplace=True)

    graph_df = pd.concat([df_neighbourhood, df_municipality, df_NL])
    graph_df.loc[:, 'a_65+'] = graph_df.loc[:, 'citizens'] - graph_df.loc[:, 'a_00_14'] - \
                               graph_df.loc[:,'a_15_24'] - graph_df.loc[:,'a_25_44'] - graph_df.loc[:,'a_45_64']
    graph_df = graph_df.T
    graph_df = round(graph_df.div(graph_df.iloc[0]) * 100, 0)
    graph_df = graph_df.drop(['citizens'])

    chart_age = px.line(graph_df, x=graph_df.index, y=[neighbourhood, municipality, 'NL'], title='Age',
                        labels={'index': 'Age band', 'value': 'Percentage(%)', 'variable': 'Location'})

    ### Education ###
    aggregations = {
        'citizens': 'sum',
        'low_edu': 'sum',
        'mid_edu': 'sum',
        'high_edu': 'sum',
    }

    df = with_coordinates.copy()
    # Neighbourhood
    df = df.loc[:, ['neighbourhood', 'municipality', 'citizens', 'low_edu', 'mid_edu', 'high_edu']]
    # Municipality
    df_municipalities = df.groupby(['municipality'], as_index=False).agg(aggregations)

    # Country
    df_NL = df_municipalities.agg(aggregations)
    columns = df_NL.to_frame().index
    df_NL = pd.DataFrame([list(df_municipalities.agg(aggregations))], columns=columns)
    df_NL.index = ['NL']

    # Making the df
    df_neighbourhood = df.loc[df['neighbourhood'] == neighbourhood]
    df_neighbourhood = df_neighbourhood.drop(columns=['municipality'])
    df_neighbourhood.set_index('neighbourhood', inplace=True)
    df_municipality = df_municipalities.loc[df_municipalities['municipality'] == municipality]
    df_municipality.set_index('municipality', inplace=True)

    graph_df = pd.concat([df_neighbourhood, df_municipality, df_NL])
    graph_df.loc[:, 'Others'] = graph_df.loc[:, 'citizens'] - graph_df.loc[:, 'low_edu'] - graph_df.loc[:,
                                                                                           'mid_edu'] - graph_df.loc[:,
                                                                                                        'high_edu']
    graph_df = graph_df.T
    graph_df = round(graph_df.div(graph_df.iloc[0]) * 100, 0)
    graph_df = graph_df.drop(['citizens'])

    chart_education = px.line(graph_df, x=graph_df.index, y=[neighbourhood, municipality, 'NL'],
                              title='Education Level',
                              labels={'index': 'Education level', 'value': 'Percentage(%)', 'variable': 'Location'})

    return chart_age, chart_education


# Update the index
@app.callback(Output('homepage', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/map':
        return page_1_layout
    elif pathname == '/chart':
        return page_2_layout
    else:  # 404 "URL not found"
        return index_page


# Run flask app
if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
