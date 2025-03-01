from typing import List, Literal
import requests # type: ignore

def tbaFetcher(compKey, authKey):
    return requests.get(f"https://www.thebluealliance.com/api/v3/event/{compKey}/matches", headers={'X-TBA-Auth-Key': authKey }).json()

class TbaWrapper:    
    def __init__(self, compKey, authKey):
        tbaResponse = tbaFetcher(compKey, authKey)
        self.tbaData = sorted(list(filter(lambda match: match['comp_level'] == 'qm', tbaResponse)), key=lambda match: match['match_number'])

    def getMatchData(self, matchNum: int): 
        return self.tbaData[matchNum - 1]

    def getAllianceTeamNums(self, matchNum: int, alliance: Literal['blue', 'red']) -> List[int]:
        teamNums = []
        for team in self.getMatchData(matchNum)['alliances'][alliance]['team_keys']: teamNums.append(int(team.replace('frc', '')))
        return teamNums

    def getAllianceScoreBreakdown(self, matchNum: int, alliance: Literal['blue', 'red']): 
        return self.getMatchData(matchNum)['score_breakdown'][alliance]

    def getClimbLevel(self, matchNum: int, alliance: Literal['blue', 'red'], teamNum: int):
        index = self.getAllianceTeamNums(alliance, matchNum).index(teamNum)
        key = 'endGameRobot' + str(index + 1)
        return self.getAllianceScoreBreakdown(matchNum, alliance)[alliance][key]
    
    def getTotalAlgaeProcessor(self, matchNum: int):
        self.getAllianceScoreBreakdown(matchNum, 'red')['wallAlgaeCount'] + self.getAllianceScoreBreakdown(matchNum, 'blue')['wallAlgaeCount']

    def getAllianceReefForLevel(self, matchNum: int, alliance: Literal['blue', 'red'], period: Literal['auto', 'teleop'], level: Literal['L1', 'L2', 'L3', 'L4']):
        scoreBreakdown = self.getAllianceScoreBreakdown(matchNum, alliance)

        periodKey = ''
        if period == 'teleop': periodKey = 'teleopReef'
        else: periodKey = 'autoReef'

        tbaLevel = ''
        if level == 'L1': return scoreBreakdown[periodKey]['trough']
        if level == 'L2': tbaLevel = 'botRow'
        if level == 'L3': tbaLevel = 'midRow'
        if level == 'L4': tbaLevel = 'topRow'

        return sum(scoreBreakdown[periodKey][tbaLevel].values())

    def getAllianceNetAlgae(self, matchNum: int, alliance: Literal['blue', 'red']):
        return self.getAllianceScoreBreakdown(matchNum, alliance)['netAlgaeCount']

class MatchScoutingDataWrapper:
    def __init__(self, redAllianceTeamNums, blueAllianceTeamNums, data):
        self.data = data
        self.redAllianceTeamNums = redAllianceTeamNums
        self.blueAllianceTeamNums = blueAllianceTeamNums
        self.redAllianceData = filter(lambda d: d['teamNum'] in redAllianceTeamNums, data)
        self.blueAllianceData = filter(lambda d: d['teamNum'] in blueAllianceTeamNums, data)