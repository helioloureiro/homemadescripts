#! /usr/bin/python3

import json
import requests
import bs4
import random
import time
import sys
import argparse

URL = "https://www.behindthename.com/random/random.php?number=2&sets=5&gender=both&surname=&all=yes"

data = { "employees" : [],
        "departments" :[]
        }


data["departments"].append({ "name" : "Product Development Area",
                             "code" : "PDU"})
data["departments"].append({ "name" : "Business Unit Global Support",
                             "code" : "BUGS"})
data["departments"].append({ "name" : "Business Area Digital Services",
                             "code" : "BGDS"})
data["departments"].append({ "name" : "Group Function",
                             "code" : "GF"})


def get_name(size):
    names_list = []
    while len(names_list) <= size:
        req = requests.get(URL)
        if req.status_code != 200:
            print(req.reason)
            time.sleep(5)
        bs = bs4.BeautifulSoup(req.text, "html.parser")
        for span in bs.find_all("span"):
            #print(span)
            #print(span.attrs.get("class"))
            if not span.attrs.get("class") == ["random-result"]: continue
            #print(span.text)
            names_list.append(span.text)
        print(len(names_list), "names on the list")

    return names_list[:size]

def generate_salary():
    main_value = random.randint(1000, 10000)

    return "%0.2f" % main_value

depts = []
for entry in  data["departments"]:
    depts.append(entry["code"])

def create_profile(number_id, name):
    try:
        first_name, last_name = name.split()
    except ValueError as e:
        name_parameters = name.split()
        first_name = " ".join(name_parameters[:-2])
        last_name = name_parameters[-1]
    salary = generate_salary()
    dept = random.choice(depts)
    return {
        "id" : number_id,
        "name" : first_name,
        "surname" : last_name,
        "salary" : salary,
        "dept"  : dept
    }

parser = argparse.ArgumentParser(description="Generate employees json file")
parser.add_argument("--output", help="output file to save data")
parser.add_argument("--entries", type=int, help="number of person entries to generate")
args = parser.parse_args()

names_list = get_name(args.entries)

counter = 0
for person in names_list:
    data["employees"].append(create_profile(counter, person))
    counter += 1

if args.output is None:
    print(json.dumps(data, indent=4))
else:
    with open(args.output, 'w') as output:
        output.write(json.dumps(data, indent=4))
