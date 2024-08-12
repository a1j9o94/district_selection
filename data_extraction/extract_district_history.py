from dotenv import load_dotenv
from district_history import DistrictHistory
from openai import OpenAI
from firecrawl import FirecrawlApp
import os
import json
import time
import backoff

load_dotenv()

debug = False

client = OpenAI()

system_prompt = """
    You are analyzing infomration from ballotpedia to create to give an overview of the district history. Act as a political consultant who is trying to decide if a democratic candidate should run in a district.A

    Use the following format replacing the disctirct number for the ballotpedia and pdf:
    "demographic_pdf": "/data_extraction/source_data/district_pdfs/district_53.pdf",
    "ballotpedia_url": "https://ballotpedia.org/Georgia_House_of_Representatives_District_53"
"""

interest_districts = [53, 56, 45, 48, 44]

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))


def get_ballotpedia_information(district_number):
    result = ""
    #check if the file exists
    if os.path.exists(f"source_data/ballotpedia_information/district_{district_number}.md"):
        with open(f"source_data/ballotpedia_information/district_{district_number}.md", "r") as f:
            result = f.read()
    else:
        #if the file doesn't exist, scrape the url
        crawl_result = app.scrape_url(f"https://ballotpedia.org/Georgia_House_of_Representatives_District_{district_number}")
        print(f"Got crawl result for district {district_number}")
        if debug:
            print(crawl_result)
        result = crawl_result["markdown"]
        #save the result to a file
        with open(f"source_data/ballotpedia_information/district_{district_number}.md", "w") as f:
            f.write(result)
    return result



@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def get_district_history(district_number):
    try:
        ballotpedia_information = get_ballotpedia_information(district_number)

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ballotpedia_information},
            ],
            response_format=DistrictHistory,
        )
        if completion.choices[0].message.parsed:
            print(f"Got completion for district {district_number}")
            return completion.choices[0].message.parsed.model_dump()
        else:
            return {"error": completion.choices[0].message.refusal}
    except Exception as e:
        print(f"Error getting district history for district {district_number}: {e}")

districts = {}

#cycle through districts 1 through 180 and get the district history for each one, then save it to a file as a json
for district_number in range(1, 181):
    try:
        districts[district_number] = get_district_history(district_number)
    except Exception as e:
        print(f"Error getting district history for district {district_number}: {e}")
    if district_number % 10 == 0:
        with open("districts.json", "w") as f:
            json.dump(districts, f, indent=2)
        print(f"Saved {district_number} districts")
    
    #sleep for 1 second to not overwhelm the api
    time.sleep(1)

#save the districts to a file as a json
with open("districts.json", "w") as f:
    json.dump(districts, f, indent=2)