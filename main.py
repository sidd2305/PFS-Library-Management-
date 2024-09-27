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
        books_df = pd.read_csv('books.csv', encoding='ISO-8859-1')
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
            "Adult-Non Fiction", "Adult-Fiction", "Childrens books",
            "Philosophy,Self Help, Motivation", "Non-English books"
        ])

        if st.button("Add Book"):
            if books_df['Book No'].str.lower().eq(book_id.lower()).any():
                st.error("A book with this Book No already exists. Please use a different Book No.")
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

    # Delete Book Page
    elif page == "Delete Book":
        st.title("Delete a Book")
        if 'Book No' in books_df.columns:
            book_to_delete = st.text_input("Search for a book to delete (by Book No)", "").strip()
            delete_search_results = books_df[books_df['Book No'].str.contains(book_to_delete, case=False, na=False)]
            
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

    # View Books Page
    elif page == "View Books":
        st.title("View Books")
        search_query = st.text_input("Search for a book by Book No", "").strip()
        if search_query:
            search_results = books_df[books_df['Book No'].str.contains(search_query, case=False, na=False)]
            st.write(search_results)
        else:
            st.write(books_df)
        st.download_button(label="Download Book Database", data=books_df.to_csv(index=False), file_name="books.csv", mime='text/csv')

    # Edit Books Page
    elif page == "Edit Books":
        st.title("Edit Books")
        search_query = st.text_input("Search for a book by Book No", "").strip()
        if search_query:
            search_results = books_df[books_df['Book No'].str.contains(search_query, case=False, na=False)]
            if not search_results.empty:
                st.write(search_results)
                book_to_edit = st.selectbox("Select a book to edit", search_results['Book No'].unique())
                book_data = books_df[books_df['Book No'] == book_to_edit].iloc[0]
                new_book_name = st.text_input("Title of the Book", book_data['Title of the Book'])
                new_book_no = st.text_input("Book No", book_data['Book No'])
                new_shelf_id = st.selectbox("Shelf No", [
                    "R-1-0", "R-1-1", "R-1-2", "R-1-3", "R-1-4", "R-1-5", "R-1-6", "R-1-7", "R-1-8", "R-1-9", "R-1-10",
                    "R-2-1", "R-2-2", "R-2-3", "R-2-4", "R-2-5", "R-2-6", "R-3-1"
                ], index=[
                    "R-1-0", "R-1-1", "R-1-2", "R-1-3", "R-1-4", "R-1-5", "R-1-6", "R-1-7", "R-1-8", "R-1-9", "R-1-10",
                    "R-2-1", "R-2-2", "R-2-3", "R-2-4", "R-2-5", "R-2-6", "R-3-1"
                ].index(book_data['Shelf No']))
                new_author = st.text_input("Author", book_data['Author'])
                valid_categories = [
                    "Adult-Non Fiction", "Adult-Fiction", "Childrens books",
                    "Philosophy,Self Help, Motivation", "Non-English books"
                ]
                current_category = book_data['Category'].strip()
                new_category = st.selectbox("Category", valid_categories, index=valid_categories.index(current_category))
                if st.button("Update Book"):
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Title of the Book'] = new_book_name
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Book No'] = new_book_no
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Shelf No'] = new_shelf_id
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Author'] = new_author
                    books_df.loc[books_df['Book No'] == book_to_edit, 'Category'] = new_category
                    books_df.to_csv('books.csv', index=False)
                    st.success(f"Book '{new_book_name}' updated successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.write("Please enter a search query to find a book to edit.")
        st.download_button(label="Download Book Database", data=books_df.to_csv(index=False), file_name="books.csv", mime='text/csv')

    # Issue/Return Book Page
    elif page == "Issue/Return Book":
        st.title("Issue or Return a Book")
        
        # Issue a book
        st.subheader("Issue a Book")
        if 'Book No' in books_df.columns:
            book_to_issue = st.text_input("Search for a book to issue (by Book No)", "").strip()
            issue_search_results = books_df[books_df['Book No'].str.contains(book_to_issue, case=False, na=False)]
            
            if not issue_search_results.empty:
                book_to_issue = st.selectbox("Select a book to issue", issue_search_results['Book No'].unique())
                
                # Check if the book is already issued
                if 'Book No' in issue_df.columns and 'Status' in issue_df.columns:
                    if issue_df[(issue_df['Book No'] == book_to_issue) & (issue_df['Status'] == 'Issued')].empty:
                        borrower_name = st.text_input("Borrower Name")
                        flat_number = st.text_input("Flat Number")
                        issued_on = st.date_input("Issued On", datetime.date.today())

                        if st.button("Issue Book"):
                            # Capitalize flat number and remove special characters
                            flat_number = re.sub(r'[^A-Za-z0-9]', '', flat_number).upper()
                            new_issue = pd.DataFrame({
                                'Book No': [book_to_issue],
                                'Title of the Book': [books_df.loc[books_df['Book No'] == book_to_issue, 'Title of the Book'].values[0]],
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
                        st.error("This book is already issued and cannot be issued again.")
                else:
                    st.error("Required columns not found in issue_df.")
            else:
                st.info("No matching books found.")
        else:
            st.error("The 'Book No' column is not found in books_df.")

        # Return a book
        st.subheader("Return a Book")
        if 'Book No' in issue_df.columns and 'Status' in issue_df.columns:
            book_to_return = st.text_input("Search for a book to return (by Book No)", "").strip()
            return_search_results = issue_df[(issue_df['Status'] == 'Issued') & (issue_df['Book No'].str.contains(book_to_return, case=False, na=False))]
            
            if not return_search_results.empty:
                book_to_return = st.selectbox("Select a book to return", return_search_results['Book No'].unique())
                returned_on = st.date_input("Returned On", datetime.date.today())

                if st.button("Return Book"):
                    issue_df.loc[issue_df['Book No'] == book_to_return, ['Status', 'Returned On']] = ['Returned', returned_on]
                    issue_df.to_csv('issue.csv', index=False)
                    st.success("Book returned successfully!")
            else:
                st.info("No matching books found.")
        else:
            st.error("Required columns not found in issue_df.")

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
