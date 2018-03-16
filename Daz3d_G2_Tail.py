from pyfbsdk import *
from pyfbsdk_additions import *
import math

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

cManager = FBConstraintManager()
tails = FBComponentList()
includeNamespace = True
modelsOnly = False
FBFindObjectsByName('MD:DD:tail*', tails, includeNamespace, modelsOnly)

parentNulls = []
constraints = []

# Add Nulls
for tail in tails:
    pos = FBVector3d()
    child = tail.Children
    tail.GetVector(pos)

    if len(child) > 0:
        cPos = FBVector3d()
        child[0].GetVector(cPos)
        
        n1 = FBModelNull('{}A'.format(tail.Name))
        n2 = FBModelNull('{}B'.format(tail.Name))
    
        n1.Translation = pos
        n2.Translation = cPos
        
        n1.Parent = tail
        n2.Parent = n1
        
        n1.Show = True
        n2.Show = True
        
        parentNulls.append(n2)

'''
# Add Chain IK
for tail in tails:
    if tail.Name != 'tail01' and tail.Name != 'tail17':
        x = cManager.TypeCreateConstraint(13)
        x.Name = 'ChainIK_{}'.format(tail.Name)
        x.ReferenceAdd(0, tail)
        x.ReferenceAdd(1, tail.Children[0])
        
        # Find the Parent null
        p = tail.Parent
        child1 = p.Children
        for i in child1:
            if i.Name.endswith('A'):
                child2 = i.Children
                x.ReferenceAdd(2, child2[0])
        
        constraints.append(x)
'''

# Build the Relational Constraint
rm = cManager.TypeCreateConstraint(7)
rm.Name = 'TailRelation'

for marker in parentNulls:
    
    cntr = parentNulls.index(marker)

    # Make the damper box
    damper = rm.CreateFunctionBox('Other', 'Damping (3D) (Clock based)')
    rm.SetBoxPosition(damper, 100, (100 * (cntr + 1)))
    dInN = damper.AnimationNodeInGet()
    dOutN = damper.AnimationNodeOutGet()
    
    # Set the value of Damping Factor
    v = 20.0 + (cntr * 5.0)
    dInN.Nodes[1].WriteData([v])

    # Add Tailbone output and attach
    tOut = rm.SetAsSource(marker)
    rm.SetBoxPosition(tOut, -240, (100 * (cntr + 1)))
    tOutN = tOut.AnimationNodeOutGet()
    FBConnect(tOutN.Nodes[0], dInN.Nodes[0])
    
    # Add Tailbone input and attach
    tIn = rm.ConstrainObject(marker)
    rm.SetBoxPosition(tIn, 520, (100 * (cntr + 1)))
    tInN = tIn.AnimationNodeInGet()
    FBConnect(dOutN.Nodes[0], tInN.Nodes[0])

# Activate the Chain Constraints
#for constraint in constraints:
#    constraint.Snap()

# Add Aim constraints in order
# Reverse the tail order
reversedTails = []
for tail in tails:
    reversedTails.append(tail)

for tail in reversedTails[::-1][1:]:
    x = cManager.TypeCreateConstraint(0)
    x.Name = 'Aim_{}'.format(tail.Name)
    x.ReferenceAdd(0, tail)
    x.ReferenceAdd(1, tail.Children[1].Children[0])
    x.Snap()
    
