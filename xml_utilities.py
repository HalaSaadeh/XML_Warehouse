import sys
import urllib
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as et

import numpy as np




class TwoTrees():
    path1=None
    path2=None
    tree1=""
    tree2=""
    tree1ld=[]
    tree2ld=[]
    es=None
    chawathe_matrix=None
    def __init__(self, path1, path2):
        self.path1=path1
        self.path2=path2
        self.tree1 = ""
        self.tree2 = ""
        self.tree1= self.docpreprocess(path1,False)
        self.tree2=self.docpreprocess(path2,True)
        self.tree1ld = []
        self.tree2ld = []
        self.tree1ld.append(LDPair("0",-1,None,0,None))
        self.tree2ld.append(LDPair("0", -1, None, 0,None))
        self.tree1ld = self.computeLD(self.tree1ld, self.tree1, None, 0)
        self.tree2ld = self.computeLD(self.tree2ld, self.tree2, None, 0)
        open("editscriptfw.xml", "w").close()

    def docpreprocess(self,path,n):
        def prep(t):
            if t is None:
                return None
            newtree=Element(t.tag)
            for k,v in t.attrib.items():
                attrchild = SubElement(newtree, '@' + k)
                attrcontent = SubElement(attrchild, v)
            for child in t:
                newtree.append(prep(child))
            if t.text is not None:
                content = t.text
                contentwords = content.split()
                for word in contentwords:
                    c = SubElement(newtree, "( " + word)
            return newtree

        if n:
            v = open(path, "r")
            f = v.read()
        else:
            f= urllib.request.urlopen(path).read()

        t = et.fromstring(f)
        tree=prep(t)
        return tree

    def computeES(self):
        chawathe_matrix=self.computeTED()
        es = self.editScript(chawathe_matrix)
        return es

    def computeLD(self,t,root,parent,pos,level=0):
        rootld=LDPair(root.tag,level,parent,pos,root)
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
                if j==cols-1 or (j<cols-1 and self.tree2ld[j+1].depth<=self.tree1ld[i].depth):
                    delete=chmatrix[i-1,j]+1
                if i==rows-1 or (i<rows-1 and self.tree1ld[i+1].depth<=self.tree2ld[j].depth):
                    insert=chmatrix[i,j-1]+1
                chmatrix[i,j]=min(insert,delete,update)
        print(chmatrix[rows - 1, cols - 1])
        return chmatrix

    def editScript(self,matrix):
        es = None
        es = Element("editscript")
        for a in es:
            print(a)
        rows=matrix.shape[0]
        cols=matrix.shape[1]
        i=rows-1
        j=cols-1
        for a in self.tree1ld:
            print(a.label)
        while i>0 and j>0:
            if (matrix[i,j]==matrix[i-1,j]+1) and (j==cols-1 or (j<cols-1 and self.tree2ld[j+1].depth<=self.tree1ld[i].depth)):
                es.insert(0, Element("delete"))
                newelem = es[0]
                parent = getParent(self.tree1ld[i], "")
                parentpath=parent.replace('.', '/')
                parentpath=parentpath.replace('@', '&commat;')
                parentpath = parentpath[(len(self.tree1.tag)):]
                parentpath=parentpath[0:len(parentpath)-1]
                parents=self.tree1.findall("./"+parentpath)
                m=""
                for k in range(len(parents)):
                    if parents[k] is (self.tree1ld[i]).parent.add:
                        m=k
                newelem.insert(0,Element("indexParent",{"indexParent": str(m)}))
                newelem.insert(1,Element("label", {"label": str(self.tree1ld[i].label) }))
                newelem.insert(2,Element("parent",  {"parent": parent}));
                newelem.insert(3,Element("pos", {"pos": str(self.tree1ld[i].pos)}))
                i=i-1
            elif (matrix[i,j]==matrix[i,j-1]+1) and (i==rows-1 or (i<rows-1 and self.tree1ld[i+1].depth<=self.tree2ld[j].depth)):
                parent = getParent(self.tree1ld[i], "")
                parentpath = parent.replace('.', '/')
                parentpath=parentpath.replace('@', '&commat;')
                parentpath = parentpath[(len(self.tree1.tag)):]
                parentpath = parentpath[0:len(parentpath) - 1]
                parents = self.tree1.findall("./" + parentpath)
                m = ""
                for k in range(len(parents)):
                    if parents[k] is (self.tree1ld[i]).parent.add:
                        m = k
                es.insert(0, Element("insert"))
                newelem = es[0]
                newelem.insert(0,Element("indexParent", {"indexParent": str(m)}))
                newelem.insert(1,Element("label", {"label": str(self.tree2ld[j].label)}))
                newelem.insert(2,Element("parent", {"parent": getParent(self.tree2ld[j],"")}));
                newelem.insert(3,Element("pos", {"pos": str(self.tree2ld[j].pos)}))
                j=j-1
            else:

                if(self.tree1ld[i].label!=self.tree2ld[j].label):
                    parent = getParent(self.tree1ld[i], "")
                    parentpath = parent.replace('.', '/')
                    parentpath = parentpath.replace('@', '&commat;')
                    parentpath = parentpath[(len(self.tree1.tag)):]
                    parentpath = parentpath[0:len(parentpath) - 1]
                    parents = self.tree1.findall("./" + parentpath)
                    m = ""
                    for k in range(len(parents)):
                        print(parents[k])
                        if parents[k] is (self.tree1ld[i]).parent.add:
                            m = k
                    es.insert(0, Element("update"))
                    newelem=es[0]
                    newelem.insert(0,Element("indexParent", {"indexParent": str(m)}))
                    newelem.insert(1,Element("initial", {"initial": self.tree1ld[i].label}))
                    newelem.insert(2,Element("new", {"new": str(self.tree2ld[j].label)}))
                    newelem.insert(3,Element("parent", {"parent": parent}));
                    newelem.insert(4,Element("pos", {"pos": str(self.tree1ld[i].pos)}))
                i=i-1
                j=j-1
        tree = et.ElementTree()
        tree._setroot(es)
        print(tree)
        tree.write("editscriptfw.xml")

