App available at https://blind-spot-map.herokuapp.com/

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
