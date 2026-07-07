import streamlit as st
from openai import OpenAI
from urllib.parse import quote_plus

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Soundscape · 노래 추천",
    page_icon="🎵",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:       #0D0D1A;
    --surface:  #161625;
    --border:   #252540;
    --amber:    #F5A623;
    --rose:     #E8688A;
    --text:     #F0EDE8;
    --muted:    #8A8599;
    --radius:   14px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    max-width: 700px;
    padding: 2.5rem 2rem 4rem;
    background-color: var(--bg);
}

/* ── Header ── */
.header-wrap { text-align: center; margin-bottom: 2.5rem; }
.header-eyebrow {
    font-size: 0.72rem; letter-spacing: 0.22em;
    text-transform: uppercase; color: var(--amber); margin-bottom: 0.6rem;
}
.header-title {
    font-family: 'Playfair Display', serif; font-size: 2.8rem;
    font-weight: 900; line-height: 1.1; color: var(--text); margin: 0 0 0.5rem;
}
.header-title span { color: var(--amber); }
.header-sub { font-size: 0.95rem; color: var(--muted); font-weight: 300; }

/* ── Survey card ── */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.6rem 1.8rem; margin-bottom: 1.2rem;
}
.card-label {
    font-size: 0.68rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--amber); margin-bottom: 0.4rem;
}
.card-question {
    font-family: 'Playfair Display', serif; font-size: 1.15rem;
    font-weight: 700; margin-bottom: 0.9rem; color: var(--text);
}

/* ── Widget overrides ── */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div:hover {
    background-color: #1E1E32 !important;
    border-color: var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
}
div[data-baseweb="radio"] label,
div[data-baseweb="checkbox"] label { color: var(--text) !important; }
div[data-baseweb="slider"] div[role="slider"] { background: var(--amber) !important; }
input[type="password"], input[type="text"] {
    background-color: #1E1E32 !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
}
input[type="password"]:focus, input[type="text"]:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px rgba(245,166,35,0.15) !important;
}
textarea {
    background-color: #1E1E32 !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
}

/* ── Primary button (submit) ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--amber) 0%, #E8961A 100%) !important;
    color: #0D0D1A !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 1rem !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important; letter-spacing: 0.04em !important;
    transition: opacity 0.15s ease !important; margin-top: 0.5rem;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stButton > button:active { transform: scale(0.985) !important; }

/* ── Artist button — ghost style inside song rows ── */
.artist-btn-wrap .stButton > button {
    width: auto !important;
    background: transparent !important;
    color: var(--muted) !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    text-decoration: underline;
    text-underline-offset: 2px;
    text-decoration-color: #3a3a55;
    letter-spacing: 0 !important;
    line-height: 1.3 !important;
    min-height: unset !important;
}
.artist-btn-wrap .stButton > button:hover {
    opacity: 1 !important;
    color: var(--amber) !important;
    text-decoration-color: var(--amber);
}

/* ── Song row layout ── */
.song-row {
    display: grid;
    grid-template-columns: 2.4rem 1fr;
    gap: 0.9rem;
    padding: 0.85rem 0;
    border-bottom: 1px solid var(--border);
    align-items: start;
}
.song-row:last-child { border-bottom: none; }
.song-num {
    font-family: 'Playfair Display', serif; font-size: 1.3rem;
    font-weight: 900; color: var(--amber); line-height: 1; padding-top: 3px;
}
.song-title-text {
    font-weight: 500; font-size: 0.98rem; color: var(--text); margin-bottom: 1px;
}
.song-reason {
    font-size: 0.79rem; color: var(--rose); margin-top: 0.2rem; font-style: italic;
}
.song-yt {
    display: inline-flex; align-items: center; gap: 0.3rem;
    margin-top: 0.45rem; padding: 0.22rem 0.6rem;
    background: rgba(255,0,0,0.12); border: 1px solid rgba(255,60,60,0.25);
    border-radius: 20px; color: #FF6060 !important; font-size: 0.72rem;
    font-weight: 500; text-decoration: none !important; letter-spacing: 0.02em;
    transition: background 0.15s, border-color 0.15s;
}
.song-yt:hover { background: rgba(255,0,0,0.22); border-color: rgba(255,80,80,0.5); color: #FF8080 !important; }

/* ── Result wrapper ── */
.result-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 2rem; margin-top: 1.5rem;
}
.result-label {
    font-size: 0.68rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--rose); margin-bottom: 0.6rem;
}
.result-title {
    font-family: 'Playfair Display', serif; font-size: 1.4rem;
    font-weight: 700; margin-bottom: 1rem; color: var(--text);
}

/* ── Artist spotlight panel ── */
.artist-panel {
    background: #12121E; border: 1px solid #2e2e50;
    border-radius: var(--radius); padding: 1.6rem 1.8rem; margin-top: 1.5rem;
}
.artist-panel-eyebrow {
    font-size: 0.68rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--amber); margin-bottom: 0.3rem;
}
.artist-panel-title {
    font-family: 'Playfair Display', serif; font-size: 1.25rem;
    font-weight: 700; color: var(--text); margin-bottom: 1rem;
}

