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
parser.add_argument('--exportFileName', type=str, help='The file name you want in the outputs folder (add .csv)')
parser.add_argument('--compKey', type=str, help='The competition key')
args = parser.parse_args()

# Use command line arguments if provided, otherwise prompt the user
scoutingDataRawFile = args.scoutingDataRaw if args.scoutingDataRaw else input('Enter the file name in the inputs folder: ')
exportFileName = args.exportFileName if args.exportFileName else input('Enter the file name you want in the outputs folder (add .csv): ')
compKey = args.compKey if args.compKey else input("Enter the competition key: ")

scoutingDataRaw = json.load(open('./inputs/' + scoutingDataRawFile))
tbaWrapper = TbaWrapper(compKey, os.getenv("TBA_KEY"))

scoutNames = getScoutNames(scoutingDataRaw)
lastMatchNum = int(getLastMatchNum(scoutingDataRaw))

scoutingData = scoutingDataTo2dArray(scoutingDataRaw, lastMatchNum)

A = np.zeros((19 * lastMatchNum, len(scoutNames)))
b = np.zeros(19 * lastMatchNum)

allianceAccuracies = []

for data in scoutingData:
    try: 
        data[0]
    except:
        continue  

    matchNum = int(data[0]['matchNum'])
    index = (matchNum - 1) * 8
    redAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    blueAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'blue')
    
    matchScoutingDataWrapper = MatchScoutingDataWrapper(redAllianceTeamNums, blueAllianceTeamNums, data)
    blueAllianceAccuracy = round(matchScoutingDataWrapper.getAllianceTotalGamePieces('blue') / tbaWrapper.getAllianceTotalGamePieces(matchNum, 'blue')  * 100, 2)
    redAllianceAccuracy = round(matchScoutingDataWrapper.getAllianceTotalGamePieces('red') / tbaWrapper.getAllianceTotalGamePieces(matchNum, 'red') * 100, 2)

    allianceAccuracies.append({'red': redAllianceAccuracy, 'blue': blueAllianceAccuracy, 'matchNum': matchNum})

    b[index] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L1'))
    b[index+1] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L2'))
    b[index+2] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L3'))
    b[index+3] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'auto', 'L4'))
    b[index+4] = correctZerosAlliance(tbaWrapper.getAllianceNetAlgae(matchNum, 'blue'))
    b[index+5] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L1'))
    b[index+6] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L2'))
    b[index+7] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L3'))
    b[index+8] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'blue', 'teleop', 'L4'))
    
    b[index+9] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L1'))
    b[index+10] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L2'))
    b[index+11] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L3'))
    b[index+12] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'auto', 'L4'))
    b[index+13] = correctZerosAlliance(tbaWrapper.getAllianceNetAlgae(matchNum, 'red'))
    b[index+14] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L1'))
    b[index+15] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L2'))
    b[index+16] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L3'))
    b[index+17] = correctZerosAlliance(tbaWrapper.getAllianceReefForLevel(matchNum, 'red', 'teleop', 'L4'))
    
    b[index+18] = correctZerosBothAlliances(tbaWrapper.getTotalAlgaeProcessor(matchNum))
    
    for scoutData in data:
        scoutIndex = scoutNames.index(scoutData['scoutName'])

        A[index+18, scoutIndex] = correctZerosScouting(b[index+18], scoutData['autoProcessorAlgae'] + scoutData['teleopProcessorAlgae'])
        
        indexOffset = 9 if scoutData['teamNum'] in redAllianceTeamNums else 0

        A[index+indexOffset, scoutIndex] = correctZerosScouting(b[index], scoutData['autoCoralL1'])
        A[index+indexOffset+1, scoutIndex] = correctZerosScouting(b[index+1], scoutData['autoCoralL2'])
        A[index+indexOffset+2, scoutIndex] = correctZerosScouting(b[index+2], scoutData['autoCoralL3'])
        A[index+indexOffset+3, scoutIndex] = correctZerosScouting(b[index+3], scoutData['autoCoralL4'])
        A[index+indexOffset+4, scoutIndex] = correctZerosScouting(b[index+4], scoutData['autoNetAlgae'] + scoutData['teleopNetAlgae'])
        A[index+indexOffset+5, scoutIndex] = correctZerosScouting(b[index+5], scoutData['teleopCoralL1'])
        A[index+indexOffset+6, scoutIndex] = correctZerosScouting(b[index+6], scoutData['teleopCoralL2'])
        A[index+indexOffset+7, scoutIndex] = correctZerosScouting(b[index+7], scoutData['teleopCoralL3'])
        A[index+indexOffset+8, scoutIndex] = correctZerosScouting(b[index+8], scoutData['teleopCoralL4'])

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

for data in scoutingDataRaw:
    matchNum = int(data['matchNum'])
    teamNum = int(data['teamNum'])
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
    combinedData['autoNetAlgae'] = data['id']
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