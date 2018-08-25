#! /usr/bin/python3

import random

DATA = [
    "Helio",
    "Alexandre",
    "Maria",
    "Caio",
    "Léo",
    "Laura",
    "Juliana",
    "Marcelo",
    "Pedro",
    "Luiz",
    "Eliana",
    "elaine",
    "Andréia",
    "André",
    "Júlia"
    ]

def get_random(total):
    return random.randint(0, total - 1)

people = len(DATA)
months = people - 1
print("People=%d" % people)
print("Months=%d" % months)
combinations = []
counter = {}

# matrix
for y in range(0,people):
    row = []
    for x in range(0, people):
        if x == y:
            row.append(x)
        else:
            row.append(None)
    #print(row)
    combinations.append(row)
    counter[y] = 0

for y in range(0,people):
    for x in range(0,people):
        if x == y:
            continue
        while True:
            dice = get_random(people)
            if not dice in combinations[y]:
                if counter[dice] >= months:
                    continue
                else:
                    counter[dice] += 1
                combinations[y][x] = dice
                break
    row = ",".join(map(str,combinations[y]))
    #print("%d: %s" % (y, row))
    #print(counter)

groups = {}
for y in range(0, people):
    for x in range(0, people):
        if x == y:
            continue
        value = combinations[x][y]
        #print("%d,%d=%d" % (x,y,value))
        if not value in groups:
            groups[value] = []
        groups[value].append("%s and %s" % (DATA[x], DATA[y]))

for month in groups.keys():
    teams = ",".join(groups[month])
    print("%d) %s" % (month, teams))
