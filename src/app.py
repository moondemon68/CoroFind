from nltk.tokenize import sent_tokenize
from algo import BM, KMP
from flask import Flask, render_template, request, redirect
import re

app = Flask(__name__)

keyword = ''
algorithm = ''
fileNames = []
foundSentences = []
foundCounts = []
foundDates = []

@app.route('/')
def home():
    return render_template('index.html', keyword = keyword, algorithm = algorithm, fileNames = fileNames, foundSentences = foundSentences, foundCounts = foundCounts, foundDates = foundDates)

@app.route('/upload', methods=['POST'])
def upload():
    global keyword, algorithm
    clear()
    keyword = request.form['keyword']
    algorithm = request.form['algorithm']
    inputFiles = request.files.getlist('inputFiles')
    for file in inputFiles:
        fileNames.append(file.filename)
        text = file.read().decode('utf-8')
        sentences = sent_tokenize(text)
        foundSentence, foundCount, foundDate = findSentence(sentences, algorithm, keyword)
        foundSentences.append(foundSentence)
        foundCounts.append(foundCount)
        foundDates.append(foundDate)
    return redirect('/')

def clear():
    global keyword, algorithm
    keyword = ''
    algorithm = ''
    fileNames.clear()
    foundSentences.clear()
    foundCounts.clear()
    foundDates.clear()

def findSentence(sentences, algorithm, keyword):
    result = []
    count = []
    date = []
    newsDate = '-'
    # Find date from any sentence, starting from top (news title)
    for sentence in sentences:
        newsDate = findDate(sentence, '')
        if newsDate != '-':
            break
    for sentence in sentences:
        if algorithm == 'KMP':
            index = KMP(sentence, keyword)
            if index != -1:
                result.append(highlight(sentence, keyword))
                count.append(findCount(sentence, keyword))
                date.append(findDate(sentence, keyword))
                if date[-1] == '-':
                    date[-1] = newsDate
        elif algorithm == 'BM':
            index = BM(sentence, keyword)
            if index != -1:
                result.append(highlight(sentence, keyword))
                count.append(findCount(sentence, keyword))
                date.append(findDate(sentence, keyword))
                if date[-1] == '-':
                    date[-1] = newsDate
        else:
            if re.search(keyword, sentence, flags=re.IGNORECASE):
                result.append(highlight(sentence, keyword))
                count.append(findCount(sentence, keyword))
                date.append(findDate(sentence, keyword))
                if date[-1] == '-':
                    date[-1] = newsDate
    return result, count, date

def highlight(sentence, keyword):
    bold = "<b>" + keyword + "</b>"
    return re.sub(keyword, bold, sentence, flags=re.IGNORECASE)

def findCount(sentence, keyword):
    regex = re.search('(?:^|\s)((?:\d*\.*)*\d+)\s(?:[\(\-\s\w,])*?' + keyword + '|' + keyword + '(?:[\)\-\s\w,])*?\s((?:\d*\.*)*\d+)(?:$|\s|.|,)', sentence, flags=re.IGNORECASE)
    if regex is not None:
        if regex.group(1) is not None:
            return regex.group(1)
        if regex.group(2) is not None:
            return regex.group(2)
    return '-'

def findDate(sentence, keyword):
    # DD Bulan
    regex = re.search('(\d\d?\s(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|November|Desember|Jan|Feb|Mar|Apr|Mei|Jun|Jul|Aug|Sep|Okt|Nov|Des)).+(?:[\(\-\s\w,"])*?' + keyword + '|' + keyword + '(?:[\(\-\s\w,"])*?(\d\d?\s(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|November|Desember|Jan|Feb|Mar|Apr|Mei|Jun|Jul|Aug|Sep|Okt|Nov|Des)).+', sentence, flags=re.IGNORECASE)
    if regex is not None:
        if regex.group(1) is not None:
            return regex.group(1)
        if regex.group(2) is not None:
            return regex.group(2)
    # DD/MM/YYYY
    regex = re.search('\(?(\d\d?\/\d\d?\/?\d?\d?\d?\d?)\)?.+(?:[\(\-\s\w,"])*?' + keyword + '|' + keyword + '(?:[\(\-\s\w,"])*?\(?(\d\d?\/\d\d?\/?\d?\d?\d?\d?)\)?.+', sentence, flags=re.IGNORECASE)
    if regex is not None:
        if regex.group(1) is not None:
            return regex.group(1)
        if regex.group(2) is not None:
            return regex.group(2)
    return '-'