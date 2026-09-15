# RT-Reddy

# Zepto Data Pipeline Capstone

## Overview
This project is an automated data pipeline that extracts book data from `books.toscrape.com`, cleans and formats the data, converts prices to Indian Rupees (INR), and stores the normalized data into a SQLite database. It also includes data validation by comparing SQL query outputs with pure pandas operations.

## How to Install and Run

1. # Install Dependencies:
   Ensure you have Python installed, then install the required libraries by running this command in your terminal:
   `pip install pandas requests beautifulsoup4`, if it throws error type all libraries in terminal to download package


2. # Run the Pipeline:
   Execute the main Python script from your terminal:
   `python zepto_pipeline_2.py`

3. # View the Results:
   - The database will be created automatically as `catalog.db`.
   - The outputs of the SQL queries will be printed in the terminal and saved in a file named `query_results.txt`.

 4. # Data Cleaning & Parsing Decisions
     When web scraping, some fields may fail to parse properly. To handle messy data without crashing the pipeline, I implemented the       following rules:
    
# Missing Numeric Data: If a price or rating failed to parse, I used a **median-imputation approach**.

# Dropping rows entirely would mean losing perfectly good data in the other columns (like the book's title and category). Using the median safely fills the gaps without heavily skewing the dataset's overall numbers.

# I stripped out alphabetical characters from the raw prices using regex and utilized a dictionary mapping to reliably convert word-based ratings (e.g., "One") into integers (e.g., 1).

# Currency Conversion Rate
As per the project requirements, the conversion from Great British Pounds (GBP) to Indian Rupees (INR) utilizes a strictly fixed, project-defined baseline. 
# Fixed Rate Used: 1 GBP = 105.50 INR. 
* This rate requires no network lookup or API key.

# Database Schema
The project uses a normalized SQLite schema with two tables:
* `categories`: Contains `category_id` (Primary Key) and `category_name`.
* `books`: Contains the cleaned book data and a `category_id` (Foreign Key) linking back to the categories table.

# Opting 5 SQL Queries to check the database matching the query and how effective it is

 # SQL VS PANDAS , each coder have their own strength to write code by using different functions , but simple and robust code is required for better understanding for both viewers and users. So i have used queries as the call to put SQL and Pandas by merging them and to know the difference between them and result shows that SQL is really good for raw business and it fill the bridge of insights actions
 # Real-world data is inherently messy. Analysts spend a significant amount of time preparing data before analyzing it

 # Filter out irrelevant records using WHERE clauses.Combine data from entirely different tables using JOIN statements.Deduplicate and clean records by removing missing values (IS NULL) or duplicate entries (DISTINCT).it acts as the data-loading engine for almost every major analytics tool.
