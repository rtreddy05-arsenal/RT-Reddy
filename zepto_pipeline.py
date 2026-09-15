# ZEPTO PIPELINE DATABASE 
# In the context of the Indian quick-commerce application Zepto, references to catalog.db 

# Install the dependency from a terminal if needed: python -m pip install pandas

# Data source: { QUERY: "https://books.toscrape.com/"

# Data source: books.toscrape.com — a public website built specifically for scraping practice. 
# It requires no login, no API key, and imposes no paid tier; you may scrape it freely. 
# (The catalogue happens to be books rather than groceries — that's fine, the exercise is about the pipeline mechanics: scrape → clean → convert → store → query,
#  which is identical regardless of product category.)

# }

import sqlite3
import requests
import pandas as pd
from bs4 import BeautifulSoup  # type: ignore[reportMissingImports]

#MODULE 1 :

#TASK-1:  Using the requests and BeautifulSoup libraries, scrape all books listed across at least 3 different book categories 
# (or, if you prefer, the first 5 paginated listing pages of the "All products" catalogue — either scope is acceptable as long as your final dataset has at least 60 books). 
# For each book capture: title, price (as listed, in GBP), star_rating (as text, e.g. "Three"), availability (as listed text), and category.

print("Scraping data from books.toscrape.com...")

category_url = {

    "Non-Fiction": "https://books.toscrape.com/catalogue/category/books/non-fiction_13/index.html",

    "Science-Fiction": "https://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html",

    "young-adult": "https://books.toscrape.com/catalogue/category/books/young-adult_21/index.html",

    "poetry": "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html",

}


# Assiging the category names to a list for iteration

category_ids= {"Non-Fiction": 1, "Science-Fiction": 2, "young-adult": 3, "poetry": 4 }

category_list = list(category_ids.items())

scraped_books = []

urlopen="https://books.toscrape.com/"

# Clean the scraped fields into proper types:

for category_name, url in category_url.items():
    response = requests.get(urlopen)
    soup = BeautifulSoup(response.text, "html.parser")

    #Finding all books on this page
    books = soup.find_all('article', class_='product_pod')

    for book in books:

        title=book.find('h3').find('a')['title']                                      # Extracting the title of the book

        price_text=book.find('p', class_='price_color').text.strip()                  # Extracting the price of the book

        rating_element=book.find('p', class_='star-rating')                           # Extracting the star rating of the book

        rating_text=rating_element['class'][1]

        availability_text=book.find('p', class_='instock availability').text.strip()  # Extracting the availability of the book

        scraped_books.append({
            'title': title,
            'price_raw': price_text,
            'star_rating_raw': rating_text,
            'availability_raw': availability_text,
            'category_id': category_ids[category_name]

        })


# Turning the scraped data into a pandas DataFrame for further processing
books_df = pd.DataFrame(scraped_books)
print(f"Scraped {len(books_df)} books.\n")

# First tasks are completed in this module, and the data is now ready for cleaning and transformation in the next steps of the pipeline.
#UPDATE: 12/09/2026
#wrote this code on 12/09/2026

#-----------------------------------------------------------------------------------------------------


#MODULE 1:
#TASK-2:Clean the scraped fields into proper types:

#Strip the currency symbol from price and convert it to a float column price_gbp.
#Convert the text star rating (One…Five) into an integer column rating (1–5).
#Parse the availability text into a boolean column in_stock.
#If any field fails to parse for a given row (e.g., unexpected text), handle it with the median-imputation approach for numeric fields or drop the row (state and justify your choice) — do not leave the pipeline crashing on messy rows.


# MODULE 1: TASK-2 (Data Cleaning)

print("Cleaning scraped data...")

                                            
books_df['price_gbp'] = pd.to_numeric(
    books_df['price_raw'].str.replace(r'[^\d.]', '', regex=True),                   # 1. Strip currency symbol and convert to float
    errors='coerce'
)


rating_dict = {                                                                      # 2. Convert text star rating to integer (1-5)
    'One': 1, 
    'Two': 2, 
    'Three': 3, 
    'Four': 4, 
    'Five': 5

    }               

books_df['rating'] = books_df['star_rating_raw'].str.strip().map(rating_dict)


books_df['in_stock'] = books_df['availability_raw'].str.lower().str.contains('in stock', na=False)  # 3. Parse availability text into a boolean column


books_df['price_gbp'] = books_df['price_gbp'].fillna(books_df['price_gbp'].median())                # 4. Handle parsing failures (Median Imputation) | Justification: Dropping rows discards valid titles/categories. 
                                                                                                    #Medians safely fill gaps without skewing data.

books_df['rating'] = books_df['rating'].fillna(books_df['rating'].median())


books_df = books_df.drop(columns=['price_raw', 'star_rating_raw', 'availability_raw'])             # 5. Drop the old raw columns
          

print("Cleaning complete. Here is the processed data:")

print(books_df.head())


# Module 1 task was wrote on 14/09/2026


#------------------------------------------------------------------------------------------------------


#MODULE 1: TASK-3 (Conversion to currency )

GBP_TO_INR = 105.50                                                            # Conversion rate from GBP to INR 


books_df['price_inr'] = books_df['price_gbp'] * GBP_TO_INR                     # Create the new price_inr column


print("Currency conversion complete. Sample of updated data:")

print(books_df[['title', 'price_gbp', 'price_inr']].head())


#Task-3 was wrote on 15/09/2026

#---------------------------------------------------------------------------------------------------------

#MODULE 1: TASK-4 (normalized SQLite schema with at least two tables)

# Define the primary/foreign key relationship,{

