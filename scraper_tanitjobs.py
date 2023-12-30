import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Function to scrape data from a specific page
def scrape_page(url):
    response = requests.get(url)

    # Request was successful code: 200
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Selectors for both featured and regular jobs
        job_elements_featured = soup.find_all('article', class_='media well listing-item listing-item__jobs listing-item__featured')
        job_elements_regular = soup.find_all('article', class_='media well listing-item listing-item__jobs listing-item__no-logo')

        # Combine both types of job elements
        job_elements = job_elements_featured + job_elements_regular

        # Check if any job elements were found
        if job_elements:
            print(f"Found {len(job_elements)} job elements on {url}.")

            # Initialize lists to store data
            job_titles = []
            job_descriptions = []
            company_names = []
            job_locations = []
            tags = []  # New column for tags

            # Iterating through elements
            for job in job_elements:
                job_title_element = job.find('div', class_="media-heading listing-item__title")
                job_description_element = job.find('div', class_='listing-item__desc hidden-sm hidden-xs')
                company_name_element = job.find('span', class_='listing-item__info--item listing-item__info--item-company')
                job_location_element = job.find('span', class_='listing-item__info--item listing-item__info--item-location')

                # Determine the tag (featured or available)
                tag = "featured" if job in job_elements_featured else "available"

                # Extract data and append to lists
                job_titles.append(job_title_element.text if job_title_element else "Title not found")
                job_descriptions.append(job_description_element.text if job_description_element else "Description not found")
                company_names.append(company_name_element.text if company_name_element else "Company not found")
                job_locations.append(job_location_element.text if job_location_element else "Location not found")
                tags.append(tag)

            # Create a DataFrame
            data = {'Job Title': job_titles, 'Description': job_descriptions, 'Company': company_names, 'Location': job_locations, 'Tags': tags}
            df = pd.DataFrame(data)

            return df

        else:
            print(f"No job elements found on {url}.")

    else:
        print(f"Failed to retrieve the page {url}. Status Code: {response.status_code}")
        return None

# Main code to iterate through pages
base_url = "https://www.tanitjobs.com/cities/jobs-in-sousse/?searchId=1702040306.949&action=search&page="

# Set the range of pages you want to scrape
start_page = 1
end_page = 10  # Change this to the desired end page

# Initialize an empty DataFrame to store the results
final_df = pd.DataFrame()

for page_number in range(start_page, end_page + 1):
    page_url = f"{base_url}{page_number}"
    page_df = scrape_page(page_url)

    if page_df is not None:
        final_df = pd.concat([final_df, page_df], ignore_index=True)

# Display the final DataFrame
print(final_df)

# Generate a new filename based on the current date and time
current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
new_filename = f'job_data_all_pages_{current_datetime}.xlsx'

# Save the final DataFrame to an Excel file
final_df.to_excel(new_filename, index=False)
