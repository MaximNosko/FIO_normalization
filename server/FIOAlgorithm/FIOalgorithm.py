
# coding: utf-8

# In[ ]:


import re
import copy


# In[2]:


#Используемые константы

pathDirectory = "./FIOAlgorithm/" #Путь к папке, где хранятся все базы

surnamesFile = "surnames.csv" #Имя файла с фамилиями

namesFile = "namesAll.csv" #Имя файла с именами

patronymicsFile = "patronymics.csv" #Имя файла с отчествами

roundFactorDefiningAfterStrict = 5 
#Перед проверкой нечетким поиском, мы определяем можем ли мы что-то определить после строгой проверки
#Для этого сравниваем все результаты, считая что если значение в 10**n раз меньше чем максимум, 
# то сичитать его нулем, не учитывать

allowedDistanceInDamerauCheck = 1
#Максимальное расстояние между проверяемым словом и словом в словаре при проверке нечетким поиском
#+ можно сделать отдельное для каждого типа части речи (+возможно потом рассчитывать его еще учитывая длину слова)
#Раньше значение было 2, но слишком много влезало ненужных фамилий

statisticsFactor = 0.00005
#Коэффициент влияния статистики на результат

roundAproximationForRecursionStart = 5
#Начальная степень округления для проверки рекурсией

roundAproximationForRecursionEnd = 1
#Конечная степень округления для проверки рекурсией (меньше не округлять)

maxDistanceInReplaceCheck = 1
#Максимальная разница длин исходного слова и слова в списке при нечетком поиске

probabilityForFoundWordsInReplace = 1
#Коэффициент, во сколько раз уменьшается вероятность слова, при нахождении его в нечетком поиске

#Стоимость соответсвующего действия в подсчете расстояния Дамерау-Левенштейна 
damerauDeleteCost = 1
damerauInsertCost = 1
damerauReplaceCost = 1
damerauTransposeCost = 1

grammaFactor = 0.000000001
#Коэффициент влияния проверки по грамматике на результат

grammaSurnameFactor = 0.0001
#Коэффициент влияния проверки фамилии по грамматике на результат 
# (т.к. многие фамилии отсутствуют в базе, данный коэффициент имеет такой большой вес)

grammaPatronymicFactor = 0#.00001
#Коэффициент влияния проверки отчества по грамматике на результат

qualityCheck = 0.0000001
#Если частота слова меньше заданной, то оно считается подозрительно редким

roundingDegree = 7
#Степень округления строгой матрицы: исключает слишком редкие элементы

genderTuple = ('МЖ', 'М', 'Ж','Несоответствие') 
#Используемые значений пола

typesOfMistakes = ("все отлично", "изменили слово", "слишком редкое слово", "слово которого нет в базах", 
                   "исправлено сокращение имени", "несоответствие пола")
#Виды результатов применения обработки


# In[3]:


def CSVtoDict(filePath):
    import csv, re    
    input_file = open(filePath,'r')
    reader = csv.DictReader(input_file, delimiter=';')
    dict_list = []
    for line in reader:
        dict_list.append(line)
    
    headings = list(dict_list[0].keys())
    dictNew = {}
    for el in dict_list:
        newEl = el.copy()
        newEl.pop("key")
        dictNew[el["key"]] = newEl
    
    if "probability" in headings:
        for el in dictNew:
            dictNew[el]["probability"] = float(dictNew[el]["probability"])
    if "frequency" in headings:
        for el in dictNew:
            dictNew[el]["frequency"] = int(dictNew[el]["frequency"])
    if "full_form" in headings:
        for el in dictNew:
            dictNew[el]["full_form"] = re.findall(r'[абвгдеёжзийклмнопрстуфхцчшщъыьэюя]\w+', dictNew[el]["full_form"])
    
    return dictNew

#Записывает в CSV файл наши словари
def DictToCSV(filePath, dictToWrite):
    import csv 
    with open(filePath, 'w', newline='') as csvfile:
        headings = ["key"]+list(dictToWrite[list(dictToWrite.keys())[0]].keys())
        csvWriter = csv.writer(csvfile, delimiter=';')
        csvWriter.writerow(headings)
        for s in dictToWrite:
            tempList = [s] + list(dictToWrite[s].values())
            csvWriter.writerow(tempList)

