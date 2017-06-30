from cmcb import league, static_data


API_KEY = static_data.LEAGUE_API_KEY


def test_api_ini():
    league_api = league.AsyncRateLeagueAPI(API_KEY)
    print(league_api)
    assert True
