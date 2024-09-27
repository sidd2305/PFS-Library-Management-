import streamlit as st
import pandas as pd
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

if check_password():

    # Load the data with error handling
    try:
        books_df = pd.read_csv('books.csv', encoding='ISO-8859-1')  # or try encoding='latin1'
        issue_df = pd.read_csv('issue.csv', encoding='ISO-8859-1')
        
        # Clean column names by stripping any leading/trailing spaces
        books_df.columns = books_df.columns.str.strip()
        issue_df.columns = issue_df.columns.str.strip()

    except FileNotFoundError:
        st.error("CSV files not found. Please check the file paths.")
        st.stop()

    # Sidebar Navigation
    st.sidebar.title("Library Management System")
    page = st.sidebar.selectbox("Choose a page", ["Home", "Add Book", "Delete Book", "View Books", "Edit Books", "Issue/Return Book", "Current Issuers", "Defaulters List"])

    # Home Page
    if page == "Home":
        st.title("Welcome to the Library Management System")
        st.write("Welcome to the PFS Library Management System, a platform maintained and managed by the residents of Purva Fountain Square. Our library offers a diverse collection of books across all categories, ensuring there's something for everyone. This system is designed to streamline the management and usage of our community library, and all residents are welcome to explore and contribute.")
        st.image("pfs.jpg", caption="Purva Fountain Square Library", use_column_width=True)

    # Delete Book Page
    elif page == "Delete Book":
        st.title("Delete a Book")

        # Check if 'Book No' column exists
        if 'Book No' in books_df.columns:
            book_no_to_delete = st.text_input("Search for a book to delete by Book No", "").strip()
            delete_search_results = books_df[books_df['Book No'].str.contains(book_no_to_delete, case=False, na=False)]
            
            if not delete_search_results.empty:
                book_to_delete = st.selectbox("Select a book to delete", delete_search_results['Book No'].unique())

                if st.button("Delete Book"):
                    books_df = books_df[books_df['Book No'] != book_to_delete]
                    books_df.to_csv('books.csv', index=False)
                    st.success("Book deleted successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.error("The 'Book No' column is not found in books_df.")

    # Add Book Page
    elif page == "Add Book":
        st.title("Add a New Book")
        book_name = st.text_input("Title of the Book")
        book_id = st.text_input("Book No")
        shelf_id = st.selectbox("Shelf No", [
            "R-1-0", "R-1-1", "R-1-2", "R-1-3", "R-1-4", "R-1-5", "R-1-6", "R-1-7", "R-1-8", "R-1-9", "R-1-10",
            "R-2-1", "R-2-2", "R-2-3", "R-2-4", "R-2-5", "R-2-6", "R-3-1"
        ])
        author = st.text_input("Author")
        
        category = st.selectbox("Category", [
            "Adult-Non Fiction",
            "Adult-Fiction",
            "Children`s books",
            "Philosophy,Self Help, Motivation",
            "Non-English books"
        ])

        # Check for duplicate book numbers
        if st.button("Add Book"):
            if book_id in books_df['Book No'].values:
                st.error("Book with this Book No already exists!")
            else:
                new_book = pd.DataFrame({
                    'Title of the Book': [book_name], 
                    'Book No': [book_id], 
                    'Shelf No': [shelf_id], 
                    'Author': [author], 
                    'Category': [category]
                })
                books_df = pd.concat([books_df, new_book], ignore_index=True)
                books_df.to_csv('books.csv', index=False)
                st.success("Book added successfully!")

    # View Books Page (search by Book No)
    elif page == "View Books":
        st.title("View Books")
        
        search_query = st.text_input("Search for a book by Book No", "").strip()
        
        if search_query:
            search_results = books_df[books_df['Book No'].str.contains(search_query, case=False, na=False)]
            st.write(search_results)
        else:
            st.write(books_df)

        # Add download options
        st.download_button(label="Download Book Database", data=books_df.to_csv(index=False), file_name="books.csv", mime='text/csv')

    # Edit Books Page (search by Book No)
    elif page == "Edit Books":
        st.title("Edit Books")
    
        # Search by Book No
        search_query = st.text_input("Search for a book by Book No", "").strip()
    
        if search_query:
            search_results = books_df[books_df['Book No'].str.contains(search_query, case=False, na=False)]
            if not search_results.empty:
                st.write(search_results)
    
                # Let the user select a book from the search results
                book_to_edit = st.selectbox("Select a book to edit", search_results['Book No'].unique())
    
                # Get the book data to edit
                book_data = books_df[books_df['Book No'] == book_to_edit].iloc[0]
    
                # Display the current details in editable fields
                new_book_name = st.text_input("Title of the Book", book_data['Title of the Book'])
                new_book_no = st.text_input("Book No", book_data['Book No'])
                new_shelf_id = st.selectbox("Shelf No", [
                    "R-1-0", "R-1-1", "R-1-2", "R-1-3", "R-1-4", "R-1-5", "R-1-6", "R-1-7", "R-1-8", "R-1-9", "R-1-10",
                    "R-2-1", "R-2-2", "R-2-3", "R-2-4", "R-2-5", "R-2-6", "R-3-1"
                ])
                new_author = st.text_input("Author", book_data['Author'])
    
                # Define valid categories
                valid_categories = [
                    "Adult-Non Fiction",
                    "Adult-Fiction",
                    "Children`s books",
                    "Philosophy,Self Help, Motivation",
                    "Non-English books"
                ]
    
                # Handle category selection
                current_category = book_data['Category'].strip()
                new_category = st.selectbox("Category", valid_categories, index=valid_categories.index(current_category))
    
                # Button to update the book details
                if st.button("Update Book"):
                    # Update each column individually to avoid overwriting the entire row
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Title of the Book'] = new_book_name
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Book No'] = new_book_no
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Shelf No'] = new_shelf_id
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Author'] = new_author
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Category'] = new_category
    
                    # Save the updated DataFrame to CSV
                    books_df.to_csv('books.csv', index=False)
                    st.success(f"Book '{new_book_name}' updated successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.write("Please enter a search query to find a book to edit.")
    
        # Add download options
        st.download_button(label="Download Book Database", data=books_df.to_csv(index=False), file_name="books.csv", mime='text/csv')

    # Issue/Return Book Page
    elif page == "Issue/Return Book":
        st.title("Issue or Return a Book")
        
        # Issue a book
        st.subheader("Issue a Book")
        
        if 'Book No' in books_df.columns:
            book_to_issue = st.text_input("Search for a book to issue by Book No", "").strip()
            issue_search_results = books_df[books_df['Book No'].str.contains(book_to_issue, case=False, na=False)]
            
            if not issue_search_results.empty:
                st.write(issue_search_results)
                book_selected_for_issue = st.selectbox("Select a book to issue", issue_search_results['Book No'].unique())
                issuer_name = st.text_input("Issuer's Name")
                issue_date = st.date_input("Issue Date", datetime.date.today())
                return_date = st.date_input("Return Date", datetime.date.today() + datetime.timedelta(days=14))

                if st.button("Issue Book"):
                    if not issue_df[issue_df['Book No'] == book_selected_for_issue].empty:
                        st.error("Book is already issued to someone else!")
                    else:
                        new_issue = pd.DataFrame({
                            'Book No': [book_selected_for_issue],
                            'Issuer Name': [issuer_name],
                            'Issue Date': [issue_date],
                            'Return Date': [return_date]
                        })
                        issue_df = pd.concat([issue_df, new_issue], ignore_index=True)
                        issue_df.to_csv('issue.csv', index=False)
                        st.success("Book issued successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.error("The 'Book No' column is not found in books_df.")

        # Return a book
        st.subheader("Return a Book")
        return_book_no = st.text_input("Enter the Book No to return", "").strip()

        if st.button("Return Book"):
            if return_book_no in issue_df['Book No'].values:
                issue_df = issue_df[issue_df['Book No'] != return_book_no]
                issue_df.to_csv('issue.csv', index=False)
                st.success("Book returned successfully!")
            else:
                st.error("This book is not issued.")

    # Current Issuers Page
    elif page == "Current Issuers":
        st.title("List of Current Issuers")
        st.write(issue_df)
        st.download_button(label="Download Current Issuers List", data=issue_df.to_csv(index=False), file_name="issuers.csv", mime='text/csv')

    # Defaulters List Page
    elif page == "Defaulters List":
        st.title("List of Defaulters")
        today = datetime.date.today()
        defaulters_df = issue_df[pd.to_datetime(issue_df['Return Date']) < pd.Timestamp(today)]
        st.write(defaulters_df)
        st.download_button(label="Download Defaulters List", data=defaulters_df.to_csv(index=False), file_name="defaulters.csv", mime='text/csv')
