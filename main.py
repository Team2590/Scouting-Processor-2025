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
args = parser.parse_args()

# Use command line arguments if provided, otherwise prompt the user
scoutingDataRawFile = args.scoutingDataRaw if args.scoutingDataRaw else input('Enter the file name in the inputs folder: ')
correctionsDataRawFile = args.correctionsDataRaw if args.correctionsDataRaw else None
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

num_corrections = len(correctionsDataRaw)
corrections_index = 2 * lastMatchNum # add corrections to the end of the matrix

A = np.zeros((2 * lastMatchNum + num_corrections, len(scoutNames)))
b = np.zeros(2 * lastMatchNum + num_corrections)

allianceAccuracies = []

uniqueMatchNumbers = sorted(list(set(int(data[0]['matchNum']) for data in scoutingData if data)))

# Initialize a dictionary to count the number of matches per scout
scoutGamePieceCounts = {scout: 0 for scout in scoutNames}

# Todo, something to lower accuracy of a specific scout if they report more than what was scored for the whole alliance
for matchNum in uniqueMatchNumbers:

    index = (matchNum - 1) * 2
    redAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    blueAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'blue')

    for team in redAllianceTeamNums:
        red_correction = next((item for item in correctionsDataRaw if int(item['teamNum']) == team and int(item['matchNum']) == matchNum), None)
        if red_correction:
            break
    for team in blueAllianceTeamNums:
        blue_correction = next((item for item in correctionsDataRaw if int(item['teamNum']) == team and int(item['matchNum']) == matchNum), None)
        if blue_correction:
            break

    blueScoutAutoCoralL1 = 0
    blueScoutAutoCoralL2 = 0
    blueScoutAutoCoralL3 = 0
    blueScoutAutoCoralL4 = 0
    blueScoutTeleopCoralL1 = 0
    blueScoutTeleopCoralL2 = 0
    blueScoutTeleopCoralL3 = 0
    blueScoutTeleopCoralL4 = 0
    blueScoutProcessorAlgae = 0
    redScoutAutoCoralL1 = 0
    redScoutAutoCoralL2 = 0
    redScoutAutoCoralL3 = 0
    redScoutAutoCoralL4 = 0
    redScoutTeleopCoralL1 = 0
    redScoutTeleopCoralL2 = 0
    redScoutTeleopCoralL3 = 0
    redScoutTeleopCoralL4 = 0
    redScoutProcessorAlgae = 0
    for scoutData in scoutingDataRaw:
        if int(scoutData['matchNum']) == matchNum:
            scoutIndex = scoutNames.index(scoutData['scoutName'])
            scoutGamePieceCounts[scoutData['scoutName']] += scoutData['autoCoralL1'] + scoutData['autoCoralL2'] + scoutData['autoCoralL3'] + scoutData['autoCoralL4'] + scoutData['teleopCoralL1'] + scoutData['teleopCoralL2'] + scoutData['teleopCoralL3'] + scoutData['teleopCoralL4'] + scoutData['teleopProcessorAlgae'] + scoutData['autoProcessorAlgae']
            if int(scoutData['teamNum']) in redAllianceTeamNums and (red_correction is None or int(scoutData['teamNum']) != int(red_correction['teamNum'])):
                redScoutAutoCoralL1 += scoutData['autoCoralL1']
                redScoutAutoCoralL2 += scoutData['autoCoralL2']
                redScoutAutoCoralL3 += scoutData['autoCoralL3']
                redScoutAutoCoralL4 += scoutData['autoCoralL4']
                redScoutTeleopCoralL1 += scoutData['teleopCoralL1']
                redScoutTeleopCoralL2 += scoutData['teleopCoralL2']
                redScoutTeleopCoralL3 += scoutData['teleopCoralL3']
                redScoutTeleopCoralL4 += scoutData['teleopCoralL4']
                redScoutProcessorAlgae += scoutData['teleopProcessorAlgae'] + scoutData['autoProcessorAlgae']
            elif int(scoutData['teamNum']) in blueAllianceTeamNums and (blue_correction is None or int(scoutData['teamNum']) != int(blue_correction['teamNum'])):
                blueScoutAutoCoralL1 += scoutData['autoCoralL1']
                blueScoutAutoCoralL2 += scoutData['autoCoralL2']
                blueScoutAutoCoralL3 += scoutData['autoCoralL3']
                blueScoutAutoCoralL4 += scoutData['autoCoralL4']
                blueScoutTeleopCoralL1 += scoutData['teleopCoralL1']
                blueScoutTeleopCoralL2 += scoutData['teleopCoralL2']
                blueScoutTeleopCoralL3 += scoutData['teleopCoralL3']
                blueScoutTeleopCoralL4 += scoutData['teleopCoralL4']
                blueScoutProcessorAlgae += scoutData['teleopProcessorAlgae'] + scoutData['autoProcessorAlgae']
    if blue_correction:
        blueScoutAutoCoralL1 += blue_correction['autoCoralL1']
        blueScoutAutoCoralL2 += blue_correction['autoCoralL2']
        blueScoutAutoCoralL3 += blue_correction['autoCoralL3']
        blueScoutAutoCoralL4 += blue_correction['autoCoralL4']
        blueScoutTeleopCoralL1 += blue_correction['teleopCoralL1']
        blueScoutTeleopCoralL2 += blue_correction['teleopCoralL2']
        blueScoutTeleopCoralL3 += blue_correction['teleopCoralL3']
        blueScoutTeleopCoralL4 += blue_correction['teleopCoralL4']
        blueScoutProcessorAlgae += blue_correction['teleopProcessorAlgae']
    if red_correction:
        redScoutAutoCoralL1 += red_correction['autoCoralL1']
        redScoutAutoCoralL2 += red_correction['autoCoralL2']
        redScoutAutoCoralL3 += red_correction['autoCoralL3']
        redScoutAutoCoralL4 += red_correction['autoCoralL4']
        redScoutTeleopCoralL1 += red_correction['teleopCoralL1']
        redScoutTeleopCoralL2 += red_correction['teleopCoralL2']
        redScoutTeleopCoralL3 += red_correction['teleopCoralL3']
        redScoutTeleopCoralL4 += red_correction['teleopCoralL4']
        redScoutProcessorAlgae += red_correction['teleopProcessorAlgae']
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
    blueOverallAccuracy = (blueAccuracyAutoCoralL1 + blueAccuracyAutoCoralL2 + blueAccuracyAutoCoralL3 + blueAccuracyAutoCoralL4 + blueAccuracyTeleopCoralL1 + blueAccuracyTeleopCoralL2 + blueAccuracyTeleopCoralL3 + blueAccuracyTeleopCoralL4 + blueAccuracyProcessorAlgae)
    redOverallAccuracy = (redAccuracyAutoCoralL1 + redAccuracyAutoCoralL2 + redAccuracyAutoCoralL3 + redAccuracyAutoCoralL4 + redAccuracyTeleopCoralL1 + redAccuracyTeleopCoralL2 + redAccuracyTeleopCoralL3 + redAccuracyTeleopCoralL4 + redAccuracyProcessorAlgae)

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

    b[index] = blueOverallAccuracy / totalBlueGamePieces
    b[index+1] = redOverallAccuracy / totalRedGamePieces

    for scoutData in scoutingDataRaw:
        if int(scoutData['matchNum']) == matchNum:
            scoutIndex = scoutNames.index(scoutData['scoutName'])
            totalGamePieces = totalRedGamePieces if int(scoutData['teamNum']) in redAllianceTeamNums else totalBlueGamePieces

            if (red_correction is None or int(scoutData['teamNum']) != int(red_correction['teamNum'])) and (blue_correction is None or int(scoutData['teamNum']) != int(blue_correction['teamNum'])):

                indexOffset = 1 if int(scoutData['teamNum']) in redAllianceTeamNums else 0

                A[index+indexOffset, scoutIndex] = 1
            elif (red_correction and int(scoutData['teamNum']) == int(red_correction['teamNum'])) or (blue_correction and int(scoutData['teamNum']) == int(blue_correction['teamNum'])):
                correction = red_correction if int(scoutData['teamNum']) in redAllianceTeamNums else blue_correction

                b[corrections_index] += abs(scoutData['autoCoralL1'] - correction['autoCoralL1']) / totalGamePieces
                b[corrections_index] += abs(scoutData['autoCoralL2'] - correction['autoCoralL2']) / totalGamePieces
                b[corrections_index] += abs(scoutData['autoCoralL3'] - correction['autoCoralL3']) / totalGamePieces
                b[corrections_index] += abs(scoutData['autoCoralL4'] - correction['autoCoralL4']) / totalGamePieces
                b[corrections_index] += abs(scoutData['teleopCoralL1'] - correction['teleopCoralL1']) / totalGamePieces
                b[corrections_index] += abs(scoutData['teleopCoralL2'] - correction['teleopCoralL2']) / totalGamePieces
                b[corrections_index] += abs(scoutData['teleopCoralL3'] - correction['teleopCoralL3']) / totalGamePieces
                b[corrections_index] += abs(scoutData['teleopCoralL4'] - correction['teleopCoralL4']) / totalGamePieces
                b[corrections_index] += abs(scoutData['teleopProcessorAlgae'] - correction['teleopProcessorAlgae']) / totalGamePieces
                b[corrections_index] += abs(scoutData['autoProcessorAlgae'] - correction['autoProcessorAlgae']) / totalGamePieces

                A[corrections_index, scoutIndex] = 1
                corrections_index += 1

