from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as et

class TwoTrees():
    path1=None
    path2=None
    tree1=""
    tree2=""
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



