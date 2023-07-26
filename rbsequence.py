
class Sequence:
    sequenceList = [
        {'name': '10-5-Go', 'interval': 5, 'warning': [-10,-5]},
        {'name': '5-4-1-Go', 'interval': 5, 'warning': [-5,-4,-1]},
        {'name': '3-2-1-Go', 'interval': 3, 'warning': [-3,-2,-1]}
    ]
    
    def __init__(self):
        pass

    def set(self, sigValues):
        print(sigValues)
        
    def getSequenceList(self):
        return Sequence.sequenceList
    
    def getSequenceNames(self):
        seqNames = []
        for s in Sequence.sequenceList: seqNames.append(s['name'])
        return seqNames
    