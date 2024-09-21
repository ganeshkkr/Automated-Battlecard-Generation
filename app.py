import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from scraper3 import fetch_data
import tempfile

# Load environment variables
load_dotenv()

# Configure the Generative AI client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(prompt):
    try:
        # Create a new chat session
        chat = genai.GenerativeModel("gemini-pro").start_chat(history=[])

        # Send the prompt and get the response
        response = chat.send_message(prompt)

        # Extract the text content from the response
        text_response = response.text

        # Print the response for debugging
        print(f"AI response: {text_response}")
        return text_response
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

def generate_sales_battlecard(company_name_1, company_url_1, company_name_2, company_url_2):
    metrics = [
        "Sales Overview",
        "Sales Channels",
        "Sales Performance",
        "Revenue Sources",
        "Sales Strategies",
        "Market Share",
        "Competitive Position"
    ]

    prompt = f"""
    Generate a sales battlecard comparing {company_name_1} and {company_name_2}. 
    Focus on these metrics: {metrics}. 
    Include data on their products, services, target markets, strengths, weaknesses, and competitive advantages.

    Company 1 URL: {company_url_1}
    Company 2 URL: {company_url_2}
    """

    try:
        # Get response from Gemini Pro
        response = get_gemini_response(prompt)
        return response
    except Exception as e:
        st.error(f"Error generating battlecard: {e}")
        return None

def generate_marketing_battlecard(company_name_1, company_url_1, company_name_2, company_url_2):
    metrics = [
        "Overview",
        "Products and Services",
        "Market Position",
        "Marketing Strategies",
        "Strengths",
        "Weaknesses",
        "Opportunities",
        "Threats"
    ]

    prompt = f"""
    Generate a marketing battlecard comparing {company_name_1} and {company_name_2}. 
    Focus on these metrics: {metrics}. 
    Include data on their products, services, target markets, strengths, weaknesses, opportunities, and threats.

    Company 1 URL: {company_url_1}
    Company 2 URL: {company_url_2}
    """

    try:
        # Get response from Gemini Pro
        response = get_gemini_response(prompt)
        return response
    except Exception as e:
        st.error(f"Error generating battlecard: {e}")
        return None

def generate_swot_analysis(company_name):
    prompt = f"Conduct a SWOT analysis for {company_name}."
    return get_gemini_response(prompt)

def save_battlecards_to_file(battlecards, filename):
    with open(filename, 'w') as file:
        for card_type, card_data in battlecards.items():
            file.write(f"--- {card_type} ---\n")
            file.write(card_data + "\n\n")

def save_feedback_to_file(feedback, filename):
    with open(filename, 'a') as file:  # Append feedback to the file
        file.write(f"--- Feedback ---\n")
        file.write(feedback + "\n\n")

# Set the title of the Streamlit app
st.title("Automated Battlecard Generation System")

# Inputs for company and competitors
company_name = st.text_input("Enter Company Name")
company_url = st.text_input("Enter Company URL")
objective = st.selectbox("Select Objective", ["SWOT", "Marketing", "Sales"])

num_competitors = st.number_input("Number of Competitors", min_value=0, max_value=10, value=0)

# Generate competitor fields based on the selected objective
competitors = [(st.text_input(f"Competitor {i+1} Name", key=f"competitor_name_{i}"), 
                st.text_input(f"Competitor {i+1} URL", key=f"competitor_url_{i}")) 
               for i in range(num_competitors)]

if st.button("Analyze"):
    urls = [company_url] + [url for _, url in competitors]
    scraped_data = fetch_data(urls)  # Fetch data from all URLs
    
    # Display scraped data
    st.subheader("Scraped Data")
    for title, paragraphs in scraped_data:
        st.write(f"**Title:** {title}")
        for para in paragraphs:
            st.write(f"- {para}")
    
    battlecards = {}
    
    if company_name and company_url:
        if objective == "SWOT":
            # Generate SWOT analysis for both the company and competitors
            company_swot = generate_swot_analysis(company_name)
            battlecards[f"SWOT Analysis for {company_name}"] = company_swot

            if num_competitors > 0:
                for competitor_name, competitor_url in competitors:
                    competitor_swot = generate_swot_analysis(competitor_name)
                    battlecards[f"SWOT Analysis for {competitor_name}"] = competitor_swot

        elif objective == "Marketing":
            if num_competitors == 1:
                company_name_2, company_url_2 = competitors[0]  # Use the first competitor only
                
                # Generate marketing battlecard
                battlecard_data = generate_marketing_battlecard(company_name, company_url, company_name_2, company_url_2)
                battlecards[f"Marketing Battlecard for {company_name} vs {company_name_2}"] = battlecard_data
            else:
                st.error("For Marketing Battlecard, please provide one competitor.")
                
        elif objective == "Sales":
            if num_competitors == 1:
                company_name_2, company_url_2 = competitors[0]  # Use the first competitor only
                
                # Generate sales battlecard
                battlecard_data = generate_sales_battlecard(company_name, company_url, company_name_2, company_url_2)
                battlecards[f"Sales Battlecard for {company_name} vs {company_name_2}"] = battlecard_data
            else:
                st.error("For Sales Battlecard, please provide one competitor.")
    
    # Display all battlecards
    if battlecards:
        st.subheader("Generated Battlecards")
        for card_type, card_data in battlecards.items():
            st.write(f"**{card_type}:**")
            st.write(card_data)
            st.session_state[f"{card_type}_text"] = card_data  # Store for editing later

        st.subheader("Edit Battlecards")
        selected_battlecard = st.selectbox("Select Battlecard to Edit", list(battlecards.keys()))
        if selected_battlecard:
            edited_battlecard = st.text_area(f"Edit {selected_battlecard}", value=st.session_state.get(f"{selected_battlecard}_text", ""), height=200)
            st.session_state[f"{selected_battlecard}_text"] = edited_battlecard

    # Download options
    if st.button("Download Battlecards"):
        if battlecards:
            file_type = st.selectbox("Select File Type", ["All", "Single"])
            
            if file_type == "All":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
                    save_battlecards_to_file(battlecards, temp_file.name)
                    temp_file.seek(0)
                    st.download_button("Download All Battlecards", temp_file.read(), file_name="battlecards.txt")

            elif file_type == "Single":
                selected_download_card = st.selectbox("Select Battlecard to Download", list(battlecards.keys()))
                if selected_download_card:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
                        save_battlecards_to_file({selected_download_card: st.session_state[f"{selected_download_card}_text"]}, temp_file.name)
                        temp_file.seek(0)
                        st.download_button(f"Download {selected_download_card}", temp_file.read(), file_name="battlecard.txt")

# Feedback Section
st.subheader("Feedback")
feedback = st.text_area("Enter your feedback here:")
if st.button("Submit Feedback"):
    if feedback:
        feedback_file = "feedback.txt"
        save_feedback_to_file(feedback, feedback_file)
        st.success("Feedback submitted successfully!")
    else:
        st.error("Please enter feedback before submitting.")
