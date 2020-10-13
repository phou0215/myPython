# -*- coding: utf-8 -*-
"""
Created on Thr Oct 18 14:25:12 2019
@author: TestEnC hanrim lee

"""
# 5G와 LTE 구분이 이루어져야 함
# 구분 방법은 Input File Tab에 5G 경우 'ENDC UE Capability' tab이 존재 함

# 기본단말_Spec정보



import os
import sys
import re
import openpyxl
import pkg_resources.py2_warn
from os.path import expanduser
import threading

#from konlpy.tag import Komoran
from time import sleep
from datetime import datetime

#import pytagcloud
from PyQt5.QtCore import QThread, pyqtSignal
#selenium library
from openpyxl.styles import Alignment, Font, NamedStyle, PatternFill
from openpyxl import formatting, styles, Workbook
from openpyxl.styles.borders import Border, Side

class Formater(QThread):

    print_flag = pyqtSignal(str)
    end_flag = pyqtSignal()
    fileCheck_flag = pyqtSignal()
    progress_flag = pyqtSignal()
    count_flag = pyqtSignal()
    dict_result = None
    tot_count = 0

    def __init__(self, filePath, parent=None):
        QThread.__init__(self, parent)

        self.file_names = filePath
        self.list_files = self.file_names.split(",")
        self.list_out_files = []
        self.dict_out = {}
        self.dict_readData = {}
        # self.list_sheet_names = []

        # self.opFlag = opFlag
        # self.modeFlag = modeFlag
        self.home = expanduser("~")

        self.end_count = "n"
        self.totalRows = 0
        self.currentRow = 0
        self.current_path = os.getcwd()
        self.battery_spec = 0.0

        # style fill pattern
        # FF0000 red
        # 0000FF blue

        # self.brown_fill = PatternFill(start_color='DDD9C4', end_color='DDD9C4', fill_type='solid')
        # self.light_brown_fill = PatternFill(start_color='EEECE1', end_color='EEECE1', fill_type='solid')
        # self.gray_fill = PatternFill(start_color='E7E6E6', end_color='E7E6E6', fill_type='solid')
        # self.dark_gray_fill = PatternFill(start_color='D9D9D9', end_color='D9D9D9', fill_type='solid')
        # self.light_gray_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
        # self.apricot_fill = PatternFill(start_color='FDE9D9', end_color='FDE9D9', fill_type='solid')
        # self.skyBlue_fill = PatternFill(start_color='DCE6F1', end_color='DCE6F1', fill_type='solid')
        # self.yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
        # self.orange_fill = PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid')
        #
        # # style font color and size
        # self.top_font = Font(name='맑은 고딕', size=12, bold=True, color='2B2B2B')
        # self.index_font = Font(name='맑은 고딕', size=11, bold=True, color='2B2B2B')
        # self.value_font = Font(name='맑은 고딕', size=11, bold=False, color='2B2B2B')
        # self.value2_font = Font(name='맑은 고딕', size=10, bold=True, color='2B2B2B')
        # self.f2_value_font = Font(name='맑은 고딕', size=10, bold=False, color='2B2B2B')
        # self.f2_blue_font = Font(name='맑은 고딕', size=10, bold=False, color='0000FF')
        # self.f2_red_font = Font(name='맑은 고딕', size=10, bold=False, color='FF0000')
        #
        # # style Alignment
        # self.general_alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
        # self.top_alignment = Alignment(wrap_text=False, horizontal="left", vertical="center")
        # self.top_alignment_2 = Alignment(wrap_text=True, horizontal="left", vertical="center")
        # self.top_alignment_3 = Alignment(wrap_text=True, horizontal="left", vertical="top")

        # # style border
        # self.thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        # ftp 관련 변수 및 설정
        # self.hostname = '192.168.0.108'
        # self.port = 21
        # self.username = 'voc'
        # self.password = 'testenc@01'

    # 분석 처리 개수 체크 함수
    def getCountRows(self):

        while True:
            if self.end_count is "n":
                sleep(0.5)
                self.count_flag.emit()
            else:
                break

    # 로그 문자 처리 함수
    def setPrintText(self, text):

        strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        text = self.find_between(text, "/s", "/e")
        print_text = strToday+":\n"+text+"\n"
        self.print_flag.emit("{}".format(print_text))

    # 쓰레드 종료 함수
    def stop(self):
        sleep(0.5)
        self.terminate()

    # 특수 문자 제거 함수
    def removeString(self, text):

        tempText = re.sub('[-=+,#/\?^$@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>\{\}`><]\'', '', text)
        return tempText

    # 문장 앞 부터 조건에 맞는 문자열 substring
    def find_between(self, s, first, last):
        try:
            returnData = ""
            start = s.index(first)+len(first)
            end = s.index(last, start)
            returnData = s[start:end]
            return returnData
        except ValueError:
            return returnData

    # 문장 뒤 부터 조건에 맞는 문자열 substring
    def find_between_r(self, s, first, last ):
        try:
            returnData = ""
            start = s.rindex(first)+len(first)
            end = s.rindex(last, start)
            returnData = s[start:end]
            return returnData
        except ValueError:
            return returnData

    # float num check a point
    def check_num(self, num):

        return_data = None
        if num is None or num == '':
            return_data = '-'
        else:
            try:
                return_data = '%.2f'%float(num)
            except:
                return_data = str(num)

        return return_data

    # check calculate comparison
    def cal_comparison(self, standard, measure):

        return_data = None
        try:
            return_data = self.check_num(abs(round(abs(float(measure)) - float(standard), 2)))
        except:
            return_data = '-'

        return return_data

    # check convert num available
    def isNumber(self, string_data):

        try:
            temp_data = float(string_data)
            return True
        except:
            return False

    # check convert num available
    def check_empty(self, string_data):

        return_data = None
        if string_data is None or string_data == '' or string_data.lower() in ['n/a', 'na', 'nt', 'n/t']:
            return_data = '-'
        else:
            return_data = str(string_data)

        return return_data

    # summary Tab
    def summary_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                temp_data = {}
                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])

                # get data from wb_input
                sheet_in = wb_input['Summary']
                temp_data['팻네임 / 모델명'] = sheet_in['C5'].value
                temp_data['OS 및 Binary Version'] = sheet_in['C8'].value + "/" + sheet_in['C6'].value
                temp_data['Chipset (AP / CP)'] = sheet_in['K6'].value
                temp_data['가로 폭 (mm) / Display Size (inch)'] = sheet_in['K7'].value
                temp_data['배터리 용량 (mAh)'] = str(sheet_in['K8'].value)+'mAh'
                self.battery_spec = float(sheet_in['K8'].value)
                temp_data['검증 차수'] = sheet_in['C9'].value
                temp_data['검증 기간'] = sheet_in['K5'].value

                #option setting wb.output
                sheet_out = wb_output['검증결과요약']
                # sheet row 3 handle
                sheet_out.merge_cells('B3:C3')
                sheet_out['B3'] = "1. 단말 기본 정보"
                # sheet row 4 handle
                sheet_out.merge_cells('B4:C4')
                sheet_out.merge_cells('D4:E4')
                sheet_out['B4'] = "팻네임 / 모델명"
                sheet_out['D4'] = temp_data['팻네임 / 모델명']
                # sheet row 5 handle
                sheet_out.merge_cells('B5:C5')
                sheet_out.merge_cells('D5:E5')
                sheet_out['B5'] = "OS 및 Binary Version"
                sheet_out['D5'] = temp_data['OS 및 Binary Version']
                # sheet row 6 handle
                sheet_out.merge_cells('B6:C6')
                sheet_out.merge_cells('D6:E6')
                sheet_out['B6'] = "Chipset (AP / CP)"
                sheet_out['D6'] = temp_data['Chipset (AP / CP)']
                # sheet row 7 handle
                sheet_out.merge_cells('B7:C7')
                sheet_out.merge_cells('D7:E7')
                sheet_out['B7'] = "가로 폭 (mm) / Display Size (inch)"
                sheet_out['D7'] = temp_data['가로 폭 (mm) / Display Size (inch)']
                # sheet row 7 handle
                sheet_out.merge_cells('B8:C8')
                sheet_out.merge_cells('D8:E8')
                sheet_out['B8'] = "배터리 용량 (mAh)"
                sheet_out['D8'] = temp_data['배터리 용량 (mAh)']
                # sheet row 10 handle
                sheet_out.merge_cells('B10:C10')
                sheet_out['B10'] = "2. 검증 차수 및 검증 기간"
                # sheet row 11 handle
                sheet_out.merge_cells('B11:C11')
                sheet_out.merge_cells('D11:E11')
                sheet_out['B11'] = "검증 차수"
                sheet_out['D11'] = temp_data['검증 차수']
                # sheet row 12 handle
                sheet_out.merge_cells('B12:C12')
                sheet_out.merge_cells('D12:E12')
                sheet_out['B12'] = "검증 기간"
                sheet_out['D12'] = temp_data['검증 기간']
                # sheet row 14 handle
                sheet_out.merge_cells('B14:D14')
                sheet_out['B14'] = '3. 검증 결과 (항목수 : 00, Test Case 수 : 78)'
                # sheet row 15 handle
                sheet_out.merge_cells('B15:C15')
                sheet_out['B15'] = '항목'
                sheet_out['D15'] = 'Pass'
                sheet_out['E15'] = 'Fail'
                # sheet row 16 handle
                sheet_out.merge_cells('B16:B19')
                sheet_out['B16'] = 'RF성능'
                sheet_out['C16'] = 'TRP'
                # sheet row 17 handle
                sheet_out['C17'] = 'TIS'
                # sheet row 18 handle
                sheet_out['C18'] = '속도'
                # sheet row 19 handle
                sheet_out['C19'] = 'Call Setup Test'
                # sheet row 20 handle
                sheet_out.merge_cells('B20:C20')
                sheet_out['B20'] = 'MOS'
                # sheet row 21 handle
                sheet_out.merge_cells('B21:C21')
                sheet_out['B21'] = '배터리소모전류 (시간)'
                # sheet row 22 handle
                sheet_out.merge_cells('B22:C22')
                sheet_out['B22'] = '주파수동조'
                # sheet row 23 handle
                sheet_out.merge_cells('B23:C23')
                sheet_out['B23'] = '발열'
                sheet_out['D23'] = ''
                sheet_out['E23'] = ''
                # sheet row 24 handle
                sheet_out.merge_cells('B24:C24')
                sheet_out['B24'] = '소계'
                sheet_out['D24'] = ''
                sheet_out['E24'] = ''
                # sheet row 25 handle
                sheet_out.merge_cells('B25:C25')
                sheet_out.merge_cells('D25:E25')
                sheet_out['B25'] = '점수 (가/감점)'
                sheet_out['D25'] = '86.9(+12)'
                # sheet row 26 handle
                sheet_out.merge_cells('B26:C26')
                sheet_out.merge_cells('D26:E26')
                sheet_out['B26'] = '배터리소모전류 (DOU, Test case : 35)'
                sheet_out['D26'] = '1.44일'

                # sheet row 26 handle
                sheet_out.merge_cells('B28:E28')
                sheet_out.merge_cells('B29:E29')
                sheet_out['B28'] = '4. 특이사항'
                sheet_out['B29'] = ''

                self.setPrintText('/s {}번 파일 "검증결과요약" 테이터 입력 완료 /e'.format(idx+1))

                if self.opFlag:

                    # all cell aligment adjust
                    for mCell in sheet_out["B3:E26"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment

                    for mCell in sheet_out["B29:E29"]:
                        for cell in mCell:
                            cell.alignment = self.top_alignment_3

                    # each coloum width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D', 'E']
                    sheet_width_list = [3.38, 20, 20, 20, 20]
                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[29].height = 85.5

                    # Set style on Cell
                    # row 3
                    sheet_out['B3'].font = self.top_font
                    sheet_out['B3'].alignment = self.top_alignment
                    # row 4
                    sheet_out['B4'].font = self.index_font
                    sheet_out['B4'].fill = self.brown_fill
                    sheet_out['B4'].border = self.thin_border
                    sheet_out['D4'].font = self.index_font
                    sheet_out['D4'].border = self.thin_border
                    sheet_out['C4'].border = self.thin_border
                    sheet_out['E4'].border = self.thin_border
                    # row 5
                    sheet_out['B5'].font = self.index_font
                    sheet_out['B5'].fill = self.brown_fill
                    sheet_out['B5'].border = self.thin_border
                    sheet_out['D5'].font = self.index_font
                    sheet_out['D5'].border = self.thin_border
                    sheet_out['C5'].border = self.thin_border
                    sheet_out['E5'].border = self.thin_border
                    # row 6
                    sheet_out['B6'].font = self.index_font
                    sheet_out['B6'].fill = self.brown_fill
                    sheet_out['B6'].border = self.thin_border
                    sheet_out['D6'].font = self.index_font
                    sheet_out['D6'].border = self.thin_border
                    sheet_out['C6'].border = self.thin_border
                    sheet_out['E6'].border = self.thin_border
                    # row 7
                    sheet_out['B7'].font = self.index_font
                    sheet_out['B7'].fill = self.brown_fill
                    sheet_out['B7'].border = self.thin_border
                    sheet_out['D7'].font = self.index_font
                    sheet_out['D7'].border = self.thin_border
                    sheet_out['C7'].border = self.thin_border
                    sheet_out['E7'].border = self.thin_border
                    # row 8
                    sheet_out['B8'].font = self.index_font
                    sheet_out['B8'].fill = self.brown_fill
                    sheet_out['B8'].border = self.thin_border
                    sheet_out['D8'].font = self.index_font
                    sheet_out['D8'].border = self.thin_border
                    sheet_out['C8'].border = self.thin_border
                    sheet_out['E8'].border = self.thin_border
                    # row 10
                    sheet_out['B10'].font = self.top_font
                    sheet_out['B10'].alignment = self.top_alignment
                    # row 11
                    sheet_out['B11'].font = self.index_font
                    sheet_out['B11'].fill = self.brown_fill
                    sheet_out['B11'].border = self.thin_border
                    sheet_out['C11'].font = self.index_font
                    sheet_out['C11'].border = self.thin_border
                    sheet_out['D11'].border = self.thin_border
                    sheet_out['D11'].font = self.index_font
                    sheet_out['E11'].border = self.thin_border

                    # row 12
                    sheet_out['B12'].font = self.index_font
                    sheet_out['B12'].fill = self.brown_fill
                    sheet_out['B12'].border = self.thin_border
                    sheet_out['C12'].font = self.index_font
                    sheet_out['C12'].border = self.thin_border
                    sheet_out['D12'].border = self.thin_border
                    sheet_out['D12'].font = self.index_font
                    sheet_out['E12'].border = self.thin_border
                    # row 14
                    sheet_out['B14'].font = self.top_font
                    sheet_out['B14'].alignment = self.top_alignment
                    # row 15
                    sheet_out['B15'].font = self.index_font
                    sheet_out['B15'].fill = self.brown_fill
                    sheet_out['B15'].border = self.thin_border
                    sheet_out['D15'].font = self.index_font
                    sheet_out['D15'].fill = self.brown_fill
                    sheet_out['D15'].border = self.thin_border
                    sheet_out['E15'].font = self.index_font
                    sheet_out['E15'].fill = self.brown_fill
                    sheet_out['E15'].border = self.thin_border
                    sheet_out['C15'].border = self.thin_border
                    # row 16
                    sheet_out['B16'].font = self.index_font
                    sheet_out['B16'].fill = self.gray_fill
                    sheet_out['B16'].border = self.thin_border
                    sheet_out['C16'].font = self.index_font
                    sheet_out['C16'].fill = self.gray_fill
                    sheet_out['C16'].border = self.thin_border
                    sheet_out['D16'].font = self.index_font
                    sheet_out['D16'].border = self.thin_border
                    sheet_out['E16'].font = self.index_font
                    sheet_out['E16'].border = self.thin_border
                    # row 17
                    sheet_out['B17'].border = self.thin_border
                    sheet_out['C17'].font = self.index_font
                    sheet_out['C17'].fill = self.gray_fill
                    sheet_out['C17'].border = self.thin_border
                    sheet_out['D17'].font = self.index_font
                    sheet_out['D17'].border = self.thin_border
                    sheet_out['E17'].font = self.index_font
                    sheet_out['E17'].border = self.thin_border
                    # row 18
                    sheet_out['B18'].border = self.thin_border
                    sheet_out['C18'].font = self.index_font
                    sheet_out['C18'].fill = self.gray_fill
                    sheet_out['C18'].border = self.thin_border
                    sheet_out['D18'].font = self.index_font
                    sheet_out['D18'].border = self.thin_border
                    sheet_out['E18'].font = self.index_font
                    sheet_out['E18'].border = self.thin_border
                    # row 19
                    sheet_out['B19'].border = self.thin_border
                    sheet_out['C19'].font = self.index_font
                    sheet_out['C19'].fill = self.gray_fill
                    sheet_out['C19'].border = self.thin_border
                    sheet_out['D19'].font = self.index_font
                    sheet_out['D19'].border = self.thin_border
                    sheet_out['E19'].font = self.index_font
                    sheet_out['E19'].border = self.thin_border
                    # row 20
                    sheet_out['B20'].font = self.index_font
                    sheet_out['B20'].fill = self.gray_fill
                    sheet_out['B20'].border = self.thin_border
                    sheet_out['D20'].font = self.index_font
                    sheet_out['D20'].border = self.thin_border
                    sheet_out['E20'].font = self.index_font
                    sheet_out['E20'].border = self.thin_border
                    sheet_out['C20'].border = self.thin_border
                    # row 21
                    sheet_out['B21'].font = self.index_font
                    sheet_out['B21'].fill = self.gray_fill
                    sheet_out['B21'].border = self.thin_border
                    sheet_out['D21'].font = self.index_font
                    sheet_out['D21'].border = self.thin_border
                    sheet_out['E21'].font = self.index_font
                    sheet_out['E21'].border = self.thin_border
                    sheet_out['C21'].border = self.thin_border
                    # row 22
                    sheet_out['B22'].font = self.index_font
                    sheet_out['B22'].fill = self.gray_fill
                    sheet_out['B22'].border = self.thin_border
                    sheet_out['D22'].font = self.index_font
                    sheet_out['D22'].border = self.thin_border
                    sheet_out['E22'].font = self.index_font
                    sheet_out['E22'].border = self.thin_border
                    sheet_out['C22'].border = self.thin_border
                    # row 23
                    sheet_out['B23'].font = self.index_font
                    sheet_out['B23'].fill = self.gray_fill
                    sheet_out['B23'].border = self.thin_border
                    sheet_out['D23'].font = self.index_font
                    sheet_out['D23'].border = self.thin_border
                    sheet_out['E23'].font = self.index_font
                    sheet_out['E23'].border = self.thin_border
                    sheet_out['C23'].border = self.thin_border
                    # row 24
                    sheet_out['B24'].font = self.index_font
                    sheet_out['B24'].fill = self.light_brown_fill
                    sheet_out['B24'].border = self.thin_border
                    sheet_out['D24'].font = self.index_font
                    sheet_out['D24'].fill = self.light_brown_fill
                    sheet_out['D24'].border = self.thin_border
                    sheet_out['C24'].border = self.thin_border
                    sheet_out['E24'].border = self.thin_border
                    sheet_out['E24'].fill = self.light_brown_fill
                    # row 25
                    sheet_out['B25'].font = self.index_font
                    sheet_out['B25'].fill = self.light_brown_fill
                    sheet_out['B25'].border = self.thin_border
                    sheet_out['D25'].font = self.index_font
                    sheet_out['D25'].fill = self.light_brown_fill
                    sheet_out['D25'].border = self.thin_border
                    sheet_out['C25'].border = self.thin_border
                    sheet_out['E25'].border = self.thin_border
                    # row 26
                    sheet_out['B26'].font = self.index_font
                    sheet_out['B26'].fill = self.gray_fill
                    sheet_out['B26'].border = self.thin_border
                    sheet_out['D26'].font = self.index_font
                    sheet_out['D26'].fill = self.light_brown_fill
                    sheet_out['D26'].border = self.thin_border
                    sheet_out['C25'].border = self.thin_border
                    sheet_out['E25'].border = self.thin_border
                    # row 28
                    sheet_out['B28'].font = self.index_font
                    # row 29
                    sheet_out['B29'].font = self.index_font
                    sheet_out['B29'].border = self.thin_border
                    sheet_out['C29'].border = self.thin_border
                    sheet_out['D29'].border = self.thin_border
                    sheet_out['E29'].border = self.thin_border

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "검증요약결과" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 시험결과요약 Tab
    def test_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                temp_data = []
                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])

                # get data from wb_input
                sheet_in = wb_input['시험결과요약']
                for i in range(6, 28):
                    temp_data.append([sheet_in['F'+str(i)].value, sheet_in['G'+str(i)].value, sheet_in['H'+str(i)].value])

                #option setting wb.output
                sheet_out = wb_output['시험결과요약']
                # sheet row 2 handle
                sheet_out.merge_cells('B2:H2')
                sheet_out['B2'] = 'H/W 검증결과 요약'

                # sheet row 4 and 5 handle
                sheet_out.merge_cells('B4:C5')
                sheet_out['B4'] = "항목"
                sheet_out.merge_cells('D4:E5')
                sheet_out['D4'] = 'Test case'
                sheet_out.merge_cells('F4:H4')
                sheet_out['F4'] = '결과'
                sheet_out['F5'] = 'Pass'
                sheet_out['G5'] = 'Fail'
                sheet_out['H5'] = '점수'

                # sheet 6 ~ 20 handle
                sheet_out.merge_cells('B6:B20')
                sheet_out['B6'] = sheet_in['B6'].value
                sheet_out.merge_cells('C6:C10')
                sheet_out['C6'] = sheet_in['C6'].value
                sheet_out.merge_cells('C11:C15')
                sheet_out['C11'] = sheet_in['C11'].value
                sheet_out.merge_cells('C16:C19')
                sheet_out['C16'] = sheet_in['C16'].value
                sheet_out['C20'] = sheet_in['C20'].value
                sheet_out.merge_cells('D6:D7')
                sheet_out['D6'] = sheet_in['D6'].value
                sheet_out.merge_cells('D8:D9')
                sheet_out['D8'] = sheet_in['D8'].value
                sheet_out['D10'] = sheet_in['D10'].value
                sheet_out.merge_cells('D11:D12')
                sheet_out['D11'] = sheet_in['D11'].value
                sheet_out.merge_cells('D13:D14')
                sheet_out['D13'] = sheet_in['D13'].value
                sheet_out['D15'] = sheet_in['D15'].value
                sheet_out.merge_cells('D16:D17')
                sheet_out['D16'] = sheet_in['D16'].value
                sheet_out.merge_cells('D18:D19')
                sheet_out['D18'] = sheet_in['D18'].value
                sheet_out['D20'] = sheet_in['D20'].value
                sheet_out['E6'] = sheet_in['E6'].value
                sheet_out['E7'] = sheet_in['E7'].value
                sheet_out['E8'] = sheet_in['E8'].value
                sheet_out['E9'] = sheet_in['E9'].value
                sheet_out['E10'] = sheet_in['E10'].value
                sheet_out['E11'] = sheet_in['E11'].value
                sheet_out['E12'] = sheet_in['E12'].value
                sheet_out['E13'] = sheet_in['E13'].value
                sheet_out['E14'] = sheet_in['E14'].value
                sheet_out['E15'] = sheet_in['E15'].value
                sheet_out['E16'] = sheet_in['E16'].value
                sheet_out['E17'] = sheet_in['E17'].value
                sheet_out['E18'] = sheet_in['E18'].value
                sheet_out['E19'] = sheet_in['E19'].value
                sheet_out['E20'] = sheet_in['E20'].value

                # sheet 21 ~ 24 handle
                sheet_out.merge_cells('B21:C24')
                sheet_out['B21'] = sheet_in['B21'].value
                sheet_out.merge_cells('D21:D22')
                sheet_out['D21'] = sheet_in['D21'].value
                sheet_out.merge_cells('D23:D24')
                sheet_out['D23'] = sheet_in['D23'].value
                sheet_out['E21'] = sheet_in['E21'].value
                sheet_out['E22'] = sheet_in['E22'].value
                sheet_out['E23'] = sheet_in['E23'].value
                sheet_out['E24'] = sheet_in['E24'].value

                #sheet 25 ~ 28 handle
                sheet_out.merge_cells('B25:C25')
                sheet_out['B25'] = sheet_in['B25'].value
                sheet_out.merge_cells('D25:E25')
                sheet_out['D25'] = sheet_in['D25'].value
                sheet_out.merge_cells('B26:C26')
                sheet_out['B26'] = sheet_in['B26'].value
                sheet_out.merge_cells('D26:E26')
                sheet_out['D26'] = sheet_in['D26'].value
                sheet_out.merge_cells('B27:C27')
                sheet_out['B27'] = '발열'
                sheet_out.merge_cells('D27:E27')
                sheet_out['D27'] = 'Live Streaming (충전/미충전), 게임(충전/미충전)'
                sheet_out.merge_cells('B28:E28')
                sheet_out['B28'] = sheet_in['B27'].value
                sheet_out.merge_cells('B29:C29')
                sheet_out['B29'] = sheet_in['B28'].value
                sheet_out.merge_cells('D29:E29')
                sheet_out['D29'] = sheet_in['D28'].value
                sheet_out.merge_cells('F29:H29')
                sheet_out['F29'] = sheet_in['F28'].value

                self.setPrintText('/s {}번 파일 "시험결과요약" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data
                for i in range(6, 27):

                    sheet_out['F' + str(i)] = temp_data[i-6][0]
                    sheet_out['G' + str(i)] = temp_data[i-6][1]
                    sheet_out['H' + str(i)] = temp_data[i-6][2]

                sheet_out['F28'] = temp_data[21][0]
                sheet_out['G28'] = temp_data[21][1]
                sheet_out['H28'] = temp_data[21][2]

                if self.opFlag:

                    # all cell aligment adjust
                    for mCell in sheet_out["B4:H29"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment

                    # all cell border adjust
                    for mCell in sheet_out["B4:H29"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["B4:H29"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['B2'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')
                    sheet_out['B2'].alignment = self.general_alignment

                    # each coloum width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                    sheet_width_list = [3.38, 9, 14.25, 8.5, 36.75, 11.25, 11.25, 11.25]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[2].height = 26.25

                    # Set Pattern Fill
                    sheet_out['B4'].fill = self.brown_fill
                    sheet_out['D4'].fill = self.brown_fill
                    sheet_out['F4'].fill = self.brown_fill
                    sheet_out['F5'].fill = self.brown_fill
                    sheet_out['G5'].fill = self.brown_fill
                    sheet_out['H5'].fill = self.brown_fill

                    for i in range(6, 28):
                        sheet_out['B' + str(i)].fill = self.gray_fill
                        sheet_out['C' + str(i)].fill = self.gray_fill
                        sheet_out['D' + str(i)].fill = self.gray_fill
                        sheet_out['E' + str(i)].fill = self.gray_fill

                    sheet_out['B28'].fill = self.dark_gray_fill
                    sheet_out['F28'].fill = self.dark_gray_fill
                    sheet_out['G28'].fill = self.dark_gray_fill
                    sheet_out['H28'].fill = self.dark_gray_fill
                    sheet_out['B29'].fill = self.gray_fill
                    sheet_out['D29'].fill = self.gray_fill
                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "시험결과요약" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # TRP Tab
    def trp_generate_data(self):
        # 절대값 abs
        try:
            for idx, item in enumerate(self.list_files):

                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                list_5g_trp = []
                list_lte_trp = []
                list_wcdma_trp = []

                # get data from wb_input
                sheet_in = wb_input['5G OTA']
                list_5g_trp.append(self.check_num(sheet_in['J5'].value))
                list_5g_trp.append(self.check_num(sheet_in['J6'].value))

                sheet_in = wb_input['LTE OTA']
                list_lte_trp.append(self.check_num(sheet_in['K17'].value))
                list_lte_trp.append(self.check_num(sheet_in['C17'].value))
                list_lte_trp.append(self.check_num(sheet_in['C10'].value))
                list_lte_trp.append(self.check_num(sheet_in['G17'].value))
                list_lte_trp.append(self.check_num(sheet_in['G10'].value))
                list_lte_trp.append(self.check_num(sheet_in['M17'].value))
                list_lte_trp.append(self.check_num(sheet_in['E17'].value))
                list_lte_trp.append(self.check_num(sheet_in['E10'].value))
                list_lte_trp.append(self.check_num(sheet_in['I17'].value))
                list_lte_trp.append(self.check_num(sheet_in['I10'].value))

                sheet_in = wb_input['WCDMA OTA']
                list_wcdma_trp.append(self.check_num(sheet_in['D9'].value))

                #option setting wb.output
                sheet_out = wb_output['TRP']
                # sheet row 2 handle
                sheet_out.merge_cells('A1:C1')
                sheet_out['A1'] = 'TRP 결과'

                # 3~4 row
                sheet_out['A3'] = '▣ SISO TRP'
                sheet_out['A4'] = ' - 5G'

                # sheet row 5 and 7 handle
                sheet_out['A5'] = '구분'
                sheet_out['B5'] = '기준(RHP)'
                sheet_out['C5'] = '측정결과'
                sheet_out['D5'] = '비교'
                sheet_out['A6'] = 'CP-OFDM (n78)'
                sheet_out['B6'] = '16.86dBm(V50S)'
                sheet_out['C6'] = list_5g_trp[0]+'dBm'
                # sheet_out['D6'] = self.check_num(abs(round(abs(float(list_5g_trp[0]))-16.86, 2))) + 'dBm'
                sheet_out['D6'] = self.cal_comparison(16.86, list_5g_trp[0]) + 'dBm'
                sheet_out['A7'] = 'DFTs-OFDM (n78)'
                sheet_out['B7'] = '-'
                sheet_out['C7'] = list_5g_trp[1]+'dBm'
                sheet_out['D7'] = '-'

                # sheet row 8 and 15 handle
                sheet_out['A8'] = ' - LTE'
                sheet_out['A9'] = '구분'
                sheet_out['B9'] = '기준(RHP)'
                sheet_out['C9'] = '측정결과'
                sheet_out['D9'] = '비교'

                sheet_out['A10'] = 'Band 1 15M'
                sheet_out['B10'] = '14.00dBm'
                sheet_out['C10'] = list_lte_trp[0] + 'dBm'
                # sheet_out['D10'] = self.check_num(abs(round(abs(float(list_lte_trp[0]))-14.00, 2))) + 'dBm'
                sheet_out['D10'] = self.cal_comparison(14.00, list_lte_trp[0]) + 'dBm'
                sheet_out['A11'] = 'Band 3 20M'
                sheet_out['B11'] = '15.00dBm'
                sheet_out['C11'] = list_lte_trp[1] + 'dBm'
                # sheet_out['D11'] = self.check_num(abs(round(abs(float(list_lte_trp[1]))-15.00, 2))) + 'dBm'
                sheet_out['D11'] = self.cal_comparison(15.00, list_lte_trp[1]) + 'dBm'
                sheet_out['A12'] = 'Band 5 10M'
                sheet_out['B12'] = '13.50dBm'
                sheet_out['C12'] = list_lte_trp[2] + 'dBm'
                # sheet_out['D12'] = self.check_num(abs(round(abs(float(list_lte_trp[2]))-13.50, 2))) + 'dBm'
                sheet_out['D12'] = self.cal_comparison(13.50, list_lte_trp[2]) + 'dBm'
                sheet_out['A13'] = 'Band 7 20M'
                sheet_out['B13'] = '13.00dBm'
                sheet_out['C13'] = list_lte_trp[3] + 'dBm'
                # sheet_out['D13'] = self.check_num(abs(round(abs(float(list_lte_trp[3])) - 13.00, 2))) + 'dBm'
                sheet_out['D13'] = self.cal_comparison(13.00, list_lte_trp[3]) + 'dBm'
                sheet_out['A14'] = 'Band 7 10M'
                sheet_out['B14'] = '13.00dBm'
                sheet_out['C14'] = list_lte_trp[4] + 'dBm'
                # sheet_out['D14'] = self.check_num(abs(round(abs(float(list_lte_trp[4])) - 13.00, 2))) + 'dBm'
                sheet_out['D14'] = self.cal_comparison(13.00, list_lte_trp[4]) + 'dBm'

                # sheet row 15 and 17 handle
                sheet_out['A15'] = ' - WCDMA (납품검사 결과)'
                sheet_out['A16'] = '구분'
                sheet_out['B16'] = '기준(RHP)'
                sheet_out['C16'] = '측정결과'
                sheet_out['A17'] = 'Band 1'
                sheet_out['B17'] = '15.00dBm'
                sheet_out['C17'] = list_wcdma_trp[0] + 'dBm'
                # sheet_out['D17'] = self.check_num(abs(round(abs(float(list_wcdma_trp[0])) - 15.00, 2))) + 'dBm'
                sheet_out['D17'] = self.cal_comparison(15.00, list_wcdma_trp[0]) + 'dBm'

                # sheet row 19 and 27 handle
                sheet_out['A19'] = '▣ MIMO TRP'
                sheet_out['A20'] = ' - LTE'
                sheet_out['A21'] = '구분'
                sheet_out['B21'] = '기준(RHP)'
                sheet_out['C21'] = '측정결과'
                sheet_out['A22'] = 'Band 1 15M'
                sheet_out['B22'] = '14.00dBm'
                sheet_out['C22'] = list_lte_trp[5] + 'dBm'
                # sheet_out['D22'] = self.check_num(abs(round(abs(float(list_lte_trp[5])) - 14.00, 2))) + 'dBm'
                sheet_out['D22'] = self.cal_comparison(14.00, list_lte_trp[5]) + 'dBm'
                sheet_out['A23'] = 'Band 3 20M'
                sheet_out['B23'] = '15.00dBm'
                sheet_out['C23'] = list_lte_trp[6] + 'dBm'
                # sheet_out['D23'] = self.check_num(abs(round(abs(float(list_lte_trp[6])) - 15.00, 2))) + 'dBm'
                sheet_out['D23'] = self.cal_comparison(15.00, list_lte_trp[6]) + 'dBm'
                sheet_out['A24'] = 'Band 5 10M'
                sheet_out['B24'] = '13.50dBm'
                sheet_out['C24'] = list_lte_trp[7]+'dBm'
                # sheet_out['D24'] = self.check_num(abs(round(abs(float(list_lte_trp[7])) - 13.50, 2))) + 'dBm'
                sheet_out['D24'] = self.cal_comparison(13.50, list_lte_trp[7]) + 'dBm'
                sheet_out['A25'] = 'Band 7 20M'
                sheet_out['B25'] = '13.00dBm'
                sheet_out['C25'] = list_lte_trp[8] + 'dBm'
                # sheet_out['D25'] = self.check_num(abs(round(abs(float(list_lte_trp[8])) - 13.00, 2))) + 'dBm'
                sheet_out['D25'] = self.cal_comparison(13.00, list_lte_trp[8]) + 'dBm'
                sheet_out['A26'] = 'Band 7 10M'
                sheet_out['B26'] = '13.00dBm'
                sheet_out['C26'] = list_lte_trp[9] + 'dBm'
                # sheet_out['D26'] = self.check_num(abs(round(abs(float(list_lte_trp[9])) - 13.00, 2))) + 'dBm'
                sheet_out['D26'] = self.cal_comparison(13.00, list_lte_trp[9]) + 'dBm'

                self.setPrintText('/s {}번 파일 "TRP" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:D26"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A4'].alignment = self.top_alignment
                    sheet_out['A8'].alignment = self.top_alignment
                    sheet_out['A15'].alignment = self.top_alignment
                    sheet_out['A19'].alignment = self.top_alignment
                    sheet_out['A20'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A5:D7"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A9:D14"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A16:D17"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A21:D26"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A3:D26"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each coloum width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D']
                    sheet_width_list = [25, 16.75, 17, 15]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for i in [5, 9, 16, 21]:
                        sheet_out['A' + str(i)].fill = self.brown_fill
                        sheet_out['B' + str(i)].fill = self.brown_fill
                        sheet_out['C' + str(i)].fill = self.brown_fill
                        sheet_out['D' + str(i)].fill = self.brown_fill

                    for i in [6, 7, 10, 11, 12, 13, 14, 17, 22, 23, 24, 25, 26]:
                        sheet_out['A'+str(i)].fill = self.gray_fill
                        sheet_out['B'+str(i)].fill = self.apricot_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "TRP" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # TIS Tab
    def tis_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                list_5g_tis = []
                list_lte_tis = []
                list_wcdma_tis = []

                # get data from wb_input
                sheet_in = wb_input['5G OTA']
                list_5g_tis.append(self.check_num(sheet_in['J7'].value))
                list_5g_tis.append(self.check_num(sheet_in['J8'].value))

                sheet_in = wb_input['LTE OTA']
                list_lte_tis.append(self.check_num(sheet_in['L17'].value))
                list_lte_tis.append(self.check_num(sheet_in['D17'].value))
                list_lte_tis.append(self.check_num(sheet_in['D10'].value))
                list_lte_tis.append(self.check_num(sheet_in['H17'].value))
                list_lte_tis.append(self.check_num(sheet_in['H10'].value))
                list_lte_tis.append(self.check_num(sheet_in['N17'].value))
                list_lte_tis.append(self.check_num(sheet_in['F17'].value))
                list_lte_tis.append(self.check_num(sheet_in['F10'].value))
                list_lte_tis.append(self.check_num(sheet_in['J17'].value))
                list_lte_tis.append(self.check_num(sheet_in['J10'].value))

                sheet_in = wb_input['WCDMA OTA']
                list_wcdma_tis.append(self.check_num(sheet_in['E9'].value))

                #option setting wb.output
                sheet_out = wb_output['TIS']
                # sheet row 2 handle
                sheet_out.merge_cells('A1:C1')
                sheet_out['A1'] = 'TIS 결과'

                # 3~4 row
                sheet_out['A3'] = '▣ SISO TIS'
                sheet_out['A4'] = ' - 5G'

                # sheet row 5 and 7 handle
                sheet_out['A5'] = '구분'
                sheet_out['B5'] = '기준(RHP)'
                sheet_out['C5'] = '측정결과'
                sheet_out['D5'] = '비교'
                sheet_out['A6'] = 'SISO (n78)'
                sheet_out['B6'] = '-'
                sheet_out['C6'] = list_5g_tis[0] + 'dBm'
                sheet_out['D6'] = '-'

                # sheet row 8 and 14 handle
                sheet_out['A8'] = ' - LTE'
                sheet_out['A9'] = '구분'
                sheet_out['B9'] = '기준(RHP)'
                sheet_out['C9'] = '측정결과'
                sheet_out['D9'] = '비교'
                sheet_out['A10'] = 'Band 1 15M'
                sheet_out['B10'] = '-92.00dBm'
                sheet_out['C10'] = list_lte_tis[0] + 'dBm'
                # sheet_out['D10'] = self.check_num(abs(round(abs(float(list_lte_tis[0])) - 92.00, 2))) + 'dBm'
                sheet_out['D10'] = self.cal_comparison(92.00, list_lte_tis[0]) + 'dBm'
                sheet_out['A11'] = 'Band 3 20M'
                sheet_out['B11'] = '-91.00dBm'
                sheet_out['C11'] = list_lte_tis[1] + 'dBm'
                # sheet_out['D11'] = self.check_num(abs(round(abs(float(list_lte_tis[1])) - 91.00, 2))) + 'dBm'
                sheet_out['D11'] = self.cal_comparison(91.00, list_lte_tis[1]) + 'dBm'
                sheet_out['A12'] = 'Band 5 10M'
                sheet_out['B12'] = '-87.00dBm'
                sheet_out['C12'] = list_lte_tis[2] + 'dBm'
                # sheet_out['D12'] = self.check_num(abs(round(abs(float(list_lte_tis[2])) - 87.00, 2))) + 'dBm'
                sheet_out['D12'] = self.cal_comparison(87.00, list_lte_tis[2]) + 'dBm'
                sheet_out['A13'] = 'Band 7 20M'
                sheet_out['B13'] = '-90.00dBm'
                sheet_out['C13'] = list_lte_tis[3] + 'dBm'
                sheet_out['D13'] = self.check_num(abs(round(abs(float(list_lte_tis[3])) - 90.00, 2))) + 'dBm'
                sheet_out['D13'] = self.cal_comparison(90.00, list_lte_tis[3]) + 'dBm'
                sheet_out['A14'] = 'Band 7 10M'
                sheet_out['B14'] = '-93.00dBm'
                sheet_out['C14'] = list_lte_tis[4] + 'dBm'
                # sheet_out['D14'] = self.check_num(abs(round(abs(float(list_lte_tis[4])) - 93.00, 2))) + 'dBm'
                sheet_out['D14'] = self.cal_comparison(93.00, list_lte_tis[4]) + 'dBm'

                # sheet row 16 and 18 handle
                sheet_out['A15'] = ' - WCDMA (납품검사 결과)'
                sheet_out['A16'] = '구분'
                sheet_out['B16'] = '기준(RHP)'
                sheet_out['C16'] = '측정결과'
                sheet_out['D16'] = '비교'
                sheet_out['A17'] = 'Band 1'
                sheet_out['B17'] = '-104.00dBm'
                sheet_out['C17'] = list_wcdma_tis[0] + 'dBm'
                # sheet_out['D17'] = self.check_num(abs(round(abs(float(list_wcdma_tis[0])) - 104.00, 2))) + 'dBm'
                sheet_out['D17'] = self.cal_comparison(104.00, list_wcdma_tis[0]) + 'dBm'

                # sheet row 19 and 22 handle
                sheet_out['A19'] = '▣ MIMO TRP'
                sheet_out['A20'] = ' - 5G'
                sheet_out['A21'] = '구분'
                sheet_out['B21'] = '기준(RHP)'
                sheet_out['C21'] = '측정결과'
                sheet_out['D21'] = '비교'
                sheet_out['A22'] = 'MIMO 4X4 (n78)'
                sheet_out['B22'] = '-'
                sheet_out['C22'] = list_5g_tis[1] + 'dBm'
                sheet_out['D22'] = '-'

                # sheet row 24 and 30 handle
                sheet_out['A24'] = ' - LTE'
                sheet_out['A25'] = '구분'
                sheet_out['B25'] = '기준(RHP)'
                sheet_out['C25'] = '측정결과'
                sheet_out['D25'] = '비교'
                sheet_out['A26'] = 'Band 1 15M'
                sheet_out['B26'] = '-86.00dBm'
                sheet_out['C26'] = list_lte_tis[5] + 'dBm'
                # sheet_out['D26'] = self.check_num(abs(round(abs(float(list_lte_tis[5])) - 86.00, 2))) + 'dBm'
                sheet_out['D26'] = self.cal_comparison(86.00, list_lte_tis[5]) + 'dBm'
                sheet_out['A27'] = 'Band 3 20M'
                sheet_out['B27'] = '-86.00dBm'
                sheet_out['C27'] = list_lte_tis[6] + 'dBm'
                # sheet_out['D27'] = self.check_num(abs(round(abs(float(list_lte_tis[6])) - 86.00, 2))) + 'dBm'
                sheet_out['D27'] = self.cal_comparison(86.00, list_lte_tis[6]) + 'dBm'
                sheet_out['A28'] = 'Band 5 10M'
                sheet_out['B28'] = '-82.50dBm'
                sheet_out['C28'] = list_lte_tis[7] + 'dBm'
                # sheet_out['D28'] = self.check_num(abs(round(abs(float(list_lte_tis[7])) - 82.50, 2))) + 'dBm'
                sheet_out['D28'] = self.cal_comparison(82.50, list_lte_tis[7]) + 'dBm'
                sheet_out['A29'] = 'Band 7 20M'
                sheet_out['B29'] = '-84.00dBm'
                sheet_out['C29'] = list_lte_tis[8] + 'dBm'
                # sheet_out['D29'] = self.check_num(abs(round(abs(float(list_lte_tis[8])) - 84.00, 2))) + 'dBm'
                sheet_out['D29'] = self.cal_comparison(84.00, list_lte_tis[8]) + 'dBm'
                sheet_out['A30'] = 'Band 7 10M'
                sheet_out['B30'] = '-87.00dBm'
                sheet_out['C30'] = list_lte_tis[9] + 'dBm'
                # sheet_out['D30'] = self.check_num(abs(round(abs(float(list_lte_tis[9])) - 87.00, 2))) + 'dBm'
                sheet_out['D30'] = self.cal_comparison(87.00, list_lte_tis[9]) + 'dBm'

                self.setPrintText('/s {}번 파일 "TIS" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:D30"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A4'].alignment = self.top_alignment
                    sheet_out['A8'].alignment = self.top_alignment
                    sheet_out['A15'].alignment = self.top_alignment
                    sheet_out['A19'].alignment = self.top_alignment
                    sheet_out['A20'].alignment = self.top_alignment
                    sheet_out['A24'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A5:D6"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A9:D14"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A16:D17"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A21:D22"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A25:D30"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A3:D30"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each coloum width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D']
                    sheet_width_list = [25, 15, 17, 15]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill

                    for i in [5, 9, 16, 21, 25]:
                        sheet_out['A' + str(i)].fill = self.brown_fill
                        sheet_out['B' + str(i)].fill = self.brown_fill
                        sheet_out['C' + str(i)].fill = self.brown_fill
                        sheet_out['D' + str(i)].fill = self.brown_fill

                    for i in [6, 10, 11, 12, 13, 14, 17, 22, 26, 27, 28, 29, 30]:
                        sheet_out['A'+str(i)].fill = self.gray_fill
                        sheet_out['B'+str(i)].fill = self.apricot_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "TIS" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 속도 Tab
    def spd_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                list_lte_spd = []

                # get data from wb_input
                sheet_in = wb_input['LTE OTA']
                # MIMO
                list_lte_spd.append(self.check_num(sheet_in['I25'].value))
                list_lte_spd.append(self.check_num(sheet_in['J25'].value))
                list_lte_spd.append(self.check_num(sheet_in['K25'].value))
                list_lte_spd.append(self.check_num(sheet_in['F25'].value))
                list_lte_spd.append(self.check_num(sheet_in['G25'].value))
                list_lte_spd.append(self.check_num(sheet_in['H25'].value))
                list_lte_spd.append(self.check_num(sheet_in['C25'].value))
                list_lte_spd.append(self.check_num(sheet_in['D25'].value))
                list_lte_spd.append(self.check_num(sheet_in['E25'].value))
                list_lte_spd.append(self.check_num(sheet_in['L25'].value))
                list_lte_spd.append(self.check_num(sheet_in['M25'].value))
                list_lte_spd.append(self.check_num(sheet_in['N25'].value))
                list_lte_spd.append(self.check_num(sheet_in['O25'].value))
                list_lte_spd.append(self.check_num(sheet_in['P25'].value))
                list_lte_spd.append(self.check_num(sheet_in['Q25'].value))
                # CA
                list_lte_spd.append(self.check_num(sheet_in['C33'].value))
                list_lte_spd.append(self.check_num(sheet_in['D33'].value))
                list_lte_spd.append(self.check_num(sheet_in['E33'].value))
                list_lte_spd.append(self.check_num(sheet_in['F33'].value))
                list_lte_spd.append(self.check_num(sheet_in['G33'].value))
                list_lte_spd.append(self.check_num(sheet_in['H33'].value))
                list_lte_spd.append(self.check_num(sheet_in['I33'].value))
                list_lte_spd.append(self.check_num(sheet_in['J33'].value))
                list_lte_spd.append(self.check_num(sheet_in['K33'].value))
                list_lte_spd.append(self.check_num(sheet_in['L33'].value))
                list_lte_spd.append(self.check_num(sheet_in['M33'].value))
                list_lte_spd.append(self.check_num(sheet_in['N33'].value))
                list_lte_spd.append(self.check_num(sheet_in['O33'].value))
                list_lte_spd.append(self.check_num(sheet_in['P33'].value))
                list_lte_spd.append(self.check_num(sheet_in['Q33'].value))
                list_lte_spd.append(self.check_num(sheet_in['R33'].value))
                list_lte_spd.append(self.check_num(sheet_in['S33'].value))
                list_lte_spd.append(self.check_num(sheet_in['T33'].value))

                #option setting wb.output
                sheet_out = wb_output['속도']
                # sheet row 2 handle
                sheet_out.merge_cells('A1:C1')
                sheet_out['A1'] = '속도 결과'

                # 3~4 row
                sheet_out['A3'] = '▣ MIMO 속도'
                sheet_out['A4'] = ' - LTE'

                # sheet row 5 and 20 handle
                sheet_out['A5'] = '구분'
                sheet_out.merge_cells('B5:C5')
                sheet_out['B5'] = '기준(Free)'
                sheet_out['D5'] = '측정결과'
                sheet_out['E5'] = '비교'

                sheet_out.merge_cells('A6:A8')
                sheet_out['A6'] = 'Band 1 15M(MCS28)'
                sheet_out['B6'] = 'RSSI'
                sheet_out['B7'] = '속도(Absolute)'
                sheet_out['B8'] = 'BLER'
                sheet_out['C6'] = '-61.00dBm'
                sheet_out['C7'] = '87700Kbps'
                sheet_out['C8'] = '20.00%'
                sheet_out['D6'] = list_lte_spd[0] + 'dBm'
                sheet_out['D7'] = list_lte_spd[1] + 'Kbps'
                sheet_out['D8'] = list_lte_spd[2] + '%'
                # sheet_out['E6'] = self.check_num(abs(round(abs(float(list_lte_spd[0])) - 61.00, 2))) + 'dBm'
                # sheet_out['E7'] = self.check_num(abs(round(abs(float(list_lte_spd[1])) - 87700, 2))) + 'Kbps'
                # sheet_out['E8'] = self.check_num(abs(round(abs(float(list_lte_spd[2])) - 20.00, 2))) + '%'
                sheet_out['E6'] = self.cal_comparison(61.00, list_lte_spd[0]) + 'dBm'
                sheet_out['E7'] = self.cal_comparison(87700.00, list_lte_spd[1]) + 'Kbps'
                sheet_out['E8'] = self.cal_comparison(20.00, list_lte_spd[2]) + '%'

                sheet_out.merge_cells('A9:A11')
                sheet_out['A9'] = 'Band 3 20M(MCS28)'
                sheet_out['B9'] = 'RSSI'
                sheet_out['B10'] = '속도(Absolute)'
                sheet_out['B11'] = 'BLER'
                sheet_out['C9'] = '-61.00dBm'
                sheet_out['C10'] = '119900Kbps'
                sheet_out['C11'] = '20.00%'
                sheet_out['D9'] = list_lte_spd[3] + 'dBm'
                sheet_out['D10'] = list_lte_spd[4] + 'Kbps'
                sheet_out['D11'] = list_lte_spd[5] + '%'
                # sheet_out['E9'] = self.check_num(abs(round(abs(float(list_lte_spd[3])) - 61.00, 2))) + 'dBm'
                # sheet_out['E10'] = self.check_num(abs(round(abs(float(list_lte_spd[4])) - 119900, 2))) + 'Kbps'
                # sheet_out['E11'] = self.check_num(abs(round(abs(float(list_lte_spd[5])) - 20.00, 2))) + '%'
                sheet_out['E9'] = self.cal_comparison(61.00, list_lte_spd[3]) + 'dBm'
                sheet_out['E10'] = self.cal_comparison(119900.00, list_lte_spd[4]) + 'Kbps'
                sheet_out['E11'] = self.cal_comparison(20.00, list_lte_spd[5]) + '%'

                sheet_out.merge_cells('A12:A14')
                sheet_out['A12'] = 'Band 5 10M(MCS27)'
                sheet_out['B12'] = 'RSSI'
                sheet_out['B13'] = '속도(Absolute)'
                sheet_out['B14'] = 'BLER'
                sheet_out['C12'] = '-60.00dBm'
                sheet_out['C13'] = '50300Kbps'
                sheet_out['C14'] = '20.00%'
                sheet_out['D12'] = list_lte_spd[6] + 'dBm'
                sheet_out['D13'] = list_lte_spd[7] + 'Kbps'
                sheet_out['D14'] = list_lte_spd[8] + '%'
                # sheet_out['E12'] = self.check_num(abs(round(abs(float(list_lte_spd[6])) - 60.00, 2))) + 'dBm'
                # sheet_out['E13'] = self.check_num(abs(round(abs(float(list_lte_spd[7])) - 50300, 2))) + 'Kbps'
                # sheet_out['E14'] = self.check_num(abs(round(abs(float(list_lte_spd[8])) - 20.00, 2))) + '%'
                sheet_out['E12'] = self.cal_comparison(60.00, list_lte_spd[6]) + 'dBm'
                sheet_out['E13'] = self.cal_comparison(50300.00, list_lte_spd[7]) + 'Kbps'
                sheet_out['E14'] = self.cal_comparison(20.00, list_lte_spd[8]) + '%'

                sheet_out.merge_cells('A15:A17')
                sheet_out['A15'] = 'Band 7 20M(MCS28)'
                sheet_out['B15'] = 'RSSI'
                sheet_out['B16'] = '속도(Absolute)'
                sheet_out['B17'] = 'BLER'
                sheet_out['C15'] = '-60.00dBm'
                sheet_out['C16'] = '119900Kbps'
                sheet_out['C17'] = '20.00%'
                sheet_out['D15'] = list_lte_spd[9] + 'dBm'
                sheet_out['D16'] = list_lte_spd[10] + 'Kbps'
                sheet_out['D17'] = list_lte_spd[11] + '%'
                # sheet_out['E15'] = self.check_num(abs(round(abs(float(list_lte_spd[9])) - 60.00, 2))) + 'dBm'
                # sheet_out['E16'] = self.check_num(abs(round(abs(float(list_lte_spd[10])) - 119900, 2))) + 'Kbps'
                # sheet_out['E17'] = self.check_num(abs(round(abs(float(list_lte_spd[11])) - 20.00, 2))) + '%'
                sheet_out['E15'] = self.cal_comparison(60.00, list_lte_spd[9]) + 'dBm'
                sheet_out['E16'] = self.cal_comparison(119900.00, list_lte_spd[10]) + 'Kbps'
                sheet_out['E17'] = self.cal_comparison(20.00, list_lte_spd[11]) + '%'

                sheet_out.merge_cells('A18:A20')
                sheet_out['A18'] = 'Band 7 10M(MCS27)'
                sheet_out['B18'] = 'RSSI'
                sheet_out['B19'] = '속도(Absolute)'
                sheet_out['B20'] = 'BLER'
                sheet_out['C18'] = '-60.00dBm'
                sheet_out['C19'] = '50300Kbps'
                sheet_out['C20'] = '20.00%'
                sheet_out['D18'] = list_lte_spd[12] + 'dBm'
                sheet_out['D19'] = list_lte_spd[13] + 'Kbps'
                sheet_out['D20'] = list_lte_spd[14] + '%'
                # sheet_out['E18'] = self.check_num(abs(round(abs(float(list_lte_spd[12])) - 60.00, 2))) + 'dBm'
                # sheet_out['E19'] = self.check_num(abs(round(abs(float(list_lte_spd[13])) - 50300, 2))) + 'Kbps'
                # sheet_out['E20'] = self.check_num(abs(round(abs(float(list_lte_spd[14])) - 20.00, 2))) + '%'
                sheet_out['E18'] = self.cal_comparison(60.00, list_lte_spd[12]) + 'dBm'
                sheet_out['E19'] = self.cal_comparison(50300.00, list_lte_spd[13]) + 'Kbps'
                sheet_out['E20'] = self.cal_comparison(20.00, list_lte_spd[14]) + '%'


                # 22 ~ 23 row
                sheet_out['A22'] = '▣ CA 속도'
                sheet_out['A23'] = ' - LTE'

                # sheet row 24 and 42 handle
                sheet_out['A24'] = '구분'
                sheet_out.merge_cells('B24:C24')
                sheet_out['B24'] = '기준(Free)'
                sheet_out['D24'] = '측정결과'
                sheet_out['E24'] = '비교'

                sheet_out.merge_cells('A25:A27')
                sheet_out['A25'] = '2CA : B3+B5(MCS28)'
                sheet_out['B25'] = 'RSSI'
                sheet_out['B26'] = '속도(Absolute)'
                sheet_out['B27'] = 'BLER'
                sheet_out['C25'] = '-58.00dBm'
                sheet_out['C26'] = '178390Kbps'
                sheet_out['C27'] = '-'
                sheet_out['D25'] = list_lte_spd[15] + 'dBm'
                sheet_out['D26'] = list_lte_spd[16] + 'Kbps'
                sheet_out['D27'] = list_lte_spd[17] + '%'
                # sheet_out['E25'] = self.check_num(abs(round(abs(float(list_lte_spd[15])) - 58.00, 2))) + 'dBm'
                # sheet_out['E26'] = self.check_num(abs(round(abs(float(list_lte_spd[16])) - 178390, 2))) + 'Kbps'
                sheet_out['E25'] = self.cal_comparison(58.00, list_lte_spd[15]) + 'dBm'
                sheet_out['E26'] = self.cal_comparison(178390.00, list_lte_spd[16]) + 'Kbps'
                sheet_out['E27'] = '-'

                sheet_out.merge_cells('A28:A30')
                sheet_out['A28'] = '3CA : B7(20M)+B3+B1(MCS28)'
                sheet_out['B28'] = 'RSSI'
                sheet_out['B29'] = '속도(Absolute)'
                sheet_out['B30'] = 'BLER'
                sheet_out['C28'] = '-58.00dBm'
                sheet_out['C29'] = '327500Kbps'
                sheet_out['C30'] = '-'
                sheet_out['D28'] = list_lte_spd[18] + 'dBm'
                sheet_out['D29'] = list_lte_spd[19] + 'Kbps'
                sheet_out['D30'] = list_lte_spd[20] + '%'
                # sheet_out['E28'] = self.check_num(abs(round(abs(float(list_lte_spd[18])) - 58.00, 2))) + 'dBm'
                # sheet_out['E29'] = self.check_num(abs(round(abs(float(list_lte_spd[19])) - 327500, 2))) + 'Kbps'
                sheet_out['E28'] = self.cal_comparison(58.00, list_lte_spd[18]) + 'dBm'
                sheet_out['E29'] = self.cal_comparison(327500.00, list_lte_spd[19]) + 'Kbps'
                sheet_out['E30'] = '-'

                sheet_out.merge_cells('A31:A33')
                sheet_out['A31'] = '3CA : B7(20M)+B3+B5(MCS28)'
                sheet_out['B31'] = 'RSSI'
                sheet_out['B32'] = '속도(Absolute)'
                sheet_out['B33'] = 'BLER'
                sheet_out['C31'] = '-58.00dBm'
                sheet_out['C32'] = '298300Kbps'
                sheet_out['C33'] = '-'
                sheet_out['D31'] = list_lte_spd[21] + 'dBm'
                sheet_out['D32'] = list_lte_spd[22] + 'Kbps'
                sheet_out['D33'] = list_lte_spd[23] + '%'
                # sheet_out['E31'] = self.check_num(abs(round(abs(float(list_lte_spd[21])) - 58.00, 2))) + 'dBm'
                # sheet_out['E32'] = self.check_num(abs(round(abs(float(list_lte_spd[22])) - 298300, 2))) + 'Kbps'
                sheet_out['E31'] = self.cal_comparison(58.00, list_lte_spd[21]) + 'dBm'
                sheet_out['E32'] = self.cal_comparison(298300.00, list_lte_spd[22]) + 'Kbps'
                sheet_out['E33'] = '-'

                sheet_out.merge_cells('A34:A36')
                sheet_out['A34'] = '3CA : B7(20M)+B3+B7(MCS28)'
                sheet_out['B34'] = 'RSSI'
                sheet_out['B35'] = '속도(Absolute)'
                sheet_out['B36'] = 'BLER'
                sheet_out['C34'] = '-58.00dBm'
                sheet_out['C35'] = '298300Kbps'
                sheet_out['C36'] = '-'
                sheet_out['D34'] = list_lte_spd[24] + 'dBm'
                sheet_out['D35'] = list_lte_spd[25] + 'Kbps'
                sheet_out['D36'] = list_lte_spd[26] + '%'
                # sheet_out['E34'] = self.check_num(abs(round(abs(float(list_lte_spd[24])) - 58.00, 2))) + 'dBm'
                # sheet_out['E35'] = self.check_num(abs(round(abs(float(list_lte_spd[25])) - 298300, 2))) + 'Kbps'
                sheet_out['E34'] = self.cal_comparison(58.00, list_lte_spd[24]) + 'dBm'
                sheet_out['E35'] = self.cal_comparison(298300.00, list_lte_spd[25]) + 'Kbps'
                sheet_out['E36'] = '-'

                sheet_out.merge_cells('A37:A39')
                sheet_out['A37'] = '4CA : B7(20M)+B3+B5+B1(MCS28)'
                sheet_out['B37'] = 'RSSI'
                sheet_out['B38'] = '속도(Absolute)'
                sheet_out['B39'] = 'BLER'
                sheet_out['C37'] = '-57.00dBm'
                sheet_out['C38'] = '386000Kbps'
                sheet_out['C39'] = '-'
                sheet_out['D37'] = list_lte_spd[27] + 'dBm'
                sheet_out['D38'] = list_lte_spd[28] + 'Kbps'
                sheet_out['D39'] = list_lte_spd[29] + '%'
                # sheet_out['E37'] = self.check_num(abs(round(abs(float(list_lte_spd[27])) - 57.00, 2))) + 'dBm'
                # sheet_out['E38'] = self.check_num(abs(round(abs(float(list_lte_spd[28])) - 386000, 2))) + 'Kbps'
                sheet_out['E37'] = self.cal_comparison(57.00, list_lte_spd[27]) + 'dBm'
                sheet_out['E38'] = self.cal_comparison(386000.00, list_lte_spd[28]) + 'Kbps'
                sheet_out['E39'] = '-'

                sheet_out.merge_cells('A40:A42')
                sheet_out['A40'] = '5CA : B7+B3+B5+B1+B7(MCS28)'
                sheet_out['B40'] = 'RSSI'
                sheet_out['B41'] = '속도(Absolute)'
                sheet_out['B42'] = 'BLER'
                sheet_out['C40'] = '-56.00dBm'
                sheet_out['C41'] = '444500Kbps'
                sheet_out['C42'] = '-'
                sheet_out['D40'] = list_lte_spd[30] + 'dBm'
                sheet_out['D41'] = list_lte_spd[31] + 'Kbps'
                sheet_out['D42'] = list_lte_spd[32] + '%'
                # sheet_out['E40'] = self.check_num(abs(round(abs(float(list_lte_spd[30])) - 56.00, 2))) + 'dBm'
                # sheet_out['E41'] = self.check_num(abs(round(abs(float(list_lte_spd[31])) - 444500, 2))) + 'Kbps'
                sheet_out['E40'] = self.cal_comparison(56.00, list_lte_spd[30]) + 'dBm'
                sheet_out['E41'] = self.cal_comparison(444500.00, list_lte_spd[31]) + 'Kbps'
                sheet_out['E42'] = '-'

                self.setPrintText('/s {}번 파일 "속도" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:E42"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A4'].alignment = self.top_alignment
                    sheet_out['A22'].alignment = self.top_alignment
                    sheet_out['A23'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A5:E20"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell border adjust
                    for mCell in sheet_out["A24:E42"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A3:E42"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D', 'E']
                    sheet_width_list = [20.63, 14, 14, 17, 15]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for i in [6, 9, 12, 15, 18, 25, 28, 31, 34, 37, 40]:
                        sheet_out['A' + str(i)].fill = self.gray_fill

                    for col in ['A', 'B', 'D', 'E']:
                        sheet_out[col + '5'].fill = self.brown_fill
                        sheet_out[col + '24'].fill = self.brown_fill

                    for i in range(6, 21):
                        sheet_out['B'+str(i)].fill = self.apricot_fill
                        sheet_out['C'+str(i)].fill = self.apricot_fill

                    for i in range(25, 43):
                        sheet_out['B'+str(i)].fill = self.apricot_fill
                        sheet_out['C'+str(i)].fill = self.apricot_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "속도" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # Call Setup Tab
    def call_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                call_val = ''

                # get data from wb_input
                sheet_in = wb_input['Call Test']

                call_val = self.check_num(sheet_in['D8'].value)

                #option setting wb.output
                sheet_out = wb_output['Call Setup Test']
                # sheet row 2 handle
                sheet_out.merge_cells('A1:C1')
                sheet_out['A1'] = 'Call Setup Test 결과'

                # 3~4 row
                sheet_out['A2'] = ' - WCDMA Call Setup Test'
                sheet_out['A3'] = '구분'
                sheet_out['B3'] = '기준'
                sheet_out['C3'] = '측정결과'
                sheet_out['D3'] = '비교'
                sheet_out['A4'] = 'Band 1'
                sheet_out['B4'] = ' -104.5dBm 이하'
                sheet_out['C4'] = call_val
                sheet_out['D4'] = '-'

                self.setPrintText('/s {}번 파일 "Call Setuo Test" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:D4"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A2'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A3:D4"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A2:D4"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D']
                    sheet_width_list = [25, 15.88, 17, 15]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    sheet_out['A4'].fill = self.gray_fill

                    for col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '3'].fill = self.brown_fill

                    sheet_out['B4'].fill = self.apricot_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "Call Setup Test" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 주파수동조 Tab
    def fre_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                list_c1 = []
                list_c2 = []
                list_c3 = []
                # get data from wb_input
                sheet_in = wb_input['주파수동조']

                for i in ['C', 'D', 'E', 'F']:
                    list_c1.append(str(sheet_in[i + '5'].value))
                    list_c1.append(str(sheet_in[i + '6'].value))
                    list_c1.append(str(sheet_in[i + '7'].value))

                for i in ['C', 'D']:
                    list_c2.append(str(sheet_in[i + '11'].value))
                    list_c2.append(str(sheet_in[i + '12'].value))
                    list_c2.append(str(sheet_in[i + '13'].value))

                for i in ['C', 'D', 'E', 'F']:
                    list_c3.append(str(sheet_in[i + '17'].value))
                    list_c3.append(str(sheet_in[i + '18'].value))
                    list_c3.append(str(sheet_in[i + '19'].value))

                # option setting wb.output
                sheet_out = wb_output['주파수동조']

                # sheet row 2 handle
                sheet_out.merge_cells('A1:D1')
                sheet_out['A1'] = '주파수동조 결과'

                # 3~8 row
                sheet_out['A3'] = '▣ LTE'
                sheet_out.merge_cells('A4:B4')
                sheet_out['A4'] = '지원 Band 및 정보'
                sheet_out['C4'] = '측정결과'
                sheet_out['D4'] = '비고'
                i = 0
                j = 0
                while i < len(list_c1):

                    sheet_out['A' + str(5 + j)] = list_c1[i]
                    sheet_out['B' + str(5 + j)] = list_c1[i+1]
                    sheet_out['C' + str(5 + j)] = list_c1[i+2]
                    sheet_out['D' + str(5 + j)] = ''
                    i = i + 3
                    j = j + 1

                # 10~13 row
                sheet_out['A10'] = '▣ WCDMA'
                sheet_out.merge_cells('A11:B11')
                sheet_out['A11'] = '지원 Band 및 정보'
                sheet_out['C11'] = '측정결과'
                sheet_out['D11'] = '비고'
                i = 0
                j = 0
                while i < len(list_c2):
                    sheet_out['A' + str(12 + j)] = list_c2[i]
                    sheet_out['B' + str(12 + j)] = list_c2[i + 1]
                    sheet_out['C' + str(12 + j)] = list_c2[i + 2]
                    sheet_out['D' + str(12 + j)] = ''
                    i = i + 3
                    j = j + 1

                # 15~20 row
                sheet_out['A15'] = '▣ GMS'
                sheet_out.merge_cells('A16:B16')
                sheet_out['A16'] = '지원 Band 및 정보'
                sheet_out['C16'] = '측정결과'
                sheet_out['D16'] = '비고'
                i = 0
                j = 0
                while i < len(list_c3):
                    sheet_out['A' + str(17 + j)] = list_c3[i]
                    sheet_out['B' + str(17 + j)] = list_c3[i + 1]
                    sheet_out['C' + str(17 + j)] = list_c3[i + 2]
                    sheet_out['D' + str(17 + j)] = ''
                    i = i + 3
                    j = j + 1

                self.setPrintText('/s {}번 파일 "주파수동조" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data
                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:D20"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A10'].alignment = self.top_alignment
                    sheet_out['A15'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A4:D8"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A11:D13"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A16:D20"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    # all cell font adjust
                    for mCell in sheet_out["A3:D20"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D']
                    sheet_width_list = [15.13, 24.5, 17, 15]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for i in [5, 6, 7, 8, 12, 13, 17, 18, 19, 20]:
                        sheet_out['A' + str(i)].fill = self.gray_fill
                        sheet_out['B' + str(i)].fill = self.gray_fill

                    for i in [4, 11, 16]:
                        sheet_out['A' + str(i)].fill = self.brown_fill
                        sheet_out['C' + str(i)].fill = self.brown_fill
                        sheet_out['D' + str(i)].fill = self.brown_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "주파수동조" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # Call Setup Tab
    def mos_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                list_val = []

                # get data from wb_input
                sheet_in = wb_input['MOS']
                list_val.append(self.check_num(sheet_in['C6'].value))
                list_val.append(self.check_num(sheet_in['D6'].value))
                list_val.append(self.check_num(sheet_in['E6'].value))
                list_val.append(self.check_num(sheet_in['F6'].value))

                #option setting wb.output
                sheet_out = wb_output['MOS']
                # sheet row 1 handle
                sheet_out.merge_cells('A1:D1')
                sheet_out['A1'] = 'MOS 결과'

                # sheet row 2 handle
                sheet_out['A2'] = '- MOS 결과'
                sheet_out['A3'] = '▣ POLQA_48K'

                # 4~6 row
                sheet_out['A4'] = '구분'
                sheet_out['B4'] = '기준'
                sheet_out['C4'] = '측정결과'
                sheet_out['D4'] = '비교'
                sheet_out['A5'] = 'Downlink MOS'
                sheet_out['B5'] = '3.5 이상'
                sheet_out['C5'] = list_val[0]
                # sheet_out['D5'] = self.check_num(abs(round(abs(float(list_val[0])) - 3.5, 2)))
                sheet_out['D5'] = self.cal_comparison(3.5, list_val[0])
                sheet_out['A6'] = 'Uplink MOS'
                sheet_out['B6'] = '3.5 이상'
                sheet_out['C6'] = list_val[1]
                # sheet_out['D6'] = self.check_num(abs(round(abs(float(list_val[1])) - 3.5, 2)))
                sheet_out['D6'] = self.cal_comparison(3.5, list_val[1])

                # sheet row 8 handle
                sheet_out['A8'] = '▣ POLQA_8K'

                # 9~11 row
                sheet_out['A9'] = '구분'
                sheet_out['B9'] = '기준'
                sheet_out['C9'] = '측정결과'
                sheet_out['A10'] = 'Downlink MOS'
                sheet_out['B10'] = '3.0 이상'
                sheet_out['C10'] = list_val[2]
                # sheet_out['D10'] = self.check_num(abs(round(abs(float(list_val[2])) - 3.0, 2)))
                sheet_out['D10'] = self.cal_comparison(3.0, list_val[2])
                sheet_out['A11'] = 'Uplink MOS'
                sheet_out['B11'] = '3.0 이상'
                sheet_out['C11'] = list_val[3]
                # sheet_out['D11'] = self.check_num(abs(round(abs(float(list_val[3])) - 3.0, 2)))
                sheet_out['D11'] = self.cal_comparison(3.0, list_val[2])

                self.setPrintText('/s {}번 파일 "MOS" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:D11"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A2'].alignment = self.top_alignment
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A8'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A4:D6"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    for mCell in sheet_out["A9:D11"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A2:D11"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D']
                    sheet_width_list = [25, 15.88, 17, 13.13]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for i in [4, 9]:
                        sheet_out['A' + str(i)].fill = self.brown_fill
                        sheet_out['B' + str(i)].fill = self.brown_fill
                        sheet_out['C' + str(i)].fill = self.brown_fill
                        sheet_out['D' + str(i)].fill = self.brown_fill

                    for i in [5, 6, 10, 11]:
                        sheet_out['A' + str(i)].fill = self.gray_fill
                        sheet_out['B' + str(i)].fill = self.apricot_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "MOS" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # DOU Tab
    def dou_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                list_input = []
                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                col_sum = list(range(4, 16))
                col_a = [1, 2, 4, 7, 13, 16, 17]
                col_b = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                col_c = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                col_d = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                col_e = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                i_sum = 0.0
                r_sum = 0.0
                t_sum = 0.0

                # get data from wb_input
                sheet_in = wb_input['배터리소모전류(DOU)']
                temp_data = []
                for i in col_a:
                    if i == 1:
                        temp_data.append(str(sheet_in['A' + str(i)].value))
                    else:
                        temp_data.append(str(sheet_in['A' + str(i + 1)].value))
                list_input.append(temp_data)

                temp_data = []
                for i in col_b:
                    temp_data.append(str(sheet_in['B' + str(i + 1)].value))
                list_input.append(temp_data)

                temp_data = []
                for i in col_c:
                    temp_data.append(str(sheet_in['C' + str(i + 1)].value))
                    if i in col_sum:
                        if self.isNumber(sheet_in['C' + str(i + 1)].value):
                            t_sum = t_sum + float(sheet_in['C' + str(i + 1)].value)
                list_input.append(temp_data)

                temp_data = []
                for i in col_d:
                    if i in col_sum:
                        if self.isNumber(sheet_in['D' + str(i + 1)].value):
                            i_sum = i_sum + float(sheet_in['D' + str(i + 1)].value)
                            temp_data.append(round(float(sheet_in['D' + str(i + 1)].value), 1))
                        else:
                            temp_data.append(self.check_empty(sheet_in['D' + str(i + 1)].value))
                    else:
                        temp_data.append(self.check_empty(sheet_in['D' + str(i + 1)].value))
                list_input.append(temp_data)

                temp_data = []
                for i in col_e:
                    if i in col_sum:
                        if self.isNumber(sheet_in['E' + str(i + 1)].value):
                            r_sum = r_sum + float(sheet_in['E' + str(i + 1)].value)
                            temp_data.append(round(float(sheet_in['E' + str(i + 1)].value), 1))
                        else:
                            temp_data.append(self.check_empty(sheet_in['E' + str(i + 1)].value))
                    else:
                        temp_data.append(self.check_empty(sheet_in['E' + str(i + 1)].value))
                list_input.append(temp_data)

                # input the data on output sheet
                sheet_out = wb_output['배터리소모전류(DOU)']

                for idx_2, item2 in enumerate(list_input):

                    if idx_2 == 0:
                        for i in range(len(item2)):
                            sheet_out['A'+str(col_a[i])] = item2[i]
                    elif idx_2 == 1:
                        for i in range(len(item2)):
                            sheet_out['B'+str(col_b[i])] = item2[i]
                    elif idx_2 == 2:
                        for i in range(len(item2)):
                            sheet_out['C'+str(col_c[i])] = item2[i]
                    elif idx_2 == 3:
                        for i in range(len(item2)):
                            sheet_out['D'+str(col_d[i])] = item2[i]
                    else:
                        for i in range(len(item2)):
                            sheet_out['E'+str(col_e[i])] = item2[i]

                # fill rest values
                sheet_out.merge_cells('A1:E1')
                sheet_out.merge_cells('A2:A3')
                sheet_out.merge_cells('B2:B3')
                sheet_out.merge_cells('C2:C3')
                sheet_out.merge_cells('D2:E2')
                sheet_out.merge_cells('A4:A6')
                sheet_out.merge_cells('A7:A12')
                sheet_out.merge_cells('A13:A15')
                sheet_out.merge_cells('A16:B16')
                sheet_out.merge_cells('A17:C17')
                sheet_out.merge_cells('D17:E17')

                sheet_out['A16'] = '소계'
                if str(t_sum) == '0' or str(t_sum) == '0.0':
                    sheet_out['C16'] = ''
                else:
                    sheet_out['C16'] = round(t_sum, 1)

                if str(r_sum) == '0' or str(r_sum) == '0.0':
                    sheet_out['E16'] = ''
                else:
                    sheet_out['E16'] = round(r_sum, 1)

                if str(i_sum) == '0' or str(i_sum) == '0.0':
                    sheet_out['D16'] = ''
                else:
                    sheet_out['D16'] = round(i_sum, 1)

                sheet_out['A17'] = '사용시간'
                sheet_out['D17'] = str(round(self.battery_spec/r_sum, 2))+"일"

                self.setPrintText('/s {}번 파일 "베터리소모전류(DOU)" 테이터 입력 완료 /e'.format(idx+1))

                if self.opFlag:

                    # all cell aligment adjust
                    for mCell in sheet_out["A1:E17"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A2:E17"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A2:E17"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each coloum width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D', 'E']
                    sheet_width_list = [10.25, 27.38, 15.5, 17, 17]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    sheet_out['A2'].fill = self.brown_fill
                    sheet_out['B2'].fill = self.brown_fill
                    sheet_out['C2'].fill = self.brown_fill
                    sheet_out['D2'].fill = self.brown_fill
                    sheet_out['D3'].fill = self.brown_fill
                    sheet_out['E3'].fill = self.brown_fill
                    sheet_out['A16'].fill = self.light_brown_fill
                    sheet_out['C16'].fill = self.light_brown_fill
                    sheet_out['D16'].fill = self.light_brown_fill
                    sheet_out['E16'].fill = self.light_brown_fill
                    sheet_out['A17'].fill = self.brown_fill
                    sheet_out['D17'].fill = self.brown_fill

                    for i in range(4, 16):
                        sheet_out['A' + str(i)].fill = self.gray_fill
                        sheet_out['B' + str(i)].fill = self.gray_fill
                        sheet_out['C' + str(i)].fill = self.gray_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "베터리소모전류(DOU)" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 베터리소모전류 Tab
    def bat_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                wb_input = openpyxl.load_workbook(item, data_only=True)
                wb_output = openpyxl.load_workbook(self.list_out_files[idx])
                col_out = ['Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB']

                # get data from wb_input
                sheet_in = wb_input['배터리소모전류']
                #option setting wb.output
                sheet_out = wb_output['배터리소모전류 세부데이터']

                # sheet row 1 handle
                sheet_out.merge_cells('A1:P1')
                sheet_out['A1'] = '베터리소모전류 결과'
                # sheet row 3~5 handle
                sheet_out['A3'] = '▣  5G 측정내역'
                sheet_out.merge_cells('A4:A5')
                sheet_out['A4'] = '차수'
                sheet_out.merge_cells('B4:B5')
                sheet_out['B4'] = '시료번호'
                sheet_out.merge_cells('C4:C5')
                sheet_out['C4'] = '베터리용량'
                sheet_out.merge_cells('D4:D5')
                sheet_out['D4'] = '측정채널'
                sheet_out.merge_cells('E4:H4')
                sheet_out['E4'] = sheet_in['E8'].value
                sheet_out.merge_cells('I4:L4')
                sheet_out['I4'] = sheet_in['I8'].value
                sheet_out.merge_cells('M4:P4')
                sheet_out['M4'] = sheet_in['M8'].value

                sheet_out.merge_cells('E5:F5')
                sheet_out['E5'] = sheet_in['E9'].value
                sheet_out.merge_cells('G5:H5')
                sheet_out['G5'] = sheet_in['G9'].value
                sheet_out.merge_cells('I5:J5')
                sheet_out['I5'] = sheet_in['I9'].value
                sheet_out.merge_cells('K5:L5')
                sheet_out['K5'] = sheet_in['K9'].value
                sheet_out.merge_cells('M5:N5')
                sheet_out['M5'] = sheet_in['M9'].value
                sheet_out.merge_cells('O5:P5')
                sheet_out['O5'] = sheet_in['O9'].value

                # sheet row 6~7 handle
                sheet_out.merge_cells('A6:D7')
                sheet_out['A6'] = 'SKT 기준'
                for col in ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']:
                    sheet_out[col + '6'] = sheet_in[col+'10'].value
                    sheet_out[col + '7'] = sheet_in[col+'11'].value

                # sheet row 8~9 handle
                for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']:

                    if col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '8'] = sheet_in[col + '12'].value
                        sheet_out[col + '9'] = sheet_in[col + '13'].value
                    else:
                        # row 8
                        if self.isNumber(sheet_in[col + '12'].value):
                            sheet_out[col + '8'] = self.check_num(round(float(sheet_in[col + '12'].value), 2))
                        else:
                            sheet_out[col + '8'] = self.check_empty(sheet_in[col + '12'].value)

                        # row 9
                        if self.isNumber(sheet_in[col + '13'].value):
                            sheet_out[col + '9'] = self.check_num(round(float(sheet_in[col + '13'].value), 2))
                        else:
                            sheet_out[col + '9'] = self.check_empty(sheet_in[col + '13'].value)

                # sheet row 12~15 handle
                sheet_out.merge_cells('A10:A11')
                sheet_out['A10'] = '차수'
                sheet_out.merge_cells('B10:B11')
                sheet_out['B10'] = '시료번호'
                sheet_out.merge_cells('C10:C11')
                sheet_out['C10'] = '베터리용량'
                sheet_out.merge_cells('D10:D11')
                sheet_out['D10'] = '측정채널'

                sheet_out.merge_cells('E10:F10')
                sheet_out['E10'] = sheet_in['Q8'].value
                sheet_out.merge_cells('G10:H10')
                sheet_out['G10'] = sheet_in['S8'].value
                sheet_out.merge_cells('I10:J10')
                sheet_out['I10'] = sheet_in['U8'].value
                sheet_out.merge_cells('K10:L10')
                sheet_out['K10'] = sheet_in['W8'].value
                sheet_out.merge_cells('M10:N10')
                sheet_out['M10'] = sheet_in['Y8'].value
                sheet_out.merge_cells('O10:P10')
                sheet_out['O10'] = sheet_in['AA8'].value

                sheet_out.merge_cells('E11:F11')
                sheet_out['E11'] = sheet_in['Q9'].value
                sheet_out.merge_cells('G11:H11')
                sheet_out['G11'] = sheet_in['S9'].value
                sheet_out.merge_cells('I11:J11')
                sheet_out['I11'] = sheet_in['U9'].value
                sheet_out.merge_cells('K11:L11')
                sheet_out['K11'] = sheet_in['W9'].value
                sheet_out.merge_cells('M11:N11')
                sheet_out['M11'] = sheet_in['Y9'].value
                sheet_out.merge_cells('O11:P11')
                sheet_out['O11'] = sheet_in['AA9'].value

                # sheet row 12~13 handle
                sheet_out.merge_cells('A12:D13')
                sheet_out['A12'] = 'SKT 기준'

                for i, col in enumerate(['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']):
                    sheet_out[col + '12'] = sheet_in[col_out[i] + '10'].value
                    sheet_out[col + '13'] = sheet_in[col_out[i] + '11'].value

                # sheet row 14~15 handle
                for i, col in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']):

                    if col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '14'] = sheet_in[col + '12'].value
                        sheet_out[col + '15'] = sheet_in[col + '13'].value
                    else:
                        # row 14
                        if self.isNumber(sheet_in[col_out[i-4] + '12'].value):
                            sheet_out[col + '14'] = self.check_num(round(float(sheet_in[col_out[i-4] + '12'].value), 2))
                        else:
                            sheet_out[col + '14'] = self.check_empty(sheet_in[col_out[i-4] + '12'].value)

                        # row 15
                        if self.isNumber(sheet_in[col_out[i-4] + '13'].value):
                            sheet_out[col + '15'] = self.check_num(round(float(sheet_in[col_out[i-4] + '13'].value), 2))
                        else:
                            sheet_out[col + '15'] = self.check_empty(sheet_in[col_out[i-4] + '13'].value)

                # sheet row 17~19 handle
                sheet_out['A17'] = '▣  LTE 측정내역'
                sheet_out.merge_cells('A18:A19')
                sheet_out['A18'] = '차수'
                sheet_out.merge_cells('B18:B19')
                sheet_out['B18'] = '시료번호'
                sheet_out.merge_cells('C18:C19')
                sheet_out['C18'] = '베터리용량'
                sheet_out.merge_cells('D18:D19')
                sheet_out['D18'] = '측정채널'
                sheet_out.merge_cells('E18:H18')
                sheet_out['E18'] = sheet_in['E16'].value
                sheet_out.merge_cells('I18:L18')
                sheet_out['I18'] = sheet_in['I16'].value
                sheet_out.merge_cells('M18:P18')
                sheet_out['M18'] = sheet_in['M16'].value

                sheet_out.merge_cells('E19:F19')
                sheet_out['E19'] = sheet_in['E17'].value
                sheet_out.merge_cells('G19:H19')
                sheet_out['G19'] = sheet_in['G17'].value
                sheet_out.merge_cells('I19:J19')
                sheet_out['I19'] = sheet_in['I17'].value
                sheet_out.merge_cells('K19:L19')
                sheet_out['K19'] = sheet_in['K17'].value
                sheet_out.merge_cells('M19:N19')
                sheet_out['M19'] = sheet_in['M17'].value
                sheet_out.merge_cells('O19:P19')
                sheet_out['O19'] = sheet_in['O17'].value

                # sheet row 20~21 handle
                sheet_out.merge_cells('A20:D21')
                sheet_out['A20'] = 'SKT 기준'
                for col in ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']:
                    sheet_out[col + '20'] = sheet_in[col+'18'].value
                    sheet_out[col + '21'] = sheet_in[col+'19'].value

                # sheet row 22~23 handle
                for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']:

                    if col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '22'] = sheet_in[col + '12'].value
                        sheet_out[col + '23'] = sheet_in[col + '13'].value
                    else:
                        # row 22
                        if self.isNumber(sheet_in[col + '20'].value):
                            sheet_out[col + '22'] = self.check_num(round(float(sheet_in[col + '20'].value), 2))
                        else:
                            sheet_out[col + '22'] = self.check_empty(sheet_in[col + '20'].value)

                        # row 23
                        if self.isNumber(sheet_in[col + '21'].value):
                            sheet_out[col + '23'] = self.check_num(round(float(sheet_in[col + '21'].value), 2))
                        else:
                            sheet_out[col + '23'] = self.check_empty(sheet_in[col + '21'].value)

                # sheet row 24~25 handle
                sheet_out.merge_cells('A24:A25')
                sheet_out['A24'] = '차수'
                sheet_out.merge_cells('B24:B25')
                sheet_out['B24'] = '시료번호'
                sheet_out.merge_cells('C24:C25')
                sheet_out['C24'] = '베터리용량'
                sheet_out.merge_cells('D24:D25')
                sheet_out['D24'] = '측정채널'

                sheet_out.merge_cells('E24:F24')
                sheet_out['E24'] = sheet_in['Q16'].value
                sheet_out.merge_cells('G24:H24')
                sheet_out['G24'] = sheet_in['S16'].value
                sheet_out.merge_cells('I24:J24')
                sheet_out['I24'] = sheet_in['U16'].value
                sheet_out.merge_cells('K24:L24')
                sheet_out['K24'] = sheet_in['W16'].value

                sheet_out.merge_cells('E25:F25')
                sheet_out['E25'] = sheet_in['Q17'].value
                sheet_out.merge_cells('G25:H25')
                sheet_out['G25'] = sheet_in['S17'].value
                sheet_out.merge_cells('I25:J25')
                sheet_out['I25'] = sheet_in['U17'].value
                sheet_out.merge_cells('K25:L25')
                sheet_out['K25'] = sheet_in['W17'].value

                # sheet row 26~27 handle
                sheet_out.merge_cells('A26:D27')
                sheet_out['A26'] = 'SKT 기준'

                for i, col in enumerate(['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']):
                    sheet_out[col + '26'] = sheet_in[col_out[i] + '18'].value
                    sheet_out[col + '27'] = sheet_in[col_out[i] + '19'].value

                # sheet row 28~29 handle
                for i, col in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']):

                    if col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '28'] = sheet_in[col + '12'].value
                        sheet_out[col + '29'] = sheet_in[col + '13'].value
                    else:
                        # row 28
                        if self.isNumber(sheet_in[col_out[i-4] + '20'].value):
                            sheet_out[col + '28'] = self.check_num(round(float(sheet_in[col_out[i-4] + '20'].value), 2))
                        else:
                            sheet_out[col + '28'] = self.check_empty(sheet_in[col_out[i-4] + '20'].value)
                        # row 29
                        if self.isNumber(sheet_in[col_out[i-4] + '21'].value):
                            sheet_out[col + '29'] = self.check_num(round(float(sheet_in[col_out[i-4] + '21'].value), 2))
                        else:
                            sheet_out[col + '29'] = self.check_empty(sheet_in[col_out[i-4] + '21'].value)


                # sheet row 31~33 handle
                sheet_out['A31'] = '▣  WCDMA 측정내역'
                sheet_out.merge_cells('A32:A33')
                sheet_out['A32'] = '차수'
                sheet_out.merge_cells('B32:B33')
                sheet_out['B32'] = '시료번호'
                sheet_out.merge_cells('C32:C33')
                sheet_out['C32'] = '베터리용량'
                sheet_out.merge_cells('D32:D33')
                sheet_out['D32'] = '측정채널'

                sheet_out.merge_cells('E32:F32')
                sheet_out['E32'] = sheet_in['E24'].value
                sheet_out.merge_cells('G32:J32')
                sheet_out['G32'] = sheet_in['G24'].value
                sheet_out.merge_cells('K32:L32')
                sheet_out['K32'] = sheet_in['K24'].value

                sheet_out.merge_cells('E33:F33')
                sheet_out['E33'] = sheet_in['E25'].value
                sheet_out.merge_cells('G33:H33')
                sheet_out['G33'] = sheet_in['G25'].value
                sheet_out.merge_cells('I33:J33')
                sheet_out['I33'] = sheet_in['I25'].value
                sheet_out.merge_cells('K33:L33')
                sheet_out['K33'] = sheet_in['K25'].value

                # sheet row 34~35 handle
                sheet_out.merge_cells('A34:D35')
                sheet_out['A34'] = 'SKT 기준'
                for col in ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
                    sheet_out[col + '34'] = sheet_in[col+'26'].value
                    sheet_out[col + '35'] = sheet_in[col+'27'].value

                # sheet row 36~37 handle
                for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:

                    if col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '36'] = sheet_in[col + '12'].value
                        sheet_out[col + '37'] = sheet_in[col + '13'].value
                    else:
                        # row 36
                        if self.isNumber(sheet_in[col + '28'].value):
                            sheet_out[col + '36'] = self.check_num(round(float(sheet_in[col + '28'].value), 2))
                        else:
                            sheet_out[col + '36'] = self.check_empty(sheet_in[col + '28'].value)
                        # row 37
                        if self.isNumber(sheet_in[col + '29'].value):
                            sheet_out[col + '37'] = self.check_num(round(float(sheet_in[col + '29'].value), 2))
                        else:
                            sheet_out[col + '37'] = self.check_empty(sheet_in[col + '29'].value)

                # sheet row 39~41 handle
                sheet_out['A39'] = '▣  WiFi 측정내역'
                sheet_out.merge_cells('A40:A41')
                sheet_out['A40'] = '차수'
                sheet_out.merge_cells('B40:B41')
                sheet_out['B40'] = '시료번호'
                sheet_out.merge_cells('C40:C41')
                sheet_out['C40'] = '베터리용량'
                sheet_out.merge_cells('D40:D41')
                sheet_out['D40'] = '측정채널'

                sheet_out.merge_cells('E40:F40')
                sheet_out['E40'] = sheet_in['E32'].value
                sheet_out.merge_cells('G40:H40')
                sheet_out['G40'] = sheet_in['G32'].value
                sheet_out.merge_cells('I40:J40')
                sheet_out['I40'] = sheet_in['I32'].value
                sheet_out.merge_cells('K40:L40')
                sheet_out['K40'] = sheet_in['K32'].value
                sheet_out.merge_cells('M40:N40')
                sheet_out['M40'] = sheet_in['M32'].value

                sheet_out.merge_cells('E41:F41')
                sheet_out['E41'] = sheet_in['E33'].value
                sheet_out.merge_cells('G41:H41')
                sheet_out['G41'] = sheet_in['G33'].value
                sheet_out.merge_cells('I41:J41')
                sheet_out['I41'] = sheet_in['I33'].value
                sheet_out.merge_cells('K41:L41')
                sheet_out['K41'] = sheet_in['K33'].value
                sheet_out.merge_cells('M41:N41')
                sheet_out['M41'] = sheet_in['M33'].value

                # sheet row 42~43 handle
                sheet_out.merge_cells('A42:D43')
                sheet_out['A42'] = 'SKT 기준'
                for col in ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:
                    sheet_out[col + '42'] = sheet_in[col+'34'].value
                    sheet_out[col + '43'] = sheet_in[col+'35'].value

                # sheet row 44~45 handle
                for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:

                    if col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '44'] = sheet_in[col + '12'].value
                        sheet_out[col + '45'] = sheet_in[col + '13'].value
                    else:
                        # row 44
                        if self.isNumber(sheet_in[col + '36'].value):
                            sheet_out[col + '44'] = self.check_num(round(float(sheet_in[col + '36'].value), 2))
                        else:
                            sheet_out[col + '44'] = self.check_empty(sheet_in[col + '36'].value)
                        # row 45
                        if self.isNumber(sheet_in[col + '37'].value):
                            sheet_out[col + '45'] = self.check_num(round(float(sheet_in[col + '37'].value), 2))
                        else:
                            sheet_out[col + '45'] = self.check_empty(sheet_in[col + '37'].value)

                # sheet row 47~49 handle
                sheet_out['A47'] = '▣  BlueTooth 측정내역'
                sheet_out.merge_cells('A48:A49')
                sheet_out['A48'] = '차수'
                sheet_out.merge_cells('B48:B49')
                sheet_out['B48'] = '시료번호'
                sheet_out.merge_cells('C48:C49')
                sheet_out['C48'] = '베터리용량'
                sheet_out.merge_cells('D48:D49')
                sheet_out['D48'] = '측정채널'
                sheet_out.merge_cells('E48:N48')
                sheet_out['E48'] = sheet_in['E40'].value

                sheet_out.merge_cells('E49:F49')
                sheet_out['E49'] = sheet_in['E41'].value
                sheet_out.merge_cells('G49:H49')
                sheet_out['G49'] = sheet_in['G41'].value
                sheet_out.merge_cells('I49:J49')
                sheet_out['I49'] = sheet_in['I41'].value
                sheet_out.merge_cells('K49:L49')
                sheet_out['K49'] = sheet_in['K41'].value
                sheet_out.merge_cells('M49:N49')
                sheet_out['M49'] = sheet_in['M41'].value

                # sheet row 50~51 handle
                sheet_out.merge_cells('A50:D51')
                sheet_out['A50'] = 'SKT 기준'

                for col in ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:
                    sheet_out[col + '50'] = sheet_in[col+'42'].value
                    sheet_out[col + '51'] = sheet_in[col+'43'].value

                for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:

                # sheet row 52~53 handle
                    if col in ['A', 'B', 'C', 'D']:
                        sheet_out[col + '52'] = sheet_in[col + '12'].value
                        sheet_out[col + '53'] = sheet_in[col + '13'].value
                    else:
                        # row 52
                        if self.isNumber(sheet_in[col + '44'].value):
                            sheet_out[col + '52'] = self.check_num(round(float(sheet_in[col + '44'].value), 2))
                        else:
                            sheet_out[col + '52'] = self.check_empty(sheet_in[col + '44'].value)
                        # row 53
                        if self.isNumber(sheet_in[col + '45'].value):
                            sheet_out[col + '53'] = self.check_num(round(float(sheet_in[col + '45'].value), 2))
                        else:
                            sheet_out[col + '53'] = self.check_empty(sheet_in[col + '45'].value)

                self.setPrintText('/s {}번 파일 "배터리소모전류 세부데이터" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data
                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:Z53"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A17'].alignment = self.top_alignment
                    sheet_out['A31'].alignment = self.top_alignment
                    sheet_out['A39'].alignment = self.top_alignment
                    sheet_out['A47'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A4:P15"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A18:P23"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A24:L29"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A32:L37"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A40:N45"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A48:N53"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A3:P53"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                                       'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
                    sheet_width_list = [29.88, 11.38, 11.38, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                                        11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]

                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']:

                        sheet_out[col + '4'].fill = self.brown_fill
                        sheet_out[col + '5'].fill = self.brown_fill
                        sheet_out[col + '6'].fill = self.apricot_fill
                        sheet_out[col + '7'].fill = self.apricot_fill
                        sheet_out[col + '10'].fill = self.brown_fill
                        sheet_out[col + '11'].fill = self.brown_fill
                        sheet_out[col + '12'].fill = self.apricot_fill
                        sheet_out[col + '13'].fill = self.apricot_fill
                        sheet_out[col + '18'].fill = self.brown_fill
                        sheet_out[col + '19'].fill = self.brown_fill
                        sheet_out[col + '20'].fill = self.apricot_fill
                        sheet_out[col + '21'].fill = self.apricot_fill

                    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:

                        sheet_out[col + '40'].fill = self.brown_fill
                        sheet_out[col + '41'].fill = self.brown_fill
                        sheet_out[col + '42'].fill = self.apricot_fill
                        sheet_out[col + '43'].fill = self.apricot_fill
                        sheet_out[col + '48'].fill = self.brown_fill
                        sheet_out[col + '49'].fill = self.brown_fill
                        sheet_out[col + '50'].fill = self.apricot_fill
                        sheet_out[col + '51'].fill = self.apricot_fill

                    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:

                        sheet_out[col + '24'].fill = self.brown_fill
                        sheet_out[col + '25'].fill = self.brown_fill
                        sheet_out[col + '26'].fill = self.apricot_fill
                        sheet_out[col + '27'].fill = self.apricot_fill
                        sheet_out[col + '32'].fill = self.brown_fill
                        sheet_out[col + '33'].fill = self.brown_fill
                        sheet_out[col + '34'].fill = self.apricot_fill
                        sheet_out[col + '35'].fill = self.apricot_fill

                    for i in [8, 9, 14, 15, 22, 23, 28, 29, 36, 37, 44, 45, 52, 53]:

                        sheet_out['A' + str(i)].fill = self.gray_fill
                        sheet_out['B' + str(i)].fill = self.gray_fill
                        sheet_out['C' + str(i)].fill = self.gray_fill
                        sheet_out['D' + str(i)].fill = self.gray_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "배터리소모전류 세부데이터" 시트 스타일 적용 완료 /e'.format(idx+1))

                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 베터리소모전류(시간) Tab
    def time_generate_data(self):

        try:
            for idx, item in enumerate(self.list_out_files):

                wb_output = openpyxl.load_workbook(item, data_only=True)

                # get data from wb_input
                sheet_in = wb_output['배터리소모전류 세부데이터']
                #option setting wb.output
                sheet_out = wb_output['배터리소모전류(시간)']
                target = sheet_in['A8'].value
                ref = sheet_in['A9'].value

                # sheet row 1 handle
                sheet_out.merge_cells('A1:H1')
                sheet_out['A1'] = '배터리소모전류 결과 (시간)'
                # sheet row 3~5 handle
                sheet_out['A3'] = '▣  5G '
                sheet_out.merge_cells('A4:A5')
                sheet_out['A4'] = '구분'
                sheet_out.merge_cells('B4:C4')
                sheet_out['B4'] = sheet_in['E4'].value
                sheet_out.merge_cells('D4:E4')
                sheet_out['D4'] = sheet_in['I4'].value
                sheet_out.merge_cells('F4:H4')
                sheet_out['F4'] = sheet_in['M4'].value

                sheet_out['B5'] = sheet_in['E5'].value
                sheet_out['C5'] = sheet_in['G5'].value
                sheet_out['D5'] = sheet_in['I5'].value
                sheet_out['E5'] = sheet_in['K5'].value
                sheet_out['F5'] = sheet_in['M5'].value
                sheet_out['G5'] = sheet_in['O5'].value
                sheet_out['H5'] = sheet_in['G11'].value

                # sheet row 6 handle
                sheet_out['A6'] = 'SKT 기준'
                sheet_out['B6'] = sheet_in['F6'].value
                sheet_out['C6'] = sheet_in['H6'].value
                sheet_out['D6'] = sheet_in['J6'].value
                sheet_out['E6'] = sheet_in['L6'].value
                sheet_out['F6'] = sheet_in['N6'].value
                sheet_out['G6'] = sheet_in['P6'].value
                sheet_out['H6'] = sheet_in['H12'].value

                # sheet row 7~8
                sheet_out['A7'] = target
                sheet_out['B7'] = sheet_in['F8'].value
                sheet_out['C7'] = sheet_in['H8'].value
                sheet_out['D7'] = sheet_in['J8'].value
                sheet_out['E7'] = sheet_in['L8'].value
                sheet_out['F7'] = sheet_in['N8'].value
                sheet_out['G7'] = sheet_in['P8'].value
                sheet_out['H7'] = sheet_in['H14'].value
                sheet_out['A8'] = ref
                sheet_out['B8'] = sheet_in['F9'].value
                sheet_out['C8'] = sheet_in['H9'].value
                sheet_out['D8'] = sheet_in['J9'].value
                sheet_out['E8'] = sheet_in['L9'].value
                sheet_out['F8'] = sheet_in['N9'].value
                sheet_out['G8'] = sheet_in['P9'].value
                sheet_out['H8'] = sheet_in['H15'].value

                # sheet row 9~10
                sheet_out.merge_cells('A9:A10')
                sheet_out['A9'] = '구분'
                sheet_out['B9'] = sheet_in['I10'].value
                sheet_out['C9'] = sheet_in['K10'].value
                sheet_out['D9'] = sheet_in['M10'].value
                sheet_out['E9'] = '동영상'
                sheet_out['F9'] = sheet_in['E10'].value

                sheet_out['B10'] = sheet_in['I11'].value
                sheet_out['C10'] = sheet_in['K11'].value
                sheet_out['D10'] = sheet_in['M11'].value
                sheet_out['E10'] = '녹화'
                sheet_out['F10'] = sheet_in['E11'].value

                # sheet row 11 handle
                sheet_out['A11'] = 'SKT 기준'
                sheet_out['B11'] = sheet_in['J12'].value
                sheet_out['C11'] = sheet_in['L12'].value
                sheet_out['D11'] = sheet_in['N12'].value
                sheet_out['E11'] = sheet_in['P12'].value
                sheet_out['F11'] = sheet_in['F12'].value

                # sheet row 12~13
                sheet_out['A12'] = target
                sheet_out['B12'] = sheet_in['J14'].value
                sheet_out['C12'] = sheet_in['L14'].value
                sheet_out['D12'] = sheet_in['N14'].value
                sheet_out['E12'] = sheet_in['P14'].value
                sheet_out['F12'] = sheet_in['F14'].value
                sheet_out['A13'] = ref
                sheet_out['B13'] = sheet_in['F15'].value
                sheet_out['C13'] = sheet_in['H15'].value
                sheet_out['D13'] = sheet_in['J15'].value
                sheet_out['E13'] = sheet_in['L15'].value
                sheet_out['F13'] = sheet_in['N15'].value

                # sheet row 15~17 handle
                sheet_out['A15'] = '▣  LTE'
                sheet_out.merge_cells('A16:A17')
                sheet_out['A16'] = '구분'
                sheet_out.merge_cells('B16:C16')
                sheet_out['B16'] = sheet_in['E18'].value
                sheet_out.merge_cells('D16:E16')
                sheet_out['D16'] = sheet_in['I18'].value
                sheet_out.merge_cells('F16:H16')
                sheet_out['F16'] = sheet_in['M18'].value

                sheet_out['B17'] = sheet_in['E19'].value
                sheet_out['C17'] = sheet_in['G19'].value
                sheet_out['D17'] = sheet_in['I19'].value
                sheet_out['E17'] = sheet_in['K19'].value
                sheet_out['F17'] = sheet_in['M19'].value
                sheet_out['G17'] = sheet_in['O19'].value
                sheet_out['H17'] = sheet_in['E25'].value

                # sheet row 18 handle
                sheet_out['A18'] = 'SKT 기준'
                sheet_out['B18'] = sheet_in['F20'].value
                sheet_out['C18'] = sheet_in['H20'].value
                sheet_out['D18'] = sheet_in['J20'].value
                sheet_out['E18'] = sheet_in['L20'].value
                sheet_out['F18'] = sheet_in['N20'].value
                sheet_out['G18'] = sheet_in['P20'].value
                sheet_out['H18'] = sheet_in['F26'].value

                # sheet row 19~20
                sheet_out['A19'] = target
                sheet_out['B19'] = sheet_in['F22'].value
                sheet_out['C19'] = sheet_in['H22'].value
                sheet_out['D19'] = sheet_in['J22'].value
                sheet_out['E19'] = sheet_in['L22'].value
                sheet_out['F19'] = sheet_in['N22'].value
                sheet_out['G19'] = sheet_in['P22'].value
                sheet_out['H19'] = sheet_in['F28'].value
                sheet_out['A20'] = ref
                sheet_out['B20'] = sheet_in['F23'].value
                sheet_out['C20'] = sheet_in['H23'].value
                sheet_out['D20'] = sheet_in['J23'].value
                sheet_out['E20'] = sheet_in['L23'].value
                sheet_out['F20'] = sheet_in['N23'].value
                sheet_out['G20'] = sheet_in['P23'].value
                sheet_out['H20'] = sheet_in['F29'].value

                # sheet row 21~22
                sheet_out.merge_cells('A21:A22')
                sheet_out['A21'] = '구분'
                sheet_out['B21'] = sheet_in['G24'].value
                sheet_out['C21'] = sheet_in['I24'].value
                sheet_out['D21'] = sheet_in['K24'].value

                sheet_out['B22'] = sheet_in['G25'].value
                sheet_out['C22'] = sheet_in['I25'].value
                sheet_out['D22'] = sheet_in['K25'].value

                # sheet row 23 handle
                sheet_out['A23'] = 'SKT 기준'
                sheet_out['B23'] = sheet_in['H26'].value
                sheet_out['C23'] = sheet_in['J26'].value
                sheet_out['D23'] = sheet_in['L26'].value

                # sheet row 24~25
                sheet_out['A24'] = target
                sheet_out['B24'] = sheet_in['H28'].value
                sheet_out['C24'] = sheet_in['J28'].value
                sheet_out['D24'] = sheet_in['L28'].value
                sheet_out['A25'] = ref
                sheet_out['B25'] = sheet_in['H29'].value
                sheet_out['C25'] = sheet_in['J29'].value
                sheet_out['D25'] = sheet_in['L29'].value

                # sheet row 27~29 handle
                sheet_out['A27'] = '▣  WCDMA'
                sheet_out.merge_cells('A28:A29')
                sheet_out['A28'] = '구분'
                sheet_out['B28'] = sheet_in['E32'].value
                sheet_out.merge_cells('C28:D28')
                sheet_out['C28'] = sheet_in['G32'].value
                sheet_out['E28'] = sheet_in['K32'].value

                sheet_out['B29'] = sheet_in['E33'].value
                sheet_out['C29'] = sheet_in['G33'].value
                sheet_out['D29'] = sheet_in['I33'].value
                sheet_out['E29'] = sheet_in['K33'].value

                # sheet row 30 handle
                sheet_out['A30'] = 'SKT 기준'
                sheet_out['B30'] = sheet_in['F34'].value
                sheet_out['C30'] = sheet_in['H34'].value
                sheet_out['D30'] = sheet_in['J34'].value
                sheet_out['E30'] = sheet_in['L34'].value

                # sheet row 31~32
                sheet_out['A31'] = target
                sheet_out['B31'] = sheet_in['F36'].value
                sheet_out['C31'] = sheet_in['H36'].value
                sheet_out['D31'] = sheet_in['J36'].value
                sheet_out['E31'] = sheet_in['L36'].value
                sheet_out['A32'] = ref
                sheet_out['B32'] = sheet_in['F37'].value
                sheet_out['C32'] = sheet_in['H37'].value
                sheet_out['D32'] = sheet_in['J37'].value
                sheet_out['E32'] = sheet_in['L37'].value


                # sheet row 34~36 handle
                sheet_out['A34'] = '▣  WiFi'
                sheet_out.merge_cells('A35:A36')
                sheet_out['A35'] = '구분'
                sheet_out.merge_cells('B35:C35')
                sheet_out['B35'] = sheet_in['E40'].value
                sheet_out['D35'] = sheet_in['I40'].value
                sheet_out['E35'] = sheet_in['K40'].value
                sheet_out['F35'] = sheet_in['M40'].value

                sheet_out['B36'] = sheet_in['E41'].value
                sheet_out['C36'] = sheet_in['G41'].value
                sheet_out['D36'] = sheet_in['I41'].value
                sheet_out['E36'] = sheet_in['K41'].value
                sheet_out['F36'] = sheet_in['M41'].value

                # sheet row 37 handle
                sheet_out['A37'] = 'SKT 기준'
                sheet_out['B37'] = sheet_in['F42'].value
                sheet_out['C37'] = sheet_in['H42'].value
                sheet_out['D37'] = sheet_in['J42'].value
                sheet_out['E37'] = sheet_in['L42'].value
                sheet_out['F37'] = sheet_in['N42'].value

                # sheet row 38~39
                sheet_out['A38'] = target
                sheet_out['B38'] = sheet_in['F44'].value
                sheet_out['C38'] = sheet_in['H44'].value
                sheet_out['D38'] = sheet_in['J44'].value
                sheet_out['E38'] = sheet_in['L44'].value
                sheet_out['F38'] = sheet_in['N44'].value
                sheet_out['A39'] = ref
                sheet_out['B39'] = sheet_in['F45'].value
                sheet_out['C39'] = sheet_in['H45'].value
                sheet_out['D39'] = sheet_in['J45'].value
                sheet_out['E39'] = sheet_in['L45'].value
                sheet_out['F39'] = sheet_in['N45'].value

                # sheet row 41~43 handle
                sheet_out['A41'] = '▣  Bluetooth'
                sheet_out.merge_cells('A42:A43')
                sheet_out['A42'] = '구분'
                sheet_out.merge_cells('B42:F42')
                sheet_out['B42'] = sheet_in['E48'].value

                sheet_out['B43'] = sheet_in['E49'].value
                sheet_out['C43'] = sheet_in['G49'].value
                sheet_out['D43'] = sheet_in['I49'].value
                sheet_out['E43'] = sheet_in['K49'].value
                sheet_out['F43'] = sheet_in['M49'].value

                # sheet row 44 handle
                sheet_out['A44'] = 'SKT 기준'
                sheet_out['B44'] = sheet_in['F50'].value
                sheet_out['C44'] = sheet_in['H50'].value
                sheet_out['D44'] = sheet_in['J50'].value
                sheet_out['E44'] = sheet_in['L50'].value
                sheet_out['F44'] = sheet_in['N50'].value

                # sheet row 45~46
                sheet_out['A45'] = target
                sheet_out['B45'] = sheet_in['F52'].value
                sheet_out['C45'] = sheet_in['H52'].value
                sheet_out['D45'] = sheet_in['J52'].value
                sheet_out['E45'] = sheet_in['L52'].value
                sheet_out['F45'] = sheet_in['N52'].value
                sheet_out['A46'] = ref
                sheet_out['B46'] = sheet_in['F53'].value
                sheet_out['C46'] = sheet_in['H53'].value
                sheet_out['D46'] = sheet_in['J53'].value
                sheet_out['E46'] = sheet_in['L53'].value
                sheet_out['F46'] = sheet_in['N53'].value

                self.setPrintText('/s {}번 파일 "배터리소모전류 결과 (시간)" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data
                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:H46"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment

                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A15'].alignment = self.top_alignment
                    sheet_out['A27'].alignment = self.top_alignment
                    sheet_out['A34'].alignment = self.top_alignment
                    sheet_out['A41'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A4:H8"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A9:F13"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A16:H20"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A21:D25"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A28:E32"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A35:F39"]:
                        for cell in mCell:
                            cell.border = self.thin_border
                    for mCell in sheet_out["A42:F46"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A3:H46"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                    sheet_width_list = [29.88, 13.38, 13.38, 13.38, 13.38, 13.38, 13.38, 13.38]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]

                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:

                        sheet_out[col + '4'].fill = self.brown_fill
                        sheet_out[col + '5'].fill = self.brown_fill
                        sheet_out[col + '6'].fill = self.apricot_fill
                        sheet_out[col + '16'].fill = self.brown_fill
                        sheet_out[col + '17'].fill = self.brown_fill
                        sheet_out[col + '18'].fill = self.apricot_fill

                    for col in ['A', 'B', 'C', 'D', 'E', 'F']:

                        sheet_out[col + '9'].fill = self.brown_fill
                        sheet_out[col + '10'].fill = self.brown_fill
                        sheet_out[col + '11'].fill = self.apricot_fill
                        sheet_out[col + '35'].fill = self.brown_fill
                        sheet_out[col + '36'].fill = self.brown_fill
                        sheet_out[col + '37'].fill = self.apricot_fill
                        sheet_out[col + '42'].fill = self.brown_fill
                        sheet_out[col + '43'].fill = self.brown_fill
                        sheet_out[col + '44'].fill = self.apricot_fill

                    for col in ['A', 'B', 'C', 'D', 'E']:

                        sheet_out[col + '28'].fill = self.brown_fill
                        sheet_out[col + '29'].fill = self.brown_fill
                        sheet_out[col + '30'].fill = self.apricot_fill


                    for col in ['A', 'B', 'C', 'D']:

                        sheet_out[col + '21'].fill = self.brown_fill
                        sheet_out[col + '22'].fill = self.brown_fill
                        sheet_out[col + '23'].fill = self.apricot_fill

                    for i in [7, 8, 12, 13, 19, 20, 24, 25, 31, 32, 38, 39, 45, 46]:

                        sheet_out['A' + str(i)].fill = self.gray_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "배터리소모전류 결과 (시간)" 시트 스타일 적용 완료 /e'.format(idx+1))

                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 첨부 1 측정기준 Tab
    def attach_generate_data_1(self):

        try:
            for idx, item in enumerate(self.list_out_files):

                wb_output = openpyxl.load_workbook(item)
                # option setting wb.output
                sheet_out = wb_output['첨부1. 측정기준 및 가점']
                list_band = ['Band 1 15M', 'Band 3 20M', 'Band 5 10M',
                             'Band 7 20M', 'Band 7 10M']
                list_trp_base = ['14.00dBm', '15.00dBm', '13.50dBm',
                                 '13.00dBm', '13.00dBm']
                list_tis_base = ['-92.00dBm', '-91.00dBm', '-87.00dBm',
                                 '-90.00dBm', '-93.00dBm']

                # sheet row 1 handle
                sheet_out.merge_cells('A1:D1')
                sheet_out['A1'] = '첨부1. 측정기준 및 가점'

                # sheet row 3 handle
                sheet_out['A3'] = '▣ RF 성능 : 기 출시 단말 측정하여 상위 70% 수준으로  설정'
                sheet_out['A4'] = '   -TRP'

                # 5~10 row
                sheet_out['A5'] = 'SISO LTE'
                sheet_out['B5'] = '기준(RHP)'
                sheet_out.merge_cells('C5:D5')
                sheet_out['C5'] = '측정기준 History'

                for i in range(6, 11):
                    sheet_out['A' + str(i)] = list_band[i - 6]
                    sheet_out['B' + str(i)] = list_trp_base[i - 6]
                sheet_out.merge_cells('C6:D10')
                sheet_out['C6'] = '기준대비 1dB 증가후 +1점/1dBm 가점\n기준대비 1dB 저하후 - 1점/1dBm 감점'
                # 11~17 row
                sheet_out['A11'] = '   -TIS (SISO LTE)'

                # 12~17 row
                sheet_out['A12'] = 'SISO LTE'
                sheet_out['B12'] = '기준(RHP)'
                sheet_out.merge_cells('C12:D12')
                sheet_out['C12'] = '측정기준 History'

                for i in range(13, 18):
                    sheet_out['A' + str(i)] = list_band[i - 13]
                    sheet_out['B' + str(i)] = list_trp_base[i - 13]
                sheet_out.merge_cells('C13:D17')
                sheet_out['C13'] = '기준대비 1dB 증가후 +1점/3dBm 가점\n기준대비 1dB 저하후 - 1점/3dBm 감점'

                # 19~25 row
                sheet_out['A19'] = '▣ 배터리 소모전류'
                sheet_out.merge_cells('A20:D20')
                sheet_out['A20'] = " - '18.1 ~ '19.8 납품검사 삼성/LG 단말 29종으로\n측정 기준으로 소모전류 (평균+STD), 배터리 용량 (3000mA) 산출"
                sheet_out.merge_cells('A21:D21')
                sheet_out['A21'] = " - Ref. 단말 대비 10% 이내 (측정기준부재항목)"

                sheet_out['A23'] = '▣ MOS'
                sheet_out.merge_cells('A24:D24')
                sheet_out['A24'] = " - ITU-T 권고 P.800 항목에 규정 참고 (LTE : 3.5, WCDMA : 3.0)"
                sheet_out.merge_cells('A25:D25')
                sheet_out['A25'] = '. MOS 3.5~4 : 자연스러운 통화 수준\n. MOS 3~3.5 : 대화는 잘 이루어지지만 품질저하 느낄 수 있음'

                self.setPrintText('/s {}번 파일 "첨부1" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:D25"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment

                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A4'].alignment = self.top_alignment
                    sheet_out['C6'].alignment = self.top_alignment_3
                    sheet_out['A11'].alignment = self.top_alignment
                    sheet_out['C13'].alignment = self.top_alignment_3
                    sheet_out['A19'].alignment = self.top_alignment
                    sheet_out['A20'].alignment = self.top_alignment_3
                    sheet_out['A21'].alignment = self.top_alignment
                    sheet_out['A23'].alignment = self.top_alignment
                    sheet_out['A24'].alignment = self.top_alignment
                    sheet_out['A25'].alignment = self.top_alignment_3

                    # all cell border adjust
                    for mCell in sheet_out["A5:D10"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    for mCell in sheet_out["A12:D17"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A2:D25"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D']
                    sheet_width_list = [25, 15.88, 17, 17]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45
                    sheet_out.row_dimensions[20].height = 45
                    sheet_out.row_dimensions[25].height = 45

                    # Set Pattern Fill
                    for i in [5, 12]:
                        sheet_out['A' + str(i)].fill = self.brown_fill
                        sheet_out['B' + str(i)].fill = self.brown_fill
                        sheet_out['C' + str(i)].fill = self.brown_fill
                        sheet_out['D' + str(i)].fill = self.brown_fill

                    for i in [5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17]:
                        sheet_out['A' + str(i)].fill = self.gray_fill
                        sheet_out['B' + str(i)].fill = self.apricot_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "첨부1" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 첨부 2 측정기준 Tab
    def attach_generate_data_2(self):

        try:
            for idx, item in enumerate(self.list_out_files):

                wb_output = openpyxl.load_workbook(item)
                # option setting wb.output
                sheet_out = wb_output['첨부2. 납품검사']
                list_items = ['고온 고습/저온 Cycling 시험	', '낙하시험', '방수시험', 'ESD (정전기) 시험',
                              '개통 및 사용성 시험', 'RF Auto (50대, 제조사 자체 측정)', 'CATS_Priority1 (제조사 자체 측정)',
                              'GPS (제조사 자체 측정)', '발열 (제조사 자체 측정)', '카메라 전.후면 화질평가 (제조사 자체 측정)',
                              'WiFi 무선성능(제조사 자체 측정)', 'BT 무선성능(제조사 자체 측정)']
                list_items_2 = ['무선기기 형식등록', 'GCF 인증서', 'WiFi 인증서', 'NFC 인증서', 'Bluetooth 인증서']

                # sheet row 1 handle
                sheet_out.merge_cells('A1:D1')
                sheet_out['A1'] = '첨부2. 납품검사'

                # sheet row 3 handle
                sheet_out['A3'] = '▣ 장소 : (빈곳)'

                # 4~16 row
                sheet_out['A4'] = '구분'
                sheet_out.merge_cells('B4:C4')
                sheet_out['B4'] = 'Item'
                sheet_out['D4'] = '결과'

                sheet_out.merge_cells('A5:A8')
                sheet_out['A5'] = '신뢰성 시험'
                sheet_out.merge_cells('A9:A16')
                sheet_out['A9'] = 'Performance'

                for i in range(5, 17):
                    sheet_out.merge_cells('B' + str(i) + ':C' + str(i))
                    sheet_out['B' + str(i)] = list_items[i - 5]

                # 18~24 row
                sheet_out['A18'] = '▣ 시험 인증서 (PLM 등록)'
                sheet_out['A19'] = '구분'
                sheet_out.merge_cells('B19:C19')
                sheet_out['B19'] = 'Item'
                sheet_out['D19'] = '결과'

                sheet_out.merge_cells('A20:A24')
                sheet_out['A20'] = '인증서'

                for i in range(20, 25):
                    sheet_out.merge_cells('B' + str(i) + ':C' + str(i))
                    sheet_out['B' + str(i)] = list_items_2[i - 20]


                self.setPrintText('/s {}번 파일 "첨부2" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:D24"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A3'].alignment = self.top_alignment
                    sheet_out['A18'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A4:D16"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    for mCell in sheet_out["A19:D24"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A2:D24"]:
                        for cell in mCell:
                            cell.font = self.index_font

                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D']
                    sheet_width_list = [25, 15.88, 23.75, 17]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for i in [4, 19]:
                        sheet_out['A' + str(i)].fill = self.brown_fill
                        sheet_out['B' + str(i)].fill = self.brown_fill
                        sheet_out['C' + str(i)].fill = self.brown_fill
                        sheet_out['D' + str(i)].fill = self.brown_fill

                    for i in range(5,17):
                        sheet_out['A' + str(i)].fill = self.gray_fill
                        sheet_out['B' + str(i)].fill = self.gray_fill

                    for i in range(20,25):
                        sheet_out['A' + str(i)].fill = self.gray_fill
                        sheet_out['B' + str(i)].fill = self.gray_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "첨부2" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # 첨부 3 측정기준 Tab
    def attach_generate_data_3(self):

        try:
            for idx, item in enumerate(self.list_out_files):

                wb_output = openpyxl.load_workbook(item)
                # option setting wb.output
                sheet_out = wb_output['첨부3. 단말 상세 SPEC']
                list_items = ['모뎀', 'RFIC', 'Display', '크기', '배터리 용량', 'Flash ROM', 'SRAM', '카메라', '사운드', 'MIC', '방수/방진', '페이', '생체인식',
                              '충전', '기타', 'LTE 주파수', 'LTE 로밍 지원 주파수', 'WCDMA 주파수', 'OS(출시버전)', '출시']
                list_items_2 = ['5G NW options', '5G Frequency', 'UE-Category', 'Max Throughput', 'ENDC capability',
                                'LTE capability', 'Modulation', 'MIMO', 'CSI-RS', 'Power', 'Waveform']

                # sheet row 1 handle
                sheet_out.merge_cells('A1:C1')
                sheet_out['A1'] = '첨부3. 단말 상세 SPEC'

                # sheet row 2 handle
                sheet_out['A2'] = '▣ 기본 정보 '

                # 3~23 row
                sheet_out['A3'] = '구분'
                sheet_out['B3'] = '모델1'
                sheet_out['C3'] = 'Ref. 모델'

                for i in range(4, 24):
                    sheet_out['A' + str(i)] = list_items[i - 4]

                # 25~37 row
                sheet_out['A25'] = '▣  N/W Feature 비교'
                sheet_out['A26'] = '구분'
                sheet_out['B26'] = '모델1'
                sheet_out['C26'] = 'Ref. 모델'

                for i in range(27, 38):
                    sheet_out['A' + str(i)] = list_items_2[i - 27]

                self.setPrintText('/s {}번 파일 "첨부3" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["A1:C37"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment
                    # top alignment adjust
                    sheet_out['A2'].alignment = self.top_alignment
                    sheet_out['A25'].alignment = self.top_alignment

                    # all cell border adjust
                    for mCell in sheet_out["A3:C23"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    for mCell in sheet_out["A26:C37"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # all cell font adjust
                    for mCell in sheet_out["A2:C3"]:
                        for cell in mCell:
                            cell.font = self.index_font
                    for mCell in sheet_out["A4:C23"]:
                        for cell in mCell:
                            cell.font = self.value_font
                    for mCell in sheet_out["A25:C26"]:
                        for cell in mCell:
                            cell.font = self.index_font
                    for mCell in sheet_out["A27:C37"]:
                        for cell in mCell:
                            cell.font = self.value_font
                    sheet_out['A1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C']
                    sheet_width_list = [20.13, 39, 39]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    for i in [3, 26]:
                        sheet_out['A' + str(i)].fill = self.brown_fill
                        sheet_out['B' + str(i)].fill = self.brown_fill
                        sheet_out['C' + str(i)].fill = self.brown_fill

                    for i in range(4, 24):
                        sheet_out['A' + str(i)].fill = self.gray_fill

                    for i in range(27, 38):
                        sheet_out['A' + str(i)].fill = self.gray_fill

                self.currentRow = self.currentRow + 1
                self.setPrintText('/s {}번 파일 "첨부3" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # f2 function
    def f2_generate_data(self):

        try:
            for idx, item in enumerate(self.list_files):

                wb_output = openpyxl.load_workbook(item, data_only=True)
                # option setting wb.output
                sheet_in = wb_output['Profile']
                wb_output.create_sheet('Comparison', 2)
                sheet_out = wb_output['Comparison']
                # 1st list items are fixed usim info, 2nd list items are variable usim info
                list_find = [['ESN', 'HPPLMN', 'HPLMNNWACT', 'FPLMN', 'PWS', 'HPLMNwACT', 'DOMAIN'],
                              ['IMEI', 'IMSI', 'KEYS', 'KEYSPS', 'MSISDN', 'SMSP', 'PSLOCI', 'ACC', 'LOCI', 'IMSI_M',
                               'MDN', 'IRM', 'IMPI', 'IMPU', 'P_CSCF']]
                list_fixed_item = []
                list_variable_item = []
                list_reference_item = [
                    '0000FFFFFFFFFFFF',
                    '01',
                    '54F050400054F0508000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000',
                    '54F08054F06054F00354F040',
                    'FCFFFFFFFFFFFFFFFFFF',
                    '54F050400054F0508000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000FFFFFF0000',
                    '800A736B74696D732E6E6574FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
                ]

                total_row = len(sheet_in['A'])

                # sheet row 1 handle
                sheet_out.merge_cells('B1:E1')
                sheet_out['B1'] = 'USIM DATA COMPARISON'
                # sheet row 2 handle
                sheet_out['B2'] = 'EF파일명'
                sheet_out['C2'] = 'DATA값'
                sheet_out['D2'] = '고정기준값'
                sheet_out['E2'] = '비교'

                # finding fixed value
                for fixed in list_find[0]:
                    for i in range(2, total_row+1):
                        if sheet_in['A' + str(i)].value == fixed:
                            data = sheet_in['Q' + str(i)].value.strip()
                            data = re.sub(r'[\n,\s,\t]', '', data)
                            list_fixed_item.append(data)
                            break

                # finding variable value
                for variable in list_find[1]:
                    for i in range(2, total_row+1):
                        if sheet_in['A' + str(i)].value == variable:
                            data = sheet_in['Q' + str(i)].value.strip()
                            data = re.sub(r'[\n,\s,\t]', '', data)
                            list_variable_item.append(data)
                            break

                # red
                # 3~ 24 rows fill data
                # 3~9까지 fixed
                # 10~24까지 variable

                # all cell font adjust
                for mCell in sheet_out["B2:E24"]:
                    for cell in mCell:
                        cell.font = self.f2_value_font

                sheet_out['B1'].font = Font(name='맑은 고딕', size=22, bold=True, color='2B2B2B')
                # 고정값 Set
                for i, f_item in enumerate(list_fixed_item):
                    sheet_out['B' + str(i + 3)] = list_find[0][i]
                    sheet_out['B' + str(i + 3)].fill = self.yellow_fill
                    sheet_out['C' + str(i + 3)] = f_item
                    sheet_out['D' + str(i + 3)] = list_reference_item[i]
                    sheet_out['D' + str(i + 3)].fill = self.yellow_fill

                    if list_fixed_item[i] == list_reference_item[i]:
                        sheet_out['E' + str(i + 3)] = 'True(일치함)'
                        sheet_out['E' + str(i + 3)].font = self.f2_blue_font
                    else:
                        sheet_out['E' + str(i + 3)] = 'False(불일치)'
                        sheet_out['E' + str(i + 3)].font = self.f2_red_font

                    sheet_out['E' + str(i + 3)].fill = self.yellow_fill

                # 가변값 Set
                for i, v_item in enumerate(list_variable_item):
                    sheet_out['B' + str(i + 10)] = list_find[1][i]
                    sheet_out['B' + str(i + 10)].fill = self.orange_fill
                    sheet_out['C' + str(i + 10)] = v_item
                    sheet_out['D' + str(i + 10)].fill = self.orange_fill
                    sheet_out['E' + str(i + 10)].fill = self.orange_fill

                self.setPrintText('/s {}번 파일 "Comparison" 테이터 입력 완료 /e'.format(idx+1))

                # set temp data

                if self.opFlag:

                    # all cell alignment adjust
                    for mCell in sheet_out["B2:E24"]:
                        for cell in mCell:
                            cell.alignment = self.general_alignment

                    # top alignment adjust
                    for mCell in sheet_out["C4:C24"]:
                        for cell in mCell:
                            cell.alignment = self.top_alignment_3

                    for mCell in sheet_out["D4:D24"]:
                        for cell in mCell:
                            cell.alignment = self.top_alignment_3

                    # all cell border adjust
                    for mCell in sheet_out["B2:E24"]:
                        for cell in mCell:
                            cell.border = self.thin_border

                    # set filter
                    sheet_out.auto_filter.ref = "B2:E24"

                    # each column width adjust
                    sheet_cell_list = ['A', 'B', 'C', 'D', 'E']
                    sheet_width_list = [4.25, 14.75, 57, 57, 23]

                    for i in range(len(sheet_cell_list)):
                        sheet_out.column_dimensions[sheet_cell_list[i]].width = sheet_width_list[i]
                    sheet_out.row_dimensions[1].height = 45

                    # Set Pattern Fill
                    sheet_out['B2'].fill = self.brown_fill
                    sheet_out['C2'].fill = self.brown_fill
                    sheet_out['D2'].fill = self.brown_fill
                    sheet_out['E2'].fill = self.brown_fill


                self.currentRow = self.currentRow + 1
                self.totalRows = self.totalRows + 1
                self.progress_flag.emit()
                self.setPrintText('/s {}번 파일 "Comparison" 시트 스타일 적용 완료 /e'.format(idx+1))
                # save file
                wb_output.save(self.list_out_files[idx])
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    # main method
    def run(self):

        try:
            ###########################__Setting print Text Thread__######################

            self.thread_count = threading.Thread(target=self.getCountRows, args=())
            self.thread_count.daemon = True
            self.thread_count.start()
            self.nowTime = datetime.today().strftime("%Y-%m-%d")

            #################################################################_SETTING INPUT_###########################################################################
            # Save root directory
            self.flag_root = os.path.isdir(self.home+"\\Desktop\\DOC\\")
            if not self.flag_root:
                os.mkdir(self.home + "\\Desktop\\DOC\\")

            # extract file name each list_files and make every out file path
            for item in self.list_files:
                temp_filename = os.path.basename(item)
                temp_filename = re.sub("(.xlsx|.xls)", "", temp_filename)
                output_file = self.home+"\\Desktop\\DOC\\result_"+temp_filename+"("+self.nowTime+").xlsx"
                self.list_out_files.append(output_file)

            if self.modeFlag == "f1":

                #################################################################_RESULT FILE Generate_###########################################################################
                # output file generate
                for item in self.list_out_files:

                    wb = Workbook()
                    s1 = wb.active
                    s1.title = "검증결과요약"
                    wb.create_sheet('시험결과요약', 1)
                    wb.create_sheet('TRP', 2)
                    wb.create_sheet('TIS', 3)
                    wb.create_sheet('속도', 4)
                    wb.create_sheet('Call Setup Test', 5)
                    wb.create_sheet('주파수동조', 6)
                    wb.create_sheet('MOS', 7)
                    wb.create_sheet('배터리소모전류(시간)', 8)
                    wb.create_sheet('배터리소모전류 세부데이터', 9)
                    wb.create_sheet('배터리소모전류(DOU)', 10)
                    wb.create_sheet('첨부1. 측정기준 및 가점', 11)
                    wb.create_sheet('첨부2. 납품검사', 12)
                    wb.create_sheet('첨부3. 단말 상세 SPEC', 13)
                    wb.save(item)

                self.setPrintText("/s Complete making Result excel file /e")
                self.setPrintText("/s Extract Original Data in each file /e")

                #Core Code
                self.start_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                #Excel input Data read
                self.setPrintText("/s STARTED_TIME: "+self.start_time+" /e")

                ########################################################################Start to generate openpyXL Sheet Style########################################################################
                # 검증결과요약 텝 생성
                self.summary_generate_data()
                self.totalRows = 1
                self.currentRow = 0
                self.progress_flag.emit()

                # 시험결과요약 텝 생성
                self.test_generate_data()
                self.totalRows = 2
                self.currentRow = 0
                self.progress_flag.emit()

                # TRP 텝 생성
                self.trp_generate_data()
                self.totalRows = 3
                self.currentRow = 0
                self.progress_flag.emit()

                # TIS 텝 생성
                self.tis_generate_data()
                self.totalRows = 4
                self.currentRow = 0
                self.progress_flag.emit()

                # 속도 텝 생성
                self.spd_generate_data()
                self.totalRows = 5
                self.currentRow = 0
                self.progress_flag.emit()

                # Call Setup Test 텝 생성
                self.call_generate_data()
                self.totalRows = 6
                self.currentRow = 0
                self.progress_flag.emit()

                # 주파수동조 텝 생성
                self.fre_generate_data()
                self.totalRows = 7
                self.currentRow = 0
                self.progress_flag.emit()

                # MOS 텝 생성
                self.mos_generate_data()
                self.totalRows = 8
                self.currentRow = 0
                self.progress_flag.emit()

                # 베터리소모전류(DOU) 텝 생성
                self.dou_generate_data()
                self.totalRows = 9
                self.currentRow = 0
                self.progress_flag.emit()

                # 베터리소모전류 세부테이터 텝 생성
                self.bat_generate_data()
                self.totalRows = 10
                self.currentRow = 0
                self.progress_flag.emit()

                # 베터리소모전류 세부테이터 텝 생성
                self.time_generate_data()
                self.totalRows = 11
                self.currentRow = 0
                self.progress_flag.emit()

                # 베터리소모전류 세부테이터 텝 생성
                self.attach_generate_data_1()
                self.totalRows = 12
                self.currentRow = 0
                self.progress_flag.emit()

                # 베터리소모전류 세부테이터 텝 생성
                self.attach_generate_data_2()
                self.totalRows = 13
                self.currentRow = 0
                self.progress_flag.emit()

                # 베터리소모전류 세부테이터 텝 생성
                self.attach_generate_data_3()
                self.totalRows = 14
                self.currentRow = 0
                self.progress_flag.emit()

                #############################################__progress 100%__#############################################
                self.end_count = "y"
                self.end_flag.emit()

                #Core Code
                self.end_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                #Excel input Data read
                self.setPrintText("/s FINISHED_TIME: "+self.end_time+" /e")

            else:
                #Core Code
                self.start_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                #Excel input Data read
                self.setPrintText("/s STARTED_TIME: "+self.start_time+" /e")
                self.f2_generate_data()
                self.end_count = "y"
                self.end_flag.emit()
                #Core Code
                self.end_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                #Excel input Data read
                self.setPrintText("/s FINISHED_TIME: "+self.end_time+" /e")

        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

if __name__ == '__main__':
    moduler = Formater('C:\\Users\\TestEnC\\Desktop\\VOC\\input_sample.xlsx', 'y',  'f1')
    moduler.run()
