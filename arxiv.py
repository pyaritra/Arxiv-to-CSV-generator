import sys
import csv
import requests
from bs4 import BeautifulSoup
import textwrap
import os

# Wrap width for authors column
wrap_width = 60

# CSV filename
csv_filename = "arxiv_papers.csv"

def check_duplicate(link):
    with open(csv_filename, "r", newline="", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if row and row[0] == link:
                return True
        return False

def print_usage():
    print("Usage:")
    print("To add a paper: python script_name.py <arxiv_paper_link>")
    print("To delete a row: python script_name.py delete <arxiv_paper_link>")
    print("To delete all rows: python script_name.py delete_all")
    print("To display usage information: python script_name.py -help")
    print("=================================================")
    print("arxiv_paper_link syntax : https://arxiv.org/abs/123x.456x")

# Process -help flag
if "-help" in sys.argv:
    print_usage()

# Process delete command
elif len(sys.argv) > 1 and sys.argv[1] == "delete":
    if len(sys.argv) > 2:
        link_to_delete = sys.argv[2]
        updated_rows = []

        if os.path.isfile(csv_filename):
            with open(csv_filename, "r", newline="", encoding="utf-8") as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    if row and row[0] != link_to_delete:
                        updated_rows.append(row)

            with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                csv_writer = csv.writer(csvfile)
                for row in updated_rows:
                    csv_writer.writerow(row)

            print(f"Row with link '{link_to_delete}' deleted successfully.")
        else:
            print("CSV file does not exist.")
    else:
        print("Please provide a link to delete.")

# Process delete_all command
elif len(sys.argv) > 1 and sys.argv[1] == "delete_all":
    if os.path.isfile(csv_filename):
        # Create a backup copy of the CSV file
        backup_filename = "arxiv_papers_backup.csv"
        shutil.copy2(csv_filename, backup_filename)
        
        # Delete the original CSV file
        os.remove(csv_filename)
        
        print("CSV file deleted and backup created.")
    else:
        print("CSV file does not exist.")

# Process add command
elif len(sys.argv) > 1:
    link = sys.argv[1]
    
    # Check for duplicates before adding
    if check_duplicate(link):
        print("Warning: The link is already in the CSV. Skipping...")
    else:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract paper title
        title_element = soup.find("h1", class_="title")
        title = title_element.get_text().strip() if title_element else "Title not found"
        title = title.replace("Title:", "").strip()  # Remove "Title:" and leading/trailing whitespace

        # Extract authors
        authors_element = soup.find("div", class_="authors")
        authors = authors_element.get_text().strip() if authors_element else "Authors not found"
        authors = authors.replace("Authors:", "").strip()  # Remove "Author(s):" and leading/trailing whitespace
        wrapped_authors = "\n".join(textwrap.wrap(authors, width=wrap_width))

        with open(csv_filename, "a", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Only write header if the file is being created for the first time
            if not os.path.isfile(csv_filename):
                csv_writer.writerow(["Paper Link", "Title", "Authors"])

            # Write paper details to the CSV file
            csv_writer.writerow([link, title, wrapped_authors])

            print(f"CSV file '{csv_filename}' updated successfully.")
else:
    print_usage()