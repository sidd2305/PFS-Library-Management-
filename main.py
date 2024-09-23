import streamlit as st
import pandas as pd
import datetime

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

        # Check if 'Title of the Book' column exists
        if 'Title of the Book' in books_df.columns:
            book_to_delete = st.text_input("Search for a book to delete", "").strip()
            delete_search_results = books_df[books_df['Title of the Book'].str.contains(book_to_delete, case=False, na=False)]
            
            if not delete_search_results.empty:
                book_to_delete = st.selectbox("Select a book to delete", delete_search_results['Title of the Book'].unique())

                if st.button("Delete Book"):
                    books_df = books_df[books_df['Title of the Book'] != book_to_delete]
                    books_df.to_csv('books.csv', index=False)
                    st.success("Book deleted successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.error("The 'Title of the Book' column is not found in books_df.")

    # Add Book Page
    elif page == "Add Book":
        st.title("Add a New Book")
        book_name = st.text_input("Title of the Book")
        book_id = st.text_input("Book No")
        shelf_id = st.text_input("Shelf No")
        author = st.text_input("Author")
        
        category = st.selectbox("Category", [
            "Adult-Fiction", 
            "Children`s books", 
            "Adult-Non Fiction", 
           
            "Philosophy, Self Help, Motivation", 
            "Non-English books"
        ])

        if st.button("Add Book"):
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

    # View Books Page (new)
    elif page == "View Books":
        st.title("View Books")
        
        search_query = st.text_input("Search for a book by title", "").strip()
        
        if search_query:
            search_results = books_df[books_df['Title of the Book'].str.contains(search_query, case=False, na=False)]
            st.write(search_results)
        else:
            st.write(books_df)

        # Add download options
        st.download_button(label="Download Book Database", data=books_df.to_csv(index=False), file_name="books.csv", mime='text/csv')

    # Edit Books Page (separate from View Books)
    elif page == "Edit Books":
        st.title("Edit Books")
    
        # Search functionality
        search_query = st.text_input("Search for a book by title", "").strip()
    
        if search_query:
            search_results = books_df[books_df['Title of the Book'].str.contains(search_query, case=False, na=False)]
            if not search_results.empty:
                st.write(search_results)
    
                # Let the user select a book from the search results
                book_to_edit = st.selectbox("Select a book to edit", search_results['Title of the Book'].unique())
    
                # Get the book data to edit
                book_data = books_df[books_df['Title of the Book'] == book_to_edit].iloc[0]
    
                # Display the current details in editable fields
                new_book_name = st.text_input("Title of the Book", book_data['Title of the Book'])
                new_book_no = st.text_input("Book No", book_data['Book No'])
                new_shelf_id = st.text_input("Shelf No", book_data['Shelf No'])
                new_author = st.text_input("Author", book_data['Author'])
    
                # Define valid categories
                valid_categories = [
                    "Non-English books",
                    "Children`s books",
                    "Adult-Non Fiction",
                   
                    "Philosophy, Self Help, Motivation",
                    "Non-English books"
                ]
    
                # Handle category selection
                current_category = book_data['Category'].strip()
                # if current_category not in valid_categories:
                #     st.warning(f"Current category '{current_category}' is not in the standard list. It will be set to 'Adult Fiction' if not changed.")
                #     current_category = "Adult Fiction"
    
                new_category = st.selectbox("Category", valid_categories, index=valid_categories.index(current_category))
    
                # Button to update the book details
                if st.button("Update Book"):
                    # Update the DataFrame with new values
                    books_df.loc[books_df['Title of the Book'] == book_to_edit] = [
                        new_book_name, new_book_no, new_shelf_id, new_author, new_category
                    ]
    
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
        
        if 'Title of the Book' in books_df.columns:
            book_to_issue = st.text_input("Search for a book to issue", "").strip()
            issue_search_results = books_df[books_df['Title of the Book'].str.contains(book_to_issue, case=False, na=False)]
            
            if not issue_search_results.empty:
                book_to_issue = st.selectbox("Select a book to issue", issue_search_results['Title of the Book'].unique())
                borrower_name = st.text_input("Borrower Name")
                flat_number = st.text_input("Flat Number")
                issued_on = st.date_input("Issued On", datetime.date.today())

                if st.button("Issue Book"):
                    new_issue = pd.DataFrame({
                        'Title of the Book': [book_to_issue],
                        'Status': ['Issued'],
                        'Issued On': [issued_on],
                        'Returned On': [''],
                        'Borrower Name': [borrower_name],
                        'Flat Number': [flat_number]
                    })
                    issue_df = pd.concat([issue_df, new_issue], ignore_index=True)
                    issue_df.to_csv('issue.csv', index=False)
                    st.success("Book issued successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.error("The 'Title of the Book' column is not found in books_df.")

        # Return a book
        st.subheader("Return a Book")
        
        if 'Title of the Book' in issue_df.columns and 'Status' in issue_df.columns:
            book_to_return = st.text_input("Search for a book to return", "").strip()
            return_search_results = issue_df[(issue_df['Status'] == 'Issued') & (issue_df['Title of the Book'].str.contains(book_to_return, case=False, na=False))]
            
            if not return_search_results.empty:
                book_to_return = st.selectbox("Select a book to return", return_search_results['Title of the Book'].unique())
                returned_on = st.date_input("Returned On", datetime.date.today())

                if st.button("Return Book"):
                    issue_df.loc[issue_df['Title of the Book'] == book_to_return, ['Status', 'Returned On']] = ['Returned', returned_on]
                    issue_df.to_csv('issue.csv', index=False)
                    st.success("Book returned successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.error("The 'Title of the Book' or 'Status' column is not found in issue_df.")

    # Current Issuers Page
    elif page == "Current Issuers":
        st.title("Current Issuers")
        
        if 'Status' in issue_df.columns:
            current_issuers = issue_df[issue_df['Status'] == 'Issued']
            st.write(current_issuers)
        else:
            st.error("The 'Status' column is not found in issue_df.")

    # Defaulters List Page
    elif page == "Defaulters List":
        st.title("Defaulters List")
        
        defaulter_days = st.number_input("Enter number of days after which a person is a defaulter", min_value=1, value=14)
        
        if 'Status' in issue_df.columns and 'Issued On' in issue_df.columns:
            issue_df['Issued On'] = pd.to_datetime(issue_df['Issued On'], errors='coerce')
            today = pd.to_datetime('today')
            defaulters = issue_df[(issue_df['Status'] == 'Issued') & ((today - issue_df['Issued On']).dt.days > defaulter_days)]
            st.write(defaulters)
        else:
            st.error("'Status' or 'Issued On' column is not found in issue_df.")
