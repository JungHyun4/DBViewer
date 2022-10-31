#-*- coding: utf-8 -*-

import pymysql
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtGui import QFont
import sys, datetime
import csv
import json
import xml.etree.ElementTree as ET

class DB_Utils:
    def queryExecutor(self, sql, params):
        conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:     # dictionary based cursor
                cursor.execute(sql, params)
                tuples = cursor.fetchall()
                return tuples
        except Exception as e:
            print(e)
            print(type(e))
        finally:
            conn.close()

    def updateExecutor(self, sql, params):
        conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
            conn.commit()
        except Exception as e:
            print(e)
            print(type(e))
        finally:
            conn.close()

class DB_Queries:
    # 모든 검색문은 여기에 각각 하나의 메소드로 정의
    def selectCustomerName(self):
        sql = "select distinct name from customers order by 1"
        params = ()

        util = DB_Utils()
        tuples = util.queryExecutor(sql=sql, params=params)
        return tuples

    def selectCustomerCity(self):
        sql = "select distinct city from customers order by 1"

        params = ()

        util = DB_Utils()
        tuples = util.queryExecutor(sql=sql, params=params)
        return tuples

    def selectCustomerCityUsingCountry(self, country):
        condition = ['country']
        values = [country]
        params_value = []
        str = ''


        str += " WHERE " + condition[0] + "= %s"
        params_value.append(values[0])
        params = (country)

        sql = "select distinct city from customers" + str + " order by 1"

        util = DB_Utils()
        tuples = util.queryExecutor(sql=sql, params=params)
        return tuples
    def selectCustomerCountry(self):
        sql = "SELECT DISTINCT country FROM customers order by 1"
        params = ()

        util = DB_Utils()
        tuples = util.queryExecutor(sql=sql, params=params)
        return tuples

    def selectOrderUsingCondition(self, name, city, country):

        condition = ['name', 'city', 'country']
        values = [name, city, country]
        params_value = []
        str = ''

        for i in range(len(condition)):
            if(values[i] == 'All'):
                continue
            else:
                    str += " AND " + condition[i] + "= %s"
                    params_value.append(values[i])

        if(str != ''):
            str = " WHERE " + str[5:]

        sql =   """ select orderNo, orderDate, requiredDate, shippedDate, status, name as customer, comments 
                    from orders join customers 
                    on orders.customerId = customers.customerId""" + str + " order by orderNO"""

        params = tuple(params_value)
        util = DB_Utils()

        tuples = util.queryExecutor(sql=sql, params=params)
        print(len(tuples))
        return tuples
    def selectDetailUsingCondition(self,orderNo):

        sql = """   select orderLineNo, orderDetails.productCode, name as productName, quantity, cast(priceEach as CHAR) as priceEach, cast((quantity * priceEach) as CHAR) as 상품주문액
                    from orderDetails left join products on orderDetails.productCode = products.productCode 
                    where orderNO = """
        sql += orderNo
        conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:  # dictionary based cursor
                cursor.execute(sql)
                tuples = cursor.fetchall()
                return tuples
        except Exception as e:
            print(e)
            print(type(e))
        finally:
            conn.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):

        # 윈도우 설정
        self.setWindowTitle("고객 테이블 검색")
        self.setGeometry(0, 0, 900, 1000)

        # 폰트 설정
        fontDB = QFontDatabase()
        fontDB.addApplicationFont('./NanumBarunGothic.ttf')
        self.setFont(QFont('NanumBarunGothic'))

        self.title_label = QLabel("주문 검색", self)
        self.title_label.setAlignment(Qt.AlignCenter)

        # 라벨 설정
        self.count_label = QLabel("주문 수 : ", self)
        self.count_value = QLabel("0",self)
        self.name_label = QLabel("고객", self)
        self.city_label = QLabel("도시", self)
        self.country_label = QLabel("국가", self)

        # 콤보박스 설정
        self.nameComboBox = QComboBox(self)
        self.cityComboBox = QComboBox(self)
        self.countryComboBox = QComboBox(self)



        # DB 검색문 실행
        query = DB_Queries()
        # 스타일 클래스
        style = Style()

        name_rows = query.selectCustomerName()  # 딕셔너리의 리스트
        country_rows = query.selectCustomerCountry()
        city_rows = query.selectCustomerCity()

        name_rows.insert(0, {'name': 'All'})
        city_rows.insert(0, {'city': 'All'})
        country_rows.insert(0, {'country': 'All'})


        name_columnName = list(name_rows[0].keys())[0]
        city_columnName = list(city_rows[0].keys())[0]
        country_columnName = list(country_rows[0].keys())[0]

        name_items = [row[name_columnName] for row in name_rows]
        city_items = [row[city_columnName] for row in city_rows]
        country_items = [row[country_columnName] for row in country_rows]

        # print(name_rows)
        # print()
        print(city_items)
        # print()
        # print(country_rows)

        self.nameComboBox.addItems(name_items)
        self.cityComboBox.addItems(city_items)
        self.countryComboBox.addItems(country_items)

        self.nameComboBox.activated.connect(self.nameComboBox_Activated)
        self.cityComboBox.activated.connect(self.cityComboBox_Activated)
        self.countryComboBox.activated.connect(self.countryComboBox_Activated)

        # 콤보박스 초기값 ALL로 설정
        self.nameValue = 'All'
        self.cityValue = 'All'
        self.countryValue = 'All'

        # 서치버튼 설정
        self.searchButton = QPushButton("검색", self)
        self.searchButton.clicked.connect(self.searchButton_Clicked)

        # 초기화 버튼 설정
        self.clearButton = QPushButton("초기화", self)
        self.clearButton.clicked.connect(self.clearButton_Clicked)


        # 테이블위젯 설정
        self.tableWidget = QTableWidget(self)  # QTableWidget 객체 생성
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableWidget.cellClicked.connect(self.order_Clicked)
        # 스타일 설정

        self.title_label.setStyleSheet(style.titleSet())
        self.name_label.setStyleSheet(style.labelSet())
        self.city_label.setStyleSheet(style.labelSet())
        self.country_label.setStyleSheet(style.labelSet())
        self.count_label.setStyleSheet(style.labelSet())
        self.count_value.setStyleSheet(style.labelSet())



        self.nameComboBox.setStyleSheet(style.comboSet())
        self.cityComboBox.setStyleSheet(style.comboSet())
        self.countryComboBox.setStyleSheet(style.comboSet())

        self.searchButton.setStyleSheet(style.BtnSet())
        self.clearButton.setStyleSheet(style.clearBtnSet())


        # 레이아웃 설정
        titleLayout = QGridLayout()
        titleLayout.addWidget(self.title_label)

        firstLayout = QHBoxLayout()
        firstLayout.addWidget(self.name_label)
        firstLayout.addWidget(self.nameComboBox, stretch=1)
        firstLayout.addWidget(self.country_label)
        firstLayout.addWidget(self.countryComboBox, stretch=1)
        firstLayout.addWidget(self.city_label)
        firstLayout.addWidget(self.cityComboBox, stretch=1)
        firstLayout.addWidget(self.searchButton, stretch=3)

        self.nameComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cityComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.nameComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.countryComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.searchButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        secondLayout = QHBoxLayout()
        secondLayout.addWidget(self.count_label)
        secondLayout.addWidget(self.count_value, stretch=1)
        secondLayout.addWidget(self.clearButton, stretch = 1)
        self.clearButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.count_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)



        tableLayout = QHBoxLayout()
        tableLayout.addWidget(self.tableWidget)
        layout = QVBoxLayout()
        layout.addLayout(titleLayout, stretch=2)
        layout.addLayout(firstLayout, stretch=1)
        layout.addLayout(secondLayout, stretch=1)
        layout.addLayout(tableLayout, stretch=4)
        self.setLayout(layout)

    def nameComboBox_Activated(self):
        self.nameValue = self.nameComboBox.currentText()
        self.cityValue = 'All';
        self.countryValue = 'All';

    def cityComboBox_Activated(self):
        self.cityValue = self.cityComboBox.currentText()
        self.nameValue = 'All'
        self.countryValue = 'All';

    def countryComboBox_Activated(self):
        self.countryValue = self.countryComboBox.currentText()
        self.cityValue = 'All'
        self.nameValue = 'All'
        if(self.countryValue == "All"):
            self.cityValue = 'All'
            self.nameValue = 'All'
            self.cityComboBox.clear()
            query2 = DB_Queries()
            city_rows = query2.selectCustomerCity()
            print(self.countryValue)
            print(city_rows)
            city_rows.insert(0, {'city': 'All'})
            city_columnName = list(city_rows[0].keys())[0]
            city_items = [row[city_columnName] for row in city_rows]
            self.cityComboBox.addItems(city_items)
        else:
            self.cityComboBox.clear()
            query1 = DB_Queries()
            city_rows = query1.selectCustomerCityUsingCountry(self.countryValue)
            print(self.countryValue)
            print(city_rows)
            city_rows.insert(0, {'city': 'All'})
            city_columnName = list(city_rows[0].keys())[0]
            city_items = [row[city_columnName] for row in city_rows]
            self.cityComboBox.addItems(city_items)




    def noResult_Message(self):
        QMessageBox.about(self, "알림", "검색 결과가 없습니다.")

    def order_Clicked(self):
        row = self.tableWidget.currentRow()
        col = 0
        orderNo = self.tableWidget.item(row,0).text()

        dialogue = SecondWindow()
        dialogue.orderNo = orderNo
        dialogue.orderNumber.setText(orderNo)
        dialogue.setDetail()
        dialogue.exec()






    def clear_tableWidget(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

    def clearButton_Clicked(self):
        self.clear_tableWidget()
        self.nameComboBox.setCurrentIndex(0)
        self.cityComboBox.setCurrentIndex(0)
        self.countryComboBox.setCurrentIndex(0)
        self.nameValue = 'All'
        self.cityValue = 'All'
        self.countryValue = 'All'
        self.count_value.setText('0')

        QMessageBox.about(self, "알림", "초기화되었습니다.")

    def searchButton_Clicked(self):


            # DB 검색문 실행
            query = DB_Queries()
            orders = query.selectOrderUsingCondition(self.nameValue, self.cityValue, self.countryValue)
            self.tableWidget.clearContents()
            # print(orders)
            if (orders == ()):
                self.clear_tableWidget()
                self.noResult_Message()
            else:
                self.tableWidget.setRowCount(len(orders))
                self.tableWidget.setColumnCount(len(orders[0]))
                columnNames = list(orders[0].keys())
                self.tableWidget.setHorizontalHeaderLabels(columnNames)
                self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

                for p in orders:  # p는 딕셔너리임.
                    rowIDX = orders.index(p)  # 테이블 위젯의 row index 할당
                    for k, v in p.items():
                        columnIDX = list(p.keys()).index(k)  # 테이블 위젯의 column index 할당
                        item = QTableWidgetItem(str(v))
                        self.tableWidget.setItem(rowIDX, columnIDX, item)
                self.saveList = orders
            self.count_value.setText(str(len(orders)))
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()


class SecondWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setNumofProduct(self , orderNo):
        sql =    """select  count(quantity)
                    from orderDetails left join products on orderDetails.productCode = products.productCode 
                    where orderNo = """
        sql += orderNo
        sql += " group by orderNo"

        conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:  # dictionary based cursor
            cursor.execute(sql)
            tuples = cursor.fetchall()
        self.productNumbur.setText(str(tuples[0]["count(quantity)"]))

    def setTotalPrice(self , orderNo):
        sql = """select   cast(sum(quantity * priceEach)as CHAR) 
                            from orderDetails left join products on orderDetails.productCode = products.productCode 
                            where orderNo = """
        sql += orderNo
        sql += " group by orderNo"
        conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:  # dictionary based cursor
            cursor.execute(sql)
            tuples = cursor.fetchall()
        self.totalPrice.setText(str(tuples[0]["cast(sum(quantity * priceEach)as CHAR)"]))

    def fileRadio_Clicked(self):
        if(self.csv_radioBtn.isChecked()):
            self.save_format = 'csv'
        elif(self.json_radioBtn.isChecked()):
            self.save_format = 'json'
        elif (self.xml_radioBtn.isChecked()):
            self.save_format = 'xml'
    def setDetail(self):
        # DB 검색문 실행
        query = DB_Queries()
        orders = query.selectDetailUsingCondition(self.orderNumber.text())
        print(orders)
        if (orders == ()):
            self.clear_tableWidget()
            self.noResult_Message()
        else:
            self.tableWidget.setRowCount(len(orders))
            self.tableWidget.setColumnCount(len(orders[0]))
            columnNames = list(orders[0].keys())
            self.tableWidget.setHorizontalHeaderLabels(columnNames)
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for p in orders:  # p는 딕셔너리임.
                rowIDX = orders.index(p)  # 테이블 위젯의 row index 할당
                for k, v in p.items():
                    columnIDX = list(p.keys()).index(k)  # 테이블 위젯의 column index 할당
                    if (columnIDX == 6):
                        if v == None:
                            item = QTableWidgetItem('--------------')
                        else:
                            item = QTableWidgetItem(str(v))
                    else:
                        if v == None:  # 파이썬이 DB의 널값을 None으로 변환함.
                            continue  # QTableWidgetItem 객체를 생성하지 않음

                        else:
                            item = QTableWidgetItem(str(v))

                    self.tableWidget.setItem(rowIDX, columnIDX, item)
            self.saveList = orders

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.setTotalPrice(self.orderNo)
        self.setNumofProduct(self.orderNo)
    def saveButton_Clicked(self):
        if (self.save_format == 'csv'):
            print()
            print('save csv')
            print()
            self.readDB_writeCSV(self.saveList)
        elif (self.save_format == 'json'):
            print()
            print('save json')
            print()
            print(self.saveList)
            self.readDB_writeJSON(self.saveList)
        elif (self.save_format == 'xml'):
            print()
            print('save xml')
            print()
            print(self.saveList)
            self.readDB_writeXML(self.saveList)

    def readDB_writeJSON(self, orders):

        # 애트리뷰트 BIRTH_DATE의 값을 MySQL datetime 타입에서 스트링으로 변환함. (CSV에서는 패키지가 변환함.)
        newDict = dict(order=orders)

        # JSON 화일에 쓰기
        # dump()에 의해 모든 작은 따옴표('')는 큰 따옴표("")로 변환됨
        # with open('order.json', 'w', encoding='utf-8') as f:
        #     json.dump(newDict, f, ensure_ascii=False)

        with open(self.orderNo + ".json", 'w', encoding='utf-8') as f:
            json.dump(newDict, f, indent=4, ensure_ascii=False)
        QMessageBox.about(self, "알림", "저장되었습니다.")

    def readDB_writeCSV(self, orders):
        # CSV 화일을 쓰기 모드로 생성
        with open(self.orderNo + ".csv", 'w', encoding='utf-8', newline='') as f:
            wr = csv.writer(f)

            # 테이블 헤더를 출력
            columnNames = list(orders[0].keys())
            print(columnNames)
            print()

            wr.writerow(columnNames)
            # 테이블 내용을 출력
            for order in orders:
                row = list(order.values())
                print(row)
                wr.writerow(row)
                # 날짜 변환 기능을 csv 패키지에서 제공함.
        QMessageBox.about(self, "알림", "저장되었습니다.")

    def readDB_writeXML(self, orders):

        # 애트리뷰트 BIRTH_DATE의 값을 MySQL datetime 타입에서 스트링으로 변환함. (CSV에서는 패키지가 변환함.)

        newDict = dict(order=orders)

        # XDM 트리 생성
        tableName = list(newDict.keys())[0]
        tableRows = list(newDict.values())[0]

        rootElement = ET.Element('Table')
        rootElement.attrib['name'] = tableName

        for row in tableRows:
            rowElement = ET.Element('Row')
            rootElement.append(rowElement)
            for columnName in list(row.keys()):
                        if row[columnName] == None:  # NICKNAME, JOIN_YYYY, NATION 처리
                            rowElement.attrib[columnName] = ''
                        else:
                            rowElement.attrib[columnName] = row[columnName]
                        if type(row[columnName]) == int:  # BACK_NO, HEIGHT, WEIGHT 처리
                            rowElement.attrib[columnName] = str(row[columnName])
        ET.ElementTree(rootElement).write(self.orderNo + '.xml', encoding='utf-8', xml_declaration=True)
        QMessageBox.about(self, "알림", "저장되었습니다.")

    def setOrderNo(self, a):
        self.orderNo = a

    def setupUI(self):

        # 윈도우 설정
        self.setWindowTitle("주문 상세 내역")
        self.setGeometry(0, 0, 900, 1000)
        self.orderNo = 0
        # 폰트 설정
        fontDB = QFontDatabase()
        fontDB.addApplicationFont('./NanumBarunGothic.ttf')
        self.setFont(QFont('NanumBarunGothic'))

        self.title_label = QLabel("주문 상세 내역", self)
        self.title_label.setAlignment(Qt.AlignLeft)

        # 라벨 설정
        self.orderNumber_label = QLabel("주문번호", self)
        self.orderNumber = QLabel("",self)
        self.productNumbur_label = QLabel("상품개수", self)
        self.productNumbur = QLabel("",self)
        self.totalPrice_label = QLabel("주문액", self)
        self.totalPrice = QLabel("", self)



        # DB 검색문 실행
        query = DB_Queries()
        # 스타일 클래스
        style = Style()

        self.saveList = ''
        self.save_format = 'csv'

        self.group3 = QButtonGroup(self)



        self.csv_radioBtn = QRadioButton('CSV', self)
        self.json_radioBtn = QRadioButton('JSON', self)
        self.xml_radioBtn = QRadioButton('XML', self)
        self.csv_radioBtn.setChecked(True)

        self.save_label = QLabel("파일 출력", self)
        self.csv_radioBtn.clicked.connect(self.fileRadio_Clicked)
        self.json_radioBtn.clicked.connect(self.fileRadio_Clicked)
        self.xml_radioBtn.clicked.connect(self.fileRadio_Clicked)

        self.group3.addButton(self.csv_radioBtn)
        self.group3.addButton(self.json_radioBtn)
        self.group3.addButton(self.xml_radioBtn)



        # 저장 버튼 설정
        self.saveButton = QPushButton("저장", self)
        self.saveButton.clicked.connect(self.saveButton_Clicked)

        # 테이블위젯 설정
        self.tableWidget = QTableWidget(self)  # QTableWidget 객체 생성
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        # 스타일 설정
        self.title_label.setStyleSheet(style.titleSet())
        self.orderNumber_label.setStyleSheet(style.labelSet())
        self.productNumbur_label.setStyleSheet(style.labelSet())
        self.totalPrice_label.setStyleSheet(style.labelSet())
        self.save_label.setStyleSheet(style.labelSet())


        self.csv_radioBtn.setStyleSheet(style.radioBtnSet())
        self.json_radioBtn.setStyleSheet(style.radioBtnSet())
        self.xml_radioBtn.setStyleSheet(style.radioBtnSet())


        self.saveButton.setStyleSheet(style.BtnSet())

        # 레이아웃 설정
        titleLayout = QGridLayout()
        titleLayout.addWidget(self.title_label)

        firstLayout = QHBoxLayout()
        firstLayout.addWidget(self.orderNumber_label)
        firstLayout.addWidget(self.orderNumber, stretch=1)
        firstLayout.addWidget(self.productNumbur_label)
        firstLayout.addWidget(self.productNumbur, stretch=1)
        firstLayout.addWidget(self.totalPrice_label)
        firstLayout.addWidget(self.totalPrice, stretch=1)



        # secondLayout = QHBoxLayout()


        lastLayout = QHBoxLayout()
        lastLayout.addWidget(self.save_label, stretch=1)
        lastLayout.addWidget(self.csv_radioBtn, stretch=1)
        lastLayout.addWidget(self.json_radioBtn, stretch=1)
        lastLayout.addWidget(self.xml_radioBtn, stretch=1)
        lastLayout.addWidget(self.saveButton, stretch=3)
        self.saveButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        tableLayout = QHBoxLayout()
        tableLayout.addWidget(self.tableWidget)
        layout = QVBoxLayout()
        layout.addLayout(titleLayout, stretch=2)
        layout.addLayout(firstLayout, stretch=1)
        # layout.addLayout(secondLayout, stretch=1)
        layout.addLayout(tableLayout, stretch=4)
        layout.addLayout(lastLayout, stretch=1)
        self.setLayout(layout)



class Style:
    def titleSet(self):
        return 'font-weight:bold; font-size:45px; max-height:190px; min-height:80px;'

    def labelSet(self):
        return 'font-weight:bold; font-size:20px; margin-left:10px; max-width:100px;'

    def radioBtnSet(self):
        return 'font-weight:bold; font-size:18px; margin-left: 10px; max-width:90px'

    def BtnSet(self):
        return 'QPushButton{background:#FF6868; font-size:23px; margin:10px 20px; min-width:150px; max-width:300px; min-height:40px; max-height:60px; border-radius:10px; padding:10px 0; border: 2px solid black; border-bottom:3px solid black; border-right:3px solid black; font-weight:bold; box-shadow:5px 5px 5px 5px black}' \
               'QPushButton::hover{border-bottom:5px solid black; border-right:5px solid black; background:pink}'

    def clearBtnSet(self):
        return 'QPushButton{background:black; font-size:23px; color:#FF6868; margin:10px 20px; min-width:150px; max-width:300px; min-height:40px; max-height:60px; border-radius:10px; padding:10px 0; border: 2px solid #FF6868; border-bottom:3px solid #FF6868; border-right:3px solid #FF6868; font-weight:bold;box-shadow:5px 5px 5px 5px black}' \
               'QPushButton::hover{border-bottom:5px solid #FF6868; border-right:5px solid #FF6868; background:white}'

    def comboSet(self):
        return 'QComboBox QAbstractItemView {' \
                    'border:1px solid black;' \
                    'background: black;' \
                    'color:black;'\
                    'selection-background-color: black;' \
                    'selection-color:black;' \
                    'selection-height:15px;}'\
               'QComboBox {' \
                    'background: black; ' \
                    'min-height:13px; '\
                    'max-height:20px; ' \
                    'max-width:250px;'\
                    'border-radius:5px;'\
                    'color:#FF6868;' \
                    'padding:7px;'\
                    'selection-background-color: rgb(255,255,255);}'

    def lineSet(self):
        return 'max-width:250px; border:none; border-bottom: 2px solid black; min-height:33px; max-height:38px; background:none; caret-color:black;'
#########################################

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

main()