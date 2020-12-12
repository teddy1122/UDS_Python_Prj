#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.08.04

DCM_Read_Driver_File = []
DCM_Read_App_File = []
DCM_Read_Cal_File = []
APP_start_address_record = []
APP_End_address_record = []
CAL_start_address_record = []
CAL_End_address_record = []
DRV_start_address_record = []
DRV_End_address_record = []

DCM_Driver_File = ''
DCM_App_File = ''
DCM_Cal_File = ''

PHY_ID = 0
FUN_ID = 0
RES_ID = 0

DCM_Driver_File_CRC = 0
DCM_App_File_CRC = 0
DCM_Cal_File_CRC = 0

Log_Info = []


File_Total_Size = 0
File_Send_Size = 0