#Преобразует словарь в два дерева - с прямым и обратным порядком слов
def DictIntoDatrie(dictToDo):
    import datrie
    ALPHABET = u'-АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    directTrie = datrie.BaseTrie(ALPHABET)
    reverseTrie = datrie.BaseTrie(ALPHABET)
    for element in dictToDo:
        directTrie[element] = dictToDo[element]["frequency"]
        reverseTrie[element[::-1]] = dictToDo[element]["frequency"]
    # directTrie.save('directTrie.trie')
    # directTrie.save('reverseTrie.trie')
    return directTrie, reverseTrie


# In[4]:


#Работа с базами, загрузка и обработка из CSV файлов
def ReadAllFromCSV():
    surnames = CSVtoDict(pathDirectory+surnamesFile)
    names = CSVtoDict(pathDirectory+namesFile)
    patronymics = CSVtoDict(pathDirectory+patronymicsFile)
    
    bases = [surnames, names, patronymics] 
    
    surnamesTrie, surnamesTrieReverse = DictIntoDatrie(surnames)
    namesTrie, namesTrieReverse = DictIntoDatrie(names)
    patronymicsTrie, patronymicsTrieReverse = DictIntoDatrie(patronymics)
    
    tries = [surnamesTrie, namesTrie, patronymicsTrie]
    triesReverse = [surnamesTrieReverse, namesTrieReverse, patronymicsTrieReverse]


# In[5]:


#def ReadAllFromFiles():
#Работа с базами, загрузка и обработка из pickle и trie
import pickle

path_to_surnames = pathDirectory +"surnames.pickle"
#path_to_names = pathDirectory +"names.pickle"
path_to_names = pathDirectory +"namesAll.pickle"
path_to_patronymics = pathDirectory +"patronymics.pickle"
with open(path_to_surnames,"rb") as f:
    surnames=pickle.load(f)
with open(path_to_names,"rb") as f:
    names=pickle.load(f)
with open(path_to_patronymics,"rb") as f:
    patronymics=pickle.load(f)  

bases = [surnames, names, patronymics] 

#Загрузка деревьев
import datrie

surnamesTrie = datrie.BaseTrie.load(pathDirectory + 'surnamesTrie.trie')
# namesTrie = datrie.BaseTrie.load('namesTrie.trie')
namesTrie = datrie.BaseTrie.load(pathDirectory + 'namesAllTrie.trie')
patronymicsTrie = datrie.BaseTrie.load(pathDirectory + 'patronymicsTrie.trie')

tries = [surnamesTrie, namesTrie, patronymicsTrie]

surnamesTrieReverse = datrie.BaseTrie.load(pathDirectory + 'surnamesTrieReverse.trie')
# namesTrieReverse = datrie.BaseTrie.load('namesTrieReverse.trie')
namesTrieReverse = datrie.BaseTrie.load(pathDirectory + 'namesAllTrieReverse.trie')
patronymicsTrieReverse = datrie.BaseTrie.load(pathDirectory + 'patronymicsTrieReverse.trie')

triesReverse = [surnamesTrieReverse, namesTrieReverse, patronymicsTrieReverse]   


# In[6]:


def ExcludeDefined(matrix,order):
    #Исключаются элементы матрицы, которые уже определены в order
    #Делается это с помощью обнуления больше не нужных элементов в строке уже определенного элемента
    for i in range(len(matrix)):
        if order[i]!=None:
            for j in range(3):
                if order[i] != j:
                    matrix[i][j]=0
                else: matrix[i][j]=1


# In[7]:


def RoundMatrix(matrix, n):
    #Производится округление матрицы с приблежением n
    #Под округлением понимается: если значения элементов строки/столбца меньше значения максимального элемента в 10**n раз, 
    # то их можно считать несущественными и округлить до нуля
    N = len(matrix)
    for i in range(N):
        for j in range(3):
            if matrix[i][j]*10**n<max(matrix[i]):
                matrix[i][j] = 0
    maxColumns = [0,0,0]
    for j in range(3): 
        for i in range(N):
            if matrix[i][j]>matrix[maxColumns[j]][j]:
                maxColumns[j] = i
    
    for j in range(3): 
        for i in range(N): 
            if matrix[i][j]*10**n<matrix[maxColumns[j]][j]:
                matrix[i][j] = 0


# In[8]:


