import requests

#Set up a simple function that takes a url from the atlanta commission website and loops through it for all 180 districts in georgia to download all the pdfs and save them in the source_data/district_pdfs folder

# https://documents.atlantaregional.com/Profiles/House/House_district_180_NN.pdf 
# That is the url for the pdf for district 180 in georgia

# return a file path to the pdf
def download_pdf(district_number: int) -> str:
    url = f"https://documents.atlantaregional.com/Profiles/House/House_district_{district_number}_NN.pdf"
    response = requests.get(url)

    #save the pdf to the source_data/district_pdfs folder
    with open(f"source_data/district_pdfs/district_{district_number}.pdf", "wb") as f:
        f.write(response.content)

    return f"source_data/district_pdfs/district_{district_number}.pdf"


for i in range(1, 181):
    file_path = download_pdf(i)
    print(f"Downloaded file to {file_path}")
