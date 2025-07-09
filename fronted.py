import streamlit as st, requests
BACKEND_URL = "http://localhost:1234"

def main():
    st.title("Personal AI Journalist")
    if "topics" not in st.session_state: st.session_state.topics = []

    with st.sidebar:
        st.header("Settings")
        source_type = st.selectbox("Data Sources", ["both", "news", "reddit"])

    st.markdown("###### Topic Management")
    c1, c2 = st.columns([4,1])
    topic = c1.text_input("Enter a topic", placeholder="e.g. BITCOIN")
    if c2.button("Add", disabled=not topic.strip() or len(st.session_state.topics) >= 3):
        if topic.lower() not in [t.lower() for t in st.session_state.topics]:
            st.session_state.topics.append(topic.strip())
        st.rerun()

    if st.session_state.topics:
        st.subheader("Selected Topics")
        for i, t in enumerate(st.session_state.topics):
            col = st.columns([4,1])
            col[0].write(f"{i+1}. {t}")
            if col[1].button("❌", key=f"del_{i}"):
                del st.session_state.topics[i]; st.rerun()

    st.markdown("---")
    if st.button("Generate Summary", disabled=not st.session_state.topics):
        with st.spinner("Working..."):
            r = requests.post(
                f"{BACKEND_URL}/generate-news-audio",
                json={"topics": st.session_state.topics, "source_type": source_type},
                timeout=120
            )
            if r.ok:
                st.audio(r.content, format="audio/mpeg")
                st.download_button("Download MP3", r.content, "news-summary.mp3")
            else:
                st.error(r.text)

if __name__ == "__main__":
    main()
