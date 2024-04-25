from enum import Enum


class Buttons(Enum):
    # BGM      = 1
    L_GEAR = 56  # scratch long note
    R_GEAR = 59  # 7th lane long note
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


# ['0', '0', '0', '-', '0', '0', '0', '|', '0', '0', '|', '0']
class Lanes(Enum):
    A = 0
    B = 1
    C = 2
    D = 4
    E = 5
    F = 6
    L_GEAR = 8
    R_GEAR = 9
    DRIFT = 11


def convertButtonsToLanes(buttons: Buttons) -> Lanes:
    if buttons == Buttons.A:
        return Lanes.A
    elif buttons == Buttons.B:
        return Lanes.B
    elif buttons == Buttons.C:
        return Lanes.C
    elif buttons == Buttons.D:
        return Lanes.D
    elif buttons == Buttons.E:
        return Lanes.E
    elif buttons == Buttons.F:
        return Lanes.F
    elif buttons == Buttons.L_GEAR:
        return Lanes.L_GEAR
    elif buttons == Buttons.R_GEAR:
        return Lanes.R_GEAR
    else:
        return Lanes.DRIFT


def convertToBase10(num: str) -> int:
    return int(num) if num[0] != "0" else int(num[1:])


def main() -> None:
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

        if line[4:6] == "01":
            continue
        channel = Buttons(int(line[4:6]))

        # initialize the current measure
        for ch in Buttons:
            linesGroupedByMeasure[currMeasure][ch] = {
                "data": "", "length": 0, "div2": 0} if ch not in linesGroupedByMeasure[currMeasure] else linesGroupedByMeasure[currMeasure][ch]

        linesGroupedByMeasure[currMeasure][channel] = {
            "data": data, "length": len(data), "div2": gridSize}

        linesGroupedByMeasure[currMeasure]["maxGrid"] = maxGrid

    # iterate through the dictionary
    for measure in linesGroupedByMeasure:
        curr = linesGroupedByMeasure[measure]
        if curr == {}:
            continue
        maxGrid: int = curr["maxGrid"]

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

        """
        TODO: I need to make maxGrid=1 measure to have 4 beats?
        4 beats per measure if 4/4
        maxGrid = 1
            : 1 grid * 4 beats
        maxGrid = 16
            : 4 grid * 4 beats
        maxGrid = 24
            : 6 grid * 4 beats
        maxGrid = 8
            : 2 grid * 4 beats
        """
        for channel in curr:
            if channel == "maxGrid" or curr[channel]["div2"] == maxGrid or curr[channel]["length"] == 0:
                continue

            data = curr[channel]["data"]
            length = curr[channel]["length"]
            div2 = curr[channel]["div2"]

            splitData = [data[i:i+2] for i in range(0, length, 2)]
            padCount = (maxGrid * 2) // div2 - 2

            # append padCount of "-" to each element in the splitData
            for i in range(len(splitData)):
                splitData[i] = splitData[i] + "0" * padCount

            # join the splitData back together
            curr[channel]["data"] = "".join(splitData)
            curr[channel]["length"] = len(curr[channel]["data"])

    # convert lane data
    for measure in linesGroupedByMeasure:
        curr = linesGroupedByMeasure[measure]

        if curr == {}:
            continue
        maxGrid: int = curr["maxGrid"]

        for channel in curr:
            if channel == "maxGrid":
                continue

            data = curr[channel]["data"]
            length = curr[channel]["length"]
            splitData = [convertToBase10(data[i:i+2])
                         for i in range(0, length, 2)]
            curr[channel]["data"] = splitData

    converted = []
    converted.append("--")

    # find the last measure in linesGroupedByMeasure
    lastMeasure = max(linesGroupedByMeasure.keys())

    for i in range(0, lastMeasure):
        curr = linesGroupedByMeasure[i] if i in linesGroupedByMeasure else {}

        if curr == {}:
            converted.append("000-000|00|0")
            converted.append("--")
            converted.append("000-000|00|0")
            converted.append("--")
            converted.append("000-000|00|0")
            converted.append("--")
            converted.append("000-000|00|0")
            converted.append("--")
            continue

        maxGrid: int = curr["maxGrid"]
        for j in range(maxGrid):
            converted.append(['0', '0', '0', '-', '0', '0',
                             '0', '|', '0', '0', '|', '0'])
            for channel in curr:
                if channel == "maxGrid":
                    continue

                data = curr[channel]["data"]
                lane = convertButtonsToLanes(channel)
                if data == []:
                    converted[-1][lane.value] = "0"
                # data[j]
                else:
                    if data[j] == 0:
                        converted[-1][lane.value] = "0"
                    else:
                        converted[-1][lane.value] = "1"  # str(data[j])

            converted[-1] = "".join(converted[-1])

            if maxGrid == 1 and j == 0:
                converted.append("--")
                converted.append("000-000|00|0")
                converted.append("--")
                converted.append("000-000|00|0")
                converted.append("--")
                converted.append("000-000|00|0")
                converted.append("--")

            elif j % (maxGrid // 4) == maxGrid // 4 - 1:
                converted.append("--")

    # print the converted data
    for i in converted:
        print(i)

    # write the converted data to a file
    with open("converted.txt", "w") as f:
        for i in converted:
            f.write(i + "\n")


if __name__ == "__main__":
    main()