/* ── Misc ── */
.divider { height: 1px; background: var(--border); margin: 1.8rem 0; }
.api-section {
    background: #12121E; border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.2rem 1.6rem; margin-bottom: 2rem;
}
.api-label {
    font-size: 0.68rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 0.4rem;
}
.stSpinner > div { border-top-color: var(--amber) !important; }
.stAlert { border-radius: 10px !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
if "playlist" not in st.session_state:
    st.session_state.playlist = []          # list of (title, artist, reason)
if "selected_artist" not in st.session_state:
    st.session_state.selected_artist = None
if "artist_songs" not in st.session_state:
    st.session_state.artist_songs = []      # list of (title, reason)


# ── Helper: fetch more songs by artist ───────────────────────────────────────
def fetch_artist_songs(client: OpenAI, artist: str) -> list[tuple[str, str]]:
    prompt = f"""음악 큐레이터로서 '{artist}'의 대표곡 및 추천곡 10곡을 알려주세요.
아래 형식으로만 답하세요. 설명이나 머리말은 쓰지 마세요.

1|노래제목|한 줄 소개
2|노래제목|한 줄 소개
...
10|노래제목|한 줄 소개"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600,
    )
    lines = [l.strip() for l in resp.choices[0].message.content.splitlines() if "|" in l]
    result = []
    for line in lines:
        parts = line.split("|")
        if len(parts) >= 3:
            result.append((parts[1].strip(), "|".join(parts[2:]).strip()))
    return result


# ── Helper: render a song list (title, artist_or_none, reason, yt_link) ──────
def render_song_list(songs, show_artist_btn=True, api_key=""):
    """Render songs using interleaved HTML + Streamlit artist buttons."""
    for i, item in enumerate(songs):
        if show_artist_btn:
            title, artist, reason = item
        else:
            title, reason = item
            artist = None

        yt_query = quote_plus(f"{title} {artist if artist else ''} official")
        yt_url = f"https://www.youtube.com/results?search_query={yt_query}"

        col_num, col_body = st.columns([0.08, 0.92])
        with col_num:
            st.markdown(f'<div class="song-num">{i+1:02d}</div>', unsafe_allow_html=True)
        with col_body:
            st.markdown(f'<div class="song-title-text">{title}</div>', unsafe_allow_html=True)
            if artist:
                # Artist as clickable ghost button
                st.markdown('<div class="artist-btn-wrap">', unsafe_allow_html=True)
                if st.button(artist, key=f"artist_{i}_{artist}"):
                    st.session_state.selected_artist = artist
                    st.session_state.artist_songs = []
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="song-reason">{reason}</div>'
                f'<a class="song-yt" href="{yt_url}" target="_blank" rel="noopener noreferrer">▶ YouTube에서 듣기</a>',
                unsafe_allow_html=True,
            )
        st.markdown('<div style="height:0.1rem;border-bottom:1px solid #252540;margin:0 0 0.1rem"></div>', unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
    <div class="header-eyebrow">✦ AI 노래 추천 서비스</div>
    <h1 class="header-title">Sound<span>scape</span></h1>
    <p class="header-sub">몇 가지 질문으로 지금 당신에게 꼭 맞는 노래를 찾아드립니다.</p>
</div>
""", unsafe_allow_html=True)


# ── API Key ───────────────────────────────────────────────────────────────────
st.markdown('<div class="api-section"><div class="api-label">🔑 OpenAI API Key</div>', unsafe_allow_html=True)
api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ── Survey ────────────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-label">Q 1</div><div class="card-question">지금 어떤 기분인가요?</div></div>', unsafe_allow_html=True)
mood = st.select_slider("mood", options=["매우 우울", "약간 우울", "평온", "약간 신남", "매우 신남"], value="평온", label_visibility="collapsed")

st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-label">Q 2</div><div class="card-question">지금 무엇을 하고 있나요?</div></div>', unsafe_allow_html=True)
activity = st.radio("activity", ["쉬는 중 / 멍때리기", "공부 / 집중 중", "운동 / 산책", "드라이브", "파티 / 모임", "잠들기 전"], horizontal=True, label_visibility="collapsed")

st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-label">Q 3</div><div class="card-question">어떤 장르를 좋아하나요? (복수 선택 가능)</div></div>', unsafe_allow_html=True)
genres = st.multiselect("genre", ["K-POP", "팝 (Pop)", "R&B / 소울", "힙합", "재즈", "클래식", "인디 / 어쿠스틱", "록 / 밴드", "EDM / 일렉트로닉", "발라드"], default=["K-POP"], label_visibility="collapsed")

st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-label">Q 4</div><div class="card-question">빠르기는 어느 정도가 좋으세요?</div></div>', unsafe_allow_html=True)
tempo = st.radio("tempo", ["느리고 잔잔하게", "중간 템포", "빠르고 신나게"], horizontal=True, label_visibility="collapsed")

