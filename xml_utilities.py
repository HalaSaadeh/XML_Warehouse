from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as et

class TwoTrees():
    path1=None
    path2=None
    tree1=""
    tree2=""
    tree1ld=[]
    tree2ld=[]
    def __init__(self, path1, path2):
        self.path1=path1
        self.path2=path2
        self.tree1= self.docpreprocess(path1)
        self.tree2=self.docpreprocess(path2)

    def docpreprocess(self,path):
        def prep(t):
            if t is None:
                return None
            newtree=Element(t.tag)
            for k,v in t.attrib.items():
                attrchild = SubElement(newtree, '@ ' + k)
                attrcontent = SubElement(attrchild, v)
            for child in t:
                newtree.append(prep(child))
            if t.text is not None:
                content = t.text
                contentwords = content.split()
                for word in contentwords:
                    c = SubElement(newtree, "( " + word)
            return newtree

        v = open(path, "r")
        f = v.read()
        t = et.fromstring(f, parser=et.XMLParser(encoding="unicode"))
        tree=prep(t)
        return tree

    def computeES(self):
        self.tree1ld=self.computeLD(self.tree1ld,self.tree1,None,0)
        self.tree2ld=self.computeLD(self.tree2ld,self.tree2,None,0)
        #chawathe_matrix=self.computeTED()
       # es=self.editScript(chawathe_matrix)

    def computeLD(self,t,root,parent,pos,level=0):
        rootld=LDPair(root.tag,level,parent,pos)
        rootld.add=root
        t.append(rootld)
        pos=0
        for child in root:
            self.computeLD(t,child,rootld,pos,level+1)
            pos=pos+1
        return t

    #def computeES(self):

class LDPair():
    label=""
    depth=0
    parent=None
    pos=0
    id=0
    add=None
    def __init__(self,label, depth,parent,pos):
        self.label=label
        self.depth=depth
        self.parent=parent
        self.pos=pos
    def printld(self):
        print(self.label, ",",self.depth)