class PatchingUtil():
    tree1=""
    tree1ld=[]
    es=None
    def __init__(self,pathfile, pathES):
        self.tree1 = ""
        self.tree1 = self.docpreprocess(pathfile, False)
        self.tree1ld = []
        self.tree1ld.append(LDPair("0", -1, None, 0, None))
        self.tree1ld = self.computeLD(self.tree1ld, self.tree1, None, 0)
        self.es=self.reverseES(pathES)


    def docpreprocess(self,path,n):
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

        if n:
            v = open(path, "r")
            f = v.read()
        else:
            f= urllib.request.urlopen(path).read()

        t = et.fromstring(f)
        tree=prep(t)
        return tree

    def computeLD(self, t, root, parent, pos, level=0):
        rootld = LDPair(root.tag, level, parent, pos, root)
        rootld.add = root
        t.append(rootld)
        pos = 0
        for child in root:
            self.computeLD(t, child, rootld, pos, level + 1)
            pos = pos + 1
        return t



    def reverseES(self, pathES):
        oldEs=urllib.request.urlopen(pathES).read()
        es=et.fromstring(oldEs)
        reverse = et.ElementTree()
        rev = Element("editscript")
        reverse._setroot(rev)
        for child in es:
            if child.tag == "insert":
                newElem = Element("delete")
                rev.append(newElem)
                for a in child:
                    newElem.append(a)
            if child.tag == "delete":
                newElem = Element("insert")
                rev.append(newElem)
                for a in child:
                    newElem.append(a)
            if child.tag == "update":
                newElem = Element("update")
                rev.append(newElem)
                for a in child:
                    if a.tag == "parent" or a.tag=="indexParent" or a.tag=="pos":
                        newElem.append(a)
                    elif a.tag=="initial":
                        newElem.append(Element("new", {"new": a.attrib["initial"]}))
                    elif a.tag=="new":
                        newElem.append(Element("initial", {"initial" : a.attrib["new"]}))

        open("editscriptbw.xml", "w").close()
        reverse.write("editscriptbw.xml")

    def patch(self):
        v = open("editscriptbw.xml", "r")
        file = v.read()
        es = et.fromstring(file)
        print("hi")
        for command in es:
            if command.tag =="delete":
                parentpath=command.find('.//parent').attrib["parent"]
                label=command.find('.//label').attrib["label"]
                parentpath=parentpath.replace('.','/')
                parentpath = parentpath[(len(self.tree1.tag)):]
                parentpath=parentpath[0:len(parentpath)-1]
                parents=self.tree1.findall("./"+parentpath)
                parent=parents[command.find('.//indexParent').attrib["indexParent"]]
                index = int(command.find('.//pos').attrib["pos"])
                child=parent[index]
                parent.remove(child)
            if command.tag =="insert":
                parentpath=command.find('.//parent').attrib["parent"]
                label=command.find('.//label').attrib["label"]
                parentpath=parentpath.replace('.','/')
                parentpath = parentpath[(len(self.tree1.tag)):]
                parentpath=parentpath[0:len(parentpath)-1]
                parents=self.tree1.findall("./"+parentpath)
                parent=parents[int(command.find('.//indexParent').attrib["indexParent"])]
                print(parent.tag)
                index=int(command.find('.//pos').attrib["pos"])
                parent.insert(index, Element(label))
            if command.tag =="update":
                parentpath=command.find('.//parent').attrib["parent"]
                initial=command.find('.//initial').attrib["initial"]
                new=command.find('.//new').attrib["new"]
                parentpath=parentpath.replace('.','/')
                parentpath = parentpath[(len(self.tree1.tag)):]
                parentpath=parentpath[0:len(parentpath)-1]
                parents=self.tree1.findall("./"+parentpath)
                parent=parents[int(command.find('.//indexParent').attrib["indexParent"])]
                index = int(command.find('.//pos').attrib["pos"])
                child=parent[index]
                child.tag=new
        self.postprocess()

    def postprocess(self):
        def docpostprocessing(t):
            if t is None:
                return None
            newtree = Element(t.tag)
            for child in t:
                if child.tag[0] == '@':
                    for attrchild in child:
                        content = attrchild.tag
                        newtree.attrib[child.tag[2:]]=content
                elif child.tag[0] == '(':
                    out = ""
                    if not newtree.text is None:
                        out = newtree.text + ""
                    out = out + " "+ child.tag[2:]
                    newtree.text = out
                else:
                    newtree.append(docpostprocessing(child))
            return newtree
        newtree=docpostprocessing(self.tree1)
        tree = et.ElementTree()
        tree._setroot(newtree)
        open("patched.xml", "w").close()
        tree.write("patched.xml")




class LDPair():
    label=""
    depth=0
    parent=None
    pos=0
    id=0
    add=None
    def __init__(self,label, depth,parent,pos,add):
        self.label=label
        self.depth=depth
        self.parent=parent
        self.pos=pos
        self.add=add
    def printld(self):
        print(self.label, ",",self.depth)

def getParent(ld,out):
    if ld.parent is None:
        return out
    out=ld.parent.label+"."+out
    return getParent(ld.parent, out)





