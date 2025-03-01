from wrappers import TbaWrapper, MatchScoutingDataWrapper
from utils import correctZerosBothAlliances, getScoutNames, getLastMatchNum, scoutingDataTo2dArray, correctZerosAlliance, correctZerosScouting, exportToCSV
from dotenv import load_dotenv # type: ignore
import numpy as np # type: ignore
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

A = np.zeros((17 * lastMatchNum, len(scoutNames)))
b = np.zeros(17 * lastMatchNum)

allianceAccuracies = []

uniqueMatchNumbers = sorted(list(set(int(data[0]['matchNum']) for data in scoutingData if data)))
for matchNum in uniqueMatchNumbers:

    index = (matchNum - 1) * 17
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

#    matchScoutingDataWrapper = MatchScoutingDataWrapper(redAllianceTeamNums, blueAllianceTeamNums, data)
#    blueAllianceAccuracy = round(matchScoutingDataWrapper.getAllianceTotalGamePieces('blue') / tbaWrapper.getAllianceTotalGamePieces(matchNum, 'blue')  * 100, 2)
#    redAllianceAccuracy = round(matchScoutingDataWrapper.getAllianceTotalGamePieces('red') / tbaWrapper.getAllianceTotalGamePieces(matchNum, 'red') * 100, 2)

#    allianceAccuracies.append({'red': redAllianceAccuracy, 'blue': blueAllianceAccuracy, 'matchNum': matchNum})

    b[index] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L1')) - (blue_correction['autoCoralL1'] if blue_correction else 0)
    b[index+1] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L2')) - (blue_correction['autoCoralL2'] if blue_correction else 0)
    b[index+2] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L3')) - (blue_correction['autoCoralL3'] if blue_correction else 0)
    b[index+3] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L4')) - (blue_correction['autoCoralL4'] if blue_correction else 0)
    b[index+4] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L1')) - (blue_correction['teleopCoralL1'] if blue_correction else 0)
    b[index+5] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L2')) - (blue_correction['teleopCoralL2'] if blue_correction else 0)
    b[index+6] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L3')) - (blue_correction['teleopCoralL3'] if blue_correction else 0)
    b[index+7] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L4')) - (blue_correction['teleopCoralL4'] if blue_correction else 0)
    
    b[index+8] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L1')) - (red_correction['autoCoralL1'] if red_correction else 0)
    b[index+9] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L2')) - (red_correction['autoCoralL2'] if red_correction else 0)
    b[index+10] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L3')) - (red_correction['autoCoralL3'] if red_correction else 0)
    b[index+11] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L4')) - (red_correction['autoCoralL4'] if red_correction else 0)
    b[index+12] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L1')) - (red_correction['teleopCoralL1'] if red_correction else 0)
    b[index+13] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L2')) - (red_correction['teleopCoralL2'] if red_correction else 0)
    b[index+14] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L3')) - (red_correction['teleopCoralL3'] if red_correction else 0)
    b[index+15] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L4')) - (red_correction['teleopCoralL4'] if red_correction else 0)
    
    b[index+16] = (
        correctZerosBothAlliances(tbaWrapper.getTotalAlgaeProcessor(matchNum))
        - (red_correction['autoProcessorAlgae'] + red_correction['teleopProcessorAlgae'] if red_correction else 0)
        - (blue_correction['autoProcessorAlgae'] + blue_correction['teleopProcessorAlgae'] if blue_correction else 0)
    )
    
    for scoutData in scoutingDataRaw:
        if int(scoutData['matchNum']) == matchNum:
            scoutIndex = scoutNames.index(scoutData['scoutName'])

            A[index+16, scoutIndex] = correctZerosScouting(b[index+16], scoutData['autoProcessorAlgae'] + scoutData['teleopProcessorAlgae'])

            indexOffset = 8 if int(scoutData['teamNum']) in redAllianceTeamNums else 0

            A[index+indexOffset, scoutIndex] = correctZerosScouting(b[index], scoutData['autoCoralL1'])
            A[index+indexOffset+1, scoutIndex] = correctZerosScouting(b[index+1], scoutData['autoCoralL2'])
            A[index+indexOffset+2, scoutIndex] = correctZerosScouting(b[index+2], scoutData['autoCoralL3'])
            A[index+indexOffset+3, scoutIndex] = correctZerosScouting(b[index+3], scoutData['autoCoralL4'])
            A[index+indexOffset+4, scoutIndex] = correctZerosScouting(b[index+5], scoutData['teleopCoralL1'])
            A[index+indexOffset+5, scoutIndex] = correctZerosScouting(b[index+6], scoutData['teleopCoralL2'])
            A[index+indexOffset+6, scoutIndex] = correctZerosScouting(b[index+7], scoutData['teleopCoralL3'])
            A[index+indexOffset+7, scoutIndex] = correctZerosScouting(b[index+8], scoutData['teleopCoralL4'])

x, residuals, rank, singular_values = np.linalg.lstsq(A, b, rcond=None) 
coefficients = x.flatten()

scouterAccuraciesEstimated = []

for i in range(len(scoutNames)): 
    acc = round(coefficients[i], 4) * 100
    if acc > 100: acc = -acc + 200
    scouterAccuraciesEstimated.append({'name': scoutNames[i], 'accuracy': acc})

scouterAccuraciesEstimated.sort(key=lambda x: x['accuracy'])

for estimate in scouterAccuraciesEstimated:
    print(str(estimate['name']) + ':', str(estimate['accuracy'].round(2)) + '%')

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

    data = next((d for d in scoutingDataRaw if int(d['teamNum']) == teamNum and int(d['matchNum']) == matchNum), None)
    if data is None:
        data = next((d for d in correctionsDataRaw if int(d['teamNum']) == teamNum and int(d['matchNum']) == matchNum), None)

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

sortedAllianceAccuracies = sorted(allianceAccuracies, key=lambda accuracies: accuracies['red'] + accuracies['blue'])

worst = min(5, len(sortedAllianceAccuracies))

for i in range(worst):
    matchNum = sortedAllianceAccuracies[i]['matchNum']
    print('Match ' + str(matchNum))
    scoutingDataForMatch = filter(lambda d: d['matchNum'] == matchNum, scoutingDataRaw)
    names = []
    for data in scoutingDataForMatch: names.append(data['scoutName'])
    filteredAccuracies = list(filter(lambda estimate: estimate['name'] in names, scouterAccuraciesEstimated))

    sortedAccuracies = sorted(filteredAccuracies, key=lambda estimate: estimate['accuracy'])

    print('Likely wrong: ' + str(sortedAccuracies[0]))

exportToCSV(exportData, './outputs/' + exportFileName)