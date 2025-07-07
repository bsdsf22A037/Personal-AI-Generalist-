import streamlit as st
import requests

BACKEND_URL = "http://localhost:1234"


def main():
    st.title("Personal AI Journalist")

    # initializing session state ---------
    if "topics" not in st.session_state:
        st.session_state.topics = []

    # setup side bar ---------
    with st.sidebar:
        st.header("Settings")
        source_type = st.selectbox(
            "Data Sources",
            options=["both", "news", "reddit"],   
            format_func=lambda x: x.capitalize()    
        )

    # topic management ---------
    st.markdown("###### Topic Management")

    col1, col2 = st.columns([4, 1])

    #  text box for a new topic 
    with col1:
        new_topic = st.text_input(
            "Enter a topic to analyze",
            placeholder="e.g. BITCOIN"
        )

    # “Add” button 
    with col2:
        
        add_disabled = len(st.session_state.topics) >= 3 or not new_topic.strip()

        if st.button("Add ➕", disabled=add_disabled):
            if new_topic.strip().lower() not in [t.lower() for t in st.session_state.topics]:
                st.session_state.topics.append(new_topic.strip())
            st.rerun()        

    #  display / remove selected topics ---------
    if st.session_state.topics:
        st.subheader("🗂 Selected Topic(s)")

        for i, topic in enumerate(st.session_state.topics[:3]):
            cols = st.columns([4, 1])

            cols[0].write(f"{i + 1}. {topic}")

            if cols[1].button("Remove ❌", key=f"remove_{i}"):
                del st.session_state.topics[i]  
                st.rerun()     


    #output part 
    st.markdown("________")    
    st.subheader("Audio Generation:")   



    #Sending data to backend 
    if st.button("Generate Summary",disabled = len(st.session_state.topics) == 0):
        if not st.session_state.topics:
            st.error("Please add at least one topic")

        else:
            with st.spinner("Analyzig topics and generating audio ...."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/generate-news-audio",
                        json={
                            "topics": st.session_state.topics,
                            "source_type":source_type
                        }
                    )
                    if response.status_code == 200:
                        st.audio(response.content,format = "audio/mpeg")
                        st.download_button(
                            "Downloaad Audio Summary",
                            data = response.content,
                            file_name = "news-summary.mp3",
                            type = "primary"
                        )

                    else:
                        handle_api_error(response)

                    
                except requests.exceptions.ConnectionError:
                    st.error("Connection error : Could not reach the backend servor")
                except Exception as e :
                    st.error(f"Unecpected Error :{str(e)}")

#Error handling     

def handle_api_error(response):
    """Handle API error responses"""       
    try:
        error_detail = response.json().get("detail","unknown error")
        st.error(f"API Error ({response.status_code}) : {error_detail}")
    except ValueError:
        st.error(f"Unexpected API Response : {response.text}")



# ------------------------------------------------------------------------
if __name__ == "__main__":
    main()
