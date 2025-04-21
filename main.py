from wrappers import TbaWrapper, MatchScoutingDataWrapper
from utils import correctZerosBothAlliances, getScoutNames, getLastMatchNum, scoutingDataTo2dArray, correctZerosAlliance, correctZerosScouting, exportToCSV
from dotenv import load_dotenv # type: ignore
import numpy as np # type: ignore
import scipy.optimize as optimize # type: ignore
import os
import json
import argparse

load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser(description='Process scouting data.')
parser.add_argument('--scoutingDataRaw', type=str, help='The file name in the inputs folder')
parser.add_argument('--correctionsDataRaw', type=str, help='The corrections file name in the inputs folder (optional)')
parser.add_argument('--exportFileName', type=str, help='The file name you want in the outputs folder (add .csv)')
parser.add_argument('--compKey', type=str, help='The competition key')
parser.add_argument('--printAccuracies', type=bool, help='Whether to print the accuracies of each scout')
args = parser.parse_args()

# Use command line arguments if provided, otherwise prompt the user
scoutingDataRawFile = args.scoutingDataRaw if args.scoutingDataRaw else input('Enter the file name in the inputs folder: ')
correctionsDataRawFile = args.correctionsDataRaw if args.correctionsDataRaw else input('Enter the corrections file name in the inputs folder: ')
exportFileName = args.exportFileName if args.exportFileName else input('Enter the file name you want in the outputs folder (add .csv): ')
compKey = args.compKey if args.compKey else input("Enter the competition key: ")

scoutingDataRaw = json.load(open('./inputs/' + scoutingDataRawFile))
correctionsDataRaw = json.load(open('./inputs/' + correctionsDataRawFile)) if correctionsDataRawFile else []
tbaWrapper = TbaWrapper(compKey, os.getenv("TBA_KEY"))

scoutNames = getScoutNames(scoutingDataRaw)
lastMatchNum = int(getLastMatchNum(scoutingDataRaw))

scoutingData = scoutingDataTo2dArray(scoutingDataRaw, lastMatchNum)

# Remove duplicates from scoutingDataRaw
unique_scouting_data = []
seen_combinations = set()

for data in scoutingDataRaw:
    team_match = (int(data['teamNum']), int(data['matchNum']))
    if team_match not in seen_combinations:
        unique_scouting_data.append(data)
        seen_combinations.add(team_match)

scoutingDataRaw = unique_scouting_data

exportData = []

team_match_combinations = []

for data in correctionsDataRaw:
    team_match_combinations.append((int(data['teamNum']), int(data['matchNum'])))

for data in scoutingDataRaw:
    team_match_combinations.append((int(data['teamNum']), int(data['matchNum'])))

team_match_combinations = sorted(list(set(team_match_combinations)), key=lambda x: (x[1], x[0]))

