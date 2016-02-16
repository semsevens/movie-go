#-*- coding: utf-8 -*-

def fuzzyMatch(strA, strB):
    count = 0
    shortLen = 0
    result = 0.0
    if len(strA) < len(strB):
        shortLen = len(strA)
        for b in strB:
            for a in strA:
                if a == b:
                    count += 1
    else:
        shortLen = len(strB)
        for a in strA:
            for b in strB:
                if b == a:
                    count += 1
    if shortLen != 0:
        result = count * 100 / shortLen
    else:
        result = 0
    # print('@@@@@@@@@@@@@')
    # print(strA)
    # print(strB)
    # print(result)
    # print('@@@@@@@@@@@@@')
    return result
