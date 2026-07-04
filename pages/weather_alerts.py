import streamlit as st
from services.weather_service import get_weather

def load_weather_alerts_page():
    st.markdown('<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; letter-spacing:2px; text-transform:uppercase;">🌤 Meteorological Alert Console</p>', unsafe_allow_html=True)
    
    if "weather_data" not in st.session_state:
        st.session_state.weather_data = None
        
    col_input, col_display = st.columns([4, 6])
    
    with col_input:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Location Search</p>', unsafe_allow_html=True)
            
            city_input = st.text_input("Enter City Name", value="", placeholder="e.g. Delhi, London, Paris, New York...", key="weather_city_search")
            if st.button("🔍 Query Weather Telemetry", use_container_width=True, key="search_weather_btn"):
                if city_input:
                    with st.spinner("Checking meteorology sensors..."):
                        data = get_weather(city_input)
                        if data:
                            st.session_state.weather_data = data
                            st.toast("✅ Meteorological telemetry updated")
                        else:
                            st.error("❌ City not found by global GPS coordinates.")
                else:
                    st.toast("⚠️ Please enter a city name first")
            
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="panel-title" style="font-size:0.8rem;">Preset Regions</p>', unsafe_allow_html=True)
            
            preset_cities = ["Delhi", "New York", "London", "Tokyo", "Sydney"]
            for city in preset_cities:
                if st.button(f"📍 {city}", use_container_width=True, key=f"weather_preset_{city.lower().replace(' ', '')}"):
                    with st.spinner(f"Querying {city} coordinates..."):
                        data = get_weather(city)
                        if data:
                            st.session_state.weather_data = data
                            st.toast("✅ Telemetry updated")
                            st.rerun()

    with col_display:
        with st.container(border=True, height=350):
            st.markdown('<p class="panel-title">Meteorological Output Console</p>', unsafe_allow_html=True)
            
            w_data = st.session_state.weather_data
            
            if w_data:
                # Select icon based on temperature
                temp = w_data["temperature"]
                if temp >= 35:
                    icon = "🔥"
                    status = "HIGH TEMPERATURE EXTREME"
                    status_color = "#EF4444"
                    suggestion = "⚠️ Core cooler override is recommended. Active external cooling processes initiated."
                elif temp >= 25:
                    icon = "☀️"
                    status = "OPTIMAL SUNNY CONDITIONS"
                    status_color = "#F59E0B"
                    suggestion = "🌤️ Standard atmospheric pressure. Optimal environment parameters active."
                elif temp >= 15:
                    icon = "🌤️"
                    status = "MODERATE ATMOSPHERIC STATE"
                    status_color = "#10B981"
                    suggestion = "🍃 Stable temperature profiles detected. Standard threat shield config applies."
                elif temp >= 5:
                    icon = "🌥️"
                    status = "COOL SECTOR PROFILE"
                    status_color = "#3B82F6"
                    suggestion = "❄️ Condensation likely. Ensure moisture barrier sealing on outer hardware."
                else:
                    icon = "❄️"
                    status = "SUB-ZERO FREEZING STATE"
                    status_color = "#00D9FF"
                    suggestion = "❄️ Warning: Cold threshold breached. Hardware heaters engaged to protect neural core."
                
                # HTML block for modern weather visualization
                weather_card_html = f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(0, 217, 255, 0.02); border:1px solid rgba(0, 217, 255, 0.08); border-radius:12px; padding:20px; font-family:'Share Tech Mono', monospace; width:100%; box-sizing:border-box;">
                        <div>
                            <span style="font-size:1.1rem; font-weight:600; color:#FFFFFF;">{w_data['city']}</span><br>
                            <span style="font-size:0.65rem; color:{status_color}; font-weight:700; letter-spacing:1px;">{status}</span>
                            <div style="font-size:2.8rem; font-weight:700; color:#00D9FF; margin-top:10px;">{temp}°C</div>
                        </div>
                        <div style="font-size:4.5rem; filter:drop-shadow(0 0 10px rgba(0, 217, 255, 0.25));">{icon}</div>
                    </div>
                """
                st.markdown(weather_card_html, unsafe_allow_html=True)
                
                st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); border-radius:8px; padding:8px 12px; text-align:center; font-family:'Share Tech Mono', monospace;">
                            <span style="font-size:0.65rem; color:#64748B;">💧 HUMIDITY</span><br>
                            <span style="font-size:1.1rem; font-weight:600; color:#10B981;">{w_data['humidity']}%</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); border-radius:8px; padding:8px 12px; text-align:center; font-family:'Share Tech Mono', monospace;">
                            <span style="font-size:0.65rem; color:#64748B;">🌬️ WIND SPEED</span><br>
                            <span style="font-size:1.1rem; font-weight:600; color:#EC4899;">{w_data['wind']} km/h</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.01); border-left:3px solid #00D9FF; padding:8px 12px; border-radius:4px; font-size:0.75rem; color:#64748B; margin-top:10px; font-family:'Outfit', sans-serif;">
                        {suggestion}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="display:flex; justify-content:center; align-items:center; height:240px; color:#64748B; font-size:0.85rem;">NO ACTIVE METEOROLOGICAL TELEMETRY SOURCE</div>', unsafe_allow_html=True)
