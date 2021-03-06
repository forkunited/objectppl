#!/usr/bin/python

import csv
import sys
import os
from collections import OrderedDict

input_file_path = sys.argv[1]
input_filter_file_path = sys.argv[2]
output_action_dir = sys.argv[3]
output_utterance_dir = sys.argv[4]

def read_messy_file(file_path):
    f = open(file_path, 'rt')
    D = dict()
    try:
        reader = csv.DictReader(f, delimiter=',')
        for record in reader:
            if record["gameid"] not in D:
                D[record["gameid"]] = []
            D[record["gameid"]].append(record)
    finally:
        f.close()
    return D

def make_action_records(record, index):
    actions = []

    listenerObjs = [dict(), dict(), dict()]
    speakerObjs = [dict(), dict(), dict()]

    clickedLisIndex = int(record["lisLocsClickedObj"]) - 2
    clickedSpIndex = int(record["spLocsClickedObj"]) - 2
    alt1LisIndex = int(record["alt1LisLocs"]) - 2
    alt1SpIndex = int(record["alt1SpLocs"]) - 2
    alt2LisIndex = int(record["alt2LisLocs"]) - 2
    alt2SpIndex = int(record["alt2SpLocs"]) - 2

    target = 0
    if record["targetStatusClickedObj"] == "target":
        target = 1
    listenerObjs[clickedLisIndex]["Name"] = record["nameClickedObj"]
    listenerObjs[clickedLisIndex]["Target"] = target
    #listenerObjs[clickedLisIndex]["Clicked"] = 1
    listenerObjs[clickedLisIndex]["Category0"] = record["basiclevelClickedObj"]
    listenerObjs[clickedLisIndex]["Category1"] = record["superdomainClickedObj"]
    speakerObjs[clickedSpIndex]["Name"] = record["nameClickedObj"]
    speakerObjs[clickedSpIndex]["Target"] = target
    #speakerObjs[clickedSpIndex]["Clicked"] = 1
    speakerObjs[clickedSpIndex]["Category0"] = record["basiclevelClickedObj"]
    speakerObjs[clickedSpIndex]["Category1"] = record["superdomainClickedObj"]

    target = 0
    if record["alt1TargetStatus"] == "target":
        target = 1
    listenerObjs[alt1LisIndex]["Name"] = record["alt1Name"]
    listenerObjs[alt1LisIndex]["Target"] = target
    #listenerObjs[alt1LisIndex]["Clicked"] = 0
    listenerObjs[alt1LisIndex]["Category0"] = record["alt1Basiclevel"]
    listenerObjs[alt1LisIndex]["Category1"] = record["alt1superdomain"]
    speakerObjs[alt1SpIndex]["Name"] = record["alt1Name"]
    speakerObjs[alt1SpIndex]["Target"] = target
    #speakerObjs[alt1SpIndex]["Clicked"] = 0
    speakerObjs[alt1SpIndex]["Category0"] = record["alt1Basiclevel"]
    speakerObjs[alt1SpIndex]["Category1"] = record["alt1superdomain"]

    target = 0
    if record["alt2TargetStatus"] == "target":
        target = 1
    listenerObjs[alt2LisIndex]["Name"] = record["alt2Name"]
    listenerObjs[alt2LisIndex]["Target"] = target
    #listenerObjs[alt2LisIndex]["Clicked"] = 0
    listenerObjs[alt2LisIndex]["Category0"] = record["alt2Basiclevel"]
    listenerObjs[alt2LisIndex]["Category1"] = record["alt2superdomain"]
    speakerObjs[alt2SpIndex]["Name"] = record["alt2Name"]
    speakerObjs[alt2SpIndex]["Target"] = target
    #speakerObjs[alt2SpIndex]["Clicked"] = 0
    speakerObjs[alt2SpIndex]["Category0"] = record["alt2Basiclevel"]
    speakerObjs[alt2SpIndex]["Category1"] = record["alt2superdomain"]

    action = dict()
    action["gameid"] = record["gameid"]
    action["roundNum"] = int(record["roundNum"])
    action["time"] = int(record["time"])
    action["lClicked"] = clickedLisIndex
    action["sClicked"] = clickedSpIndex

    action["trial_index"] = index

    for i in range(len(listenerObjs)):
        for key in listenerObjs[i]:
            action["l" + key + "_" + str(i)] = listenerObjs[i][key]
            action["s" + key + "_" + str(i)] = speakerObjs[i][key]
            if listenerObjs[i]["Target"] == 1:
                action["lTargetName"] = listenerObjs[i]["Name"]
                action["lTargetCategory0"] = listenerObjs[i]["Category0"]
                action["lTargetCategory1"] = listenerObjs[i]["Category1"]
            if speakerObjs[i]["Target"] == 1:
                action["sTargetName"] = speakerObjs[i]["Name"]
                action["sTargetCategory0"] = speakerObjs[i]["Category0"]
                action["sTargetCategory1"] = speakerObjs[i]["Category1"]

    actions.append(action)

    return actions

def make_utterance_records(record):
    utterances = []

    s = record["speakerMessages"].split("___")
    l = record["listenerMessages"].split("___")
    timeStamps = record["messageTimeStamps"].split("___")

    # NOTE: This alternates speaker and listener messages
    # But this is not necessarily the correct ordering.  The
    # correct ordering is not recoverable from the source data
    s_index = 0
    l_index = 0
    for i in range(len(timeStamps)):
        time_i = int(timeStamps[i])
        message = None
        sender = None
        if s_index < len(s) and (i % 2 == 0 or l_index >= len(l)):
            message = s[s_index]
            s_index += 1
            sender = "speaker"
        else:
            message = l[l_index]
            l_index += 1
            sender = "listener"

        utterance = dict()
        utterance["gameid"] = record["gameid"]
        utterance["roundNum"] = int(record["roundNum"])
        utterance["time"] = time_i
        utterance["sender"] = sender
        utterance["contents"] = message

        utterances.append(utterance)

    return utterances

def process_game(game_records, filter):
    actions = []
    utterances = []
    for record in game_records:
        has_round = False
        round = record["roundNum"]
        for filter_record in filter:
            if filter_record["roundNum"] == round:
                has_round = True
                break
        if not has_round:
            continue

        actions.extend(make_action_records(record, filter_record["trial_inds"]))
        utterances.extend(make_utterance_records(record))
    return actions, utterances


def process_games(game_record_dict, filter_dict):
    processed_games = dict()
    for key, value in game_record_dict.items():
        if key not in filter_dict:
            continue
        processed_games[key] = process_game(value, filter_dict[key])
    return processed_games


def output_csv(file_path, rows):
    fields = OrderedDict([(k, None) for k in rows[0].keys()])
    f = open(file_path, 'wb')
    try:
        writer = csv.DictWriter(f, delimiter=',', fieldnames=fields, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    finally:
        f.close()


def output_games(action_dir, utterance_dir, games_to_action_utterances):
    for game, action_utterances in games_to_action_utterances.items():
        output_csv(os.path.join(action_dir, game), action_utterances[0])
        output_csv(os.path.join(utterance_dir, game), action_utterances[1])


processed_games = process_games(read_messy_file(input_file_path), read_messy_file(input_filter_file_path))
output_games(output_action_dir, output_utterance_dir, processed_games)
