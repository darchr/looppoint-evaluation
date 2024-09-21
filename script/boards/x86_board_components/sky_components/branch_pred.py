from m5.objects import (
    BranchPredictor,
    DerivO3CPU,
    X86O3CPU,
    OpDesc,
    FUDesc,
    FUPool,
    SimpleIndirectPredictor,
    LTAGE_TAGE,
    TournamentBP,
    LTAGE,
    SimpleBTB,
    ReturnAddrStack,
)


class IndirectPred(SimpleIndirectPredictor):
    indirectSets = 128 # Cache sets for indirect predictor
    indirectWays = 4 # Ways for indirect predictor
    indirectTagSize = 16 # Indirect target cache tag bits
    indirectPathLength = 7 # Previous indirect targets to use for path history
    indirectGHRBits = 16 # Indirect GHR number of bits

class LTAGE_SETUP(LTAGE_TAGE): #changed name
    nHistoryTables = 12 
    minHist = 4 
    maxHist = 34
    tagTableTagWidths = [0, 7, 7, 8, 8, 9, 10, 11, 12, 12, 13, 14, 15]
    logTagTableSizes = [14, 10, 10, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9]
    logUResetPeriod = 19

class LTAGE_BP(LTAGE):
    btb = SimpleBTB(numEntries=512, tagBits=19)#changed default from 4092 -> 512, 16 -> 19
    ras = ReturnAddrStack(numEntries=32) #default 12 -> 32

    indirectBranchPred = IndirectPred() # use NULL to disable

    tage = LTAGE_SETUP()

class TournBP(TournamentBP):
    """
    Tournament Branch Predictor using default values
    """
    localPredictorSize = 2048
    localCtrBits = 2
    localHistoryTableSize = 2048
    globalPredictorSize = 8192
    globalCtrBits = 2
    choicePredictorSize = 8192
    choiceCtrBits = 2

    btb = SimpleBTB(numEntries=4096, tagBits=18)
    ras = ReturnAddrStack(numEntries=16)
    # instShiftAmt = 2 #unsure if this needs to be added but i will keep it?