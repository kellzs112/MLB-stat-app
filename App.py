import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MLB Statcast & Betting Assistant", layout="wide")
st.title("⚾ MLB Statcast + Betting Insights")

@st.cache_data
def get_today_pitchers():
    url = "https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date=2025-06-04&hydrate=team,linescore,probablePitcher"
    res = requests.get(url)
    data = res.json()

    games = []
    for date_info in data["dates"]:
        for game in date_info["games"]:
            teams = game["teams"]
            game_info = {
                "Matchup": f"{teams['away']['team']['name']} @ {teams['home']['team']['name']}",
                "Home Starter": teams['home'].get("probablePitcher", {}).get("fullName", "TBD"),
                "Away Starter": teams['away'].get("probablePitcher", {}).get("fullName", "TBD"),
            }
            games.append(game_info)
    return pd.DataFrame(games)

st.subheader("📅 Today's Matchups")
df_pitchers = get_today_pitchers()
st.dataframe(df_pitchers, use_container_width=True)

st.subheader("🔍 Key Hitter Stats (Barrel %, ISO, LA)")
data = [
    {"Player": "Shohei Ohtani", "Barrel%": 16.4, "ISO": 0.295, "Launch Angle": 18.5},
    {"Player": "Aaron Judge", "Barrel%": 21.1, "ISO": 0.320, "Launch Angle": 17.2},
    {"Player": "Juan Soto", "Barrel%": 15.7, "ISO": 0.270, "Launch Angle": 13.3},
    {"Player": "Mookie Betts", "Barrel%": 12.4, "ISO": 0.250, "Launch Angle": 16.0}
]
df_hitters = pd.DataFrame(data)
st.dataframe(df_hitters, use_container_width=True)

st.subheader("💸 Betting Props (Placeholder)")
props = [
    {"Player": "Shohei Ohtani", "HR Prop": "+300", "Total Bases": "Over 1.5 (-110)"},
    {"Player": "Aaron Judge", "HR Prop": "+270", "Total Bases": "Over 1.5 (-105)"},
    {"Player": "Juan Soto", "HR Prop": "+330", "Total Bases": "Over 1.5 (+100)"}
]
df_props = pd.DataFrame(props)
st.dataframe(df_props, use_container_width=True)

st.subheader("🧠 AI Bet Picks (Beta)")
top_pick = df_hitters.loc[df_hitters["Barrel%"].idxmax()]
player_name = top_pick['Player']
barrel = top_pick['Barrel%']
iso = top_pick['ISO']
hr_prop = df_props.loc[df_props['Player'] == player_name, 'HR Prop'].values[0]

st.markdown(
    f"""
**Top Power Hitter:** `{player_name}`  
**Barrel %:** `{barrel}` | **ISO:** `{iso}`  
**Suggested HR Prop:** `{hr_prop}`
"""
)
# ==============================
# 📊 Live Player Stat Search
# ==============================

st.subheader("📊 Real-Time Player Stats (2024 Season)")

def search_player_id(name):
    try:
        query = name.replace(" ", "%20")
        url = f"https://search-api.mlb.com/svc/search/v2/mlb_global/search?query={query}"
        res = requests.get(url)
        results = res.json()
        for item in results.get('docs', []):
            if 'player_id' in item:
                return item['player_id']
    except Exception as e:
        st.error(f"Error finding player: {e}")
    return None

def get_player_stats(player_id):
    try:
        url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season=2024"
        res = requests.get(url)
        data = res.json()
        if data['stats'] and data['stats'][0]['splits']:
            return data['stats'][0]['splits'][0]['stat']
        else:
            return {"message": "No stats found."}
    except Exception as e:
        return {"error": str(e)}

# Streamlit Input
player_name = st.text_input("Enter full player name (e.g. Aaron Judge)")

if player_name:
    with st.spinner("Searching..."):
        player_id = search_player_id(player_name)
    if player_id:
        with st.spinner("Fetching player stats..."):
            stats = get_player_stats(player_id)
        st.success(f"Stats for {player_name}")
        st.json(stats)
    else:
        st.error("Player not found or unavailable.")
