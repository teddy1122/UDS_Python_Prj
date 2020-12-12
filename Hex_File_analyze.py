#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.07.23
import os
import File_data
import binascii
# from File_data import DCM_Read_Driver_File,\
# DCM_Read_App_File,\
# DCM_Read_Cal_File,\
# APP_start_address_record,\
# APP_End_address_record,\
# CAL_start_address_record,\
# CAL_End_address_record,\
# DRV_start_address_record,\
# DRV_End_address_record

class Hex_File_analyze():
    def __init__(self):
#        self.DCM_Read_Driver_File = []
#        self.DCM_Read_App_File = []
#        self.DCM_Read_Cal_File = []
#        self.APP_start_address_record = []
#        self.APP_End_address_record = []
#        self.CAL_start_address_record = []
#        self.CAL_End_address_record = []
#        self.DRV_start_address_record = []
#        self.DRV_End_address_record = []
        pass
    def file_analyze(self,DRV_APP_CAL,file_handle):
#         global DCM_Read_Driver_File
#         global DCM_Read_App_File
#         global DCM_Read_Cal_File
#         global APP_start_address_record
#         global APP_End_address_record
#         global CAL_start_address_record
#         global CAL_End_address_record
#         global DRV_start_address_record
#         global DRV_End_address_record
        if(DRV_APP_CAL == 0):#driver
            File_data.DCM_Read_Driver_File.clear()
            File_data.DRV_start_address_record.clear()
            File_data.DRV_End_address_record.clear()
            print("clear Driver buffer\r\n")
        elif(DRV_APP_CAL == 1):#App
            File_data.DCM_Read_App_File.clear()
            File_data.APP_start_address_record.clear()
            File_data.APP_End_address_record.clear()
            print("clear App buffer\r\n")
        elif(DRV_APP_CAL == 2):#Cal
            File_data.DCM_Read_Cal_File.clear()
            File_data.CAL_start_address_record.clear()
            File_data.CAL_End_address_record.clear()
            print("clear Cal buffer\r\n")
        else:
            pass
        
        file_data = open(file_handle,"r")
        error_info = 'NO'
        block_end_address = 0
        last_block_end_address = 0
        read_line_length = 0
        address_h = 0
        last_address_h = 0
        data_last_address_H = 0
        Temp_start_address_record = []
        Temp_End_address_record = []
        file_type = os.path.splitext(file_handle)[-1]
        CRC_INFO = 0
        if(file_type == '.hex' or file_type == '.HEX'):
            for flie_read_line in file_data.readlines():
                read_line_length = int(flie_read_line[1:3],16)
                hex_file_type = int(flie_read_line[7:9:1],16)
                if(hex_file_type == 0):
        #             print('数据记录')
                    block_end_address = int(flie_read_line[3:7:1],16)
                    if((last_block_end_address+1)&0xFFFF != block_end_address):#不连�?的地址
                        Temp_start_address_record.append(address_h*65536+block_end_address)
                        #if block_address_start_flag == True:
                            #block_address_start_flag = False
                        if(data_last_address_H != address_h ):
                            Temp_End_address_record.append(last_address_h*65536+last_block_end_address)
                        else:
                            Temp_End_address_record.append(address_h*65536+last_block_end_address)
                        #else:
                            #End_address_record.append(address_h*65536+last_block_end_address)
                    block_end_address += read_line_length-1
                    last_block_end_address = block_end_address
                    data_last_address_H = address_h
    #                 print("data:{0}".format(flie_read_line[9:-3]))
                    self.store_download_data(DRV_APP_CAL,flie_read_line[9:-3])
                    pass
                elif(hex_file_type == 1):
        #             print('文件结束记录')
                    Temp_End_address_record.append(address_h*65536+last_block_end_address)
                    Temp_End_address_record.pop(0)
                    if(DRV_APP_CAL == 0):#driver
                        File_data.DRV_start_address_record = Temp_start_address_record
                        File_data.DRV_End_address_record = Temp_End_address_record
                        File_data.DCM_Driver_File = ''.join(File_data.DCM_Read_Driver_File)
                        File_data.File_Total_Size += len(File_data.DCM_Driver_File)/2
                        print("File_Total_Size1:{0}".format(File_data.File_Total_Size))
                        #print(File_data.DCM_Driver_File)
                        File_data.DCM_Driver_File_CRC =  binascii.crc32(binascii.a2b_hex(File_data.DCM_Driver_File))
                        print("DCM_Driver_File_CRC:{0}\n".format(hex(File_data.DCM_Driver_File_CRC)))
                        CRC_INFO = File_data.DCM_Driver_File_CRC
                    elif(DRV_APP_CAL == 1):#App
                        File_data.APP_start_address_record = Temp_start_address_record
                        File_data.APP_End_address_record = Temp_End_address_record
                        File_data.DCM_App_File = ''.join(File_data.DCM_Read_App_File)
                        File_data.File_Total_Size += len(File_data.DCM_App_File)/2
                        print("File_Total_Size2:{0}".format(File_data.File_Total_Size))
                        File_data.DCM_App_File_CRC =  binascii.crc32(binascii.a2b_hex(File_data.DCM_App_File))
                        print("DCM_App_File_CRC:{0}\n".format(hex(File_data.DCM_App_File_CRC)))
                        CRC_INFO = File_data.DCM_App_File_CRC
                    elif(DRV_APP_CAL == 2):#Cal
                        File_data.CAL_start_address_record = Temp_start_address_record
                        File_data.CAL_End_address_record = Temp_End_address_record
                        File_data.DCM_Cal_File = ''.join(File_data.DCM_Read_Cal_File)
                        File_data.File_Total_Size += len(File_data.DCM_Cal_File)/2
                        print("File_Total_Size3:{0}".format(File_data.File_Total_Size))
                        File_data.DCM_Cal_File_CRC =  binascii.crc32(binascii.a2b_hex(File_data.DCM_Cal_File))
                        print("DCM_Cal_File_CRC:{0}\n".format(hex(File_data.DCM_Cal_File_CRC)))
                        CRC_INFO = File_data.DCM_App_File_CRC
                    print('start_address_record:')
                    print(File_data.DRV_start_address_record)
                    print("\r\nEnd_address_record:")
                    print(File_data.DRV_End_address_record)
                    
                elif(hex_file_type == 2):
                    print('扩展段地址记录')
                    pass
                elif(hex_file_type == 4):
    #                print('扩展线性地址记录')
                    last_address_h = address_h            
                    address_h = int(flie_read_line[9:9+read_line_length*2:1],16)
    #                print("last:{0},now:{1}".format(hex(last_address_h),hex(address_h)))
                    pass
                elif(hex_file_type == 5):
                    print('开始线性地址记录')
    #                print(flie_read_line)
                else:
                    print('not valied:{0}'.format(hex_file_type)) 
        #         print(flie_read_line)
        else:
            pass
        file_data.close()
        return (Temp_start_address_record,Temp_End_address_record,error_info,CRC_INFO) 
    def store_download_data(self,DRV_APP_CAL,Filedata):
#         global DCM_Read_Driver_File
#         global DCM_Read_App_File
#         global DCM_Read_Cal_File
        if(DRV_APP_CAL == 0):#driver
            File_data.DCM_Read_Driver_File.append(Filedata)

        elif(DRV_APP_CAL == 1):#App
            File_data.DCM_Read_App_File.append(Filedata)
            
        elif(DRV_APP_CAL == 2):#Cal
            File_data.DCM_Read_Cal_File.append(Filedata)
        else:
            pass