for team_match in team_match_combinations:
    teamNum = team_match[0]
    matchNum = team_match[1]

    data = next((d for d in correctionsDataRaw if int(d['teamNum']) == teamNum and int(d['matchNum']) == matchNum), None)
    if data is None:
        data = next((d for d in scoutingDataRaw if int(d['teamNum']) == teamNum and int(d['matchNum']) == matchNum), None)

    redAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    blueAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'blue')

    alliance = ''
    if teamNum in redAllianceTeamNums: alliance = 'red'
    if teamNum in blueAllianceTeamNums: alliance = 'blue'

    climbLvl = tbaWrapper.getClimbLevel(matchNum, alliance, teamNum)

    parked = 0
    shallow = 0
    deep = 0
    if climbLvl == 'Parked': parked = 1
    if climbLvl == 'ShallowCage': shallow = 1
    if climbLvl == 'DeepCage': deep = 1

    driverStationPos = 0
    if alliance == 'red': driverStationPos = tbaWrapper.getAllianceTeamNums(matchNum, 'red').index(teamNum) + 1
    else: driverStationPos = tbaWrapper.getAllianceTeamNums(matchNum, 'blue').index(teamNum) + 1

    autoMoved = 0
    if tbaWrapper.getAutoMoved(matchNum, alliance, teamNum) == 'Yes': autoMoved = 1

    combinedData = {}
    combinedData['id'] = data['id']
    combinedData['matchNum'] = data['matchNum']
    combinedData['teamNum'] = teamNum
    combinedData['scoutName'] = data['scoutName']
    combinedData['driverStationPos'] = driverStationPos
    combinedData['startingPos'] = data['startingPos']
    combinedData['autoCoralL1'] = data['autoCoralL1']
    combinedData['autoCoralL2'] = data['autoCoralL2']
    combinedData['autoCoralL3'] = data['autoCoralL3']
    combinedData['autoCoralL4'] = data['autoCoralL4']
    combinedData['autoAlgaeRemovedFromReef'] = data['autoAlgaeRemovedFromReef']
    combinedData['autoProcessorAlgae'] = data['autoProcessorAlgae']
    combinedData['autoNetAlgae'] = data['autoNetAlgae']
    combinedData['autoMoved'] = autoMoved
    combinedData['teleopCoralL1'] = data['teleopCoralL1']
    combinedData['teleopCoralL2'] = data['teleopCoralL2']
    combinedData['teleopCoralL3'] = data['teleopCoralL3']
    combinedData['teleopCoralL4'] = data['teleopCoralL4']
    combinedData['teleopAlgaeRemovedFromReef'] = data['teleopAlgaeRemovedFromReef']
    combinedData['teleopProcessorAlgae'] = data['teleopProcessorAlgae']
    combinedData['teleopNetAlgae'] = data['teleopNetAlgae']
    combinedData['parkClimb'] = parked
    combinedData['shallowClimb'] = shallow
    combinedData['deepClimb'] = deep
    combinedData['timeTakenToClimb'] = data['timeTakenToClimb']
    combinedData['lostComms'] = data['lostComms']
    exportData.append(combinedData)

teamGamePieceCounts = {}

for data in exportData:
    teamNum = data['teamNum']
    totalGamePieces = (int(data['autoCoralL1']) + int(data['autoCoralL2']) + int(data['autoCoralL3']) + int(data['autoCoralL4']) +
                      int(data['teleopCoralL1']) + int(data['teleopCoralL2']) + int(data['teleopCoralL3']) + int(data['teleopCoralL4']) +
                       int(data['teleopProcessorAlgae']) + int(data['autoProcessorAlgae']))
    if teamNum not in teamGamePieceCounts:
        teamGamePieceCounts[teamNum] = {'totalGamePieces': 0, 'matches': 0}
    teamGamePieceCounts[teamNum]['totalGamePieces'] += totalGamePieces
    teamGamePieceCounts[teamNum]['matches'] += 1

averageGamePiecesPerTeam = {teamNum: max(counts['totalGamePieces'] / counts['matches'], 1) for teamNum, counts in teamGamePieceCounts.items()}


num_corrections = len(correctionsDataRaw)
corrections_index = 2 * lastMatchNum # add corrections to the end of the matrix

A = np.zeros((2 * lastMatchNum + num_corrections, len(scoutNames)))
b = np.zeros(2 * lastMatchNum + num_corrections)

allianceAccuracies = []

uniqueMatchNumbers = sorted(list(set(int(data[0]['matchNum']) for data in scoutingData if data)))

# print missing data
missingMatches = set()
for matchNum in uniqueMatchNumbers:
    redTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    blueTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'blue')

    for teamNum in redTeamNums + blueTeamNums:
        alliance = "red" if teamNum in redTeamNums else "blue"

        inScoutingData = any(int(entry['matchNum']) == matchNum and int(entry['teamNum']) == teamNum for entry in scoutingDataRaw)
        inCorrectionsData = any(int(entry['matchNum']) == matchNum and int(entry['teamNum']) == teamNum for entry in correctionsDataRaw)

        if not (inScoutingData or inCorrectionsData):
            missingMatches.add(matchNum)
            print(f"Missing data for Match {matchNum}, Team {teamNum} (Alliance: {alliance})")
print()

# Initialize a dictionary to count the number of matches per scout
scoutGamePieceCounts = {scout: 0 for scout in scoutNames}

