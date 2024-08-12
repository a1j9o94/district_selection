import google.generativeai as genai
import os
import sys
import time
from dotenv import load_dotenv


load_dotenv()

def get_analyst_prompt():
    return f"""
        You are an expert political analyst and operative for the Democratic Party in Georgia. Your task is to create a detailed report outlining the Democratic Party's ability to win a specific district. Use the following information to complete your analysis:

        Analyze the provided information carefully, paying attention to:
        1. Historical election results
        2. Demographic trends
        3. Voter registration data
        4. Economic indicators
        5. Educational attainment
        6. Racial and ethnic composition
        7. Age distribution
        8. Family structure

        Create a comprehensive report that includes:

        1. A clear recommendation for the Democratic Party's strategy in this district
        2. A primer of basic demographic information, including:
        - Total population
        - Percentage of college-educated voters
        - Median income
        - Racial and ethnic breakdown
        - Percentage of households with children
        - Any other relevant demographic information
        3. Analysis of historical voting patterns and trends
        4. Evaluation of the district's competitiveness
        5. Identification of key voter groups and potential areas for Democratic growth
        6. Assessment of the opportunity cost of allocating resources to this district versus others
        7. Suggested campaign strategies and focus areas
        8. If a democratic candidate does not currently hold the seat, give recommendations for candidate recruitment in the district. What are the key issues and platforms a candidate in this district should focus on?

        When writing your report:
        - Use markdown formatting for better readability
        - Start with an executive summary containing your main recommendation
        - Be sure to include relevant context for the narrative like if the current representative is an incument, or there is an interesting trend in the history
        - Organize the information into clear sections with appropriate headers
        - Use bullet points or numbered lists where appropriate
        - Include relevant statistics and data to support your analysis
        - Consider both quantitative and qualitative factors in your assessment

        Remember that your goal is to provide a strategic analysis that will help the Democratic Party make informed decisions about resource allocation and campaign strategy across the state. Be objective in your analysis, but frame your recommendations in a way that aligns with Democratic Party goals.

        Think through your analysis and what you want to include in <thinking> tag.

        Present your final report within <report> tags, ensuring it is well-structured, informative, and actionable.
    """

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

def generate_district_report(district_number):
    #get the ballotpedia information for the district
    with open(f"source_data/ballotpedia_information/district_{district_number}.md", "r") as f:
        ballotpedia_information = f.read()
    
    genai.configure(api_key=os.environ["GOOGLE_GEMINI_API_KEY"])

    # Create the model
    generation_config = {
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 16000,
        "response_mime_type": "text/plain",
    }

    system_prompt = get_analyst_prompt()

    model = genai.GenerativeModel(
        model_name = 'gemini-1.5-pro-exp-0801',
        system_instruction = system_prompt,
        generation_config = generation_config
    )

    files = [upload_to_gemini(f"source_data/district_pdfs/district_{district_number}.pdf", mime_type="application/pdf")]
    wait_for_files_active(files)

    chat = model.start_chat(
        history=[{
           "role": "user",
           "parts": [
            files[0],
            f"The following is information from ballotpedia: {ballotpedia_information}"
           ]
        }]
    )

    response = chat.send_message("Write a report on the democratic party's ability to win this district.")

    response_text = response.text

    #create the reports folder if it doesn't exist
    if not os.path.exists("source_data/district_reports"):
        os.makedirs("source_data/district_reports")

    # save the response to a file create if it doesn't exist
    file_path = f"source_data/district_reports/district_{district_number}.md"
    with open(file_path, "w") as f:
        f.write(response_text)



# take a command line argument for the district number
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analysis.py <district_number>")
        sys.exit(1)
    
    generate_district_report(sys.argv[1])

