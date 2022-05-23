import pandas as pd
import numpy as np

# df = pd.read_excel("https://raw.githubusercontent.com/laurens-kolenbrander/DEiA-2/blob/73ac2e4abc9fda81321891ed8de4da258670c27c/2019_cbs_data.xls?token=GHSAT0AAAAAABUAYSV2GPBNRDKI4XE6TY2UYTPOCYA")
df = pd.read_excel("2019_cbs_data.xls")

regio_type = ['Land', 'Gemeente', 'Wijk']
df = df[~df.recs.isin(regio_type)]
df.head()

# If the files are already downloaded, set from_scratch = False
from_scratch = True


def minimal_distance(distances=pd.read_csv("neighbourhood_distances.csv")):
    ''' Calculate minimum distance for each facility type in each neighbourhood
    '''
    minimals = pd.DataFrame([], columns=['neighbourhood', 'sport_distance', 'play_distance', 'park_distance'])
    short = distances[['neighbourhood', 'distance', 'category']]

    sport = short[short['category'] == 'sport']
    park = short[short['category'] == 'park']
    playground = short[short['category'] == 'playground']
    neighbourhoods = short['neighbourhood']
    filt = neighbourhoods.drop_duplicates()

    for i in filt:
        single = sport[sport['neighbourhood'] == i]
        single = single.sort_values(by=['distance'])
        sportmin = single.iloc[0]['distance']

        psingle = park[park['neighbourhood'] == i]
        psingle = psingle.sort_values(by=['distance'])
        parkmin = psingle.iloc[0]['distance']

        plsingle = playground[playground['neighbourhood'] == i]
        plsingle = plsingle.sort_values(by=['distance'])
        playmin = plsingle.iloc[0]['distance']

        minimals = pd.concat([minimals, pd.DataFrame([[i, sportmin, playmin, parkmin]],
                                                     columns=['neighbourhood', 'sport_distance', 'play_distance',
                                                              'park_distance'])])

    return minimals


if from_scratch:
    # Import of neighbourhood distances
    distances = pd.read_csv("neighbourhood_distances.csv")

    minimals = minimal_distance()
    # Save to csv
    minimals.to_csv('minimaldistances_concat.csv')

else:
    # Importing minimal distance
    minimals = pd.read_csv('minimaldistances_concat.csv')
    minimals = minimals.drop(columns='Unnamed: 0')
# Translation of column names of the dataset

df_filtered = df[['regio',  # neighbourhood
                  'gm_naam',  # municipality, only for simple reading afterwards
                  'a_inw',  # inhabitants
                  'a_vrouw',  # women amount
                  'a_00_14',  # 0-15
                  'a_15_24',  # 15-24
                  'a_25_44',  # 25-44
                  'a_45_64',  # 45-64
                  'a_geb',  # births
                  'a_hh_m_k',  # households with children
                  'a_ongeh',  # unmarried
                  'p_huurw',  # perc. rental
                  'p_arb_pp',  # perc. nett working participaton
                  'a_opl_lg',  # amount low education
                  'a_opl_md',  # amount mid edu
                  'a_opl_hg',  # amount high edu
                  'g_hh_sti',  # average standardized income
                  'g_pau_hh',  # cars per hh
                  'pst_mvp'  # most occuring postal
                  ]]

df_renamed = df_filtered.rename(columns={'regio': 'neighbourhood',
                                         'gm_naam': 'municipality',
                                         'a_inw': 'citizens',
                                         'a_vrouw': 'females',
                                         'a_ongeh': 'not_married',
                                         'p_huurw': 'rental_perc',
                                         'p_arb_pp': 'percentage_working',
                                         'a_opl_lg': 'low_edu',
                                         'a_opl_md': 'mid_edu',
                                         'a_opl_hg': 'high_edu',
                                         'a_geb': 'births',
                                         'g_hh_sti': 'avg_income',
                                         'a_hh_m_k': 'households_with_children',
                                         'g_pau_hh': 'cars_per_household',
                                         'pst_mvp': 'postal_code_center'
                                         })

df_renamed.head()


def percentage_missing(df=df_renamed, missing_value='.', percentage=True):
    ''' Counts missing values as specified in missing_value.
    Optionally percentage can be set to False for the count of values
    '''
    total = df.shape[0]
    for column in df.columns:
        count = df[df[column] == missing_value].shape[0]
        if count != 0:
            if percentage:
                print(f'{column}: {round(count / total * 100)}%')
            else:
                print(f'{column}: {count}')


