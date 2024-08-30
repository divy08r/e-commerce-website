# Personalized Travel Itinerary Generator

## Introduction

The **Personalized Travel Itinerary Generator** is a web application designed to help users create custom travel itineraries based on their preferences, such as budget, interests, and trip duration. The app utilizes Flask for the backend, MongoDB Atlas for data storage, and the Bard API to generate tailored itineraries. Users can also download the generated itineraries as `.ics` files for easy calendar integration.

## Features

- **User Authentication:** Secure user registration and login system.
- **Custom Itineraries:** Generate detailed travel plans based on user-provided destination, dates, and preferences.
- **Calendar Integration:** Downloadable `.ics` files for seamless calendar management.
- **Data Storage:** All user data and itineraries are stored securely using MongoDB Atlas.

## Folder Structure

```plaintext
personalized-travel-itinerary/
│
├── app.py                  # Main application script
├── templates/              # HTML templates
│   ├── error.html          # error layout
│   ├── index.html          # Home page for itinerary input
│   ├── register.html       # Registration page
│   ├── login.html          # Login page
│   └── itinerary.html      # Itinerary display page
│
├── static/                 # Static files
│   ├── css/
│   │   ├── styles-index.css
│   │   ├── styles-login.css
│   │   ├── styles-register.css  
│   │   └── styles-itinerary.css  
│   │   
│   └── js/
│       └── scripts.js      # JavaScript files
│
├── .env                    # Environment variables (not included in repo)
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Git ignore file
```

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.x**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).
- **MongoDB Atlas Account**: You'll need a MongoDB Atlas account for storing user data. Sign up and create a cluster at [mongodb.com](https://www.mongodb.com/cloud/atlas).
- **Bard API Key (Google Generative AI)**: Sign up for the Bard API (Google Generative AI) and obtain your API key. More details can be found on the [Google Developers](https://developers.google.com/) website.

## Installation

To set up the project locally, follow these steps:

### 1. Clone the Repository

Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/divy08r/e-commerce-website.git
cd e-commerce-website
```

### 2. Create and Activate a Virtual Environment

Create a virtual environment to manage the project's dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install the necessary Python packages listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of the project and add the following environment variables:

```plaintext
SECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_uri
PALM_API_KEY=your_bard_api_key
```

Replace `your_secret_key`, `your_mongodb_uri`, and `your_bard_api_key` with your actual values.

### 5. Run the Application

To start the Flask application, run the following command:

```bash
python app.py
```

### 6. Access the Application

Open your web browser and navigate to:

```plaintext
http://127.0.0.1:5000/
```

Now you can register, log in, and start creating personalized travel itineraries!


