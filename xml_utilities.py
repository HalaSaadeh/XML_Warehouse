import sys
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as et

import numpy as np


class TwoTrees():
    path1=None
    path2=None
    tree1=""
    tree2=""
    tree1ld=[""]
    tree2ld=[""]
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
        chawathe_matrix=self.computeTED()
        es = self.editScript(chawathe_matrix)
        return es

    def computeLD(self,t,root,parent,pos,level=0):
        rootld=LDPair(root.tag,level,parent,pos)
        rootld.add=root
        t.append(rootld)
        pos=0
        for child in root:
            self.computeLD(t,child,rootld,pos,level+1)
            pos=pos+1
        return t

    def computeTED(self):
        rows=len(self.tree1ld)
        cols=len(self.tree2ld)
        chmatrix=np.zeros((rows,cols))
        for i in range(1,rows):
            chmatrix[i,0]=chmatrix[i-1,0]+1
        for j in range(1,cols):
            chmatrix[0,j]=chmatrix[0,j-1]+1
        for i in range(1,rows):
            for j in range(1,cols):
                insert = sys.maxsize
                update = sys.maxsize
                delete = sys.maxsize
                if self.tree1ld[i].depth == self.tree2ld[j].depth:
                    if self.tree1ld[i].label == self.tree2ld[j].label:
                        update=chmatrix[i-1,j-1]
                    else:
                        update=chmatrix[i-1,j-1]+1
                if j==cols-1 or (j<cols-1 and self.tree2ld[i+1].depth<=self.tree1ld[i].depth):
                    delete=chmatrix[i-1,j]+1
                if i==rows-1 or (i<rows-1 and self.tree1ld[i+1].depth<=self.tree2ld[j].depth):
                    insert=chmatrix[i,j-1]+1
                chmatrix[i,j]=min(insert,delete,update)
        print(chmatrix[rows - 1, cols - 1])
        return chmatrix

    def editScript(self,matrix):
        rows=matrix.shape[0]
        cols=matrix.shape[1]
        i=rows-1
        j=cols-1
        while i>0 and j>0:
            if (matrix[i,j]==matrix[i-1,j]+1) and (j==cols-1 or (j<cols-1 and self.tree2ld[i+1].depth<=self.tree1ld[i].depth)):
                print("del",i)
                i=i-1
            elif (matrix[i,j]==matrix[i,j-1]+1) and (i==rows-1 or (i<rows-1 and self.tree1ld[i+1].depth<=self.tree2ld[j].depth)):
                print("ins",j)
                j=j-1
            else:
                if(self.tree1ld[i].label!=self.tree2ld[j].label):
                    print("update", i, self.tree2ld[j].label)
                i=i-1
                j=j-1

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