x, residuals = optimize.nnls(A, b) # nnls is the non-negative least squares algorithm
#x, residuals, rank, singular_values = np.linalg.lstsq(A, b, rcond=None) # lstsq is the least squares algorithm, but it allows negative values

coefficients = x.flatten()

scouterAccuraciesEstimated = []

for i in range(len(scoutNames)): 
    acc = 100 - round(coefficients[i], 4) * 100
    scouterAccuraciesEstimated.append({'name': scoutNames[i], 'accuracy': acc, 'gamePieceCount': scoutGamePieceCounts[scoutNames[i]]})

scouterAccuraciesEstimated.sort(key=lambda x: (x['accuracy'], x['gamePieceCount']))

for estimate in scouterAccuraciesEstimated:
    print(str(estimate['name']) + ':', str(round(estimate['accuracy'], 2)) + '%', 'with ' + str(estimate['gamePieceCount']) + ' game pieces')

medianAccuracy = np.median(list(abs(estimate['accuracy']) for estimate in scouterAccuraciesEstimated)).round(2)

print('Median scout accuracy:', str(medianAccuracy) + '%')

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
    if tbaWrapper.getClimbLevel(matchNum, alliance, teamNum): autoMoved = 1

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

sortedAllianceAccuracies = sorted(allianceAccuracies, key=lambda x: x["missedGamePieces"], reverse=True)

worst = min(10, len(sortedAllianceAccuracies))

for i in range(worst):
    matchNum = sortedAllianceAccuracies[i]['matchNum']
    print('Match ' + str(matchNum) + " " + sortedAllianceAccuracies[i]['alliance'] + ' alliance has ' + str(sortedAllianceAccuracies[i]['missedGamePieces']) + ' missed game pieces')
    scoutingDataForMatch = filter(lambda d: d['matchNum'] == matchNum, scoutingDataRaw)
    names = []
    for data in scoutingDataForMatch: names.append(data['scoutName'])
    filteredAccuracies = list(filter(lambda estimate: estimate['name'] in names, scouterAccuraciesEstimated))

    sortedAccuracies = sorted(filteredAccuracies, key=lambda estimate: estimate['accuracy'])

    print('Likely wrong: ' + str(sortedAccuracies[0]))

exportToCSV(exportData, './outputs/' + exportFileName)
