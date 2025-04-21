import csv


def getScoutNames(data): 
    return list(set(d['scoutName'] for d in data))

def getLastMatchNum(data): 
    return max(map(lambda d: int(d['matchNum']), data))

def scoutingDataTo2dArray(data, lastMatchNum):
    organized = [[] for _ in range(lastMatchNum)]
    for scoutData in data:
        organized[int(scoutData['matchNum']) - 1].append(scoutData)
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
    
def exportToCSV(data, filename):
    if not data:
        print("No data to write.")
        return
    
    keys = data[0].keys()  # Get column names from the first dictionary
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        
        writer.writeheader()  # Write column names
        writer.writerows(data)  # Write rows
    
    print(f"\nData successfully written to {filename}")