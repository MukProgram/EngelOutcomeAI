import streamlit as st
import time

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

example_files = {
    "example1.txt": "some content",
    "example2.txt": "some content",
    "example3.txt": "some content"
}

for filename, content in example_files.items():
    if st.sidebar.button(f"Download {filename}"):
        st.session_state[filename] = content

st.sidebar.title("Upload Patient Notes")
uploaded_file = st.sidebar.file_uploader("Drag and drop your patient notes", type="txt", accept_multiple_files=True)

st.title("Predicted Engel Score")

if 'score_generated' not in st.session_state:
    st.session_state['score_generated'] = False

if uploaded_file:
    if not st.session_state['score_generated']:
        with st.spinner('Generating...'):
            time.sleep(5)  # Simulate generation delay

        # Example score calculation (replace with actual calculation logic)
        st.metric("Engel Score", 5)
        st.session_state['score_generated'] = True  # Set flag to avoid re-generating

    st.write("---")
    st.subheader("Explanation of the Prediction")

    # Explanation text
    explanation_text = "The reason we have this Engel score is due to various factors including the patient's medical history and symptoms."

    # Button to trigger explanation animation
    if st.button("Show Explanation"):
        display_text_animated(explanation_text)

else:
    st.write("Please upload a file to view the Engel Score")



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
                height: 0%;
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
