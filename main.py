import requests
import openai
import os
import sys


from PyQt5.QtWidgets import *
from PyQt5 import uic
import PyQt5
import config

from PIL import Image
from io import BytesIO

# API KEY
OPENAI_API_KEY = config.OPENAI_API_KEY
naver_client_id = config.naver_client_id
naver_client_secret = config.naver_client_secret

openai.api_key = OPENAI_API_KEY
model = "gpt-3.5-turbo"

input_txt = ""
work_name = ""
work_author = ""

# Poem Translating

def read_poem():
    global input_txt
    global work_name
    global work_author

    f = open('./input.txt', 'r', encoding = 'UTF8')
    lines = f.readlines()
    work_name = lines[0][:len(lines[0]) - 1]
    work_author = lines[1][:len(lines[1]) - 1]

    idx = 0
    for now_line in lines:
        idx = idx + 1
        if idx <= 3:  
            continue
        input_txt = input_txt + now_line
    f.close()

def naver_search(naverSearchText : str):
    headers = {
        "X-Naver-Client-Id" : naver_client_id,
        "X-Naver-Client-Secret" : naver_client_secret
    }

    url = "https://openapi.naver.com/v1/search/blog?query=" + naverSearchText # JSON 결과
    naver_data = requests.get(url, headers=headers).json()

    idx = 0

    query = "Web search results:\n\n"
    for i in naver_data['items']:
        idx = idx + 1
        i['description'] = i['description'].replace('<b>', '')
        i['description'] = i['description'].replace('</b>', '')

        query = query + "[" + str(idx) + "] " + i['description'] + "\n"
        query = query + "URL : " + i['link'] + "\n\n"

    return query

def make_photo(label):
    label.setText("Please wait for a moment. Generating Image is in progress.")
    query = input_txt

    messages = [
        {"role": "system", "content": "You are very kind assitant. Please translate these poems to english."},
        {"role": "user", "content": query}
    ]

    response_text = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    query = response_text['choices'][0]['message']['content']

    print("Sentence Translating is done.")
    label.setText("Please wait for a moment. Sentence Translating is done.")
    messages = [  
        {"role": "system", "content": " Please extract keywords from important words in the given sentence. Please make the answer in one row. Make 10 keywords"},
        {"role": "user", "content": query}
    ]

    response_text = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    response_text = response_text['choices'][0]['message']['content']
    query = response_text

    print("Extracting keywords is done.")
    label.setText("Please wait for a moment. Extracting keywords is done.")

    query = query + ", digital art" + ", masterpiece" + ", best quality" 
    keywords = query

    response_image = openai.Image.create(
      prompt = query,
      n=1,
      size="512x512"
    )

    image_url = response_image['data'][0]['url']

    print("Generating Image is done.")
    label.setText("Please wait for a moment. Generating Image is done.")

    res = os.system(f'curl -o ./now.jpg "{image_url}"')

    label.setText("Please wait for a moment. Downloading file is done.")
    print("Downloading file is done.")
    return keywords

def interpretation():
    query = naver_search(work_author + "의 " + work_name + " 해석")

    query = query + "다음은 " + work_author + "의 " + work_name + "입니다.\n\n"
    query = query + input_txt + "\n\n"
    query = query + "Query : " + work_author + "의 " + work_name + "을 주어둔 자료를 바탕으로 해석해 줄 수 있을까?"

    print("Naver loading Complete!")

    messages = [  
        {"role": "system", "content": "Using the provided web search results and the poems, write a comprehensive reply to the given query. And, please answer to Korean."},
        {"role": "user", "content": query}
    ]

    response_text = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    response_text = response_text['choices'][0]['message']['content']
    return response_text

def author_interpretation():
    query = naver_search(work_author + "의 삶에 대한 분석")
    query = query + "작가님의 삶을 위의 내용을 통해 분석해줘."
    messages = [  
        {"role": "system", "content": "Using the provided web search results and the poems, write a comprehensive reply to the given query. And, please answer to Korean."},
        {"role": "user", "content": query}
    ]

    response_text = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    response_text = response_text['choices'][0]['message']['content']

    return response_text

def poem_recommendation():
    query = naver_search(work_author + "의 " + work_name + "와 비슷한 " + work_author + "의 시")
    query = query + "Query : " + work_author + " 작가님의 " + work_name + "와 비슷한 시를 5개 추천해줘."
    messages = [  
        {"role": "system", "content": "Using the provided web search results, write a comprehensive reply to the given query. And, please answer to Korean."},
        {"role": "user", "content": query}
    ]

    response_text = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    response_text = response_text['choices'][0]['message']['content']

    return response_text