st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-label">Q 5</div><div class="card-question">노래 언어 선호도가 있나요?</div></div>', unsafe_allow_html=True)
language = st.radio("language", ["한국어", "영어", "상관없음"], horizontal=True, label_visibility="collapsed")

st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-label">Q 6 &nbsp;(선택)</div><div class="card-question">좋아하는 아티스트나 노래, 또는 특별히 원하는 분위기를 적어주세요.</div></div>', unsafe_allow_html=True)
extra = st.text_area("extra", placeholder="예: 아이유 느낌, 잔잔하고 가사가 좋은 노래, 2010년대 팝...", height=90, label_visibility="collapsed")

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)


# ── Submit ────────────────────────────────────────────────────────────────────
if st.button("🎵 나만의 플레이리스트 받기"):
    if not api_key:
        st.error("OpenAI API Key를 입력해주세요.")
    elif not genres:
        st.error("장르를 하나 이상 선택해주세요.")
    else:
        prompt = f"""당신은 음악 전문 큐레이터입니다. 아래 사용자 설문 결과를 바탕으로 노래 10곡을 추천해주세요.

[설문 결과]
- 현재 기분: {mood}
- 지금 하는 활동: {activity}
- 선호 장르: {', '.join(genres)}
- 선호 템포: {tempo}
- 언어 선호: {language}
- 추가 요청: {extra if extra else '없음'}

[출력 형식]
반드시 아래 형식으로만 답하세요. 번호, 노래제목, 아티스트, 추천이유(한 문장) 순서로 작성하세요.
각 항목은 | 로 구분합니다. 설명이나 머리말은 절대 쓰지 마세요.

1|노래제목|아티스트|추천이유
2|노래제목|아티스트|추천이유
...
10|노래제목|아티스트|추천이유"""

        with st.spinner("🎼 당신만을 위한 플레이리스트를 만들고 있어요..."):
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.85,
                    max_tokens=900,
                )
                raw = response.choices[0].message.content.strip()
                lines = [l.strip() for l in raw.splitlines() if l.strip() and "|" in l]
                parsed = []
                for line in lines:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        parsed.append((parts[1].strip(), parts[2].strip(), "|".join(parts[3:]).strip()))
                st.session_state.playlist = parsed
                st.session_state.selected_artist = None
                st.session_state.artist_songs = []
            except Exception as e:
                err = str(e)
                if "api_key" in err.lower() or "authentication" in err.lower() or "401" in err:
                    st.error("API Key가 올바르지 않습니다. 다시 확인해주세요.")
                elif "rate" in err.lower():
                    st.error("요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
                else:
                    st.error(f"오류가 발생했습니다: {err}")


# ── Playlist result ───────────────────────────────────────────────────────────
if st.session_state.playlist:
    st.markdown('<div class="result-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="result-label">✦ 추천 플레이리스트</div>', unsafe_allow_html=True)
    st.markdown('<div class="result-title">지금 당신에게 어울리는 10곡</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.75rem;color:var(--muted);margin-bottom:1rem;">가수 이름을 클릭하면 해당 아티스트의 다른 추천곡을 볼 수 있어요.</p>', unsafe_allow_html=True)

    render_song_list(st.session_state.playlist, show_artist_btn=True, api_key=api_key)

    st.markdown('</div>', unsafe_allow_html=True)


# ── Artist spotlight — triggered when an artist button is clicked ─────────────
if st.session_state.selected_artist and api_key:
    artist = st.session_state.selected_artist

    # Fetch if not yet loaded for this artist
    if not st.session_state.artist_songs:
        with st.spinner(f"🎤 {artist}의 추천곡을 불러오고 있어요..."):
            try:
                client = OpenAI(api_key=api_key)
                st.session_state.artist_songs = fetch_artist_songs(client, artist)
            except Exception as e:
                st.error(f"오류: {e}")

    if st.session_state.artist_songs:
        st.markdown('<div class="artist-panel">', unsafe_allow_html=True)
        st.markdown(f'<div class="artist-panel-eyebrow">아티스트 더보기</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="artist-panel-title">{artist}의 추천곡 10</div>', unsafe_allow_html=True)

        for i, (title, desc) in enumerate(st.session_state.artist_songs):
            yt_query = quote_plus(f"{title} {artist} official")
            yt_url = f"https://www.youtube.com/results?search_query={yt_query}"
            col_num, col_body = st.columns([0.08, 0.92])
            with col_num:
                st.markdown(f'<div class="song-num">{i+1:02d}</div>', unsafe_allow_html=True)
            with col_body:
                st.markdown(
                    f'<div class="song-title-text">{title}</div>'
                    f'<div class="song-reason">{desc}</div>'
                    f'<a class="song-yt" href="{yt_url}" target="_blank" rel="noopener noreferrer">▶ YouTube에서 듣기</a>',
                    unsafe_allow_html=True,
                )
            st.markdown('<div style="height:0.1rem;border-bottom:1px solid #252540;margin:0 0 0.1rem"></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✕ 닫기", key="close_artist"):
            st.session_state.selected_artist = None
            st.session_state.artist_songs = []
            st.rerun()
