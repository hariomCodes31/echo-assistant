import streamlit as st
import math

# ── Unit conversion tables ────────────────────────────────────────────────────
CONVERSIONS = {
    "Temperature": {
        "units": ["Celsius", "Fahrenheit", "Kelvin"],
        "convert": lambda val, frm, to: (
            val if frm == to else
            (val * 9 / 5 + 32) if frm == "Celsius" and to == "Fahrenheit" else
            (val + 273.15) if frm == "Celsius" and to == "Kelvin" else
            ((val - 32) * 5 / 9) if frm == "Fahrenheit" and to == "Celsius" else
            ((val - 32) * 5 / 9 + 273.15) if frm == "Fahrenheit" and to == "Kelvin" else
            (val - 273.15) if frm == "Kelvin" and to == "Celsius" else
            ((val - 273.15) * 9 / 5 + 32)
        ),
    },
    "Length": {
        "units": ["Meters", "Kilometers", "Miles", "Feet", "Inches", "Centimeters"],
        "factors": {"Meters": 1, "Kilometers": 1000, "Miles": 1609.34,
                    "Feet": 0.3048, "Inches": 0.0254, "Centimeters": 0.01},
    },
    "Weight": {
        "units": ["Kilograms", "Grams", "Pounds", "Ounces", "Tonnes"],
        "factors": {"Kilograms": 1, "Grams": 0.001, "Pounds": 0.453592,
                    "Ounces": 0.0283495, "Tonnes": 1000},
    },
    "Data": {
        "units": ["Bytes", "Kilobytes", "Megabytes", "Gigabytes", "Terabytes"],
        "factors": {"Bytes": 1, "Kilobytes": 1024, "Megabytes": 1024 ** 2,
                    "Gigabytes": 1024 ** 3, "Terabytes": 1024 ** 4},
    },
    "Speed": {
        "units": ["m/s", "km/h", "mph", "knots"],
        "factors": {"m/s": 1, "km/h": 1 / 3.6, "mph": 0.44704, "knots": 0.514444},
    },
    "Area": {
        "units": ["Square Meters", "Square Kilometers", "Square Feet", "Acres", "Hectares"],
        "factors": {"Square Meters": 1, "Square Kilometers": 1e6,
                    "Square Feet": 0.092903, "Acres": 4046.86, "Hectares": 10000},
    },
}


def _factor_convert(val, frm, to, factors):
    return val * factors[frm] / factors[to]


def _safe_eval(expr: str):
    """Evaluate a simple arithmetic expression safely."""
    allowed = set("0123456789+-*/()., %eE")
    clean = expr.replace(" ", "").replace("^", "**")
    if not all(c in allowed or c == "*" for c in clean):
        return None, "Invalid characters in expression"
    try:
        result = eval(clean, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi, "e": math.e})
        return result, None
    except ZeroDivisionError:
        return None, "Division by zero"
    except Exception as ex:
        return None, str(ex)


