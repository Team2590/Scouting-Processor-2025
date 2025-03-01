from wrappers import TbaWrapper, MatchScoutingDataWrapper
from utils import correctZerosBothAlliances, getScoutNames, getLastMatchNum, scoutingDataTo2dArray, correctZerosAlliance, correctZerosScouting
from dotenv import load_dotenv # type: ignore
import numpy as np # type: ignore
import os
import json

load_dotenv()

scoutingDataRaw = json.load(open('./inputs/' + input('Enter the Enter the file name in the inputs folder: ')))
compKey = input("Enter the competition key: ")

tbaWrapper = TbaWrapper(compKey, os.getenv("TBA_KEY"))

scoutNames = getScoutNames(scoutingDataRaw)
lastMatchNum = int(getLastMatchNum(scoutingDataRaw))

scoutingData = scoutingDataTo2dArray(scoutingDataRaw, lastMatchNum)

A = np.zeros((19 * lastMatchNum, len(scoutNames)))
b = np.zeros(19 * lastMatchNum)

for data in scoutingData:
    try: 
        data[0]
    except:
        continue  

    matchNum = int(data[0]['matchNum'])
    index = (matchNum - 1) * 8
    redAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    blueAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    
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