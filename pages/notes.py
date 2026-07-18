import streamlit as st
import json
import os
from datetime import datetime

NOTES_FILE = "notes.json"


def load_notes():
    """Load saved notes from the local JSON file."""
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_notes(notes: list):
    """Persist notes list to the local JSON file."""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_notes_page():
    st.markdown(
        '<p class="panel-title" style="font-size:1.5rem; color:#00D9FF; '
        'letter-spacing:2px; text-transform:uppercase;">📝 Notes & Clipboard</p>',
        unsafe_allow_html=True,
    )

    # ── Initialise session notes from file ──────────────────────────────────
    if "notes_list" not in st.session_state:
        st.session_state.notes_list = load_notes()

    col_editor, col_saved = st.columns([5, 5])

    # ── LEFT: Note editor ────────────────────────────────────────────────────
    with col_editor:
        with st.container(border=True):
            st.markdown('<p class="panel-title">✏️ New Note</p>', unsafe_allow_html=True)

            note_title = st.text_input(
                "Title",
                placeholder="Note title...",
                key="note_title_input",
                label_visibility="collapsed",
            )

            note_body = st.text_area(
                "Content",
                placeholder="Write your note here...",
                height=200,
                key="note_body_input",
                label_visibility="collapsed",
            )

            tag_options = ["📌 General", "🔧 Dev", "💡 Idea", "⚠️ Important", "📅 Todo"]
            selected_tag = st.selectbox("Tag", tag_options, key="note_tag_select")

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("💾 Save Note", use_container_width=True, key="save_note_btn"):
                    if note_body.strip():
                        entry = {
                            "id": int(datetime.now().timestamp() * 1000),
                            "title": note_title.strip() or "Untitled",
                            "body": note_body.strip(),
                            "tag": selected_tag,
                            "created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        }
                        st.session_state.notes_list.insert(0, entry)
                        save_notes(st.session_state.notes_list)
                        st.toast("✅ Note saved!")
                        st.rerun()
                    else:
                        st.toast("⚠️ Note body cannot be empty.")

            with btn_col2:
                export_data = json.dumps(st.session_state.notes_list, indent=2)
                st.download_button(
                    label="📥 Export All",
                    data=export_data,
                    file_name="echo_notes.json",
                    mime="application/json",
                    use_container_width=True,
                    key="export_notes_btn",
                )

        # ── Clipboard / scratch area ─────────────────────────────────────────
        with st.container(border=True):
            st.markdown('<p class="panel-title">📋 Quick Clipboard</p>', unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.7rem; color:#64748B; margin-bottom:8px;">'
                "Temporary scratch space — not saved between sessions.</div>",
                unsafe_allow_html=True,
            )
            st.text_area(
                "Clipboard",
                height=100,
                key="clipboard_scratch",
                placeholder="Paste or jot something quickly...",
                label_visibility="collapsed",
            )

    # ── RIGHT: Saved notes list ──────────────────────────────────────────────
    with col_saved:
        with st.container(border=True, height=500):
            notes = st.session_state.notes_list
            header_col, count_col = st.columns([7, 3])
            with header_col:
                st.markdown('<p class="panel-title">🗂️ Saved Notes</p>', unsafe_allow_html=True)
            with count_col:
                st.markdown(
                    f'<div style="text-align:right; font-family:\'Share Tech Mono\', monospace; '
                    f'font-size:0.75rem; color:#00D9FF; margin-top:4px;">{len(notes)} notes</div>',
                    unsafe_allow_html=True,
                )

            if not notes:
                st.markdown(
                    '<div style="text-align:center; color:#64748B; font-family:\'Share Tech Mono\', '
                    'monospace; font-size:0.75rem; padding:40px;">📭 No notes yet. Create your first one!</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Search filter
                search = st.text_input(
                    "Search",
                    placeholder="🔍 Search notes...",
                    key="notes_search",
                    label_visibility="collapsed",
                )
                filtered = (
                    [n for n in notes if search.lower() in n["title"].lower() or search.lower() in n["body"].lower()]
                    if search
                    else notes
                )

                for i, note in enumerate(filtered):
                    tag_color_map = {
                        "📌 General": "#00D9FF",
                        "🔧 Dev": "#10B981",
                        "💡 Idea": "#F59E0B",
                        "⚠️ Important": "#EF4444",
                        "📅 Todo": "#8B5CF6",
                    }
                    tag_color = tag_color_map.get(note.get("tag", "📌 General"), "#00D9FF")

                    card_col, del_col = st.columns([9, 1])
                    with card_col:
                        st.markdown(
                            f"""
                            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
                                        border-left:3px solid {tag_color}; border-radius:6px;
                                        padding:8px 12px; margin-bottom:6px;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                    <span style="font-family:'Outfit', sans-serif; font-size:0.85rem;
                                                 font-weight:600; color:#FFFFFF;">{note['title']}</span>
                                    <span style="font-size:0.65rem; color:{tag_color}; font-family:'Share Tech Mono',
                                                 monospace;">{note.get('tag','')}</span>
                                </div>
                                <div style="font-family:'Outfit', sans-serif; font-size:0.75rem; color:#94A3B8;
                                            white-space:pre-wrap; word-break:break-word;">{note['body'][:120]}{'...' if len(note['body']) > 120 else ''}</div>
                                <div style="font-size:0.6rem; color:#475569; margin-top:4px;
                                            font-family:'Share Tech Mono', monospace;">{note.get('created','')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with del_col:
                        if st.button("🗑️", key=f"del_note_{note['id']}_{i}", help="Delete note"):
                            st.session_state.notes_list = [n for n in st.session_state.notes_list if n["id"] != note["id"]]
                            save_notes(st.session_state.notes_list)
                            st.toast("🗑️ Note deleted.")
                            st.rerun()
