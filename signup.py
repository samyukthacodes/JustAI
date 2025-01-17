import streamlit as st
import openai
import os
from dotenv import load_dotenv
import datetime
import bcrypt
from deta import Deta

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set up Deta
DETA_KEY = os.getenv('DETA_KEY')
deta = Deta(DETA_KEY)
db = deta.Base('StreamlitAuth')

# Function to hash the password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')  # Decode bytes to string

# Function to insert a new user
def insert_user(email, username, password):
    date_joined = str(datetime.datetime.now())
    hashed_password = hash_password(password)

    return db.put({'key': username, 'username': username, 'password': hashed_password, 'date_joined': date_joined})

# Function to authenticate a user
def authenticate_user(username, password):
    user = db.get(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

# Function to sign up a new user
def sign_up():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign Up]')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

        if st.form_submit_button('Sign Up'):
            if password1 == password2:
                result = insert_user(email, username, password1)
                st.success(f"User {username} successfully created! Date joined: {result['date_joined']}")
            else:
                st.error("Passwords do not match. Please try again.")

# Function to log in a user
def login():
    with st.form(key='login', clear_on_submit=True):
        st.subheader(':green[Log In]')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')

        if st.form_submit_button('Log In'):
            user = authenticate_user(username, password)
            if user:
                # Set the state variable to indicate successful login
                st.session_state.is_authenticated = True
                st.success(f"Welcome back, {user['username']}! Last login: {datetime.datetime.now()}")
            else:
                st.error("Authentication failed. Please check your username and password.")

# Function to display the legal advice chatbot
def legal_advice_chatbot():
    st.header("AI Legal Advisor")
    st.subheader("Ask for Legal Advice")

    # User input for legal advice
    user_prompt = st.text_area("Enter your legal query:")
    
    if st.button("Get Legal Advice"):
        if user_prompt:
            # Call OpenAI API for legal advice
            completion = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Act as an AI Legal Advisor. {user_prompt}",
                max_tokens=200,
                temperature=0.7,
            )
            st.success(f"Legal Advice: {completion.choices[0].text.strip()}")
        else:
            st.warning("Please enter a legal query.")

# Function to display the dashboard
def dashboard():
    st.title("Just AI Dashboard")
    st.header("Welcome to the Dashboard!")

    # Add your dashboard content here

# Main part of the Streamlit app
if __name__ == "__main__":
    # Display the login or sign-up page based on the selected navigation
    selected_page = st.sidebar.radio("Navigation", ["Home", "Sign Up", "Log In", "Legal Advice", "Dashboard"])

    if selected_page == "Home":
        st.header("Welcome to the Home Page!")
        st.write("Navigate to 'Sign Up', 'Log In', 'Legal Advice', or 'Dashboard' using the sidebar.")

    elif selected_page == "Sign Up":
        sign_up()

    elif selected_page == "Log In":
        login()

    elif selected_page == "Legal Advice":
        # Check if the user is authenticated
        if hasattr(st.session_state, 'is_authenticated') and st.session_state.is_authenticated:
            legal_advice_chatbot()
        else:
            st.warning("Please log in to access the legal advice chatbot.")

    elif selected_page == "Dashboard":
        # Check if the user is authenticated
        if hasattr(st.session_state, 'is_authenticated') and st.session_state.is_authenticated:
            dashboard()
        else:
            st.warning("Please log in to access the dashboard.")
