from wrappers import TbaWrapper
import os

tbaWrapper = TbaWrapper('2025isde1', os.getenv('TBA_KEY'))

for data in tbaWrapper.tbaData: 
    print(tbaWrapper.getAllianceTeamNums(data['match_number'], 'blue'))