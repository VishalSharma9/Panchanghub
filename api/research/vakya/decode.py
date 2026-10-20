import re,unicodedata
V="गीर्नः श्रेयः|धेनव श्री|रुद्रस्तु नम्यः|भवो हि याज्यः|धन्येयं नारी|धनवान् पुत्रः|गुह्या सुरा राज्ञा|बालेन कुलम्|धनुर्भिः खलैः|दश सूनवः|होमस्य स्रुवः|दीनास्ते नृणाम्|मुखं नारीणाम्|भवभग्नास्ते|श्रीर्निधीयते|शं किल नाथः".split("|")
D={}
for g,s in [("कखगघङचछजझञ",1),("टठडढणतथदधन",1),("पफबभम",1),("यरलवशषसहळ",1)]:
    for i,c in enumerate(g): D[c]=(i+1)%10
VIR="\u094d"
def digits(w):
    out=[]; w=w.replace(" ","")
    chars=list(w)
    for i,c in enumerate(chars):
        if c in D:
            if i+1<len(chars) and chars[i+1]==VIR: continue
            out.append(D[c])
        elif c in "अआइईउऊएऐओऔ": out.append(0)
    return out
def val(w):
    d=digits(w); m=d[1]*10+d[0]; deg=d[3]*10+d[2]; sg=int("".join(map(str,d[4:][::-1]))) if len(d)>4 else 0
    return sg*30+deg+m/60, (sg,deg,m), d
if __name__=="__main__":
    for i,w in enumerate(V,1): print(i,w,val(w))
