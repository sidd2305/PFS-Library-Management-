import streamlit as st
import pandas as pd
import sqlite3
import datetime
import re

# Password authentication
def check_password():
    def password_entered():
        if st.session_state["password"] == "pfs123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove password from state
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Incorrect password, show input again
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password")
        return False
    else:
        return True

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    # Create a table for issued books if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS issued_books (
                    book_no TEXT,
                    title TEXT,
                    status TEXT,
                    issued_on DATE,
                    returned_on DATE,
                    borrower_name TEXT,
                    flat_number TEXT
                 )''')
    conn.commit()
    conn.close()

# Fetch all issued books from the database
def fetch_issued_books():
    conn = sqlite3.connect("library.db")
    df = pd.read_sql_query("SELECT * FROM issued_books", conn)
    conn.close()
    return df

# Insert a new issue into the database
def issue_book_to_db(book_no, title, borrower_name, flat_number, issued_on):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("INSERT INTO issued_books (book_no, title, status, issued_on, borrower_name, flat_number) VALUES (?, ?, ?, ?, ?, ?)",
              (book_no, title, 'Issued', issued_on, borrower_name, flat_number))
    conn.commit()
    conn.close()

# Update the return date for a returned book
def return_book_in_db(book_no, returned_on):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("UPDATE issued_books SET status = ?, returned_on = ? WHERE book_no = ? AND status = 'Issued'",
              ('Returned', returned_on, book_no))
    conn.commit()
    conn.close()

# Filter defaulters who have not returned books for more than 14 days
def fetch_defaulters():
    conn = sqlite3.connect("library.db")
    query = '''SELECT * FROM issued_books WHERE status = 'Issued' AND DATE(issued_on) < DATE('now', '-14 days')'''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if check_password():
    init_db()  # Initialize the database

    # Load the data with error handling
    try:
        books_df = pd.read_csv('books.csv', encoding='ISO-8859-1')
        # Clean column names by stripping any leading/trailing spaces
        books_df.columns = books_df.columns.str.strip()
    except FileNotFoundError:
        st.error("CSV files not found. Please check the file paths.")
        st.stop()

    # Ensure necessary columns are of string type before using string operations
    books_df['Book No'] = books_df['Book No'].astype(str)
    
    # Sidebar Navigation
    st.sidebar.title("Library Management System")
    page = st.sidebar.selectbox("Choose a page", ["Home", "Add Book", "Delete Book", "View Books", "Edit Books", "Issue/Return Book", "Current Issuers", "Defaulters List"])

    # Define categories
    categories = [
        "Adult-Fiction",
        "Adult-Non Fiction",
        "Philosophy,Self Help, Motivation",
        "Children`s books",
        "Non-English books"
    ]

    # Home Page
    if page == "Home":
        st.title("Welcome to the Library Management System")
        st.write("Welcome to the PFS Library Management System, a platform maintained and managed by the residents of Purva Fountain Square. Our library offers a diverse collection of books across all categories, ensuring there's something for everyone. This system is designed to streamline the management and usage of our community library, and all residents are welcome to explore and contribute.")
        st.image("pfs.jpg", caption="Purva Fountain Square Library", use_column_width=True)
    # View Books Page
    # View Books Page
    # View Books Page
    elif page == "View Books":
        st.title("View All Books")
        st.write("Here are the books available in the library:")
    
        # Display the full books.csv table by default
        st.write(books_df)
    
        # Search for a specific book by exact Book Number
        book_number_search = st.text_input("Search by Book Number").strip()
        if book_number_search:
            book_search_results = books_df[books_df['Book No'] == book_number_search]
            if not book_search_results.empty:
                st.write("Search Results:")
                st.write(book_search_results)
            else:
                st.info("No book found with that number.")
        else:
            st.write("Enter a Book Number to search.")
    
    # Edit Books Page
    elif page == "Edit Books":
        st.title("Edit Book Information")
        
        # Search for a specific book by exact Book Number
        book_number_search = st.text_input("Search Book to Edit by Book Number").strip()
        
        if book_number_search:
            selected_book = books_df[books_df['Book No'] == book_number_search]
            
            if not selected_book.empty:
                st.write("Current Details:")
                st.write(selected_book)
                
                # Editable fields with current values as defaults
                new_title = st.text_input("New Title", selected_book['Title of the Book'].values[0])
                new_category = st.selectbox("New Category", categories, index=categories.index(selected_book['Category'].values[0]))
                new_author = st.text_input("New Author", selected_book['Author'].values[0])
    
                if st.button("Save Changes"):
                    # Update the books dataframe with new values
                    books_df.loc[books_df['Book No'] == selected_book['Book No'].values[0], 
                                 ['Title of the Book', 'Category', 'Author']] = [new_title, new_category, new_author]
                    
                    # Save the updated dataframe to CSV
                    books_df.to_csv('books.csv', index=False, encoding='ISO-8859-1')
                    
                    st.success("Book information updated successfully.")
            else:
                st.info("No book found with that number.")
        else:
            st.write("Enter a Book Number to search.")


    # Issue/Return Book Page
    elif page == "Issue/Return Book":
        st.title("Issue or Return a Book")
        
        # Issue a book
        st.subheader("Issue a Book")
        
        # Search for a book by Book No
        book_to_issue = st.text_input("Search for a book to issue (by Book No)", "").strip()
        issue_search_results = books_df[books_df['Book No'].str.contains(book_to_issue, case=False, na=False)]
        
        if not issue_search_results.empty:
            book_to_issue = st.selectbox("Select a book to issue", issue_search_results['Book No'].unique())
            book_name = books_df.loc[books_df['Book No'] == book_to_issue, 'Title of the Book'].values[0]
            borrower_name = st.text_input("Borrower Name")
            flat_number = st.text_input("Flat Number")
            issued_on = st.date_input("Issued On", datetime.date.today())
            
            if st.button("Issue Book"):
                flat_number = re.sub(r'[^A-Za-z0-9]', '', flat_number).upper()
                issue_df = fetch_issued_books()
                
                if issue_df[(issue_df['book_no'] == book_to_issue) & (issue_df['status'] == 'Issued')].empty:
                    issue_book_to_db(book_to_issue, book_name, borrower_name, flat_number, issued_on)
                    st.success(f"Book '{book_name}' (No: {book_to_issue}) issued to {borrower_name} successfully!")
                else:
                    st.error("This book is already issued and cannot be issued again.")
        else:
            st.info("No matching books found.")
        
        # Return a book
        st.subheader("Return a Book")
        book_to_return = st.text_input("Search for a book to return (by Book No)", "").strip()
        return_search_results = fetch_issued_books()
        return_search_results = return_search_results[return_search_results['book_no'].str.contains(book_to_return, case=False, na=False)]
        
        if not return_search_results.empty:
            book_to_return = st.selectbox("Select a book to return", return_search_results['book_no'].unique())
            book_title = return_search_results.loc[return_search_results['book_no'] == book_to_return, 'title'].values[0]
            st.write(f"Title of the Book: {book_title}")
            
            if st.button("Return Book"):
                return_book_in_db(book_to_return, datetime.date.today())
                st.success(f"Book '{book_title}' (No: {book_to_return}) returned successfully!")
        else:
            st.info("No matching issued books found.")
    
    # Current Issuers Page
    elif page == "Current Issuers":
        st.title("List of Currently Issued Books")
        issue_df = fetch_issued_books()
        st.write(issue_df[issue_df['status'] == 'Issued'])
    
    # Defaulters List Page
    elif page == "Defaulters List":
        st.title("List of Defaulters")
        defaulters = fetch_defaulters()
        if not defaulters.empty:
            st.write(defaulters)
        else:
            st.info("No defaulters found.")
