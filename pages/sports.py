import streamlit as st
from services.sports_service import parse_scoreboard

def load_sports_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">🏆 Sports Telemetry Console</p>', unsafe_allow_html=True)
    
    col_ctrl, col_desc = st.columns([6, 4])
    with col_ctrl:
        search_filter = st.text_input("Filter Matchups / Teams", value="", placeholder="Search by team name...", key="sports_filter_input")
    with col_desc:
        st.markdown("""
            <div style="padding: 5px 10px; font-family:'Share Tech Mono', monospace; font-size:0.75rem; color:#64748B; border-left:2px solid #00D9FF; margin-top: 10px;">
                ACTIVE LINKS: ESPN Scoreboard Core API Feed<br>
                REFRESH RATE: Instant Session Synced
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    
    # Define tabs
    tab_cricket, tab_soccer, tab_nba = st.tabs(["🏏 Cricket", "⚽ Premier League", "🏀 NBA Basketball"])
    
    sports_map = {
        "cricket": (tab_cricket, "cricket", "https://a.espncdn.com/i/teamlogos/cricket/500/scoreboard/6.png"),
        "soccer": (tab_soccer, "soccer", "https://a.espncdn.com/i/teamlogos/soccer/500/scoreboard/360.png"),
        "nba": (tab_nba, "nba", "https://a.espncdn.com/i/teamlogos/nba/500/scoreboard/gs.png")
    }
    
    for key, (tab, sport_key, fallback_img) in sports_map.items():
        with tab:
            with st.spinner(f"Acquiring {key} telemetry..."):
                matches = parse_scoreboard(sport_key)
                
            # Filter
            if search_filter:
                matches = [m for m in matches if search_filter.lower() in m["name"].lower() or search_filter.lower() in m["home_team"]["name"].lower() or search_filter.lower() in m["away_team"]["name"].lower()]
                
            if not matches:
                st.markdown(f'<div style="text-align:center; color:#64748B; font-family:\'Share Tech Mono\', monospace; font-size:0.8rem; padding:30px;">NO ACTIVE OR SIMULATED MATCHES FOR {key.upper()}</div>', unsafe_allow_html=True)
                continue
                
            for m in matches:
                home = m["home_team"]
                away = m["away_team"]
                status = m["status"]
                completed = m.get("completed", False)
                
                # Determine colors based on status and winners
                status_color = "#64748B"
                status_label = "LIVE"
                if completed:
                    status_color = "#10B981"
                    status_label = "FINAL"
                elif "scheduled" in status.lower() or "pm" in status.lower() or "am" in status.lower():
                    status_color = "#7B61FF"
                    status_label = "SCHEDULED"
                else:
                    status_color = "#EF4444"
                    status_label = "LIVE MATCH"
                    
                home_won = home.get("winner", False)
                away_won = away.get("winner", False)
                
                home_color = "#FFFFFF"
                away_color = "#FFFFFF"
                if completed:
                    if home_won:
                        home_color = "#10B981"
                        away_color = "#64748B"
                    elif away_won:
                        away_color = "#10B981"
                        home_color = "#64748B"
                elif status_label == "LIVE MATCH":
                    home_color = "#00D9FF"
                    away_color = "#00D9FF"
                    
                home_logo = home.get("logo") or fallback_img
                away_logo = away.get("logo") or fallback_img
                
                # HTML template card
                card_html = f"""<div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; margin-bottom: 12px; font-family: 'Share Tech Mono', monospace; box-shadow: 0 4px 10px rgba(0,0,0,0.25);">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 8px; margin-bottom: 12px;">
<span style="font-size: 0.7rem; color: #64748B; letter-spacing:1px;">{m['sport']} • {status}</span>
<span style="font-size: 0.65rem; color: {status_color}; border: 1px solid {status_color}; border-radius: 4px; padding: 1px 6px; font-weight: bold; letter-spacing:1px; text-transform: uppercase;">{status_label}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; align-items: center; gap: 12px; width: 38%;">
<img src="{away_logo}" style="width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,0.05); object-fit: contain; padding: 2px;" onerror="this.src='{fallback_img}'">
<span style="font-weight: 600; font-size: 0.85rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: {away_color};">{away['name']}</span>
</div>
<div style="font-size: 1.15rem; font-weight: 700; width: 10%; text-align: right; color: {away_color};">{away['score']}</div>
<div style="font-size: 0.8rem; color: #64748B; width: 4%; text-align: center;">-</div>
<div style="font-size: 1.15rem; font-weight: 700; width: 10%; text-align: left; color: {home_color};">{home['score']}</div>
<div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px; width: 38%; text-align: right;">
<span style="font-weight: 600; font-size: 0.85rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: {home_color};">{home['name']}</span>
<img src="{home_logo}" style="width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,0.05); object-fit: contain; padding: 2px;" onerror="this.src='{fallback_img}'">
</div>
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)
                
    st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="panel-title" style="font-size:0.85rem;">Sports Query Terminal</p>', unsafe_allow_html=True)
        st.markdown("""
            <div style="font-size: 0.75rem; color:#64748B; font-family:'Outfit', sans-serif;">
                You can ask the primary voice or chat interface for sports telemetry. ECHO X will automatically query sports metrics and speak the latest scores.
                <br><i>Try: "What is the score of the India match?" or "Show me NBA scoreboard"</i>
            </div>
        """, unsafe_allow_html=True)
