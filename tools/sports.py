from services.sports_service import parse_scoreboard

def sports(command):
    """
    Evaluates sports command text and returns formatted result if matched.
    """
    cmd = command.lower().strip()
    
    # Define sports triggers
    is_sports_query = False
    target_sport = None
    
    # Check sports keywords
    if "cricket" in cmd:
        target_sport = "cricket"
        is_sports_query = True
    elif "nba" in cmd or "basketball" in cmd:
        target_sport = "nba"
        is_sports_query = True
    elif "football" in cmd or "soccer" in cmd or "premier league" in cmd or "epl" in cmd:
        target_sport = "soccer"
        is_sports_query = True
    elif any(kw in cmd for kw in ["score", "scores", "match", "matches", "matchup", "matchups", "game", "games"]):
        is_sports_query = True
        
    if not is_sports_query:
        return None
        
    if target_sport:
        sports_to_query = [target_sport]
    else:
        # Default query all
        sports_to_query = ["cricket", "soccer", "nba"]
        
    results = []
    for sport in sports_to_query:
        matches = parse_scoreboard(sport)
        if matches:
            results.append(f"🏆 {sport.upper()} TELEMETRY:")
            for m in matches[:3]:
                status = m.get("status", "Scheduled")
                home = m.get("home_team", {})
                away = m.get("away_team", {})
                results.append(f"• {home.get('name')} ({home.get('score')}) vs {away.get('name')} ({away.get('score')}) | Status: {status}")
        else:
            results.append(f"🏆 {sport.upper()}: No active telemetry found.")
            
    return "\n".join(results)