def organize_poems():
    query = "다음은 " + work_author + "의 " + work_name + "입니다.\n\n"
    query = query + input_txt + "\n\n"
    query = query + "Query : " + "위에 있는 " + work_name + "를 우리가 잘 이해할 수 있게 각 문장마다 형식을 풀어서 바꿔줘. 각 문장마다로."
    messages = [  
        {"role": "system", "content": "Using the provided poems, write a comprehensive reply to the given query. And, please answer to Korean."},
        {"role": "user", "content": query}
    ]

    response_text = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    response_text = response_text['choices'][0]['message']['content']

    return response_text

#read_poem()
#photo = make_photo()
#work_result = interpretation()
#name_result = author_interpretation()
#recommendation_result = poem_recommendation()
#organize_result = organize_poems()

"""
"""
class MainWindows(QMainWindow):
    def __init__(self):
        super( ).__init__()
        self.ui = uic.loadUi('Main_UI.ui', self)
        self.setUI()

    def setUI(self):
        self.pushButton.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick_2)
        self.checkBox.stateChanged.connect(self.const_checkBox)
        self.checkBox_2.stateChanged.connect(self.const_checkBox)

    def buttonClick(self):
        global work_author, work_name, input_txt        
        if self.textEdit_2.toPlainText() == "":
            QMessageBox.about(self, "Info", "작품의 제목이 입력되지 않았습니다.")
            return
        
        if self.textEdit_3.toPlainText() == "":
            QMessageBox.about(self, "Info", "작품의 작가가 입력되지 않았습니다.")
            return
        
        if self.textEdit.toPlainText() == "":
            QMessageBox.about(self, "Info", "작품의 내용이 입력되지 않았습니다.")
            return
    
        self.checkBox.setChecked(True)
        self.checkBox_2.setChecked(True)
        work_name = self.textEdit_2.toPlainText()
        work_author = self.textEdit_3.toPlainText()
        input_txt = self.textEdit.toPlainText()

    def buttonClick_2(self):
        if input_txt == "":
            QMessageBox.about(self, "Info", "입력해야 할 사항이 입력되지 않았습니다.")
            return
        if self.comboBox.currentText().startswith("Generate"):
            self.hide()
            self.first = FirstWindows()
            self.first.exec()
            self.show()
            return
        if self.comboBox.currentText().startswith("Similar"):
            self.hide()
            self.second = SecondWindows()
            self.second.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("work"):
            self.hide()
            self.third = ThirdWindows()
            self.third.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("Line"):
            self.hide()
            self.fourth = FourthWindows()
            self.fourth.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("author"):
            self.hide()
            self.fifth = FifthWindows()
            self.fifth.exec()
            self.show()
            return

    def const_checkBox(self):
        if input_txt == "":
            self.checkBox.setChecked(False)
            self.checkBox_2.setChecked(False)
        else:
            self.checkBox.setChecked(True)
            self.checkBox_2.setChecked(True)


class FirstWindows(QDialog, QWidget):
    def __init__(self):
        super(FirstWindows, self).__init__()
        self.ui = uic.loadUi('First_UI.ui', self)
        self.setUI()
        self.show()
    
    def setUI(self):
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)
        self.checkBox.setChecked(True)
        self.pushButton_3.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick_2)

    def buttonClick(self):
        self.label.setText("It needs a long time to generate a photo. Please wait a moment.")
        keywords = make_photo(self.label)
        self.label_2.setText("Keywords : " + keywords)
        img = PyQt5.QtGui.QPixmap('now.jpg')
        self.pixmap.setPixmap(img)
        self.label.setText("All process is completed!")
        self.checkBox_2.setChecked(True)

    def buttonClick_2(self):
        if self.comboBox.currentText().startswith("Input"):
            QMessageBox.about(self, "Info", "기존에 사용한 모든 창을 닫으면 처음 창으로 돌아갈 수 있습니다!")
            return
        if self.comboBox.currentText().startswith("Similar"):
            self.hide()
            self.second = SecondWindows()
            self.second.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("work"):
            self.hide()
            self.third = ThirdWindows()
            self.third.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("Line"):
            self.hide()
            self.fourth = FourthWindows()
            self.fourth.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("author"):
            self.hide()
            self.fifth = FifthWindows()
            self.fifth.exec()
            self.show()
            return


