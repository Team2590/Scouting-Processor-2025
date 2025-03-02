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
        index = self.getAllianceTeamNums(matchNum, alliance).index(teamNum)
        key = 'endGameRobot' + str(index + 1)
        return self.getAllianceScoreBreakdown(matchNum, alliance)[key]
    
    def getTotalAlgaeProcessor(self, matchNum: int):
        return self.getAllianceScoreBreakdown(matchNum, 'red')['wallAlgaeCount'] + self.getAllianceScoreBreakdown(matchNum, 'blue')['wallAlgaeCount']

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

    def getAllianceProcessorAlgae(self, matchNum: int, alliance: Literal['blue', 'red']):
        return self.getAllianceScoreBreakdown(matchNum, alliance)['wallAlgaeCount']

    def getAllianceNetAlgae(self, matchNum: int, alliance: Literal['blue', 'red']):
        return self.getAllianceScoreBreakdown(matchNum, alliance)['netAlgaeCount']
    
    def getAllianceTotalGamePieces(self, matchNum, alliance: Literal['blue', 'red']): 
        total = 0
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'auto', 'L1'))
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'auto', 'L2'))
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'auto', 'L3'))
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'auto', 'L4'))
        total += (self.getAllianceNetAlgae(matchNum, alliance))
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'teleop', 'L1'))
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'teleop', 'L2'))
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'teleop', 'L3'))
        total += (self.getAllianceReefForLevel(matchNum, alliance, 'teleop', 'L4'))
        return total

    def getAutoMoved(self, matchNum, alliance, teamNum):
        data = self.getAllianceScoreBreakdown(matchNum, alliance)
        key = 'autoLineRobot' + str(self.getAllianceTeamNums(matchNum, alliance).index(teamNum) + 1)
        return data[key]


class MatchScoutingDataWrapper:
    def __init__(self, redAllianceTeamNums, blueAllianceTeamNums, data):
        self.data = data
        self.redAllianceTeamNums = redAllianceTeamNums
        self.blueAllianceTeamNums = blueAllianceTeamNums
        self.redAllianceData = filter(lambda d: d['teamNum'] in redAllianceTeamNums, data)
        self.blueAllianceData = filter(lambda d: d['teamNum'] in blueAllianceTeamNums, data)
        
    def getAllianceTotalGamePieces(self, alliance: Literal['blue', 'red']):
        total = 0

        if alliance == 'red':
            for data in self.redAllianceData: 
                total += data['autoCoralL1']
                total += data['autoCoralL2']
                total += data['autoCoralL3']
                total += data['autoCoralL4']
                total += data['autoNetAlgae'] + data['teleopNetAlgae']
                total += data['teleopCoralL1']
                total += data['teleopCoralL2']
                total += data['teleopCoralL3']
                total += data['teleopCoralL4']

        else:
            for data in self.blueAllianceData:
                total += data['autoCoralL1']
                total += data['autoCoralL2']
                total += data['autoCoralL3']
                total += data['autoCoralL4']
                total += data['autoNetAlgae'] + data['teleopNetAlgae']
                total += data['teleopCoralL1']
                total += data['teleopCoralL2']
                total += data['teleopCoralL3']
                total += data['teleopCoralL4']

        return total
