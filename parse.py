from enum import Enum

class Buttons(Enum):
    BGM      = 1
    L_GEAR   = 56 # scratch long note
    R_GEAR   = 59 # 7th lane long note
    A = 11
    B = 12
    C = 13
    D = 14
    E = 15
    F = 18
    HOLD_A = 51
    HOLD_B = 52
    HOLD_C = 53
    HOLD_D = 54
    HOLD_E = 55
    HOLD_F = 58   
    
    def __str__(self) -> str:
        return '%s' % self.name
    

def convertToBase10(num:str)->int:
    return int(num) if num[0] != "0" else int(num[1:])

def main()->None:
    # open test.bms file as text
    lines = []
    with open("test.bms", "r", encoding="utf-8") as f:
        # save as a list of lines
        lines = f.readlines()
        
    # find index of *---------------------- MAIN DATA FIELD
    idx = lines.index("*---------------------- MAIN DATA FIELD\n")
    
    # trim the list of lines to only include the main data field
    lines = lines[idx+1:]
    
    # find the first element that is not "\n"
    firstIdx = 0
    while lines[firstIdx] == "\n":
        firstIdx += 1
    
    # convert firstMeasure into a base 10 integer
    # #001 -> 1
    firstMeasure = convertToBase10(lines[firstIdx][1:4])
            
    
    """
           2 4 6
        S 1 3 5 7
    S: 16
    1,2,3,4,5: 11, 12, 13, 14, 15
    6,7: 18, 19
    
    S: L gear(16)
    7: R gear(19)
    123->123(11, 12, 13)
    567->567(14, 15, 18)
    """
    
    linesGroupedByMeasure = {}
    maxGrid = 0
    for line in lines[firstIdx:]:
        if line == "\n":
            maxGrid = 0
            continue
        
        currMeasure = convertToBase10(line[1:4])
        
        if currMeasure not in linesGroupedByMeasure:
            linesGroupedByMeasure[currMeasure] = {}
        
        sepIndex = line.index(":")
        data = line[sepIndex+1:].strip()
        
        gridSize = len(data) // 2
        maxGrid = gridSize if gridSize > maxGrid else maxGrid
        
        channel = int(line[4:6])
        linesGroupedByMeasure[currMeasure][channel] = {"data": data, "length": len(data), "div2": gridSize}
        
        linesGroupedByMeasure[currMeasure]["maxGrid"] = maxGrid
                
    # iterate through the dictionary
    for measure in linesGroupedByMeasure:
        curr = linesGroupedByMeasure[measure]
        maxGrid:int = curr["maxGrid"]
        
        # pad the data with 0s evenly to fit the maxGrid size
        """
        (maxGrid = 16)
        turn
        0000000000000002
        02020002
        00000002000002000000020000000000
        0002
        
        into
        
        00--00--00--00--00--00--00--02-- (len:16,div2: 8 -> 2 padding)
        02------02------00------02------ (len:8, div2: 4 -> 6 padding)
        00000002000002000000020000000000 (len:32,div2: 16-> 0 padding)
        00--------------02-------------- (len:4, div2: 2 -> 14 padding)
        """
        
        for channel in curr:
            if channel == "maxGrid" or curr[channel]["div2"] == maxGrid:
                continue
            
            data = curr[channel]["data"]
            length = curr[channel]["length"]
            div2 = curr[channel]["div2"]
            
            splitData = [data[i:i+2] for i in range(0, length, 2)]
            padCount = (maxGrid * 2) // div2 - 2
            
            # append padCount of "-" to each element in the splitData
            for i in range(len(splitData)):
                splitData[i] = splitData[i] + "-" * padCount
            
            # join the splitData back together
            curr[channel]["data"] = "".join(splitData)
            curr[channel]["length"] = len(curr[channel]["data"])
            
    for measure in linesGroupedByMeasure:
        print(f"Measure: {measure}")
        curr = linesGroupedByMeasure[measure]
        maxGrid:int = curr["maxGrid"]
        
        for channel in curr:
            if channel == "maxGrid":
                continue
            
            # print(f"Channel: {channel}")
            print(f"{Buttons(channel)} {curr[channel]["data"]}")
  
        print()
    
    # input()
    

if __name__=="__main__":
    main()