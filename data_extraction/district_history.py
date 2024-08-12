# create a pydantic model for the district history that follows the json structure below:
'''
"53": {
        "election_history":{
            "2022": {
                "democrat": {
                    "votes": 13664,
                    "Candidate": "Kelly Coffman"
                },
                "republican": {
                    "votes": 15160,
                    "Candidate": "Deborah Silcox"
                }
            },
            "2024": {
                "democrat": {
                    "votes": 0,
                    "Candidate": "Susie Greenberg"
                },
                "republican": {
                    "votes": 0,
                    "Candidate": "Deborah Silcox"
                }
            }
        },
        "demographic_pdf": "/data_extraction/source_data/district_pdfs/district_53.pdf",
        "ballotpedia_url": "https://ballotpedia.org/Georgia_House_of_Representatives_District_53"
    }
'''

from pydantic import BaseModel
from typing import List, Dict

class Candidate(BaseModel):
    name: str
    party: str

class ElectionResult(BaseModel):
    votes: int
    candidate: Candidate

class Election(BaseModel):
    year: int
    results: List[ElectionResult]

class DistrictHistory(BaseModel):
    district: int
    election_history: List[Election]
    district_commentary: str
    demographic_pdf: str
    ballotpedia_url: str