var getUtteranceActionObjectTarget = function(uA) {
    var target = "";
    if (parseInt(uA.action.lTarget_0) == 1)
        target = uA.action.lName_0;
    else if (parseInt(uA.action.lTarget_1) == 1)
        target = uA.action.lName_1;
    else if (parseInt(uA.action.lTarget_2) == 1)
        target = uA.action.lName_2;
    return target;
};

var getUtteranceActionObjectContext = function(uA) {
    var target = getUtteranceActionObjectTarget(uA);
    var o0 = uA.action.lName_0;
    var o1 = uA.action.lName_1;
    var o2 = uA.action.lName_2;

    var objs = [o0,o1,o2];
    objs.sort();
    return objs[0] + "." + objs[1] + "." + objs[2] + "-" + target
};

var utteranceActionToRoundPartition = function(part) {
    var keyFn = function(key, uA) {
        var gameid = gameppl.rgame.getUtteranceActionPairGame(uA);
        var roundNum = gameppl.rgame.getUtteranceActionPairRound(uA)
        return gameid + "_" + roundNum;
    };

    var valueFn = function(key, uA) {
        var gameid = gameppl.rgame.getUtteranceActionPairGame(uA);
        var roundNum = gameppl.rgame.getUtteranceActionPairRound(uA)
        return { "gameid" : gameid, "roundNum" : roundNum, "index" : uA.action.trial_index };
    };

    gameppl.partition.mapKeysAndValues(part, keyFn, valueFn);
}

module.exports = {
    getUtteranceActionObjectTarget : getUtteranceActionObjectTarget,
    getUtteranceActionObjectContext : getUtteranceActionObjectContext,
    utteranceActionToRoundPartition : utteranceActionToRoundPartition
};
