from FIOAlgorithm import FIOalgorithm
def fio_to_array(massiv):
    obr_massiv=FIOalgorithm.NotBruteAtAll(massiv) #список обработанных ФИО
    rez_m=[] #список для результатов
    nomer=1 #текущий индекс
    for i in range(0, len(obr_massiv), 2):# шаг обусловлен особенностями списка, который отдаёт внешний алгоритм
        rez_m.append({"Имя":None,"Фамилия":None,"Отчество":None,"Пол":None,"Правильность":True,"Номер":str(nomer)})# заготовка строки-результата
        nomer+=1
        if not((obr_massiv[i][1]==[[0, '']]) or (obr_massiv[i][1]==[])): # проверка наличия исправлений
            rez_m[len(rez_m) - 1]["Правильность"]=False
        slova=obr_massiv[i][0][0].split()# получаем составляющие ФИО
        rez_m[len(rez_m) - 1]["Пол"] = obr_massiv[i][0][1]
        if rez_m[len(rez_m) - 1]["Пол"] == "М":
            rez_m[len(rez_m) - 1]["Пол"]="Мужской" # производим преобразования для обеспечения возможности полного написания пола
        elif rez_m[len(rez_m) - 1]["Пол"] == "Ж":
            rez_m[len(rez_m) - 1]["Пол"]="Женский"
        obr_massiv[i + 1].sort() # внешний алгоритм возвращает слова ФИО в порядке отсортированного списка, иначально в списке порядок следования соотвествует начальному порядку следования
        for ti,z in enumerate(obr_massiv[i+1]):
            if z==0:
                rez_m[len(rez_m)-1]["Фамилия"]=slova[ti]
            elif z==1:
                rez_m[len(rez_m) - 1]["Имя"] = slova[ti]
            elif z==2:
                rez_m[len(rez_m) - 1]["Отчество"] = slova[ti]
    return rez_m
from flask import Flask
from flask import request
from flask_cors import CORS
from json import dumps
app = Flask(__name__)
CORS(app)
@app.route('/', methods=["POST"])
def start_obr():
    tm=dict(request.form)
    return dumps(fio_to_array(tm["str[]"]))
app.run(host='0.0.0.0', port=8765)