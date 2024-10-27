import streamlit 

streamlit.sidebar.title("Example")
streamlit.sidebar.write("Download these example patient files to generate and example engel score")

example_files = {
    "example1.txt": "some content",
    "example2.txt": "some content",
    "example3.txt": "some content"
}

for filename, content in example_files.items():
    if streamlit.sidebar.button(f"Download {filename}"):
        streamlit.session_state[filename] = content


streamlit.sidebar.title("Upload Patient Notes")
uploaded_file = streamlit.sidebar.file_uploader("Drag and drop your patients notes", type="txt", accept_multiple_files=True)

streamlit.title("Predicted Engel Score")

if uploaded_file:
    # engel_score = calculate_engel_score(uploaded_file)
    streamlit.metric("Engel Score", 5)
    # streamlit.metric("Engel Score", 5, delta="") --> if we want to show a change in engel score
else:
    streamlit.write("Please upload a file to view the Engel Score")


streamlit.write("---")
streamlit.subheader("Explanation of the Prediction")


# engel_score_explnation = explain_engel_score(uploaded_file)
# streamlit.write(engel_score_explnation)

streamlit.write("The reason we have this engel score is ....")

streamlit.markdown(
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
