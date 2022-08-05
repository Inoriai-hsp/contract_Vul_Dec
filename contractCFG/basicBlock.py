class BasicBlock:
    def __init__(self):
        self.start = -1
        self.end = -1
        self.instructions = {}
        self.fallsTo = -1
        self.jumpType = 0 # 0: fall, 1: unconditional, 2: conditional, 3: terminal
    
    def getFallsTo(self):
        return self.fallsTo

    def setFallsTo(self, address):
        self.fallsTo = address

    def getJumpType(self):
        return self.jumpType

    def setJumpType(self, jumpType):
        self.jumpType = jumpType

    def getInstructions(self):
        return self.instructions

    def setInstructions(self, instructions):
        self.instructions = instructions
    
    def setStart(self, start):
        self.start = start

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def setEnd(self, end):
        self.end = end
