import requests
import bs4
import regex as re
from urllib.parse import urlparse
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys
import streamlit as st

def main():
    """
    The main function coordinates the program's execution. It prompts the user for a valid URL
    and then prints an AI-generated summary of hikers' reviews for a hike.
    """
    st.header("Summary of HikingUpward.com Hike Reviews")
    url = st.text_input("Enter the url for the hikingupward.com hike and press Enter.")
    if is_valid_url(url) is True:
        hiking_comments = parse_hiking_url(url)
        st.write(google_ai_summary(hiking_comments))
    
def is_valid_url(url):
    """
    This function validates user input to ensure it points to a valid hike review page on hikingupward.com.
    A valid URL starts with "https", points to "www.hikingupward.com",
    and has a path that begins with one of the specified hiking area codes.
    """
    # attempt to parse the url
    result = urlparse(url)
    # check if all components are present
    # hiking_areas will need to be updated as needed
    hiking_areas = [
        "GWNF",
        "GSMNP",
        "JNF",
        "MNF",
        "NNF",
        "PNF",
        "SNP",
        "WMNF",
        "UNF",
    ]
    if (
        result.scheme == "https"
        and result.netloc == "www.hikingupward.com"
        and result.path.split("/")[1] in hiking_areas
    ):
        return True
    else:
        return False


def parse_hiking_url(hiking_url):
    """
    This function takes a URL for a hike on hikingupward.com and fetches the list of comments from that hike's page - including archived comments.
    If the page has no comments, it returns the message "There are no comments."
    """
    original_request = requests.get(hiking_url)
    original_soup = bs4.BeautifulSoup(original_request.text, "html5lib")
    comments_link = ""
    for a in original_soup.find_all("a"):
        if "all_reviews" in str(a):
            comments_link = "https://www.hikingupward.com" + str(a["href"])
    if comments_link == "":
        return "There are no comments."
    else:
        return get_comments(comments_link)

def get_comments(comments_link):
    """
    This function takes a URL for the comments page of a hike on hikingupward.com and returns a string of comments from that page.
    """
    comments_request = requests.get(comments_link)
    comments_soup = bs4.BeautifulSoup(comments_request.text, "html5lib")
    comments = [
        comment.get_text()
        for comment in comments_soup.select("font")
        if 'font size="1"' in str(comment)
    ]
    return ' '.join(comments)

def google_ai_summary(comments):
    """
    This functions takes the comments for a hike and uses a Google AI model to summarize what hikers liked and disliked about the hike
    and what they thought about the parking area. The function also checks for a valid Google API key.
    """
    # try to obtain Google API key from .env
    try:
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=google_api_key)
    # provide error message if there is a problem.
    except:
        return "\nPlease make sure that you saved a valid Google API key in a .env file with the variable name 'GOOGLE_API_KEY'."
    else:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # change prompt as needed depending on the response the user wants
        prompt = "Please write a summary of the following reviews of a hike that includes what users liked about the hike, what they disliked about the hike, and a summary of how they described the parking lot."
        response = model.generate_content(prompt + ': ' + comments)
        return response.text

if __name__ == "__main__":
    main()