# Todo, something to lower accuracy of a specific scout if they report more than what was scored for the whole alliance
for matchNum in uniqueMatchNumbers:

    if matchNum in missingMatches:
        continue

    index = (matchNum - 1) * 2
    redAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    blueAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'blue')

    red_corrections = {}
    blue_corrections = {}

    for correction in correctionsDataRaw:
        if int(correction['matchNum']) == matchNum and int(correction['teamNum']) in redAllianceTeamNums:
            red_corrections[int(correction['teamNum'])] = correction
        elif int(correction['matchNum']) == matchNum and int(correction['teamNum']) in blueAllianceTeamNums:
            blue_corrections[int(correction['teamNum'])] = correction

    blueScoutAutoCoralL1 = 0
    blueScoutAutoCoralL2 = 0
    blueScoutAutoCoralL3 = 0
    blueScoutAutoCoralL4 = 0
    blueScoutTeleopCoralL1 = 0
    blueScoutTeleopCoralL2 = 0
    blueScoutTeleopCoralL3 = 0
    blueScoutTeleopCoralL4 = 0
    blueScoutProcessorAlgae = 0
    blueScoutNetAlgae = 0
    redScoutAutoCoralL1 = 0
    redScoutAutoCoralL2 = 0
    redScoutAutoCoralL3 = 0
    redScoutAutoCoralL4 = 0
    redScoutTeleopCoralL1 = 0
    redScoutTeleopCoralL2 = 0
    redScoutTeleopCoralL3 = 0
    redScoutTeleopCoralL4 = 0
    redScoutProcessorAlgae = 0
    redScoutNetAlgae = 0
    for scoutData in scoutingDataRaw:
        if int(scoutData['matchNum']) == matchNum:
            scoutIndex = scoutNames.index(scoutData['scoutName'])
            scoutGamePieceCounts[scoutData['scoutName']] += int(scoutData['autoCoralL1']) + int(scoutData['autoCoralL2']) + int(scoutData['autoCoralL3']) + int(scoutData['autoCoralL4']) + int(scoutData['teleopCoralL1']) + int(scoutData['teleopCoralL2']) + int(scoutData['teleopCoralL3']) + int(scoutData['teleopCoralL4']) + int(scoutData['teleopProcessorAlgae']) + int(scoutData['autoProcessorAlgae'])
            if int(scoutData['teamNum']) in redAllianceTeamNums and red_corrections.get(int(scoutData['teamNum'])) is None:
                redScoutAutoCoralL1 += int(scoutData['autoCoralL1'])
                redScoutAutoCoralL2 += int(scoutData['autoCoralL2'])
                redScoutAutoCoralL3 += int(scoutData['autoCoralL3'])
                redScoutAutoCoralL4 += int(scoutData['autoCoralL4'])
                redScoutTeleopCoralL1 += int(scoutData['teleopCoralL1'])
                redScoutTeleopCoralL2 += int(scoutData['teleopCoralL2'])
                redScoutTeleopCoralL3 += int(scoutData['teleopCoralL3'])
                redScoutTeleopCoralL4 += int(scoutData['teleopCoralL4'])
                redScoutProcessorAlgae += int(scoutData['teleopProcessorAlgae']) + int(scoutData['autoProcessorAlgae'])
                redScoutNetAlgae += int(scoutData['teleopNetAlgae']) + int(scoutData['autoNetAlgae'])
            elif int(scoutData['teamNum']) in blueAllianceTeamNums and blue_corrections.get(int(scoutData['teamNum'])) is None:
                blueScoutAutoCoralL1 += int(scoutData['autoCoralL1'])
                blueScoutAutoCoralL2 += int(scoutData['autoCoralL2'])
                blueScoutAutoCoralL3 += int(scoutData['autoCoralL3'])
                blueScoutAutoCoralL4 += int(scoutData['autoCoralL4'])
                blueScoutTeleopCoralL1 += int(scoutData['teleopCoralL1'])
                blueScoutTeleopCoralL2 += int(scoutData['teleopCoralL2'])
                blueScoutTeleopCoralL3 += int(scoutData['teleopCoralL3'])
                blueScoutTeleopCoralL4 += int(scoutData['teleopCoralL4'])
                blueScoutProcessorAlgae += int(scoutData['teleopProcessorAlgae']) + int(scoutData['autoProcessorAlgae'])
                blueScoutNetAlgae += int(scoutData['teleopNetAlgae']) + int(scoutData['autoNetAlgae'])
    
    for correction in blue_corrections.values():
        blueScoutAutoCoralL1 += correction['autoCoralL1']
        blueScoutAutoCoralL2 += correction['autoCoralL2']
        blueScoutAutoCoralL3 += correction['autoCoralL3']
        blueScoutAutoCoralL4 += correction['autoCoralL4']
        blueScoutTeleopCoralL1 += correction['teleopCoralL1']
        blueScoutTeleopCoralL2 += correction['teleopCoralL2']
        blueScoutTeleopCoralL3 += correction['teleopCoralL3']
        blueScoutTeleopCoralL4 += correction['teleopCoralL4']
        blueScoutProcessorAlgae += correction['teleopProcessorAlgae']
        blueScoutNetAlgae += correction['teleopNetAlgae'] + correction['autoNetAlgae']

    for correction in red_corrections.values():
        redScoutAutoCoralL1 += correction['autoCoralL1']
        redScoutAutoCoralL2 += correction['autoCoralL2']
        redScoutAutoCoralL3 += correction['autoCoralL3']
        redScoutAutoCoralL4 += correction['autoCoralL4']
        redScoutTeleopCoralL1 += correction['teleopCoralL1']
        redScoutTeleopCoralL2 += correction['teleopCoralL2']
        redScoutTeleopCoralL3 += correction['teleopCoralL3']
        redScoutTeleopCoralL4 += correction['teleopCoralL4']
        redScoutProcessorAlgae += correction['teleopProcessorAlgae']
        redScoutNetAlgae += correction['teleopNetAlgae'] + correction['autoNetAlgae']
   
    blueAccuracyAutoCoralL1 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L1') - blueScoutAutoCoralL1)
    blueAccuracyAutoCoralL2 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L2') - blueScoutAutoCoralL2)
    blueAccuracyAutoCoralL3 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L3') - blueScoutAutoCoralL3)
    blueAccuracyAutoCoralL4 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L4') - blueScoutAutoCoralL4)
    blueAccuracyTeleopCoralL1 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L1') - blueScoutTeleopCoralL1)
    blueAccuracyTeleopCoralL2 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L2') - blueScoutTeleopCoralL2)
    blueAccuracyTeleopCoralL3 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L3') - blueScoutTeleopCoralL3)
    blueAccuracyTeleopCoralL4 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L4') - blueScoutTeleopCoralL4)
    blueAccuracyProcessorAlgae = abs(tbaWrapper.getAllianceProcessorAlgae(matchNum, 'blue') - blueScoutProcessorAlgae)
    redAccuracyAutoCoralL1 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L1') - redScoutAutoCoralL1)
    redAccuracyAutoCoralL2 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L2') - redScoutAutoCoralL2)
    redAccuracyAutoCoralL3 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L3') - redScoutAutoCoralL3)
    redAccuracyAutoCoralL4 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L4') - redScoutAutoCoralL4)
    redAccuracyTeleopCoralL1 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L1') - redScoutTeleopCoralL1)
    redAccuracyTeleopCoralL2 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L2') - redScoutTeleopCoralL2)
    redAccuracyTeleopCoralL3 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L3') - redScoutTeleopCoralL3)
    redAccuracyTeleopCoralL4 = abs(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L4') - redScoutTeleopCoralL4)
    redAccuracyProcessorAlgae = abs(tbaWrapper.getAllianceProcessorAlgae(matchNum, 'red') - redScoutProcessorAlgae)

    # only count net algae for accuracy if the other alliance didn't score any processor algae
    if tbaWrapper.getAllianceProcessorAlgae(matchNum, 'blue') == 0:
        redAccuracyNetAlgae = abs(tbaWrapper.getAllianceNetAlgae(matchNum, 'red') - redScoutNetAlgae)
        countRedNetAlgae = 1
    else:
        redAccuracyNetAlgae = 0
        countRedNetAlgae = 0
    if tbaWrapper.getAllianceProcessorAlgae(matchNum, 'red') == 0:
        blueAccuracyNetAlgae = abs(tbaWrapper.getAllianceNetAlgae(matchNum, 'blue') - blueScoutNetAlgae)
        countBlueNetAlgae = 1
    else:
        blueAccuracyNetAlgae = 0
        countBlueNetAlgae = 0

    blueOverallAccuracy = (blueAccuracyAutoCoralL1 + blueAccuracyAutoCoralL2 + blueAccuracyAutoCoralL3 + blueAccuracyAutoCoralL4 + blueAccuracyTeleopCoralL1 + blueAccuracyTeleopCoralL2 + blueAccuracyTeleopCoralL3 + blueAccuracyTeleopCoralL4 + blueAccuracyProcessorAlgae + blueAccuracyNetAlgae)
    redOverallAccuracy = (redAccuracyAutoCoralL1 + redAccuracyAutoCoralL2 + redAccuracyAutoCoralL3 + redAccuracyAutoCoralL4 + redAccuracyTeleopCoralL1 + redAccuracyTeleopCoralL2 + redAccuracyTeleopCoralL3 + redAccuracyTeleopCoralL4 + redAccuracyProcessorAlgae + redAccuracyNetAlgae)

    allianceAccuracies.append({
        'matchNum': matchNum,
        'alliance': 'blue',
        'missedGamePieces': blueOverallAccuracy,
    })
    allianceAccuracies.append({
        'matchNum': matchNum,
        'alliance': 'red',
        'missedGamePieces': redOverallAccuracy,
    })

    totalBlueGamePieces = tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L1') + tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L2') + tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L3') + tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L4') + tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L1') + tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L2') + tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L3') + tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L4') + tbaWrapper.getAllianceProcessorAlgae(matchNum, 'blue')
    totalRedGamePieces = tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L1') + tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L2') + tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L3') + tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L4') + tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L1') + tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L2') + tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L3') + tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L4') + tbaWrapper.getAllianceProcessorAlgae(matchNum, 'red')

    if countBlueNetAlgae == 1:
        totalBlueGamePieces += tbaWrapper.getAllianceNetAlgae(matchNum, 'blue')
    if countRedNetAlgae == 1:
        totalRedGamePieces += tbaWrapper.getAllianceNetAlgae(matchNum, 'red')

    blueAllianceAverageGamePieces = sum(averageGamePiecesPerTeam[team] for team in blueAllianceTeamNums)
    redAllianceAverageGamePieces = sum(averageGamePiecesPerTeam[team] for team in redAllianceTeamNums)

    b[index] = blueOverallAccuracy / totalBlueGamePieces * blueAllianceAverageGamePieces / 3 # Weighted by how many game pieces the alliance would typically score, so more important robots are weighted more
    b[index+1] = redOverallAccuracy / totalRedGamePieces * redAllianceAverageGamePieces / 3

    for scoutData in scoutingDataRaw:
        if int(scoutData['matchNum']) == matchNum:
            scoutIndex = scoutNames.index(scoutData['scoutName'])
            totalGamePieces = totalRedGamePieces if int(scoutData['teamNum']) in redAllianceTeamNums else totalBlueGamePieces
            
            correction = None

            for correctionData in red_corrections.values():
                if int(correctionData['teamNum']) == int(scoutData['teamNum']):
                    correction = correctionData

            for correctionData in blue_corrections.values():
                if int(correctionData['teamNum']) == int(scoutData['teamNum']):
                    correction = correctionData

            if not correction:
                indexOffset = 1 if int(scoutData['teamNum']) in redAllianceTeamNums else 0
                A[index+indexOffset, scoutIndex] = averageGamePiecesPerTeam[int(scoutData["teamNum"])] # Weighted by how many game pieces the robot typically scores, so more important robots are weighted more
            else: 
                b[corrections_index] += abs(int(scoutData['autoCoralL1']) - int(correction['autoCoralL1'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['autoCoralL2']) - int(correction['autoCoralL2'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['autoCoralL3']) - int(correction['autoCoralL3'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['autoCoralL4']) - int(correction['autoCoralL4'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['teleopCoralL1']) - int(correction['teleopCoralL1'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['teleopCoralL2']) - int(correction['teleopCoralL2'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['teleopCoralL3']) - int(correction['teleopCoralL3'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['teleopCoralL4']) - int(correction['teleopCoralL4'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['teleopProcessorAlgae']) - int(correction['teleopProcessorAlgae'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['autoProcessorAlgae']) - int(correction['autoProcessorAlgae'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['autoNetAlgae']) - int(correction['autoNetAlgae'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                b[corrections_index] += abs(int(scoutData['teleopNetAlgae']) - int(correction['teleopNetAlgae'])) / totalGamePieces * averageGamePiecesPerTeam[int(scoutData["teamNum"])]
                A[corrections_index, scoutIndex] = averageGamePiecesPerTeam[int(scoutData["teamNum"])] # Weighted by how many game pieces the robot typically scores, so more important robots are weighted more
                corrections_index += 1

x, residuals = optimize.nnls(A, b) # nnls is the non-negative least squares algorithm
#x, residuals, rank, singular_values = np.linalg.lstsq(A, b, rcond=None) # lstsq is the least squares algorithm, but it allows negative values

coefficients = x.flatten()

scouterAccuraciesEstimated = []

for i in range(len(scoutNames)): 
    game_piece_count = scoutGamePieceCounts[scoutNames[i]]

    if game_piece_count == 0:
        acc = 100 - round(coefficients[i], 4) * 100
    else:
        acc = 100 - round(coefficients[i], 4) * 100 - 1 / game_piece_count
    scouterAccuraciesEstimated.append({'name': scoutNames[i], 'accuracy': acc, 'gamePieceCount': scoutGamePieceCounts[scoutNames[i]]})

scouterAccuraciesEstimated.sort(key=lambda x: (x['accuracy'], x['gamePieceCount']))

if args.printAccuracies:
    for estimate in scouterAccuraciesEstimated:
        print(str(estimate['name']) + ':', str(round(estimate['accuracy'], 2)) + '%', 'with ' + str(estimate['gamePieceCount']) + ' game pieces')

medianAccuracy = np.median(list(abs(estimate['accuracy']) for estimate in scouterAccuraciesEstimated)).round(2)

print('Median scout accuracy:', str(medianAccuracy) + '%')

print() # for formatting

sortedAllianceAccuracies = sorted(allianceAccuracies, key=lambda x: x["missedGamePieces"], reverse=True)

worst = min(10, len(sortedAllianceAccuracies))

for i in range(worst):
    matchNum = sortedAllianceAccuracies[i]['matchNum']
    alliance = sortedAllianceAccuracies[i]['alliance']
    allianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, alliance)
    print('Match ' + str(matchNum) + " " + alliance + ' alliance has ' + str(sortedAllianceAccuracies[i]['missedGamePieces']) + ' missed game pieces')
    scoutingDataForMatch = list(filter(lambda d: d['matchNum'] == matchNum and d['teamNum'] in allianceTeamNums, scoutingDataRaw))
    names = []
    for data in scoutingDataForMatch: names.append(data['scoutName'])
    if len(names) == 0: continue
    filteredAccuracies = list(filter(lambda estimate: estimate['name'] in names, scouterAccuraciesEstimated))

    sortedAccuracies = sorted(filteredAccuracies, key=lambda estimate: estimate['accuracy'])

    redAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')

    leastAccurate = sortedAccuracies[0]

    teamNum = list(filter(lambda x: x['scoutName'] == leastAccurate['name'], scoutingDataForMatch))[0]['teamNum']

    name = str(sortedAccuracies[0]['name'])

    if (teamNum in redAllianceTeamNums):
        print('Incorrect data from Match ' + str(matchNum) + ', likely from Team ' + str(teamNum) + ' (Alliance: red) scouted by ' + name)
    else:
        print('Incorrect data from Match ' + str(matchNum) + ', likely from Team ' + str(teamNum) + ' (Alliance: blue) scouted by ' + name)

exportToCSV(exportData, './outputs/' + exportFileName)
