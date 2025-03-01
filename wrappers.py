from typing import List, Literal
import requests

def tbaFetcher(compKey, authKey):
    return requests.get(f"https://www.thebluealliance.com/api/v3/event/{compKey}/matches", headers={'X-TBA-Auth-Key': authKey }).json()

class TbaWrapper:    
    def __init__(self, compKey, authKey):
        tbaResponse = tbaFetcher(compKey, authKey)
        self.tbaData = sorted(list(filter(lambda match: match['comp_level'] == 'qm', tbaResponse)), key=lambda match: match['match_number'])

    def getMatchData(self, matchNum: int): return self.tbaData[matchNum - 1]

    def getAllianceTeamNums(self, matchNum: int, alliance: Literal['blue', 'red']) -> List[int]:
        teamNums = []
        for team in self.getMatchData(matchNum)['alliances'][alliance]['team_keys']: teamNums.append(int(team.replace('frc', '')))
        return teamNums

    def getAllianceScoreBreakdown(self, matchNum: int, alliance: Literal['blue', 'red']): return self.getMatchData(matchNum)['score_breakdown'][alliance]

    def getClimbLevel(self, matchNum: int, alliance: Literal['blue', 'red'], teamNum: int):
        data = self.getMatchData(matchNum) 
        index = self.getAllianceTeamNums(alliance, matchNum).index(teamNum)
        key = 'endGameRobot' + str(index + 1)
        return data['score_breakdown'][alliance][key]


class MatchScoutingDataWrapper:
    def __init__(self):
        pass