for column in df_renamed.columns:
    if (not column in ('neighbourhood', 'municipality')):
        df_renamed[column] = df_renamed[column].replace('.', 0).apply(str).str.replace(',', '.').astype(float)
from sklearn.preprocessing import MinMaxScaler


def demand(df_renamed=df_renamed,
           citizens_weight=1, females_weight=1, a_00_14_weight=1, a_45_64_weight=1, births_weight=1,
           households_with_children_weight=1,
           singles_weight=1, rental_weight=1, working_weight=1, low_edu_weight=1, high_edu_weight=1, cars_weight=1,

           citizens_quantile=0.5, females_quantile=0.5, a_00_14_quantile=0.5, a_45_64_quantile=0.5, births_quantile=0.5,
           households_with_children_quantile=0.5,
           singles_quantile=0.5, rental_quantile=0.5, working_quantile=0.5, low_edu_quantile=0.5, high_edu_quantile=0.5,
           cars_quantile=0.5):
    ''' When a variable is not to be considered the weight should be set to zero
    For higher weight, >1  and lower 0 < weight < 1

    Quantiles set the demand for each variable. When higher, only higher values will be taken into account for demand calculation (and vice versa).
    '''
    df = df_renamed.copy()
    # Children under 15
    df['demand_a_00_14'] = df['a_00_14'] \
        .apply(lambda x: a_00_14_weight * 1 if (x > df['a_00_14'].quantile(a_00_14_quantile)) else 0)
    # + 45 < Age < 64
    df['demand_a_45_64'] = df['a_45_64'] \
        .apply(lambda x: a_45_64_weight * 1 if (x > df['a_45_64'].quantile(a_45_64_quantile)) else 0)
    # Households with children
    df['demand_households_with_children'] = df['households_with_children'] \
        .apply(lambda x: households_with_children_weight * 1 if (
                x > df['households_with_children'].quantile(households_with_children_quantile)) else 0)
    # cars per household
    df['demand_cars'] = df['cars_per_household'] \
        .apply(lambda x: cars_weight * 1 if (x > df['cars_per_household'].quantile(cars_quantile)) else 0)
    # births
    df['demand_births'] = df['births'] \
        .apply(lambda x: births_weight * 1 if (x > df['births'].quantile(births_quantile)) else 0)
    # rental homes
    df['demand_rental'] = df['rental_perc'] \
        .apply(lambda x: rental_weight * 1 if (x > df['rental_perc'].quantile(rental_quantile)) else 0)
    # %female
    df['demand_females'] = df['females'] \
        .apply(lambda x: females_weight * 1 if (x > df['females'].quantile(females_quantile)) else 0)
    # %singles
    df['demand_singles'] = df['not_married'] \
        .apply(lambda x: singles_weight * 1 if (x > df['not_married'].quantile(singles_quantile)) else 0)
    # education level
    df['demand_low_edu'] = df['low_edu'] \
        .apply(lambda x: low_edu_weight * 1 if (x > df['low_edu'].quantile(low_edu_quantile)) else 0)
    df['demand_high_edu'] = df['high_edu'] \
        .apply(lambda x: high_edu_weight * 1 if (x > df['high_edu'].quantile(high_edu_quantile)) else 0)
    # %unemployed
    df['demand_percentage_working'] = df['percentage_working'] \
        .apply(lambda x: working_weight * 1 if (x > df['percentage_working'].quantile(working_quantile)) else 0)
    # town size
    df['demand_citizens'] = df['citizens'] \
        .apply(lambda x: citizens_weight * 1 if (x > df['citizens'].quantile(citizens_quantile)) else 0)
    return df


if from_scratch:
    df_demand = demand(df_renamed)



def demand_play(df):
    ''' When a variable is not to be considered the weight should be set to zero
    For higher weight, >1  and lower <1
    '''
    df['play_demand'] = df['demand_a_00_14'] \
                        + df['demand_households_with_children'] \
                        + df['demand_cars'] \
                        + df['demand_births'] \
                        + df['demand_rental']
    df['play_demand'] = MinMaxScaler().fit_transform(np.array(df['play_demand']).reshape(-1, 1))
    df['play_demand'] = df['play_demand'].apply(lambda x: round(x, 3))

    return df


if from_scratch:
    df_demand = demand_play(df_demand)


def demand_sport(df):
    ''' When a variable is not to be considered the weight should be set to zero
    For higher weight, >1  and lower <1
    '''
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

    return df


if from_scratch:
    df_demand = demand_sport(df_demand)


