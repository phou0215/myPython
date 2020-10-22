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
# to print the maximum number of occupied rows in console
# ws.max_row
# to print the maximum number of occupied columns in console
# ws.max_column
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

    ####################################################################__condition method group__####################################################################
    # LTE UE Capabiility Tab UE/UL/DL category (3 unit)
    def get_conditional_1(self, ws):

        list_return = ['', '', '']
        list_merged = ws.merged_cells.ranges
        list_merged = [str(x) for x in list_merged]
        # UE category, DL category, UL category value
        for cell in ws['A']:
            if cell.value is None:
                continue
            if 'ue category' in cell.value.lower().strip():

                values = []
                cell_address = cell.coordinate
                cell_rows = [int(cell.row)]
                for item in list_merged:
                    if cell_address in item:
                        to_row = re.findall('[1-9]{1,2}', item.split(':')[1])
                        for idx in range(int(cell.row) + 1, int(to_row[0]) + 1):
                            cell_rows.append(idx)
                        break
                # 조회된 row에 있는 값을 가지고 values list에 입력
                for idx_row in cell_rows:
                    c_value = ws['C' + str(idx_row)].value
                    e_value = ws['E' + str(idx_row)].value
                    if c_value not in [None, '-', '/', '']:
                        c_value = re.sub('[A-Za-z]', '', c_value)
                        values.append(int(c_value))
                    if e_value not in [None, '-', '/', '']:
                        e_value = re.sub('[A-Za-z]', '', e_value)
                        values.append(int(e_value))
                    if c_value in [None, '-', '/', '']:
                        values.append(0)
                    if e_value in [None, '-', '/', '']:
                        values.append(0)
                # top_value
                top_value = max(values)
                list_return[0] = top_value
                continue
            elif 'dl category' in cell.value.lower().strip():
                values = []
                cell_address = cell.coordinate
                cell_rows = [int(cell.row)]
                for item in list_merged:
                    if cell_address in item:
                        to_row = re.findall('[1-9]{1,2}', item.split(':')[1])
                        for idx in range(int(cell.row) + 1, int(to_row[0]) + 1):
                            cell_rows.append(idx)
                        break
                # 조회된 row에 있는 값을 가지고 values list에 입력
                for idx_row in cell_rows:
                    c_value = ws['C' + str(idx_row)].value
                    e_value = ws['E' + str(idx_row)].value
                    if c_value not in [None, '-', '/', '']:
                        c_value = re.sub('[A-Za-z]', '', c_value)
                        values.append(int(c_value))
                    if e_value not in [None, '-', '/', '']:
                        e_value = re.sub('[A-Za-z]', '', e_value)
                        values.append(int(e_value))
                    if c_value in [None, '-', '/', '']:
                        values.append(0)
                    if e_value in [None, '-', '/', '']:
                        values.append(0)
                # top_value
                top_value = max(values)
                list_return[1] = top_value
                continue
            elif 'ul category' in cell.value.lower().strip():
                values = []
                cell_address = cell.coordinate
                cell_rows = [int(cell.row)]
                for item in list_merged:
                    if cell_address in item:
                        to_row = re.findall('[1-9]{1,2}', item.split(':')[1])
                        for idx in range(int(cell.row) + 1, int(to_row[0]) + 1):
                            cell_rows.append(idx)
                        break
                # 조회된 row에 있는 값을 가지고 values list에 입력
                for idx_row in cell_rows:
                    c_value = ws['C' + str(idx_row)].value
                    e_value = ws['E' + str(idx_row)].value
                    if c_value not in [None, '-', '/', '']:
                        c_value = re.sub('[A-Za-z]', '', c_value)
                        values.append(int(c_value))
                    if e_value not in [None, '-', '/', '']:
                        e_value = re.sub('[A-Za-z]', '', e_value)
                        values.append(int(e_value))
                    if c_value in [None, '-', '/', '']:
                        values.append(0)
                    if e_value in [None, '-', '/', '']:
                        values.append(0)
                # top_value
                top_value = max(values)
                list_return[2] = top_value
                continue
        return list_return

    # LTE UE Capabiility ab DL256QAM/ UL64QAM / ULCA / MC-PUSCH / 4X4 MIMO / CA 지원여부 / Max CC(7 unit)
    # [None, '-', '/', '']
    def get_conditional_2(self, ws):
        list_return = ['', '', '', '', '', '', '']
        #####__DL256QAM Data Get__#####
        for cell in ws['B']:
            if cell.value is None:
                continue
            if 'dl modulation' in cell.value.lower():
                cell_row = cell.row
                c_value = ws['C'+str(cell_row)].value.strip()
                if c_value != '256QAM':
                    list_return[0] = 'Y'
                else:
                    list_return[0] = 'N'
                break
        #####__UL64QAM Data Get__#####
        for cell in ws['D']:
            if cell.value is None:
                continue
            if 'ul modulation' in cell.value.lower():
                cell_row = cell.row
                c_value = ws['C'+str(cell_row)].value.strip()
                if c_value != '64QAM':
                    list_return[1] = 'Y'
                else:
                    list_return[1] = 'N'
                break
        #####__ULCA Data Get__#####
        for cell in ws['D']:
            if cell.value is None:
                continue
            if 'uplink' in cell.value.lower():
                cell_row = cell.row
                max_row = ws.max_row
                flag_support = False
                for idx in range(cell_row + 1, max_row + 1):
                    ca_value = ws['D' + str(idx)].value.strip()
                    if '-' in ca_value:
                        flag_support = True
                        break
                if flag_support:
                    list_return[2] = 'Y'
                else:
                    list_return[2] = 'N'
                break
        #####__MC-PUSCH Data Get__#####
        for cell in ws['D']:
            if cell.value is None:
                continue
            if 'mc-pusch' in cell.value.lower():
                cell_row = cell.row
                e_value = ws['E'+str(cell_row)].value.strip().lower()
                if e_value.lower() == 'supported':
                    list_return[3] = 'Y'
                else:
                    list_return[3] = 'N'
                break
        #####__4X4 MIMO Data Get__#####
        for cell in ws['E']:
            if cell.value is None:
                continue
            if 'mimo layer' in cell.value.lower():
                cell_row = cell.row
                max_row = ws.max_row
                flag_support = False
                for idx in range(cell_row + 1, max_row + 1):
                    ca_value = ws['E' + str(idx)].value.strip()
                    if ca_value not in [None, '-', '/', '']:
                        flag_support = True
                        break
                if flag_support:
                    list_return[4] = 'Y'
                else:
                    list_return[4] = 'N'
                break
        #####__CA 지원여부 Data Get__#####
        for cell in ws['B']:
            if cell.value is None:
                continue
            if 'combination' in cell.value.lower():
                cell_row = cell.row
                max_row = ws.max_row
                flag_support = False
                for idx in range(cell_row + 1, max_row + 1):
                    ca_value = ws['B' + str(idx)].value.strip()
                    if '+' in ca_value:
                        flag_support = True
                        break
                if flag_support:
                    list_return[5] = 'Y'
                else:
                    list_return[5] = 'N'
                break
        #####__MAX CC Data Get__#####
        for cell in ws['B']:
            if cell.value is None:
                continue
            if 'combination' in cell.value.lower():
                cell_row = cell.row
                max_row = ws.max_row
                max_cc = 0
                for idx in range(cell_row + 1, max_row + 1):
                    ca_value = ws['B' + str(idx)].value.strip()
                    if '+' in ca_value:
                        list_band = ca_value.split('+')
                        if len(list_band) > max_cc:
                            max_cc = len(list_band)

                if max_cc > 0:
                    list_return[6] = max_cc
                else:
                    list_return[6] = 'N'
                break
        # retrun values
        return list_return

    # ueCapaInfo Tab == > CRDX(Short) / CRDX(Long) / L2W H/O / SRVCC(B2) / SRVCC(CS H/O) / ANR(Inter Freq.)
    # / ANR(Inter RAT) / TTIB / MFBI / A6 Event / RoHC(Profile) 1 / RoHC(Profile) 2/ RoHC(Profile) 4(13 unit)
    def get_conditional_3(self, ws):
        list_return = ['', '', '', '', '', '', '', '', '', '', '', '', '']
        tot_job_count = 0
        cs_ho_values = ['', '', '']
        ##__ueCapaInfo data extract__##
        for cell in ws['A']:
            if cell.value is None:
                continue
            if tot_job_count == 13:
                break
            # get just one value extract
            if cell.value.lower().strip() == 'supportedrohc-profiles':
                cell_row = cell.row
                max_row = ws.max_row
                supported_job_count = 0

                for idx in range(cell_row + 1, max_row + 1):
                    ca_value = ws['A' + str(idx)].value.lower().strip()
                    if supported_job_count == 3:
                        break
                    #####__profile0x0001__#####
                    if 'profile0x0001-r15' in ca_value:
                        if 'true' in ca_value:
                            list_return[10] = 'Y'
                        else:
                            list_return[10] = 'N'
                        supported_job_count = supported_job_count + 1
                        tot_job_count = tot_job_count + 1
                    #####__profile0x0002__#####
                    if 'profile0x0002-r15' in ca_value:
                        if 'true' in ca_value:
                            list_return[11] = 'Y'
                        else:
                            list_return[11] = 'N'
                        supported_job_count = supported_job_count + 1
                        tot_job_count = tot_job_count + 1
                    #####__profile0x0004__#####
                    if 'profile0x0004-r15' in ca_value:
                        if 'true' in ca_value:
                            list_return[12] = 'Y'
                        else:
                            list_return[12] = 'N'
                        supported_job_count = supported_job_count + 1
                        tot_job_count = tot_job_count + 1

            # get 1 ~ 10 unit extract
            if cell.value.lower().strip() == '[feature group indicators]':
                cell_row = cell.row
                max_row = ws.max_row
                feature_job_count = 0
                for idx in range(cell_row + 1, max_row + 1):
                    ca_value = ws['A' + str(idx)].value.lower().strip()
                    if feature_job_count == 12:
                        break
                    #####__CRDX(Short)__#####
                    if 'pc_featrgrp_4' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[0] = 'Y'
                        else:
                            list_return[0] = 'N'
                        tot_job_count = tot_job_count + 1
                        feature_job_count = feature_job_count + 1
                    #####__CRDX(Long)__#####
                    if 'pc_featrgrp_5' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[1] = 'Y'
                        else:
                            list_return[1] = 'N'
                        tot_job_count = tot_job_count + 1
                        feature_job_count = feature_job_count + 1
                    #####__L2W H/O__#####
                    if 'pc_featrgrp_8' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[2] = 'Y'
                        else:
                            list_return[2] = 'N'
                        tot_job_count = tot_job_count + 1
                        feature_job_count = feature_job_count + 1
                    #####__SRVCC(B2)__#####
                    if 'pc_featrgrp_22' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[3] = 'Y'
                        else:
                            list_return[3] = 'N'
                        tot_job_count = tot_job_count + 1
                        feature_job_count = feature_job_count + 1
                    #####__featrgrp_13__#####
                    if 'pc_featrgrp_13' in ca_value:
                        list_info = ca_value.split(':')
                        cs_ho_values.append(list_info[1].lower().strip())
                        feature_job_count = feature_job_count + 1
                    #####__featrgrp_25__#####
                    if 'pc_featrgrp_25' in ca_value:
                        list_info = ca_value.split(':')
                        cs_ho_values.append(list_info[1].lower().strip())
                        feature_job_count = feature_job_count + 1
                    #####__featrgrp_27__#####
                    if 'pc_featrgrp_27' in ca_value:
                        list_info = ca_value.split(':')
                        cs_ho_values.append(list_info[1].lower().strip())
                        feature_job_count = feature_job_count + 1
                    #####__ANR(Inter Freq.)__#####
                    if 'pc_featrgrp_18' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[5] = 'Y'
                        else:
                            list_return[5] = 'N'
                        tot_job_count = tot_job_count + 1
                        feature_job_count = feature_job_count + 1
                    #####__ANR(Inter RAT)__#####
                    if 'pc_featrgrp_19' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[6] = 'Y'
                        else:
                            list_return[6] = 'N'
                        tot_job_count = tot_job_count + 1
                        feature_job_count = feature_job_count + 1
                    #####__TTIB and MFBI__#####
                    if 'pc_featrgrp_28' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[7] = 'Y'
                            list_return[8] = 'Y'
                        else:
                            list_return[7] = 'N'
                            list_return[8] = 'N'
                        tot_job_count = tot_job_count + 2
                        feature_job_count = feature_job_count + 2
                    #####__A6 Event__#####
                    if 'pc_featrgrp_111' in ca_value:
                        list_info = ca_value.split(':')
                        if list_info[1].lower().strip() == 'support':
                            list_return[9] = 'Y'
                        else:
                            list_return[9] = 'N'
                        tot_job_count = tot_job_count + 1
                        feature_job_count = feature_job_count + 1

                #####__SRVCC(CS H/O)__#####
                set_cs_ho_values = set(cs_ho_values)
                cs_ho_values = list(set_cs_ho_values)
                if len(cs_ho_values) == 1 and cs_ho_values[0] == 'support':
                    list_return[4] = 'Y'
                else:
                    list_return[4] = 'N'
                tot_job_count = tot_job_count + 1

    # LTE UE Capabiility tab 지원주파수 EUTRA-FDD(B1) / EUTRA-FDD(B3) /EUTRA-FDD(B5) / EUTRA-FDD(B7) / EUTRA-FDD(B8) (5 unit)
    def get_conditional_4(self, ws):

        list_return = ['N', 'N', 'N', 'N', 'N']
        for cell in ws['B']:
            if cell.value is None:
                continue
            if cell.value.lower().strip() == 'band list':
                row_idx = cell.row
                c_value = ws['C' + str(row_idx)].value.lower().strip()
                # band 1 check
                if '1' in c_value:
                    list_return[0] = 'Y'
                # band 3 check
                if '3' in c_value:
                    list_return[1] = 'Y'
                # band 5 check
                if '5' in c_value:
                    list_return[2] = 'Y'
                # band 7 check
                if '7' in c_value:
                    list_return[3] = 'Y'
                # band 8 check
                if '8' in c_value:
                    list_return[4] = 'Y'
                break
        # return band info
        return list_return


    #  LTE UE Capabiility tab 지원 CA ==> 5CA(2UL 지원여부) / 5CA(B1+B3+B5+B7+B7) / 4CA(2UL 지원여부) / 4CA(B1+B3+B5+B7)
    #  / 3DL+1UL(B1+B3+B5) / 3DL+2UL(B1+B3+B5) / 2DL+1UL(B1+B3) / 2DL+2UL(B1+B3) (8 unit)
    def get_conditional_5(self, ws):

        list_return = ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']
        list_band_info = []
        list_ca_info = []

        for cell in ws['B']:
            if cell.value is None:
                continue
            # first find 'band combination'
            if cell.value.lower().strip() == 'band combination':
                cell_row = cell.row
                max_row = ws.max_row
                # append band info in list_band_info
                for idx in range(cell_row + 1, max_row + 1):
                    band_value = ws['B'+str(idx)].value.lower().strip()
                    ca_value = ws['C'+str(idx)].value.lower().strip()
                    ca_value = ca_value.replace('a', '')
                    list_band_info.append(band_value)
                    list_ca_info.append(ca_value)

                # check band info
                for idx, item in enumerate(list_band_info):
                    # size CA count
                    list_ca_band = item.split('+')
                    ca_count = len(list_ca_band)
                    # check uplink support 2UL in 5CA
                    if ca_count == 5:
                        ul_count = 0
                        # check ul count on ca band
                        for ca in list_ca_band:
                            if 'ul' in ca:
                                ul_count = ul_count + 1
                        if ul_count >= 2:
                            list_return[0] = 'Y'

                    # check 1+3+5+7+7 band combination  in 5CA
                    if ca_count == 5:
                        ca_info = list_ca_info[idx]
                        # check ul count on ca band
                        for ca in list_ca_band:
                            if 'ul' in ca:
                                ul_count = ul_count + 1
                        if ul_count >= 2:
                            list_return[0] = 'Y'




        # return band info
        return list_return
    def get_conditional_6(self, ws):
        pass
    def get_conditional_7(self, ws):
        pass
    def get_conditional_8(self, ws):
        pass
    def get_conditional_9(self, ws):
        pass
    def get_conditional_10(self, ws):
        pass
    def get_conditional_11(self, ws):
        pass
    def get_conditional_12(self, ws):
        pass
    def get_conditional_13(self, ws):
        pass
    def get_conditional14(self, ws):
        pass
    def get_conditional_15(self, ws):
        pass
    def get_conditional_16(self, ws):
        pass
    def get_conditional_17(self, ws):
        pass
    def get_conditional_18(self, ws):
        pass
    def get_conditional_19(self, ws):
        pass

    # extract condition in extract sheet 'A', 'B', 'C' column
    def extract_condition(self, ws):

        list_return = []
        for item in ['A', 'B', 'C']:
            list_temp = []
            for cell in ws[item]:
                list_temp.append(cell.value)
            list_return.append(list_temp)
        return list_return

    # check convert num available
    def check_empty(self, string_data):

        return_data = ''
        if string_data is None or string_data == '' or string_data.lower() in ['n/a', 'na', 'nt', 'n/t']:
            return_data = '-'
        else:
            return_data = str(string_data)
        return return_data

    # check empty cell in sheet
    def check_condition(self, ws):
        return_ws = ws
        max_row = ws.max_row
        self.setPrintText('Check Empty Cell Count max_rows : {}'.format(max_row))
        for item in ['A', 'B', 'C']:
            for cell in return_ws[item]:
                if cell.value is None or cell.value == '' or cell.value.lower() in ['n/a', 'na', 'nt', 'n/t']:
                    cell.value = '-'
        self.setPrintText('Check Empty Cell job is Completed')
        return return_ws

    def bsp_generate_data(self):

        try:

            for idx, item in enumerate(self.list_files):

                net_type = ''
                list_input_rows = []
                wb_output = openpyxl.load_workbook(item, data_only=True)
                list_sheets = wb_output.sheetnames
                #check net type
                if ('ENDC UE Capability' and 'ueCapaInfo_5G-NR' and '추출정보' and '기본단말_Spec정보') in list_sheets:
                    net_type = '5G'
                # LTE type
                elif ('LTE UE Capabiility' and 'ueCapaInfo_LTE' and '추출정보', '기본단말_Spec정보') in list_sheets and \
                        ('ENDC UE Capability' and 'ueCapaInfo_5G-NR') not in list_sheets:
                    net_type = 'LTE'
                else:
                    net_type = 'unknown'

                # 추출 작업 시작
                if net_type == '5G':

                    ws_lte_cap = wb_output['LTE UE Capabiility']
                    ws_endc_cap = wb_output['ENDC UE Capability']
                    ws_lte_ueCap = wb_output['ueCapaInfo_LTE']
                    ws_5g_nr = wb_output['ueCapaInfo_5G-NR']
                    ws_spec = wb_output['기본단말_Spec정보']
                    ws_extract = wb_output['추출정보']
                    ws_spec_re = self.check_condition(ws_spec)
                    ws_extract_re = self.check_condition(ws_extract)
                    # A, B, C column 조건 값 추출
                    a_condi, b_condi, c_condi = self.extract_condition(ws_extract_re)

                    # check row index match condition(입력해야 할 대상에 row 주소값 확인)
                    for idx_2 in range(1, ws_spec_re.max_row + 1):
                        value_a = ws_spec_re.cell(row=idx_2, column=1).value
                        value_b = ws_spec_re.cell(row=idx_2, column=2).value
                        value_c = ws_spec_re.cell(row=idx_2, column=3).value
                        # generate condition
                        for idx_3, data in enumerate(a_condi):
                            if value_a == data and value_b == b_condi[idx_3] and value_c == c_condi[idx_3]:
                                list_input_rows.append(idx_2)
                                break
                    # Check len count
                    if len(list_input_rows) != 49:
                        self.setPrintText('{} 파일에 추출정보에 있는 값 중 기본단말_Spec정보에 없는 것이 있습니다. 정보를 다시 확인해 주세요.'.format(item))
                        break




                elif net_type == 'LTE':
                    pass
                else:
                    self.setPrintText('Net Type Unknown Check input sheet names')
                    self.setPrintText('LTE Type only {}, {}, {}, {} sheet exists'.format('LTE UE Capabiility', 'ueCapaInfo_LTE', '추출정보', '기본단말_Spec정보'))
                    self.setPrintText('5G Type {}, {}, {}, {}, {} sheet exists'.format('LTE UE Capabiility',
                                                                                   'ENDC UE Capability', 'ueCapaInfo_LTE', 'ueCapaInfo_5G-NR', '추출정보', '기본단말_Spec정보'))
                    continue


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
