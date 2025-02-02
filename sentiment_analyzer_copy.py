# GUI modules
from tkinter import *
from tkinter import scrolledtext, messagebox
# Web Scraping Modules
from bs4 import BeautifulSoup
import requests
# Sentiment Analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Global variables
reviewsTitleArray = []
reviewsBodyArray = []
sa = SentimentIntensityAnalyzer()
product_title = ""

# Function to scrape reviews
def GetTextFromWeb():
    global product_title, reviewsTitleArray, reviewsBodyArray

    # Clear previous data
    reviewsTitleArray.clear()
    reviewsBodyArray.clear()
    txtOutput.delete(1.0, END)

    amazonURL = url.get().strip()

    if not amazonURL:
        messagebox.showerror("Error", "Please enter a valid Amazon product URL!")
        return

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    try:
        webPage = requests.get(amazonURL, headers=HEADERS)
        webPage.raise_for_status()  # Raises error if request fails

        soup = BeautifulSoup(webPage.content, "html.parser")

        # Get product title
        title_tag = soup.find(id='productTitle')
        product_title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"

        # Get reviews
        reviews_data = soup.findAll('div', {'data-hook': 'review'})
        if not reviews_data:
            messagebox.showwarning("No Reviews", "No reviews found for this product!")
            return

        for text in reviews_data:
            review_title = text.find('a', {'data-hook': 'review-title'}).text.strip()
            review_body = text.find('span', {'data-hook': 'review-body'}).text.strip().lower()
            reviewsTitleArray.append(review_title)
            reviewsBodyArray.append(review_body)

        sentiment_analysis()

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")

# Sentiment analysis function
def sentiment_analysis():
    total_compound = 0
    txtOutput.insert(END, f"Product: {product_title}\n\n", "header")

    for review in reviewsBodyArray:
        score = sa.polarity_scores(review)
        sentiment = "Neutral"
        color = "gray"

        if score['compound'] > 0:
            sentiment = "Positive" if score['pos'] > 0.5 else "Slightly Positive"
            color = "green"
        elif score['compound'] < 0:
            sentiment = "Negative" if score['neg'] > 0.5 else "Slightly Negative"
            color = "red"

        # Display results in GUI
        result = f"Review: {review}\nSentiment: {sentiment} (Pos: {score['pos']}, Neg: {score['neg']}, Neu: {score['neu']})\n\n"
        txtOutput.insert(END, result, color)

        total_compound += score['compound']

    if reviewsBodyArray:
        average_score = total_compound / len(reviewsBodyArray)
        txtOutput.insert(END, f"\nAverage Sentiment Score: {average_score:.2f}\n", "header")

# GUI setup
window = Tk()
window.geometry("900x600")
window.title("Amazon Review Analyzer")
window.config(bg="#f4f4f4")

# Input Frame
inputFrame = Frame(window, bg="#d9d9d9", pady=10)
inputFrame.pack(fill=X)

Label(inputFrame, text="Enter Amazon Product URL:", bg="#d9d9d9", font=("Arial", 12)).pack(side=LEFT, padx=10)
url = Entry(inputFrame, font=('Arial', 12), width=50)
url.pack(side=LEFT, padx=10)

btnSubmit = Button(inputFrame, text="Analyze Reviews", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=GetTextFromWeb)
btnSubmit.pack(side=LEFT, padx=10)

# Output Text Box (Scrollable)
txtOutput = scrolledtext.ScrolledText(window, width=100, height=25, wrap=WORD, font=('Arial', 10))
txtOutput.pack(pady=20)

# Configure tag colors
txtOutput.tag_configure("header", foreground="blue", font=("Arial", 12, "bold"))
txtOutput.tag_configure("green", foreground="green")
txtOutput.tag_configure("red", foreground="red")
txtOutput.tag_configure("gray", foreground="gray")

window.mainloop()