def load_calculator_page():
    st.markdown(
        '<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; '
        'letter-spacing:2px; text-transform:uppercase;">🔢 Calculator & Unit Converter</p>',
        unsafe_allow_html=True,
    )

    col_calc, col_conv = st.columns([5, 5])

    # ── LEFT: Calculator ─────────────────────────────────────────────────────
    with col_calc:
        with st.container(border=True):
            st.markdown('<p class="panel-title">🧮 Expression Calculator</p>', unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.7rem; color:#64748B; margin-bottom:10px;">'
                "Supports: <code style='color:#00D9FF;'>+ - * / () % ** sqrt pi e</code></div>",
                unsafe_allow_html=True,
            )

            expr = st.text_input(
                "Expression",
                placeholder="e.g. (25 * 4) / 2 + sqrt(144)",
                key="calc_expr_input",
                label_visibility="collapsed",
            )

            if st.button("⚡ Calculate", use_container_width=True, key="calc_btn"):
                if expr.strip():
                    result, err = _safe_eval(expr.strip())
                    if err:
                        st.session_state.calc_result = f"❌ Error: {err}"
                        st.session_state.calc_history_entry = None
                    else:
                        formatted = f"{result:.10g}"
                        st.session_state.calc_result = formatted
                        if "calc_history" not in st.session_state:
                            st.session_state.calc_history = []
                        st.session_state.calc_history.insert(0, f"{expr.strip()} = {formatted}")
                        st.session_state.calc_history = st.session_state.calc_history[:10]
                else:
                    st.toast("⚠️ Enter an expression first.")

            # Result display
            result_val = st.session_state.get("calc_result", "")
            is_error = str(result_val).startswith("❌")
            color = "#EF4444" if is_error else "#00D9FF"
            if result_val:
                st.markdown(
                    f"""
                    <div style="background:rgba(0,217,255,0.04); border:1px solid rgba(0,217,255,0.15);
                                border-radius:8px; padding:16px; margin-top:10px; text-align:center;">
                        <div style="font-size:0.65rem; color:#64748B; font-family:'Share Tech Mono',monospace;
                                    margin-bottom:4px;">RESULT</div>
                        <div style="font-size:1.8rem; font-weight:700; color:{color};
                                    font-family:'Share Tech Mono',monospace; letter-spacing:1px;
                                    text-shadow:0 0 10px {color}55;">{result_val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # History
            history = st.session_state.get("calc_history", [])
            if history:
                st.markdown(
                    '<div style="font-size:0.7rem; color:#64748B; font-family:\'Share Tech Mono\',monospace;'
                    'margin-top:14px; margin-bottom:6px; text-transform:uppercase; letter-spacing:1px;">History</div>',
                    unsafe_allow_html=True,
                )
                for h in history:
                    st.markdown(
                        f'<div style="font-size:0.72rem; font-family:\'Share Tech Mono\',monospace;'
                        f'color:#94A3B8; border-bottom:1px solid rgba(255,255,255,0.04); padding:3px 0;">{h}</div>',
                        unsafe_allow_html=True,
                    )
                if st.button("🗑️ Clear History", key="clear_calc_hist", use_container_width=True):
                    st.session_state.calc_history = []
                    st.session_state.calc_result = ""
                    st.rerun()

    # ── RIGHT: Unit Converter ─────────────────────────────────────────────────
    with col_conv:
        with st.container(border=True):
            st.markdown('<p class="panel-title">🔄 Unit Converter</p>', unsafe_allow_html=True)

            category = st.selectbox(
                "Category",
                list(CONVERSIONS.keys()),
                key="conv_category",
            )
            config = CONVERSIONS[category]
            units = config["units"]

            val_col, from_col, to_col = st.columns([3, 3, 3])
            with val_col:
                input_val = st.number_input(
                    "Value", value=1.0, format="%.6g", key="conv_value", label_visibility="visible"
                )
            with from_col:
                from_unit = st.selectbox("From", units, key="conv_from")
            with to_col:
                to_unit = st.selectbox("To", units, index=1 if len(units) > 1 else 0, key="conv_to")

            # Perform conversion
            try:
                if "convert" in config:
                    converted = config["convert"](input_val, from_unit, to_unit)
                else:
                    converted = _factor_convert(input_val, from_unit, to_unit, config["factors"])
                conv_str = f"{converted:.8g}"
                conv_color = "#10B981"
                conv_err = ""
            except Exception as ex:
                conv_str = "Error"
                conv_color = "#EF4444"
                conv_err = str(ex)

            st.markdown(
                f"""
                <div style="background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2);
                            border-radius:8px; padding:16px; margin-top:10px; text-align:center;">
                    <div style="font-size:0.65rem; color:#64748B; font-family:'Share Tech Mono',monospace;
                                margin-bottom:4px;">{input_val} {from_unit} =</div>
                    <div style="font-size:1.8rem; font-weight:700; color:{conv_color};
                                font-family:'Share Tech Mono',monospace; letter-spacing:1px;
                                text-shadow:0 0 10px {conv_color}55;">{conv_str}</div>
                    <div style="font-size:0.75rem; color:#64748B; margin-top:4px;">{to_unit}</div>
                    {'<div style="font-size:0.65rem; color:#EF4444; margin-top:4px;">' + conv_err + '</div>' if conv_err else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick reference table
            st.markdown(
                '<div style="font-size:0.7rem; color:#64748B; font-family:\'Share Tech Mono\',monospace;'
                'margin-top:16px; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;">'
                f"Quick Reference — {category}</div>",
                unsafe_allow_html=True,
            )
            if "factors" in config:
                base_unit = units[0]
                rows_html = ""
                for u in units:
                    factor_val = 1.0 / config["factors"][u]
                    rows_html += (
                        f'<tr><td style="color:#94A3B8;padding:3px 8px;">{u}</td>'
                        f'<td style="color:#00D9FF;font-family:\'Share Tech Mono\',monospace;'
                        f'padding:3px 8px; text-align:right;">{factor_val:.6g} / {base_unit}</td></tr>'
                    )
                st.markdown(
                    f'<table style="width:100%; font-size:0.72rem; border-collapse:collapse;">'
                    f"{rows_html}</table>",
                    unsafe_allow_html=True,
                )
