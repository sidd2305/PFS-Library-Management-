import streamlit as st
import pandas as pd
import datetime

# Load the data with error handling
try:
    books_df = pd.read_csv('books.csv')
    issue_df = pd.read_csv('issue.csv')
    
    # Clean column names by stripping any leading/trailing spaces
    books_df.columns = books_df.columns.str.strip()
    issue_df.columns = issue_df.columns.str.strip()

except FileNotFoundError:
    st.error("CSV files not found. Please check the file paths.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("Library Management System")
page = st.sidebar.selectbox("Choose a page", ["Home", "Add Book", "Delete Book","View/Edit Books", "Issue/Return Book", "Report Defaulters"])

# Home Page
if page == "Home":
    st.title("Welcome to the Library Management System")
    st.write("Welcome to the PFS Library Management System, a platform maintained and managed by the residents of Purva Fountain Square. Our library offers a diverse collection of books across all categories, ensuring there's something for everyone. This system is designed to streamline the management and usage of our community library, and all residents are welcome to explore and contribute.")

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

    if st.button("Add Book"):
        new_book = pd.DataFrame({'Book Name': [book_name], 'Book ID': [book_id], 'Shelf ID': [shelf_id]})
        books_df = pd.concat([books_df, new_book], ignore_index=True)
        books_df.to_csv('books.csv', index=False)
        st.success("Book added successfully!")

# View/Edit Books Page
elif page == "View/Edit Books":
    st.title("View or Edit Books")
    
    # Add download options
    st.download_button(label="Download Database of Book Details",data=books_df.to_csv(index=False), file_name="books.csv", mime='text/csv')
    st.download_button(label="Download Database of Book Issuer Details", data=issue_df.to_csv(index=False), file_name="issue.csv", mime='text/csv')
    
    # Check if 'Book Name' column exists
    if 'Book Name' in books_df.columns:
        st.write(books_df)

        book_to_edit = st.text_input("Search for a book", "").strip()
        search_results = books_df[books_df['Book Name'].str.contains(book_to_edit, case=False, na=False)]
        
        if not search_results.empty:
            book_to_edit = st.selectbox("Select a book to edit", search_results['Book Name'].unique())
            book_data = books_df[books_df['Book Name'] == book_to_edit]
            new_book_name = st.text_input("Book Name", book_data['Book Name'].values[0])
            new_shelf_id = st.text_input("Shelf ID", book_data['Shelf ID'].values[0])

            if st.button("Edit Book"):
                books_df.loc[books_df['Book Name'] == book_to_edit, 'Book Name'] = new_book_name
                books_df.loc[books_df['Book Name'] == book_to_edit, 'Shelf ID'] = new_shelf_id
                books_df.to_csv('books.csv', index=False)
                st.success("Book information updated!")
        else:
            st.info("No matching books found.")
    else:
        st.error("The 'Book Name' column is not found in books_df.")

# Issue/Return Book Page
elif page == "Issue/Return Book":
    st.title("Issue or Return a Book")
    
    # Issue a book
    st.subheader("Issue a Book")
    if 'Book Name' in books_df.columns:
        book_to_issue = st.text_input("Search for a book to issue", "").strip()
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
    if 'Book Name' in issue_df.columns and 'Status' in issue_df.columns:
        book_to_return = st.text_input("Search for a book to return", "").strip()
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

# Report Defaulters Page
elif page == "Report Defaulters":
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
