"""
MontyHallProblem

Description:
"""
import random
import math

# constants.
NUM_DOORS = 3
# end constants.

carDoor = None

def generateCarDoor():
    global carDoor
    carDoor = random.randint(1, NUM_DOORS)

def getRemainingChoices(toExclude, lo, hi):
    uwu = []
    for i in range(lo, hi):
        canAdd = True
        for j in toExclude:
            if i == j:
                canAdd = False
        if canAdd:
            uwu.append(i)
    return uwu

def generateRandomGoatKnown(initChoice):
    uwu = getRemainingChoices([carDoor, initChoice], 1, NUM_DOORS + 1)
    return uwu[random.randint(0, len(uwu) - 1)]

def takeNumericInput():
    global running
    choice = input()
    if choice == "quit":
        print("Goodbye")
        raise SystemExit
    choiceInt = int(choice)
    return choiceInt

def doManualSim(trials):
    trial = 0
    remainPlayersWon = 0
    remainPlayersTotal = 0
    switchPlayersWon = 0
    switchPlayersTotal = 0
    while trial < trials:
        choicesInit = getRemainingChoices([-1], 1, NUM_DOORS+1)
        print("Choose a door. Choices: %s" % choicesInit)
        initChoice = takeNumericInput()
        generateCarDoor()
        goatInfo = generateRandomGoatKnown(initChoice)
        print("Door #%d is known to be a goat." % goatInfo)
        print("Please pick from the following choices: %s" % str(getRemainingChoices([goatInfo], 1, NUM_DOORS + 1)))
        remainChoice = takeNumericInput()
        if remainChoice == initChoice:
            remainPlayersTotal += 1
            if remainChoice == carDoor:
                print("You got the car!")
                remainPlayersWon += 1
            else:
                print("You did not get the car!")
        else:
            switchPlayersTotal += 1
            if remainChoice == carDoor:
                print("You got the car!")
                switchPlayersWon += 1
            else:
                print("You did not get the car!")
        print("-----------------------\n")
        trial += 1
    print("SwitchWon (n=%d): %.4f%%" % (switchPlayersTotal, float(100.0 * switchPlayersWon / switchPlayersTotal)))
    print("RemainWon (n=%d): %.4f%%" % (remainPlayersTotal, float(100.0 * remainPlayersWon / remainPlayersTotal)))
    
def doAutoSim(trials):
    trial = 0
    half = trials / 2
    remainPlayersWon = 0
    remainPlayersTotal = 0
    switchPlayersWon = 0
    switchPlayersTotal = 0
    while trial < trials:
        choicesInit = getRemainingChoices([-1], 1, NUM_DOORS+1)
        initChoice = random.randint(1, NUM_DOORS)
        generateCarDoor()
        goatInfo = generateRandomGoatKnown(initChoice)
        remainingChoices = getRemainingChoices([goatInfo], 1, NUM_DOORS + 1)
        remainChoice = None
        if trial < half:
            remainPlayersTotal += 1
            remainChoice = initChoice
            if remainChoice == carDoor:
                remainPlayersWon += 1
        else:
            switchPlayersTotal += 1
            for i in remainingChoices:
                if i != initChoice:
                    remainChoice = i
                    break
            if remainChoice == carDoor:
                switchPlayersWon += 1
        trial += 1
    print("SwitchWon (n=%d): %.4f%%" % (switchPlayersTotal, float(100.0 * switchPlayersWon / switchPlayersTotal)))
    print("RemainWon (n=%d): %.4f%%" % (remainPlayersTotal, float(100.0 * remainPlayersWon / remainPlayersTotal)))

print("Would you like to:")
print("[1] Try the simulation yourself for a set number of trials?")
print("[2] Run the simulation with an automated number of trials?")
print("[3] Quit")
choice = takeNumericInput()
if choice != 3:
    print("How many trials would you like?")
    trials = takeNumericInput()
    if choice == 1:
        doManualSim(trials)
    elif choice == 2:
        doAutoSim(trials)
