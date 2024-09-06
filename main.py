import streamlit as st
import pandas as pd
import datetime

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

    # Check if 'Book Name' column exists
    if 'Book Name' in books_df.columns:
        book_to_delete = st.text_input("Search for a book to delete", "").strip()
        delete_search_results = books_df[books_df['Book Name'].str.contains(book_to_delete, case=False, na=False)]
        
        if not delete_search_results.empty:
            book_to_delete = st.selectbox("Select a book to delete", delete_search_results['Book Name'].unique())

            if st.button("Delete Book"):
                books_df = books_df[books_df['Book Name'] != book_to_delete]
                books_df.to_csv('books.csv', index=False)
                st.success("Book deleted successfully!")
        else:
            st.info("No matching books found.")
    else:
        st.error("The 'Book Name' column is not found in books_df.")

# Add Book Page
elif page == "Add Book":
    st.title("Add a New Book")
    book_name = st.text_input("Book Name")
    book_id = st.text_input("Book ID")
    shelf_id = st.text_input("Shelf ID")
    author = st.text_input("Author")
    
    category = st.selectbox("Category", [
        "Adult Fiction", 
        "Children's Fiction", 
        "Adult Non Fiction", 
        "General Knowledge", 
        "Philosophy", 
        "Other Languages", 
        "Self Help"
    ])

    if st.button("Add Book"):
        new_book = pd.DataFrame({
            'Book Name': [book_name], 
            'Book ID': [book_id], 
            'Shelf ID': [shelf_id], 
            'Author': [author], 
            'Category': [category]
        })
        books_df = pd.concat([books_df, new_book], ignore_index=True)
        books_df.to_csv('books.csv', index=False)
        st.success("Book added successfully!")

# View Books Page (new)
elif page == "View Books":
    st.title("View Books")
    
    search_query = st.text_input("Search for a book by name", "").strip()
    
    if search_query:
        search_results = books_df[books_df['Book Name'].str.contains(search_query, case=False, na=False)]
        st.write(search_results)
    else:
        st.write(books_df)

    # Add download options
    st.download_button(label="Download Book Database", data=books_df.to_csv(index=False), file_name="books.csv", mime='text/csv')

# Edit Books Page (separate from View Books)
elif page == "Edit Books":
    st.title("Edit Books")

    # Check if 'Book Name' column exists
    if 'Book Name' in books_df.columns:
        book_to_edit = st.text_input("Search for a book to edit", "").strip()
        search_results = books_df[books_df['Book Name'].str.contains(book_to_edit, case=False, na=False)]
        
        if not search_results.empty:
            book_to_edit = st.selectbox("Select a book to edit", search_results['Book Name'].unique())
            book_data = books_df[books_df['Book Name'] == book_to_edit]
            
            new_book_name = st.text_input("Book Name", book_data['Book Name'].values[0])
            new_shelf_id = st.text_input("Shelf ID", book_data['Shelf ID'].values[0])
            new_author = st.text_input("Author", book_data['Author'].values[0])
            new_category = st.selectbox("Category", [
                "Adult Fiction", 
                "Children's Fiction", 
                "Adult Non Fiction", 
                "General Knowledge", 
                "Philosophy", 
                "Other Languages", 
                "Self Help"
            ], index=["Adult Fiction", "Children's Fiction", "Adult Non Fiction", "General Knowledge", "Philosophy", "Other Languages", "Self Help"].index(book_data['Category'].values[0]))

            if st.button("Edit Book"):
                books_df.loc[books_df['Book Name'] == book_to_edit, ['Book Name', 'Shelf ID', 'Author', 'Category']] = [new_book_name, new_shelf_id, new_author, new_category]
                books_df.to_csv('books.csv', index=False)
                st.success("Book information updated!")
        else:
            st.info("No matching books found.")
    else:
        st.error("The 'Book Name' column is not found in books_df.")

# Issue/Return Book Page
# Issue/Return Book Page
elif page == "Issue/Return Book":
    st.title("Issue or Return a Book")
    
    # Issue a book
    st.subheader("Issue a Book")
    
    # Ensure the 'Book Name' column is of string type
    books_df['Book Name'] = books_df['Book Name'].astype(str)
    
    if 'Book Name' in books_df.columns:
        book_to_issue = st.text_input("Search for a book to issue", "").strip()
        
        # Avoid AttributeError by ensuring string type before applying .str.contains
        issue_search_results = books_df[books_df['Book Name'].str.contains(book_to_issue, case=False, na=False)]
        
        if not issue_search_results.empty:
            book_to_issue = st.selectbox("Select a book to issue", issue_search_results['Book Name'].unique())
            borrower_name = st.text_input("Borrower Name")
            flat_number = st.text_input("Flat Number")
            issued_on = st.date_input("Issued On", datetime.date.today())

            if st.button("Issue Book"):
                new_issue = pd.DataFrame({
                    'Book Name': [book_to_issue],
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
        st.error("The 'Book Name' column is not found in books_df.")

    # Return a book
    st.subheader("Return a Book")
    
    # Ensure the 'Book Name' and 'Status' columns are string type
    issue_df['Book Name'] = issue_df['Book Name'].astype(str)
    issue_df['Status'] = issue_df['Status'].astype(str)
    
    if 'Book Name' in issue_df.columns and 'Status' in issue_df.columns:
        book_to_return = st.text_input("Search for a book to return", "").strip()
        
        # Avoid AttributeError by ensuring string type before applying .str.contains
        return_search_results = issue_df[(issue_df['Status'] == 'Issued') & 
                                         (issue_df['Book Name'].str.contains(book_to_return, case=False, na=False))]
        
        if not return_search_results.empty:
            book_to_return = st.selectbox("Select a book to return", return_search_results['Book Name'].unique())
            returned_on = st.date_input("Returned On", datetime.date.today())

            if st.button("Return Book"):
                issue_df.loc[issue_df['Book Name'] == book_to_return, 'Status'] = 'Returned'
                issue_df.loc[issue_df['Book Name'] == book_to_return, 'Returned On'] = returned_on
                issue_df.to_csv('issue.csv', index=False)
                st.success("Book returned successfully!")
        else:
            st.info("No matching books found.")
    else:
        st.error("The 'Book Name' or 'Status' column is not found in issue_df.")

# Current Issuers Page
elif page == "Current Issuers":
    st.title("Current Issuers")

    if 'Book Name' in issue_df.columns and 'Status' in issue_df.columns:
        current_issuers_df = issue_df[issue_df['Status'] == 'Issued']

        if not current_issuers_df.empty:
            st.write("The following books are currently issued:")
            st.write(current_issuers_df[['Book Name', 'Borrower Name', 'Issued On', 'Flat Number']])
        else:
            st.write("No books are currently issued.")
    else:
        st.error("The 'Book Name' or 'Status' column is not found in issue_df.")

# Report Defaulters Page
elif page == "Defaulters List":
    st.title("Defaulter List")
    current_date = datetime.date.today()

    if 'Issued On' in issue_df.columns and 'Status' in issue_df.columns:
        defaulter_df = issue_df[(issue_df['Status'] == 'Issued') & 
                                (pd.to_datetime(issue_df['Issued On']) + pd.Timedelta(days=7) < pd.to_datetime(current_date))]

        if not defaulter_df.empty:
            st.write("The following borrowers have not returned the books within 7 days:")
            st.write(defaulter_df[['Book Name', 'Borrower Name', 'Issued On', 'Flat Number']])
        else:
            st.write("No defaulters found.")
    else:
        st.error("The 'Issued On' or 'Status' column is not found in issue_df.")