class SecondWindows(QDialog, QWidget):
    def __init__(self):
        super(SecondWindows, self).__init__()
        self.ui = uic.loadUi('Second_UI.ui', self)
        self.setUI()
        self.show()
    
    def setUI(self):
        self.checkBox.setChecked(True)
        self.pushButton.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick_2)

    def buttonClick(self):
        self.label.setText("It needs a long time to ask GPT. Please wait a moment....")
        result = poem_recommendation()
        self.textBrowser.append(result)
        self.label.setText("All process is completed!")
        self.checkBox_2.setChecked(True)

    def buttonClick_2(self):
        if self.comboBox.currentText().startswith("Input"):
            QMessageBox.about(self, "Info", "기존에 사용한 모든 창을 닫으면 처음 창으로 돌아갈 수 있습니다!")
            return
        if self.comboBox.currentText().startswith("Generate"):
            self.hide()
            self.first = FirstWindows()
            self.first.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("work"):
            self.hide()
            self.third = ThirdWindows()
            self.third.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("Line"):
            self.hide()
            self.fourth = FourthWindows()
            self.fourth.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("author"):
            self.hide()
            self.fifth = FifthWindows()
            self.fifth.exec()
            self.show()
            return
        
class ThirdWindows(QDialog, QWidget):
    def __init__(self):
        super(ThirdWindows, self).__init__()
        self.ui = uic.loadUi('Third_UI.ui', self)
        self.setUI()
        self.show()
    
    def setUI(self):
        self.checkBox.setChecked(True)
        self.pushButton.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick_2)

    def buttonClick(self):
        self.label.setText("It needs a long time to ask GPT. Please wait a moment....")
        result = interpretation()
        self.textBrowser.append(result)
        self.label.setText("All process is completed!")
        self.checkBox_2.setChecked(True)

    def buttonClick_2(self):
        if self.comboBox.currentText().startswith("Input"):
            QMessageBox.about(self, "Info", "기존에 사용한 모든 창을 닫으면 처음 창으로 돌아갈 수 있습니다!")
            return
        if self.comboBox.currentText().startswith("Generate"):
            self.hide()
            self.first = FirstWindows()
            self.first.exec()
            self.show()
            return
        if self.comboBox.currentText().startswith("Similar"):
            self.hide()
            self.second = SecondWindows()
            self.second.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("Line"):
            self.hide()
            self.fourth = FourthWindows()
            self.fourth.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("author"):
            self.hide()
            self.fifth = FifthWindows()
            self.fifth.exec()
            self.show()
            return

class FourthWindows(QDialog, QWidget):
    def __init__(self):
        super(FourthWindows, self).__init__()
        self.ui = uic.loadUi('Fourth_UI.ui', self)
        self.setUI()
        self.show()
    
    def setUI(self):
        self.checkBox.setChecked(True)
        self.pushButton.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick_2)

    def buttonClick(self):
        self.label.setText("It needs a long time to ask GPT. Please wait a moment....")
        result = organize_poems()
        self.textBrowser.append(result)
        self.label.setText("All process is completed!")
        self.checkBox_2.setChecked(True)

    def buttonClick_2(self):
        if self.comboBox.currentText().startswith("Input"):
            QMessageBox.about(self, "Info", "기존에 사용한 모든 창을 닫으면 처음 창으로 돌아갈 수 있습니다!")
            return
        if self.comboBox.currentText().startswith("Generate"):
            self.hide()
            self.first = FirstWindows()
            self.first.exec()
            self.show()
            return
        if self.comboBox.currentText().startswith("Similar"):
            self.hide()
            self.second = SecondWindows()
            self.second.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("work"):
            self.hide()
            self.third = ThirdWindows()
            self.third.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("author"):
            self.hide()
            self.fifth = FifthWindows()
            self.fifth.exec()
            self.show()
            return
        
class FifthWindows(QDialog, QWidget):
    def __init__(self):
        super(FifthWindows, self).__init__()
        self.ui = uic.loadUi('Fifth_UI.ui', self)
        self.setUI()
        self.show()
    
    def setUI(self):
        self.checkBox.setChecked(True)
        self.pushButton.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick_2)

    def buttonClick(self):
        self.label.setText("It needs a long time to ask GPT. Please wait a moment....")
        result = author_interpretation()
        self.textBrowser.append(result)
        self.label.setText("All process is completed!")
        self.checkBox_2.setChecked(True)

    def buttonClick_2(self):
        if self.comboBox.currentText().startswith("Input"):
            QMessageBox.about(self, "Info", "기존에 사용한 모든 창을 닫으면 처음 창으로 돌아갈 수 있습니다!")
            return
        if self.comboBox.currentText().startswith("Generate"):
            self.hide()
            self.first = FirstWindows()
            self.first.exec()
            self.show()
            return
        if self.comboBox.currentText().startswith("Similar"):
            self.hide()
            self.second = SecondWindows()
            self.second.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("work"):
            self.hide()
            self.third = ThirdWindows()
            self.third.exec()
            self.show()
            return
        if self.comboBox.currentText().endswith("Line"):
            self.hide()
            self.fourth = FourthWindows()
            self.fourth.exec()
            self.show()
            return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MainWindows()
    myWindow.show( )
    app.exec_()