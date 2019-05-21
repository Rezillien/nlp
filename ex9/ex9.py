from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

data_path = Path("./out")
data_files = data_path.glob("*.txt.ccl")
bills = np.random.choice(list(data_files), 100)
print("<ex4>")
#ls out/ | shuf | head -n+100 | xargs -I{} mv out/{} random
print("<ex5>")
random_path = Path("./random")
random_files = random_path.glob("*.txt.ccl")


all = []

for f in list(random_files):
    file=open(f, "r")
    root = ET.parse(file).getroot()
    for i in root:
        for j in i:
            e = dict()
            for k in jL
                if k.tag=="tok":
                    token = ""
                    for l in k:
                        if l.tag=="orth":
                            token=l.text
                            break
                    for l in k:
                        if l.tag == "ann" and l.text != "0":
                            e[(e.attrib["chan"], e.text)]=e.get((e.attrib["chan"], e.text), [])+[token]




