from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
import xlrd as xlrd
import pymorphy2

dict = {'сладкий': 1, 'кислый': 1, 'вкус': 1,
        'цена': 2, 'дорого': 2, 'дешево': 2,
        'еда': 3, 'полуфабрикаты': 3}

fruitDict = {'Горох': 'Горох', 'Соя': 'Соя', 'Кукуруза': 'Кукуруза', 'Каштан': 'Каштан', 'Личи': 'Личи',
             'Кешью,': 'Кешью,', 'Манго': 'Манго', 'Кокос': 'Кокос', 'Персик': 'Персик', 'Вишня': 'Вишня',
             'Яблоко': 'Яблоко', 'Груша': 'Груша', 'Виноград': 'Виноград',
             'Помидор': 'Помидор', 'Банан': 'Банан', 'Гранат': 'Гранат', 'Мандарин': 'Мандарин', 'Апельсин': 'Апельсин',
             'Грейпфрут': 'Грейпфрут', 'Лимон': 'Лимон',
             'Клубника': 'Клубника', 'Малина': 'Малина', 'Джекфрут': 'Джекфрут', 'Шелковица': 'Шелковица',
             'Ананас': 'Ананас',
             }
morph = pymorphy2.MorphAnalyzer()


class Conversation:
    def __init__(self):
        # Load UI definition from file
        qfile_stats = QFile('conversation.ui')
        qfile_stats.open(QFile.ReadOnly)
        qfile_stats.close()

        self.ui = QUiLoader().load(qfile_stats)
        mes = """Вы можете задать следующие вопросы：
-Какой вкус у яблока
-Какая цена на манго
-Еда из апельсинов

Название фрукта можно заменить на:
Горох, Соя, Какая цена на манго, Каштан, Личи, Кешью, Манго, Кокос, Персик, Вишня, Яблоко, Груша, Виноград, Помидор, Банан, Гранат, Мандарин, Апельсин, Грейпфрут, Лимон, Клубника, Малина, Джекфрут, Шелковица, Ананас
        """
        self.ui.textBrowser.append(mes)
        self.ui.textEdit_2.setPlaceholderText("please enter")
        self.ui.pushButton.clicked.connect(self.send)

        answer = 'Apples are very sweet and have a hard taste'
        print(morph.lat2cyr(answer))

    def readData(self):
        # Read table data
        book = xlrd.open_workbook('fruit2.xlsx')
        sheet1 = book.sheets()[0]
        nrows = sheet1.nrows
        ncols = sheet1.ncols
        values = []
        for row in range(nrows):
            row_values = sheet1.row_values(row)
            values.append(row_values)
        return values, nrows, ncols

    def send(self):
        # 接收用户输入信息
        msg = self.ui.textEdit_2.toPlainText()
        print(msg)
        self.ui.textBrowser_2.append('user:')
        self.ui.textBrowser_2.append(msg)
        self.ui.textBrowser_2.append('')

        # 删除 ？，。

        # 分词 俄语原形
        lis = [n for n in msg.split(' ')]
        lis2 = []
        print(lis)
        for word in lis:
            p = morph.parse(word)[0]
            lis2.append(p.normal_form)
        print(lis2)

        for word in lis2:
            for k, v in dict.items():
                if word.lower() == k:
                    # 是第几个问题
                    question_num = v
                    # print('%s is %s' % (k, v))
                else:
                    continue
        name = ''
        for word in lis2:
            for k, v in fruitDict.items():
                # 是什么水果
                if word.lower() == k.lower():
                    name = v
                else:
                    continue
        print(question_num, name)
        self.ui.textEdit_2.clear()

        if name == '':
            info_msg = 'please tell which fruit you want to ask'
            self.ui.textBrowser_2.append('AI:')
            self.ui.textBrowser_2.append(info_msg)
        else:
            # 搜索水果
            data = self.readData()
            nrows = data[1]
            values = data[0]
            ncols = data[2]
            # Find the row of the searched fruit -  row
            for row in range(nrows):
                cell = values[row][1]
                # cell = sheet1.cell(row, 1)
                if name.lower() == cell.lower():
                    itemNum = row
                    # return itemNum
                    print(itemNum)
                    print(values[itemNum])
                    break
                else:
                    continue

            name_sentence = morph.parse(name)[0].make_agree_with_number(2).word
            # sweet1 = values[itemNum][8][0]
            # sweet2 = morph.parse(values[itemNum][8])[1].make_agree_with_number(2).word
            if question_num == 1:
                answer = f'{name_sentence} {values[itemNum][8]} и имеют {values[itemNum][9]} вкус'
            elif question_num == 2:
                if values[itemNum][6] == 0:
                    answer = f'Цена {name_sentence} {values[itemNum][5]}, скидка не производится в настоящее время'
                else:
                    answer = f'The price of {name} is {values[itemNum][5]}. сейчас цена снижена, скидка {values[itemNum][6]}, сейчас хорошее время для покупки'

            elif question_num == 3:
                answer = f'{name} можно превратить в {values[itemNum][10]}. Это очень вкусная еда'
            # 显示回答
            self.ui.textBrowser_2.append('AI:')
            self.ui.textBrowser_2.append(answer)
            self.ui.textBrowser_2.append('')


app = QApplication([])
search = Conversation()
search.ui.show()
app.exec_()
