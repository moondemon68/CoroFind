import re, os, random, string, json
from nltk.tokenize import sent_tokenize
from algo import BM, KMP
from flask import Flask, render_template, render_template_string, request, redirect

app = Flask(__name__)

results_dir = os.path.join(app.instance_path, 'results')
if not os.path.exists(os.path.dirname(results_dir)):
    os.makedirs(results_dir)

keyword = ''
algorithm = ''
fileNames = []
foundSentences = []
foundCounts = []
foundDates = []
code = ''

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result/<fileCode>')
def result(fileCode):
    global keyword, algorithm, code
    if not os.path.isfile(results_dir + '/' + fileCode):
        return render_template_string(fileCode)
    data = json.load(open(results_dir + '/' + fileCode))
    data = data[0]
    keyword = data['keyword']
    algorithm = data['algorithm']
    fileNames = data['fileNames']
    foundSentences = data['foundSentences']
    foundCounts = data['foundCounts']
    foundDates = data['foundDates']
    code = data['code']
    return render_template('result.html', keyword = keyword, algorithm = algorithm, fileNames = fileNames, foundSentences = foundSentences, foundCounts = foundCounts, foundDates = foundDates, code = code)

@app.route('/upload/text', methods=['POST'])
def uploadText():
    global keyword, algorithm, code
    clear()
    keyword = request.form['keywordText']
    algorithm = request.form['algorithmText']
    inputText = request.form['inputText']

    fileNames.append('Text')
    sentences = sent_tokenize(inputText)
    foundSentence, foundCount, foundDate = findSentence(sentences, algorithm, keyword)
    foundSentences.append(foundSentence)
    foundCounts.append(foundCount)
    foundDates.append(foundDate)
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    data = [{'keyword': keyword, 'algorithm': algorithm, 'fileNames': fileNames, 'foundSentences': foundSentences, 'foundCounts': foundCounts, 'foundDates': foundDates, 'code': code}]
    with open(results_dir + '/' + code, 'w') as file:
        json.dump(data, file)
    return redirect('/result/' + code)

@app.route('/upload/file', methods=['POST'])
def uploadFile():
    global keyword, algorithm, code
    clear()
    keyword = request.form['keywordFile']
    algorithm = request.form['algorithmFile']
    inputFiles = request.files.getlist('inputFiles')
    for file in inputFiles:
        fileNames.append(file.filename)
        text = file.read().decode('utf-8')
        sentences = sent_tokenize(text)
        foundSentence, foundCount, foundDate = findSentence(sentences, algorithm, keyword)
        foundSentences.append(foundSentence)
        foundCounts.append(foundCount)
        foundDates.append(foundDate)
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    data = [{'keyword': keyword, 'algorithm': algorithm, 'fileNames': fileNames, 'foundSentences': foundSentences, 'foundCounts': foundCounts, 'foundDates': foundDates, 'code': code}]
    with open(results_dir + '/' + code, 'w') as file:
        json.dump(data, file)
    return redirect('/result/' + code)

def clear():
    global keyword, algorithm, code
    keyword = ''
    algorithm = ''
    code = ''
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
    regex = re.search('(?:^|\s)((?:\d*\.*)*\d+)\s(?:[\(\-\s\w,:])*?' + keyword + '|' + keyword + '(?:[\)\-\s\w,:])*?\s((?:\d*\.*)*\d+)(?:$|\s|.|,)', sentence, flags=re.IGNORECASE)
    if regex is not None:
        if regex.group(1) is not None:
            return regex.group(1)
        if regex.group(2) is not None:
            return regex.group(2)
    return '-'

def findDate(sentence, keyword):
    # DD Bulan
    regex = re.search('(\d\d?\s(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|November|Desember|Jan|Feb|Mar|Apr|Mei|Jun|Jul|Aug|Sep|Okt|Nov|Des)).+(?:[\(\-\s\w,":])*?' + keyword + '|' + keyword + '(?:[\(\-\s\w,":])*?(\d\d?\s(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|November|Desember|Jan|Feb|Mar|Apr|Mei|Jun|Jul|Aug|Sep|Okt|Nov|Des)).+', sentence, flags=re.IGNORECASE)
    if regex is not None:
        if regex.group(1) is not None:
            return regex.group(1)
        if regex.group(2) is not None:
            return regex.group(2)
    # DD/MM/YYYY
    regex = re.search('\(?(\d\d?\/\d\d?\/?\d?\d?\d?\d?)\)?.+(?:[\(\-\s\w,":])*?' + keyword + '|' + keyword + '(?:[\(\-\s\w,":])*?\(?(\d\d?\/\d\d?\/?\d?\d?\d?\d?)\)?.+', sentence, flags=re.IGNORECASE)
    if regex is not None:
        if regex.group(1) is not None:
            return regex.group(1)
        if regex.group(2) is not None:
            return regex.group(2)
    return '-'