from country_state_city import Country, State, City

# Get all countries
countries = Country.get_countries()
print(countries)
# # Get a country by code
# usa = Country.get_country_by_code('IN')
# print(f"Country: {usa.name}, Flag: {usa.flag}")



from country_state_city import Country, State, City
# Get all states of a country
selectd_country = "IN"
states = State.get_states_of_country(selectd_country)
for state in states:
    print(f"- {state.name} ({state.iso_code})")


selectd_state = 'UP'
# Get all cities of a state
cities = City.get_cities_of_state(selectd_country, selectd_state)
for city in cities[:5]:
    print(f"- {city.name}")

# # print(f"Number of cities in California: {len(cities)}")
# # # print(cities)