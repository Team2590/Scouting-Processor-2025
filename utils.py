def getScoutNames(data): 
    return list(set(d['scoutName'] for d in data))

def getLastMatchNum(data): 
    return max(map(lambda d: d['matchNum'], data))

def scoutingDataTo2dArray(data, lastMatchNum):
    organized = [[] for _ in range(lastMatchNum)]
    for scoutData in data:
        organized[scoutData['matchNum'] - 1].append(scoutData)
    return organized

def correctZerosAlliance(number): 
    if number != 0:
        return number + 3
    else:
        return 0
    
def correctZerosScouting(allianceTotal, scouterData):
    if allianceTotal != 0:
        return scouterData + 1
    else: 
        return scouterData
    
def correctZerosBothAlliances(number): 
    if number != 0:
        return number + 6
    else:
        return 0