def demand_park(df):
    # calculated sum of demand
    df['park_demand'] = df['demand_households_with_children'] \
                        - df['demand_low_edu'] \
                        + df['demand_high_edu'] \
                        + df['demand_a_00_14'] \
                        - df['demand_a_45_64'] \
                        + df['demand_females'] \
                        + df['demand_singles']
    df['park_demand'] = MinMaxScaler().fit_transform(np.array(df['park_demand']).reshape(-1, 1))
    df['park_demand'] = df['park_demand'].apply(lambda x: round(x, 3))
    return df


if from_scratch:
    df_demand = demand_park(df_demand)


def Demand_with_distance(df_demand, minimals=minimals, play_distance_min=0.4, park_distance_min=1,
                         sport_distance_min=1):
    df = df_demand.merge(minimals, left_on='neighbourhood', right_on='neighbourhood')

    for index, row in df.iterrows():
        if (row['play_distance'] <= play_distance_min):
            df.loc[index, 'play_demand'] = 0.0

        if (row['park_distance'] <= park_distance_min):
            df.loc[index, 'park_demand'] = 0.0

        if (row['sport_distance'] <= sport_distance_min):
            df.loc[index, 'sport_demand'] = 0.0

    return df


if from_scratch:
    df_demand = Demand_with_distance(df_demand, minimals)
if from_scratch:
    # Importing coordinates
    post_coordinate_map = pd.read_csv('postcode_coordinate.csv')
    post_coordinate_map = post_coordinate_map[['postcode', 'provincie', 'latitude', 'longitude']]

    # This drops 74 rows
    cbs_data_prepped = df_demand[df_demand['postal_code_center'] != '.']
    cbs_data_prepped['postal_code_center'] = cbs_data_prepped['postal_code_center'].astype(int)

    with_coordinates = pd.merge(cbs_data_prepped, post_coordinate_map, how='left', left_on=['postal_code_center'],
                                right_on=['postcode'])
    with_coordinates.drop(columns=['postcode'], inplace=True)

    # Save to csv
    with_coordinates.to_csv('with_coordinates.csv')

else:
    # Importing minimal distance
    with_coordinates = pd.read_csv('with_coordinates.csv')
    with_coordinates = with_coordinates.drop(columns='Unnamed: 0')


# with_coordinates.head()
def Demand_threshold(with_coordinates=with_coordinates, play_demand_threshold=0.7, park_demand_threshold=0.7,
                     sport_demand_threshold=0.6):
    # Playground
    play_output_list = with_coordinates[
        ['neighbourhood', 'municipality', 'a_00_14', 'births', 'rental_perc', 'play_demand', 'latitude', 'longitude',
         'play_distance']]
    # Filter by play_demand_threshold
    play_output_list = play_output_list[play_output_list['play_demand'] > play_demand_threshold]
    play_output_list = play_output_list.sort_values(by=['play_demand'], ascending=False)
    # Save
    play_output_list.to_csv('play_output_list.csv', index=False)

    # Park
    park_output_list = with_coordinates[
        ['neighbourhood', 'municipality', 'households_with_children', 'high_edu', 'a_00_14', 'a_45_64', 'females',
         'not_married', 'park_demand', 'latitude', 'longitude', 'park_distance']]
    park_output_list = park_output_list[park_output_list['park_demand'] > park_demand_threshold]
    park_output_list = park_output_list.sort_values(by=['park_demand'], ascending=False)
    park_output_list.to_csv('park_output_list.csv', index=False)

    # Sport
    sport_output_list = with_coordinates[
        ['neighbourhood', 'municipality', 'a_00_14', 'a_15_24', 'a_25_44', 'a_45_64', 'sport_demand', 'latitude',
         'longitude', 'sport_distance']]
    sport_output_list = sport_output_list[sport_output_list['sport_demand'] > sport_demand_threshold]
    sport_output_list = sport_output_list.sort_values(by=['sport_demand'], ascending=False)
    sport_output_list.to_csv('sport_output_list.csv', index=False)

    return play_output_list, park_output_list, sport_output_list


if from_scratch:
    play_output_list, park_output_list, sport_output_list = Demand_threshold(with_coordinates,
                                                                             play_demand_threshold=0.7,
                                                                             park_demand_threshold=0.7,
                                                                             sport_demand_threshold=0.6)

else:
    # Importing minimal distance
    play_output_list = pd.read_csv('play_output_list.csv')
    park_output_list = pd.read_csv('park_output_list.csv')
    sport_output_list = pd.read_csv('sport_output_list.csv')