def GetOrder(matrix):
    #Определяет порядок элементов по матрице, исходя из гипотезы что в ней по одному элементу на строку
    N = len(matrix)
    order = []
    for i in range(N):
        order.append(None)
        for j in range(3):
            if matrix[i][j]!=0:
                order[i] = j
                break
    return order


# In[9]:


def GetComplexOrder(matrix, order):
    #Грубое определение порядка элементов по матрице
    #проверять по максимуму + исходя из количества слов
    N = len(matrix)
    for i in range(N):
        if order[i]==None:
            for j in range(3):
                if matrix[i][j]!=0:
                    order[i] = j
                    break
    return order


# In[10]:


def СheckMatrix(matrix):  
    #Проверяет матрицу: если в ней в одной строке по одному элементу, возвращает True
    N = len(matrix)
    for i in range(N):
        k = 0
        for j in range(3):
            if (matrix[i][j] != 0): k+=1
        if (k != 1):
            return False
    return True


# In[11]:


def StrictCheck(words): 
    #Строгая проверка: на вхождение слов в базы
    N = len(words)
    result = []
    for i in range(N):
        result.append([0,0,0])
        w = words[i].strip()
        for j in range(3):
            if w in bases[j]:
                result[i][j] = bases[j][w]["probability"]
    return result


# In[12]:


def damerauPy(s, t): #расстояние Дамерау-Левенштейна (расстояние с перестановкой)
    if s == t: return 0
    elif len(s) == 0: return len(t)
    elif len(t) == 0: return len(s)
    
    deleteCost = damerauDeleteCost
    insertCost = damerauInsertCost
    replaceCost = damerauReplaceCost
    transposeCost = damerauTransposeCost
    
    s = " "+s
    t = " "+t
    M = len(s)
    N = len(t)
    d = [list(range(N))]
    for i in range(1,M):
        d.append([])
        for j in range(N):
            d[i].append(0)
        d[i][0] = i
        
    for i in range(1,M):
        for j  in range(1,N):          
            # Стоимость замены
            if (s[i] == t[j]):
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = d[i-1][j-1] + replaceCost                   
            d[i][j] = min(
                             d[i][j],                               # замена
                             d[i-1][j] + deleteCost,                # удаление
                             d[i][j-1] + insertCost                 # вставка               
                         )
            if(i > 1 and j > 1 and s[i] == t[j-1] and s[i-1] == t[j]):
                d[i][j] = min(
                                  d[i][j],
                                  d[i-2][j-2] + transposeCost         # транспозиция
                             )
    return d[M-1][N-1]


# In[13]:


