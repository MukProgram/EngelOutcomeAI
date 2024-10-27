import streamlit as st
import time
from llm import calculate_engel_pretrained

st.set_page_config(layout="wide")

# Function to animate text appearing word by word
def display_text_animated(text, delay=0.05):
    words = text.split()
    displayed_text = ""
    placeholder = st.empty()  # Create an empty placeholder for the explanation

    for word in words:
        displayed_text += word + " "
        placeholder.write(displayed_text)  # Update the placeholder with the current text
        time.sleep(delay)  # Wait for the specified delay

# Main app
st.sidebar.title("Example")
st.sidebar.write("Download these example patient files to generate an example Engel score")


file_content_1 = ""
with open("../../data/clinical_notes/EA0001.txt", 'r') as file:  # Open the file in read mode_
    file_content_1 = file.read()      # Read the entire file content
  

st.sidebar.download_button(
    label="Sample Clinical Note Text 1",
    data=file_content_1,
    file_name="clinical_note_example_1.txt",
    mime="text/plain"
)

file_content_2 = ""
with open("../../data/clinical_notes/EA0002.txt", 'r') as file:  # Open the file in read mode_
    file_content_2 = file.read()      # Read the entire file content

st.sidebar.download_button(
    label="Sample Clinical Note Text 2",
    data=file_content_2,
    file_name="clinical_note_example_2.txt",
    mime="text/plain"
)

file_content_3 = ""
with open("../../data/clinical_notes/EA0003.txt", 'r') as file:  # Open the file in read mode_
    file_content_3 = file.read()      # Read the entire file content

st.sidebar.download_button(
    label="Sample Clinical Note Text 3",
    data=file_content_3,
    file_name="clinical_note_example_3.txt",
    mime="text/plain"
)

st.sidebar.title("Upload Patient Notes")
uploaded_file = st.sidebar.file_uploader("Drag and drop your patient notes", type="txt")

uploaded_file_string = uploaded_file.read().decode("utf-8") if uploaded_file else ""
res = calculate_engel_pretrained(uploaded_file_string)
res = json.loads(res)
explanation_text = res["reasoning"]
gener_score = res["score"]





col1, col2 = st.columns([3, 2]) 
with col1:
    st.title("Predicted Engel Score")

    if 'score_generated' not in st.session_state:
        st.session_state['score_generated'] = False

    if uploaded_file:
        if not st.session_state['score_generated']:
            with st.spinner('Generating...'):
                time.sleep(5)  # Simulate generation delay

            # Example score calculation (replace with actual calculation logic)
        st.metric("Engel Score", gener_score)
        st.session_state['score_generated'] = True  # Set flag to avoid re-generating

        st.write("---")
        st.subheader("Explanation of the Prediction")


        # Button to trigger explanation animation
        if st.button("Show Explanation"):
            display_text_animated(explanation_text)

    else:
        st.write("Please upload a file to view the Engel Score")
with col2:
    if uploaded_file:
        st.subheader("Clinic Note Display")
        st.write(uploaded_file_string)

# Hide Streamlit style
hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 20%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom styling for the Streamlit app
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F0F2F6;
    }

    section[data-testid="stSidebar"] {
        background-color: #bacdf2;
    }

    div.stDownloadButton > button {
        color: #ffffff;
        background-color: #0072B2;
        border-radius: 5px;
        padding: .5em 1em;
    }

    div.stDownloadButton > button:hover {
        background-color: #005282;
        border-color: black;
    }

    div.stButton > button {
        color: #ffffff;
        background-color: #0072B2;
        border-radius: 5px;
        padding: .5em 1em;
    }

    div.stButton > button:hover {
        background-color: #005282;
        border-color: black;
    }

    h1, h2, h3 {
        color: #395ca0;
    }
    div[data-testid="stMetricValue"] {
        color: #333333 !important;
    }
    p {
        color: #333333;
    }
    section[data-testid="stSidebar"] {
        padding-top: 0rem;
    }
    header {visibility: hidden;}

    div.block-container{padding-top:2rem;}
    </style>
    """,
    unsafe_allow_html=True
)