#  QUERY :{   categories(category_id INTEGER PRIMARY KEY, category_name TEXT UNIQUE)
# books(book_id INTEGER PRIMARY KEY, title TEXT, price_gbp REAL, price_inr REAL,
      #rating INTEGER, in_stock INTEGER, category_id INTEGER REFERENCES categories(category_id))

# }

print("Setting up SQLite schema and storing data...")



# Connect to the database
conn = sqlite3.connect('catalog.db')
cursor = conn.cursor()

# Enable foreign key constraint checking in SQLite
cursor.execute("PRAGMA foreign_keys = ON;")


cursor.execute("DROP TABLE IF EXISTS books;")                        # Drop tables if they already exist so the script is safely re-runnable


cursor.execute("DROP TABLE IF EXISTS categories;")


# 1. Create the 'categories' table (Primary Key)

cursor.execute('''                                                    
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE
)
''')

# 2. Create the 'books' table (Foreign Key referencing categories)


cursor.execute('''

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
''')

# 3. Insert the category mapping into the 'categories' table
                                                                   
                                                        
 # category_list was defined in Module 1 as [('Non-Fiction', 1), ...]


cursor.executemany(
    "INSERT INTO categories (category_name, category_id) VALUES (?, ?)", 
    category_list
)

# 4. Insert the cleaned DataFrame into the 'books' table


books_df.to_sql('books', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("Normalized schema created and data successfully stored in catalog.db!")


#-----------------------------------------------------------------------------------------------


#MODULE 1 : TASK 5(Querying the database and running 5 SQL queries)


conn = sqlite3.connect('catalog.db')



print("\nSetting up database and running queries...")
conn = sqlite3.connect('catalog.db')
cursor = conn.cursor()

# 1. Drop existing tables safely (drop 'books' first due to foreign key)
cursor.execute("DROP TABLE IF EXISTS books;")
cursor.execute("DROP TABLE IF EXISTS categories;")

# 2. Create normalized schema
cursor.execute('''CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY, 
    category_name TEXT UNIQUE
)''')

cursor.execute('''CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)''')

# 3. Insert data 
# Insert categories
categories_df = pd.DataFrame(category_list, columns=['category_name', 'category_id'])
categories_df.to_sql('categories', conn, if_exists='append', index=False)

# Insert books
books_df.to_sql('books', conn, if_exists='append', index=False)

# 4. Define the 5 required SQL queries
queries = [
    "SELECT title, price_inr FROM books WHERE in_stock = 1;",
    "SELECT title, price_inr FROM books ORDER BY price_inr DESC LIMIT 5;",
    "SELECT DISTINCT rating FROM books;",
    "SELECT title, price_inr FROM books WHERE price_inr BETWEEN 2000 AND 4500;",
    """SELECT b.title, c.category_name, b.rating 
       FROM books b 
       JOIN categories c ON b.category_id = c.category_id 
       ORDER BY b.rating DESC 
       LIMIT 10;"""
]

# 5. Execute and save each query
with open("query_results.txt", "w", encoding="utf-8") as file:
    for i, q in enumerate(queries, start=1):
        # Clean up whitespace for formatting
        cleaned_query = "\n".join(line.strip() for line in q.strip().splitlines())
        result = pd.read_sql_query(cleaned_query, conn)
        
        output_text = f"- QUERY {i} -\n{cleaned_query}\n\nOUTPUT:\n{result}\n\n"
        print(output_text)
        file.write(output_text)

conn.close()
print("Pipeline complete! Results saved to query_results.txt.")


  


#Task 5 was wrote on 15/9/2026


#-------------------------------------------------------------------------------------------------



#MODULE 1: TASK 6 (SQL VS PANDAS)


# First, align the sorting and index so they are directly comparable


print("\nValidating SQL JOIN against Pandas Merge...")
conn = sqlite3.connect('catalog.db')

# 1. Read back at least two queries using pd.read_sql
query_1_sql = "SELECT title, price_inr FROM books WHERE in_stock = 1;"
df_sql_query1 = pd.read_sql(query_1_sql, conn)

query_5_sql = """
    SELECT b.title, c.category_name, b.rating 
    FROM books b 
    JOIN categories c ON b.category_id = c.category_id 
    ORDER BY b.rating DESC 
    LIMIT 10;
"""
df_sql_join = pd.read_sql(query_5_sql, conn)

conn.close()

print("\n--- Output from SQL JOIN (pd.read_sql) ---")
print(df_sql_join)

# 2. Reproduce the JOIN query using pure Pandas (no SQL)
# Merge the in-memory DataFrames on 'category_id'


df_merged = pd.merge(books_df, categories_df, on='category_id', how='inner')


# Select the same columns, sort by rating descending, and limit to top 10

df_pandas_merge = df_merged[['title', 'category_name', 'rating']].sort_values(
    by=['rating', 'title'], ascending=[False, True]
).head(10)


# Reset index so it matches the clean index of the SQL output (0-9)


df_pandas_merge = df_pandas_merge.reset_index(drop=True)

print("\n--- Output from Pandas Merge (pd.merge) ---")

print(df_pandas_merge)


sql_aligned = df_sql_join.sort_values(by='title').reset_index(drop=True)
pandas_aligned = df_pandas_merge.sort_values(by='title').reset_index(drop=True)

# Find any differences between the two
differences = sql_aligned.compare(pandas_aligned)

if differences.empty:
    print("\nEquivalence Confirmed: No differences found! The SQL and Pandas outputs are identical.")
else:
    print("\nWarning: Differences found between the outputs:")
    print(differences)