def forReplaceCheckTrie(w, index, mistakes = allowedDistanceInDamerauCheck):
    #Нечеткая проверка по деревьям

    wDirect, wReverse = w[:len(w)//2],w[len(w)//2+1:][::-1]

    listDirectFull, listReverseFull = tries[index].keys(wDirect),triesReverse[index].keys(wReverse)
    res = {'':0} #Словарь результатов
    
    #Перестановка центральных букв
    wMistakeInMiddle = w[:len(w)//2-1]+w[len(w)//2]+w[len(w)//2-1]+w[len(w)//2+1:]
    if wMistakeInMiddle in tries[index].keys():
        res[wMistakeInMiddle] = bases[index][wMistakeInMiddle]["probability"]*10**(-probabilityForFoundWordsInReplace*1) 
    
    #Отсечение лишних слов через мешок букв
    listDirect = []
    listReverse = []
    wBag = set(w)
    for l in listDirectFull:
        bs = set(l)
        if len(bs-wBag)<=mistakes and len(wBag-bs)<=mistakes:
            listDirect.append(l)
    for l in listReverseFull:
        bs = set(l)
        if len(bs-wBag)<=mistakes and len(wBag-bs)<=mistakes:
            listReverse.append(l)

    for l in listDirect:
        dist = damerauPy(w, l) #Подсчет расстояния
        if (dist <= mistakes):
            res[l] = bases[index][l]["probability"]*10**(-probabilityForFoundWordsInReplace*dist) 
    for lRev in listReverse:
        l = lRev[::-1]
        dist = damerauPy(w, l)
        if (dist <= mistakes): 
            res[l] = bases[index][l]["probability"]*10**(-probabilityForFoundWordsInReplace*dist)  

    iMax = ""
    for i in res:
        if res[i]>=res[iMax]: iMax = i
    
    return iMax, res[iMax]


# In[14]:


def grammaCheckSurnames(s):
    #Проверка окончаний фамилий
    pattern = '\w*(ов|ова|ев|ёв|ева|ёва|ив|ин|ина|ын|их|ых|ский|цкий|ая|ко|дзе'               '|онок|ян|ен|ук|юк|ун|ний|ный|чай|ий|ич|ов|ук|ик|цки|дзки|ан)$'
    
    if (re.match(pattern,s)): return 1
    else: return 0
    
def grammaCheckPatronymic(s):
    #Проверка окончаний отчеств
    pattern = '\w*(ович|евич|ич|овна|евна|ична|инична)$'
    if (re.match(pattern,s)):
        return 1
    else: return 0

def GrammaCheck(words):
    #Проверка по грамматике - проверяются окончания отчества и фамилии 
    # и возвращается матрица с элементами домноженными на соответсвующие коэффициенты
    #+возможно добавить разные веса для разных окончаний (частых и более редких)
    
    N = len(words)
    grammaRes = []
    for i in range(N):
        grammaRes.append([0,0,0])
        w = words[i]
        grammaRes[i][0] = grammaCheckSurnames(w)* grammaFactor * grammaSurnameFactor
        grammaRes[i][2] = grammaCheckPatronymic(w)*grammaFactor * grammaPatronymicFactor
    return grammaRes
    #Пока не используется:
    #для определения имени нет метода, но можно заполнять по методу исключения:
    # if flag:
    #     #По принципу исключения заполняет вероятности имен
    #     k = 0
    #     for i in range(N):
    #         flag = True
    #         for j in range(3):
    #             if (result[i][j] != 0): 
    #                 flag = False 
    #                 break
    #         if(flag):
    #             result[i][1] = 1
    #             k+=1
    #     if(k==0):
    #         for i in range(N): result[i][1] = 0.001*0.30
    #     elif(k>1): 
    #         for i in range(N): result[i][1] = 0.001*result[i][1]*0,9/k
    #     
    # return result


# In[15]:


#Матрицы значения статистики порядка слов

#               F     I    O
statistics1 = [[0.45,0.40,0.15]]
#               F     I    O
statistics2 = [[0.50,0.45,0.05],
               [0.30,0.30,0.30]]
#               F     I    O
statistics3 = [[0.50,0.45,0.05],
              [0.10,0.50,0.40],
              [0.40,0.05,0.55]]
#               F     I    O
statistics4 = [[0.30,0.15,0.05],
              [0.30,0.40,0.30],
              [0.20,0.40,0.30],
              [0.20,0.05,0.35]]

statistics = [statistics1,statistics2,statistics3,statistics4]

def SetStatistics(order):
    #Метод обновляет статистику с учетом результата выполнения алгоритма
    N = len(order)
    if N<=4:
        for i in range(N):
            for j in range(3):
                if (j == order[i]): 
                    statistics[N-1][i][j] += 0.002
                else: statistics[N-1][i][j] -= 0.001


# In[16]:


def CheckGender(result):
    #Метод определения пола по результату
    genderResult = [[],[],[]]
    
    for i in range(3):
        for r in result[i]:
            if r in bases[i]: 
                genderResult[i].append(genderTuple.index(bases[i][r]["gender"]))
    
    index = 0
    for i in range(3):
        for j in range(len(genderResult[i])):
            if index==genderResult[i][j] or index==0:
                index = genderResult[i][j]
            elif index!=genderResult[i][j] and genderResult[i][j]!=0:
                index = 3
                return genderTuple[index]
    return genderTuple[index]


# In[17]:


def ComplexOrder(matrix, order):
    #+ещё подредактировать этот метод
    
    #Из матрицы исключаются элементы, уже определенные в order
    ExcludeDefined(matrix,order)

    #проверяем можем ли мы однозначно определить все слова (в строке по одному значению)
    if СheckMatrix(matrix):
        return GetOrder(matrix)
    
    N = len(matrix)
    
    #Создаем массивы с индексами максимальных элементов по строкам и столбцам
    maxRows = []
    maxColumns = [0,0,0]
    for i in range(N):
        maxRows.append(0)
    
    for i in range(N):
        for j in range(3):
            if matrix[i][j]>matrix[i][maxRows[i]]: 
                maxRows[i] = j
            
    for j in range(3):
        for i in range(N):
            if matrix[i][j]>matrix[maxColumns[j]][j]: 
                maxColumns[j] = i

    #Если элемент максимален и в своей строке и в своем столбце, то считаем это значение правильным
    for i in range(N):
        for j in range(3):
            if maxRows[i]==j and maxColumns[j]==i:
                if order[i]==None:
                    order[i] = maxRows[i]
    
    #Подсчитываем количество определенных элементов
    #+возможно переместить этот блок ниже, после RecursiveProcessing
    n = order.count(None)
    if n==0:
        return order
    elif n<=N-2:
        #Если определено достаточное количетсво элементов, то оставшиеся мы можем определить методом исключения
        k = 0 #Количество неопределенных частей имени
        num = 0
        for j in range(3):
            if j not in order: 
                k+=1
                num = j
        #Если не определена только одна, то можно предположить, что её и следует сопоставить оставшемуся слову
        #Сопоставляется только в случае если его вероятность не равна 0 
        if k==1:
            for i in range(N):
                if order[i] == None and matrix[i][num]>0: 
                    order[i] = num
                    
        if order.count(None) == 0: return order

    #Исключаем опредленные элементы
    ExcludeDefined(matrix, order)
    #Выполняем проверку рекурсивным алгоритмом применяя округление
    matrix = RecursiveProcessing(matrix, None, True)
    
    return GetComplexOrder(matrix, order)


# In[18]:


def RecursiveProcessing(matrix, matrixOld = None, flag = False, aproximation = roundAproximationForRecursionStart): 
    #Рекурсивное изменение значений в матрице - преобразует матрицу 
    #  F  I  O               ` F  I  O
    # [[1,0,1],                [[0,0,1],
    #  [1,1,1],     в матрицу   [0,1,0],
    #  [1,0,0]]                 [1,0,0]]
    #Т.е. выбирает очевидные варианты
    
    #matrixOld - значение матрицы в предыдущей итерации. Если никаких изменений не было произведено, метод завершается
    #flag - нужно или не нужно использовать округление значений матрицы
    #aproximation - степень округления
    
    #Если никаких изменений не было произведено, или степень оркгуления достигла минимума, метод завершается
    if(matrix==matrixOld and not flag) or (aproximation==roundAproximationForRecursionEnd and flag): 
        return matrix 
    
    #Сохраняется текущее значение матрицы, для сравнения в следующей итерации
    matrixOld = copy.deepcopy(matrix)
    N = len(matrix)
    
    #Подсчитывается количество ненулевых элементов в каждом столбце
    countersColumns = []
    for j in range(3):
        countersColumns.append(0)
        for i in range(N):
            if matrix[i][j]!=0: countersColumns[j]+=1
    
    #Подсчитывается количество ненулевых элементов в каждой строке  
    countersRows = []
    for i in range(N):
        countersRows.append(0)
        for j in range(3):
            if matrix[i][j]!=0: countersRows[i]+=1
    
    #Если в каждой строке по одному значению, следовательно желаемое было достигнуто, найдены все слова
    if countersRows.count(1)== N: 
        return matrix
        #+ добавить проверку значений по столбцам np.array(countersColumns).sum()==N или all(element in countersColumns == N) 
    else:
        #Если есть один элемент, который является единственным в своем столбце, то обнуляются лишние элементы в его строке
        # [[0,0,1],    [[0,0,1],
        #  [1,1,1], ->  [0,1,0],
        #  [1,0,0]]     [1,0,0]]
        for j in range(3):
            if countersColumns[j]==1:
                m = -1
                for i in range(N):
                    if matrix[i][j]!=0:
                        m = i
                        break
                if m > -1:
                    for k in range(3):
                        #элементы обнуляются с условием - если они в свою очередь не являются единственными в своем столбце
                        if k!=j and countersColumns[k]>1:
                            matrix[m][k] = 0
        
        #Проводится то же самое что и перед этим, но уже для строк а не столбцов
        for i in range(N):
            if countersRows[i]==1:
                for j in range(3):
                    m = -1
                    if matrix[i][j]!=0:
                        m = j
                        break
                    if m > -1:
                        for k in range(N):
                            if k!=i and countersRows[k]>1: 
                                matrix[k][m] = 0    
        
        #Если необходимо выполнение метода с округлением элементов, то оно выполняется, 
        # и при последующем вызове метода, коэффициент округления будет меньше на единицу
        #+возможно вызывать его не здесь, а только при условии что не происходит никаких изменений в методе
        if flag:
            RoundMatrix(matrix, aproximation)
        return RecursiveProcessing(matrix, matrixOld, flag, aproximation-1)


# In[19]:


def preprocessing(line):
    #Предобработка входной строки
    #На вход получает строку символов, на выходе возвращает список обработанных слов
    t = line.lower()
    wordsOriginal = re.findall(r"[\w']+", t)
    
    #+обработка фамильных приставок (фон, оглы ...), не рассматривать их как отдельное слово
    
    wasYO = False #Была ли вообще Ё. Пока что не используется. 
    # На будущее - если человек напечатал Ё, то скорее всего она там должна быть.
    words = copy.deepcopy(wordsOriginal)
    for i in range(len(words)):
        if "ё" in words[i]:
            wasYO = True
            words[i] = words[i].replace('ё','е')
    
    return words


# In[21]:


def FixYoForm(result):        
    for i in range(len(result)):
        for j in range(len(result[i])):
            if result[i][j] in bases[i] and bases[i][result[i][j]]["yoform"]!="":
                result[i][j] = bases[i][result[i][j]]["yoform"]


# In[20]:


def WordsProcessing(line):
    
    words = preprocessing(line)
    N = len(words) #Количество слов
    qualityFlag = []
    
    #Создаем массив для записи результатов
    #Результат хранится в виде: [[фамилия1,фамилия2...],[имя1,имя2...],[отчество1,отчество2...]]
    result = []
    for i in range(3):
        result.append([])
    
    #Создаем массив для записи порядка
    #Порядок хранится в виде массива, где каждому введенному слову сопоставляется номер значения(0 = фамилия, 1 = имя, 2 = отчество)
    #Для Иван Иванович Сидоров порядок будет [1,2,0] (т.е. порядок имя, отчество, фамилия)
    order = []
    for i in range(N):
        order.append(None)
    
    resultStrict = StrictCheck(words) #матрица с вероятностями после строгой проверки
    #Теперь когда у нас база отчеств полная, используем проверку по грамматике только после, когда не прошла строгая проверка

    recurMatrix = RecursiveProcessing(copy.deepcopy(resultStrict)) #проводится обработка матрицы (выбираются очевидные варианты)
    roundedMatrix = copy.deepcopy(recurMatrix)
    RoundMatrix(roundedMatrix,roundingDegree) #округляется, чтобы убрать слишком редкие слова
    
    #проверяем можем ли мы однозначно определить все слова (в строке по одному значению)
    if СheckMatrix(roundedMatrix):  
        order = GetOrder(roundedMatrix) #определяем порядок слов
        qualityFlag.append([0,""])
        for i in range(N):
            result[order[i]].append(words[i])
    else:
        #Проверяем можем ли мы с уверенностью что-то определить
        #Для этого если вероятность одного значения в столбце значительно больше остальных мы его запоминаем.
        orderTemp = copy.deepcopy(order)
        for j in range(3):
            temp = []
            for i in range(N):
                temp.append(resultStrict[i][j])
            indexMax = temp.index(max(temp))
            f = True
            for i in range(N):
                if i != indexMax and resultStrict[i][j]*10**roundFactorDefiningAfterStrict >= resultStrict[indexMax][j]:
                    f = False
            if f: 
                orderTemp[indexMax] = j  
        
        #Оставшиеся слова, не определенные в строгой проверке, проверяем через расстояние между словами
        
        replaceWords = [] #матрица для слов, полученных в результате нечеткого поиска
        replaceValues = [] #матрица вероятностей, соответсвующих словам из нечеткого поиска
        for i in range(N):
            replaceWords.append([words[i],words[i],words[i]])
            replaceValues.append([0,0,0])
        
        for i in range(N):
            if order[i] is None:
                if orderTemp[i] is not None:
                    order[i] = orderTemp[i]
                    wordRepl,valueRepl = forReplaceCheckTrie(words[i], order[i])
                    if wordRepl != "":
                        replaceWords[i][order[i]], replaceValues[i][order[i]] = wordRepl,valueRepl                    
                else:
                    for j in range(3):
                        wordRepl,valueRepl = forReplaceCheckTrie(words[i], j)
                        if wordRepl != "":
                            replaceWords[i][j], replaceValues[i][j] = wordRepl,valueRepl
        
        #Суммируем полученные значения
        resForNow = []
        for i in range(N):
            resForNow.append([0,0,0])
        for i in range(N):
            for j in range(3):
                if resultStrict[i][j]>replaceValues[i][j]:
                    resForNow[i][j] = resultStrict[i][j]
                    replaceWords[i][j] = words[i]
                else:
                    resForNow[i][j] = replaceValues[i][j]
        
        #Анализируем полученную матрицу
        order = ComplexOrder(resForNow, order)
       
        #Если до сих пор что-то не определено (случается елси остались полные строки нулей) 
        # используем проверку по грамматике и статистике
        if None in order:
            #матрица с вероятностями после проверки по грамматике (окончания фамилий и отчеств)   
            resultGramma = GrammaCheck(words)  
            for i in range(N):
                if resultStrict[i].count(0)==3:
                    for j in range(3):
                        resForNow[i][j]+=resultGramma[i][j]
            #Если у нас существует статистика для введенного количества слов, учитываем её
            if N<=4:
                for i in range(N):
                    for j in range(3):
                        resForNow[i][j] += statisticsFactor*statistics[N-1][i][j]
                        
            order = ComplexOrder(resForNow, order)
       
        #Исходя из порядка, записываем результат
        for i in range(N):
            result[order[i]].append(replaceWords[i][order[i]]) 

    #Заполняем комментарии после проверки на основе результата
    #0 = ок, 1 = поменяли, 2 = редкое слово, 3 = слово которого нет в базах, 4 = сокращение имени, 5 = нессответствие пола.

    for i in range(N):
        if words[i] not in result[order[i]]:
            qualityFlag.append([1, words[i], replaceWords[i][order[i]]]) #слово которое заменили и на какое заменили
        for res in result[order[i]]:
            if res in bases[order[i]]:
                if (bases[order[i]][res]["probability"]<qualityCheck):
                    qualityFlag.append([2,res]) #редкое слово
            else:
                qualityFlag.append([3,res]) #слово которого нет в базах
    
    #Выявляем, нашли ли мы сокращение имени или полное имя 
    #resultOriginal = copy.deepcopy(result) #Сделать копию оригинального результата?
    i = 1 #База с именами
    for j in range(len(result[i])):
        if result[i][j] in bases[i]:
            if len(bases[i][result[i][j]]["full_form"]) > 0: 
                shortName = result[i][j]
                fullForms = copy.deepcopy(bases[i][result[i][j]]["full_form"])
                genderWithoutName = CheckGender(result)
                if genderWithoutName == genderTuple[1] or genderWithoutName == genderTuple[2]:
                    for name in fullForms:
                        if bases[i][name]["gender"]!=genderWithoutName: 
                            fullForms.remove(name)
                if len(fullForms)==1: result[i][j] = fullForms[0] #Не обязательно, в принципе
                #else: result[i][j] = fullForms
                qualityFlag.append([4, shortName, '; '.join(fullForms)]) #сокращение имени
    
    #!проверить адекватность работы с сокращениями
    gender = CheckGender(result) #получаем пол, исходя из результата
    #Если пол с ошибкой, т.е. Петров Анна, значит несоответствие
    if gender == genderTuple[3]:
        qualityFlag.append([5,""])

    #Заменяем слово соответствующей ему Ё-формой
    FixYoForm(result)
    SetStatistics(order) #обновляем статистику
    return order,result, gender, qualityFlag #+ probability + добавить разные варинаты результата


# In[22]:

import json
def NotBruteAtAll(inputFIO):
    res = []
    for line in inputFIO:

        order,result, gender, qualityFlag = WordsProcessing(line)
        #вывод результата в виде строки
        resultStr = ""
        for r in result:
            for w in r:
                resultStr += w.title() + " "
        resultStr=resultStr.strip()
        
        output = [resultStr, gender]
        qualityZero = [0,""]
        if len(qualityFlag)>1 and qualityZero in qualityFlag:
            qualityFlag.remove(qualityZero)
        res.append([output, qualityFlag])
        res.append(order)
    
    return res


# In[23]:

