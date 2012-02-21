"""
Dialog engine support code.
Each npc's DialogTree is organized into a tree of DialogNodes.  Most nodes display
some text; they also provide DialogOptions, which link to other nodes.  (If a DialogNode
does not contain any text, then it's not actually displayed to the user, but is used
to organize the logic in jumping to other nodes).

The NPC text file can include code - hopefully not much, since it's a bit onerous
to debug complex snippets.  The code helps the NPCs become a little more lifelike - e.g.
they can say "hello" on the first meeting and "welcome back" later.  The whole
procedure is a little awkward, and perhaps wouldn't work well for a dialog-focused
game like Curse of Monkey Island or Starcon 2.  But our prime focus is on (a) killing
monsters, and (b) taking their stuff.

INTRO CODE
~
Root|~
<directions to first node>
~
NodeName|Blah blah
blah blah
blah blah~
DialogString|NextNode|PreLogic|PostLogic|TriggerCode
DialogString2|NextNode|PreLogic|PostLogic|TriggerCode
~

"""

from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
class DialogOption:
    def __init__(self, Text, NextNode, PreLogic = None, PostLogic = None, TriggerCode = None):
        self.Text = Text
        self.NextNode = NextNode
        self.PreLogic = PreLogic
        self.PostLogic = PostLogic
        self.TriggerCode = TriggerCode
    def __str__(self):
        return "<DialogOption '%s'>"%self.Text
    def GetNode(self):
        #print "GetNode() called on '%s'"%self.Text
        if self.NextNode:
            #print "Returning NextNode %s"%self.NextNode
            return self.NextNode
        if self.PostLogic:
            #print "Applying post logic:", self.PostLogic
            NodeID = apply(self.PostLogic, (Global.Party, Global.Maze))
            #print "Post logic gave node ID:", NodeID
            return NodeID
        print "We have neither NextNode nor PostLogic!!!"
        return None

class DialogNode:
    """
    A logic node.  Its function gets Party and Maze as parameters, and should return the name or number
    of the next node.  
    """
    def __init__(self, Name, Text):
        self.Name = Name
        self.Text = Text
        self.Choices = []
    def __str__(self):
        return "<Node '%s' (%s)>"%(self.Name, str(self.Text)[:50])
    def AddChoice(self, Text, NextNode, PreLogic = None, PostLogic = None, TriggerCode = None):
        Choice = DialogOption(Text, NextNode, PreLogic, PostLogic, TriggerCode)
        self.Choices.append(Choice)
    def GetChoices(self):
        List = []
        for Choice in self.Choices:
            if (not Choice.PreLogic) or (apply(Choice.PreLogic, (Global.Party, Global.Maze))):
                List.append(Choice)
        return List
    def DebugPrint(self):
        print "---Node '%s': %s"%(self.Name, self.Text)
        for Choice in self.Choices:
            print Choice.Text
            print "-next:",Choice.NextNode
            print "-pre:",Choice.PreLogic
            print "-post:",Choice.PostLogic
            print "-trig:",Choice.TriggerCode
           
class DialogTree:
    """
    A DialogTree represents a conversation you can have with an NPC.  Some are more talkative than others;
    many just give some general information and send you on your way.  A dialog tree is made of NODES.  Each
    node SAYS STUFF, and provides one or more OPTIONS.  The options can have pre-logic (to see whether they're
    shown), or post-logic (to see where they head to).  If a node has no text, it isn't displayed at all.
    """
    def __init__(self, Name):
        self.Nodes = []
        self.NodeDict = {}
        self.RootNode = None
        self.Name = Name
    def AddNode(self, Node):
        self.Nodes.append(Node)
        self.NodeDict[Node.Name] = Node
    def GetFirstNode(self):
        print "Dialog:GetFirstNode()"
        Node = self.Nodes[0]
        if Node.Text:
            print "Root node has text.  Use it!"
            return Node
        # Branch immediately:
        for Branch in Node.Choices:
            if (not Branch.PreLogic) or (apply(Branch.PreLogic, (Global.Party, Global.Maze))):
                return self.GetNextNode(Branch)
