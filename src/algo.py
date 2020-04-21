def computeFail(pattern):
    m = len(pattern)
    fail = [0 for x in range(m)]
    i, j = 1, 0
    while i < m:
        if pattern[j].lower() == pattern[i].lower():
            fail[i] = j + 1
            i += 1
            j += 1
        elif j > 0:
            j = fail[j-1]
        else:
            fail[i] = 0
            i += 1
    return fail

def KMP(text, pattern):
    n, m = len(text), len(pattern)
    fail = computeFail(pattern)
    i, j = 0, 0
    while i < n:
        if pattern[j].lower() == text[i].lower():
            if j == m - 1:
                return i - m + 1
            i += 1
            j += 1
        elif j > 0:
            j = fail[j-1]
        else:
            i += 1
    return -1

def buildLast(pattern):
    last = [-1 for x in range(128)]
    for i in range(len(pattern)):
        last[ord(pattern[i].lower())] = i
    return last

def BM(text, pattern):
    last = buildLast(pattern)
    n, m = len(text), len(pattern)
    i = m - 1
    if i > n - 1:
        return -1
    j = m - 1
    while True:
        if (pattern[j].lower() == text[i].lower()):
            if (j == 0):
                return i
            else:
                i -= 1
                j -= 1
        else:
            lo = last[ord(text[i].lower())]
            i += m - min(j, lo + 1)
            j = m - 1
        if (i > n - 1):
            break
    return -1