##                print "Follow branch with prelogic:", Branch.PreLogic
##                if Branch.TriggerCode:
##                    apply(Branch.TriggerCode, (Global.Party, Global.Maze))
##                NodeID = Branch.GetNode()
##                if type(NodeID) == types.IntType:
##                    return self.Nodes[NodeID]
##                else:
##                    return self.NodeDict[NodeID]
    def GetNode(self, Name):
        return self.NodeDict.get(Name,None)
    def GetNextNode(self, Choice):
        print "Following choice:", Choice
        NodeID = Choice.GetNode()
        print "Node ID is:", NodeID
        if Choice.TriggerCode:
            apply(Choice.TriggerCode, (Global.Party, Global.Maze))        
        if NodeID == None:
            return None
        if type(NodeID) == types.IntType:
            Node = self.Nodes[NodeID]
        else:
            Node = self.NodeDict.get(NodeID, None)
        if not Node:
            print "Node is None - conversation will stop now!"
            print self.NodeDict.keys()
        if Node and not Node.Text:
            print "Branch immediately from %s"%Node.Name
            # Branch immediately:
            for Branch in Node.Choices:
                if (not Branch.PreLogic) or (apply(Branch.PreLogic, (Global.Party, Global.Maze))):
                    return self.GetNextNode(Branch)
            return None
        return Node
    def IntegrityCheck(self):
        for Node in self.Nodes:
            if Node.Text.find("|")!=-1:
                print "WARNING!  Node '%s' has a pipe in its text, probably broken"%Node.Name
                print "Text: '%s'"%Node.Text
            for Choice in Node.Choices:
                if Choice.NextNode:
                    if type(Choice.NextNode) == types.IntType:
                        OtherNode = self.Nodes[Choice.NextNode]
                    else:
                        OtherNode = self.NodeDict.get(Choice.NextNode, None)
                    if not OtherNode:
                        print "** WARNING: Choice '%s' from node %s directs to nonexistent '%s'"%(Choice.Text, Node.Name, Choice.NextNode)
    def GetFunction(self, Name):
        if Name=="None" or not Name:
            return None
        try:
            return self.Locals[Name]
        except:
            print "** UNKNOWN FUNCTION: '%s'"%Name
            GlobKeys = self.Locals.keys()
            GlobKeys.sort()
            print GlobKeys
    def DebugPrint(self):
        print "\n\n\n"
        print "---Dialog tree '%s'"%self.Name
        for Node in self.Nodes:
            Node.DebugPrint()
    def Load(self):
        File = open(os.path.join("NPC", "%s.txt"%self.Name))
        FileText = File.read()
        File.close()
        # Let's ignore carriage returns, so that we work properly on Linux:
        FileText = FileText.replace("\r", "")
        FuncEnd = FileText.find("~")
        print "FuncEnd:", FuncEnd
        # Local execution context:
        self.Globals = globals()
        self.Locals = locals()        
        exec(FileText[:FuncEnd], self.Globals, self.Locals)
        LastTilde = FuncEnd        
        NextTilde = FileText.find("~", FuncEnd + 1)
        while NextTilde!=-1:
            Bits = FileText[LastTilde+1:NextTilde].split("|")
            if len(Bits)<2:
                print "*** Error: Bad dialog node definition: '%s'"%FileText[LastTilde+1:NextTilde]
            NodeBody = Bits[1].strip()
            NodeBody = NodeBody.replace("\n"," ")
            NodeBody = NodeBody.replace("\\n","\n")
            NewNode = DialogNode(Bits[0].strip(), NodeBody)
            self.AddNode(NewNode)
            FinalTilde = FileText.find("~", NextTilde+1)
            if FinalTilde==-1:
                FinalTilde = len(FileText)
            Lines = FileText[NextTilde+1:FinalTilde].split("\n")
            for Line in Lines:
                Line = Line.strip()
                if len(Line)==0 or Line[0]=="#":
                    continue
                Bits = Line.split("|")
                Text = Bits[0]
                if len(Bits)>1:
                    NextNode = Bits[1]
                else:
                    NextNode = None
                if NextNode=="" or NextNode=="None":
                    NextNode = None
                if len(Bits)>2:
                    PreLogic = self.GetFunction(Bits[2])
                else:
                    PreLogic = None
                if len(Bits)>3:
                    PostLogic = self.GetFunction(Bits[3])
                else:
                    PostLogic = None
                if len(Bits)>4:
                    TriggerCode = self.GetFunction(Bits[4])
                else:
                    TriggerCode = None                    
                NewNode.AddChoice(Text, NextNode, PreLogic, PostLogic, TriggerCode)
            LastTilde = FinalTilde
            NextTilde = FileText.find("~", LastTilde + 1)
        # For development:
        #self.DebugPrint() #%%%
        #self.IntegrityCheck() #%%%


if __name__ == "__main__":
    Tree = DialogTree(sys.argv[1])
    Tree.Load()
    Tree.IntegrityCheck()