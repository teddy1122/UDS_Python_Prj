#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.07.23
import File_data
from enum import IntEnum
import ISO15765_Tp
import threading
import time
import copy
import datetime
class Uds_Tester_Step(IntEnum):
    UDS_STEP_EXT_SESSION               = 0x00    #10 03
    UDS_STEP_PROGRAME_PRECONDITION     = 0x01    #31 01 ff 02
    UDS_STEP_CONTROL_STOP_DTC          = 0x02    #85 02
    UDS_STEP_COMMUNICATION_STOP_CRL    = 0x03    #28 03 03
    UDS_STEP_PROG_SESSION              = 0x04    #10 02
    UDS_STEP_SECURITY1_REQ_SEED        = 0x05    #27 01
    UDS_STEP_SECURITY1_SEND_KEY        = 0x06    #27 02
    UDS_STEP_REQ_DOWNLOAD              = 0x07    #34 00 44 XXXXXXXX
    UDS_STEP_TRANSFER_DATA             = 0x08    #36
    UDS_STEP_TRANSFER_EXT              = 0x09    #37
    UDS_STEP_CHECK_PROG_INTEGRITY      = 0x0A    #31 01 F0 01
    UDS_STEP_WRITER_FINGER             = 0x0B    #2E
    UDS_STEP_READ_DID                  = 0x0C    #22
    UDS_STEP_ERASE_MEMORY              = 0x0D    #31 01 FF 00 44 XXXX
    UDS_STEP_CHECK_PROG_DEPENDENCE     = 0x0E    #31 01 FF 01
    UDS_STEP_ECU_RESET                 = 0x0F    #11 01
    UDS_STEP_DEFAULT_SESSION           = 0x10    #10 01
    UDS_STEP_14_CLEAR_SRV              = 0x11    #14 FF FF FF
    UDS_STEP_19_READ_DTC               = 0x12    #19 XX XX XX
    UDS_STEP_22_READ_DID1              = 0x13    #22 F1 80
    UDS_STEP_COMMUNICATION_START_CRL   = 0x14    #28 01 01
    UDS_STEP_CONTROL_START_DTC         = 0x15    #85 01
    UDS_STEP_IDLE                      = 0xFF

class Uds_Tester_Send_Rec(IntEnum):
    UDS_IDLE = 0
    UDS_SEND = 1
    UDS_RECV = 2

class Uds_Tester_ID_Type(IntEnum):
    UDS_FUN = 0
    UDS_PHY = 1


send_data_info = {
Uds_Tester_Step.UDS_STEP_EXT_SESSION            :[Uds_Tester_ID_Type.UDS_PHY,0x10, 0x03],
Uds_Tester_Step.UDS_STEP_PROGRAME_PRECONDITION  :[Uds_Tester_ID_Type.UDS_PHY,0x31, 0x01, 0xff, 0x02],
Uds_Tester_Step.UDS_STEP_CONTROL_STOP_DTC       :[Uds_Tester_ID_Type.UDS_FUN,0x85, 0x02],
Uds_Tester_Step.UDS_STEP_COMMUNICATION_STOP_CRL :[Uds_Tester_ID_Type.UDS_FUN,0x28, 0x03, 0x03],
Uds_Tester_Step.UDS_STEP_PROG_SESSION           :[Uds_Tester_ID_Type.UDS_PHY,0x10, 0x02],
Uds_Tester_Step.UDS_STEP_SECURITY1_REQ_SEED     :[Uds_Tester_ID_Type.UDS_PHY,0x27, 0x09],
Uds_Tester_Step.UDS_STEP_SECURITY1_SEND_KEY     :[Uds_Tester_ID_Type.UDS_PHY,0x27, 0x0A,0x00,0x00,0x00,0x00],
Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD           :[Uds_Tester_ID_Type.UDS_PHY,0x34, 0x00, 0x44, 0x01, 0x02, 0x03, 0x04,0x11,0x12,0x13,0x14],
Uds_Tester_Step.UDS_STEP_TRANSFER_DATA          :[Uds_Tester_ID_Type.UDS_PHY,0x36, 0x00],
Uds_Tester_Step.UDS_STEP_TRANSFER_EXT           :[Uds_Tester_ID_Type.UDS_PHY,0x37],
Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY   :[Uds_Tester_ID_Type.UDS_PHY,0x31, 0x01, 0xF0, 0x01,0x00,0x00,0x00,0x00],
Uds_Tester_Step.UDS_STEP_WRITER_FINGER          :[Uds_Tester_ID_Type.UDS_PHY,0x2E, 0xF1, 0x5A,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09],
Uds_Tester_Step.UDS_STEP_READ_DID               :[Uds_Tester_ID_Type.UDS_PHY,0x22, 0xF1, 0x5B],
Uds_Tester_Step.UDS_STEP_ERASE_MEMORY           :[Uds_Tester_ID_Type.UDS_PHY,0x31, 0x01, 0xFF, 0x00, 0x44, 0x10, 0x11, 0x12, 0x13, 0x14, 0x21, 0x22, 0x23],
Uds_Tester_Step.UDS_STEP_CHECK_PROG_DEPENDENCE  :[Uds_Tester_ID_Type.UDS_PHY,0x31, 0x01, 0xFF, 0x01],
Uds_Tester_Step.UDS_STEP_ECU_RESET              :[Uds_Tester_ID_Type.UDS_FUN,0x11, 0x01],
Uds_Tester_Step.UDS_STEP_DEFAULT_SESSION        :[Uds_Tester_ID_Type.UDS_PHY,0x10, 0x01],
Uds_Tester_Step.UDS_STEP_14_CLEAR_SRV           :[Uds_Tester_ID_Type.UDS_PHY,0x14, 0xFF, 0xFF, 0xFF],
Uds_Tester_Step.UDS_STEP_19_READ_DTC            :[Uds_Tester_ID_Type.UDS_PHY,0x19, 0x0A],
Uds_Tester_Step.UDS_STEP_22_READ_DID1           :[Uds_Tester_ID_Type.UDS_PHY,0x22, 0xF1, 0x87],
Uds_Tester_Step.UDS_STEP_IDLE                   :[Uds_Tester_ID_Type.UDS_PHY,0x10, 0x01]

}

updata_flow = {
0x00 : Uds_Tester_Step.UDS_STEP_EXT_SESSION          ,
0x01 : Uds_Tester_Step.UDS_STEP_PROGRAME_PRECONDITION    ,
0x02 : Uds_Tester_Step.UDS_STEP_CONTROL_STOP_DTC          ,
0x03 : Uds_Tester_Step.UDS_STEP_COMMUNICATION_STOP_CRL    ,

0x04 : Uds_Tester_Step.UDS_STEP_READ_DID    ,
0x05 : Uds_Tester_Step.UDS_STEP_PROG_SESSION         ,
0x06 : Uds_Tester_Step.UDS_STEP_SECURITY1_REQ_SEED   ,
0x07 : Uds_Tester_Step.UDS_STEP_SECURITY1_SEND_KEY   ,


#0x08 : Uds_Tester_Step.UDS_STEP_ERASE_MEMORY        ,
0x08 : Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD         ,
0x09 : Uds_Tester_Step.UDS_STEP_TRANSFER_DATA        ,
0x0A : Uds_Tester_Step.UDS_STEP_TRANSFER_EXT         ,
0x0B : Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY,

0x0C : Uds_Tester_Step.UDS_STEP_WRITER_FINGER ,

0x0D : Uds_Tester_Step.UDS_STEP_ERASE_MEMORY        ,

0x0E : Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD         ,
0x0F : Uds_Tester_Step.UDS_STEP_TRANSFER_DATA        ,
0x10 : Uds_Tester_Step.UDS_STEP_TRANSFER_EXT         ,
0x11 : Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY,


#0x12 : Uds_Tester_Step.UDS_STEP_ERASE_MEMORY        ,

#0x13 : Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD         ,
#0x14 : Uds_Tester_Step.UDS_STEP_TRANSFER_DATA        ,
#0x15 : Uds_Tester_Step.UDS_STEP_TRANSFER_EXT         ,
#0x16 : Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY,

0x12 : Uds_Tester_Step.UDS_STEP_CHECK_PROG_DEPENDENCE  ,

#0x17 : Uds_Tester_Step.UDS_STEP_IDLE,
0x13 : Uds_Tester_Step.UDS_STEP_ECU_RESET            ,
0x14 : Uds_Tester_Step.UDS_STEP_DEFAULT_SESSION      ,
0x15 : Uds_Tester_Step.UDS_STEP_14_CLEAR_SRV         ,
0x16 : Uds_Tester_Step.UDS_STEP_19_READ_DTC          ,
0x17 : Uds_Tester_Step.UDS_STEP_IDLE,
0xFF : Uds_Tester_Step.UDS_STEP_IDLE                 ,
}

class Uds(threading.Thread):
    def __init__(self):
        super(Uds,self).__init__()
        self.DCM_receive_flag = 0
        self.DCM_receive_Data = []
        self.UDS_Tester_Step = 0
        self.UDS_Tester_Send_Or_Receive_Ctrl = Uds_Tester_Send_Rec.UDS_IDLE
        self.Srv36_Block_Size = 0

        self.Srv36_Block_Tx_status = 0
        self.Srv36_File_Sector_Num = 0
        self.Srv36_File_Sector_Size = 0
        self.Srv36_File_Type = 0
        self.Current_file_data = 0
        self.Srv36_index = 1
        self.req_seed = []
        self.uds_running = True
        self.CAN_Transmit = ISO15765_Tp.CAN_Tp()
        self.CAN_Transmit.daemon = True
        self.CAN_Transmit.start()
    def Dcm_RxIndication(self):
        ret = self.CAN_Transmit.CanIf_Indication_To_Dcm()
        self.DCM_receive_flag = copy.deepcopy(ret[0])
        self.DCM_receive_Data = copy.deepcopy(ret[1])
        #print("DCM_Data:{0}".format(self.DCM_receive_Data))
        self.CAN_Transmit.CanIf_Clear_Indica_To_Dcm_Flag()#maybe lost data
    def UDS_Tester_Send_Request(self,step):
        id_key = send_data_info[step][0]
        temp_ID = 0
        if id_key:
            temp_ID = File_data.PHY_ID
        else:
            temp_ID = File_data.FUN_ID
        if step == Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD:
            print("self.Srv36_File_Type:{0}".format(self.Srv36_File_Type))
            if self.Srv36_File_Type == 0:#driver file
                if len(File_data.DRV_start_address_record)!=0:
                    send_data_info[step][4] = (File_data.DRV_start_address_record[0] & 0xFF000000)>>24
                    send_data_info[step][5] = (File_data.DRV_start_address_record[0] & 0x00FF0000)>>16
                    send_data_info[step][6] = (File_data.DRV_start_address_record[0] & 0x0000FF00)>>8
                    send_data_info[step][7] = (File_data.DRV_start_address_record[0] & 0x000000FF)
                    send_data_info[step][8] = ((File_data.DRV_End_address_record[0] - File_data.DRV_start_address_record[0]+1) & 0xFF000000)>>24
                    send_data_info[step][9] = ((File_data.DRV_End_address_record[0] - File_data.DRV_start_address_record[0]+1) & 0x00FF0000)>>16
                    send_data_info[step][10] = ((File_data.DRV_End_address_record[0] - File_data.DRV_start_address_record[0]+1) & 0x0000FF00)>>8
                    send_data_info[step][11] = ((File_data.DRV_End_address_record[0] - File_data.DRV_start_address_record[0]+1) & 0x000000FF)
                    self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
                    #print("DRV data:{0}".format(File_data.DRV_start_address_record))
                    self.Srv36_File_Sector_Num = len(File_data.DRV_start_address_record)
                    self.Srv36_File_Sector_Size = File_data.DRV_End_address_record.pop(0)-File_data.DRV_start_address_record.pop(0)+1
                    self.Srv36_Block_Tx_status = 1
                    self.Current_file_data = File_data.DCM_Driver_File[0:(self.Srv36_File_Sector_Size*2)]
                    File_data.DCM_Driver_File = File_data.DCM_Driver_File[(self.Srv36_File_Sector_Size*2):]
                else:
                    self.Srv36_File_Type = 1
            if self.Srv36_File_Type == 1:#App File
                if len(File_data.APP_start_address_record)!=0:
                    send_data_info[step][4] = (File_data.APP_start_address_record[0] & 0xFF000000)>>24
                    send_data_info[step][5] = (File_data.APP_start_address_record[0] & 0x00FF0000)>>16
                    send_data_info[step][6] = (File_data.APP_start_address_record[0] & 0x0000FF00)>>8
                    send_data_info[step][7] = (File_data.APP_start_address_record[0] & 0x000000FF)
                    send_data_info[step][8] = ((File_data.APP_End_address_record[0] - File_data.APP_start_address_record[0]+1) & 0xFF000000)>>24
                    send_data_info[step][9] = ((File_data.APP_End_address_record[0] - File_data.APP_start_address_record[0]+1) & 0x00FF0000)>>16
                    send_data_info[step][10] = ((File_data.APP_End_address_record[0] - File_data.APP_start_address_record[0]+1) & 0x0000FF00)>>8
                    send_data_info[step][11] = ((File_data.APP_End_address_record[0] - File_data.APP_start_address_record[0]+1) & 0x000000FF)
                    self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
                    self.Srv36_File_Sector_Num = len(File_data.APP_start_address_record)
                    self.Srv36_File_Sector_Size = File_data.APP_End_address_record.pop(0)-File_data.APP_start_address_record.pop(0)+1
                    self.Srv36_Block_Tx_status = 1
                    self.Current_file_data = File_data.DCM_App_File[0:self.Srv36_File_Sector_Size*2]
                    File_data.DCM_App_File = File_data.DCM_App_File[self.Srv36_File_Sector_Size*2:]
                else:
                    self.Srv36_File_Type = 2
            if self.Srv36_File_Type == 2:#Call File
                if len(File_data.CAL_start_address_record)!=0:
                    send_data_info[step][4] = (File_data.CAL_start_address_record[0] & 0xFF000000)>>24
                    send_data_info[step][5] = (File_data.CAL_start_address_record[0] & 0x00FF0000)>>16
                    send_data_info[step][6] = (File_data.CAL_start_address_record[0] & 0x0000FF00)>>8
                    send_data_info[step][7] = (File_data.CAL_start_address_record[0] & 0x000000FF)
                    send_data_info[step][8] = ((File_data.CAL_End_address_record[0] - File_data.CAL_start_address_record[0]+1) & 0xFF000000)>>24
                    send_data_info[step][9] = ((File_data.CAL_End_address_record[0] - File_data.CAL_start_address_record[0]+1) & 0x00FF0000)>>16
                    send_data_info[step][10] = ((File_data.CAL_End_address_record[0] - File_data.CAL_start_address_record[0]+1) & 0x0000FF00)>>8
                    send_data_info[step][11] = ((File_data.CAL_End_address_record[0] - File_data.CAL_start_address_record[0]+1) & 0x000000FF)
                    self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
                    self.Srv36_File_Sector_Num = len(File_data.CAL_start_address_record)
                    self.Srv36_File_Sector_Size = File_data.CAL_End_address_record.pop(0)-File_data.CAL_start_address_record.pop(0)+1
                    self.Srv36_Block_Tx_status = 1
                    #print("size:{0} Cal_Data:{1}".format(self.Srv36_File_Sector_Size,File_data.DCM_Cal_File))
                    self.Current_file_data = File_data.DCM_Cal_File[0:(self.Srv36_File_Sector_Size*2)]
                    File_data.DCM_Cal_File = File_data.DCM_Cal_File[(self.Srv36_File_Sector_Size*2):]
                else:
                    self.Srv36_File_Type = 3

            #print("current file data:{0} size:{1}\r\n".format(self.Current_file_data,self.Srv36_File_Sector_Size))
        elif step == Uds_Tester_Step.UDS_STEP_TRANSFER_DATA:
            if self.Srv36_Block_Tx_status == 0:#no data transfer currently
                print("No data transfer currently\r\n")
            else:#have file data need to transfer
                if self.Srv36_File_Sector_Num != 0:#this file data haven't over
                    if self.Srv36_File_Sector_Size > (self.Srv36_Block_Size-2):
                        print("Srv36 num sector:{0} size:{1}".format(self.Srv36_File_Sector_Num,self.Srv36_File_Sector_Size))
                        send_data_info[step] = send_data_info[step][0:3]
                        send_data_info[step][2] = self.Srv36_index
                        self.Srv36_File_Sector_Size -= (self.Srv36_Block_Size-2)
                        send_data_info[step].extend(list(bytes.fromhex(self.Current_file_data[0:(self.Srv36_Block_Size-2)*2])))
                        #print("Transmit1 data{0} datasize:{1} Srv36_File_Sector_Size{2}".format(send_data_info[step],len(send_data_info[step]),self.Srv36_File_Sector_Size))
                        self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
                        File_data.File_Send_Size += self.Srv36_Block_Size
                        print("Send_data_size1:{0}\r\n".format(File_data.File_Send_Size))
                        self.Current_file_data = self.Current_file_data[(self.Srv36_Block_Size-2)*2:]
                        #print("self.Current_file_data1:{0} len:{1}".format(self.Current_file_data,len(self.Current_file_data)))
                        self.Srv36_index += 1
                        if self.Srv36_index > 0xFF:
                            self.Srv36_index = 0
                    else:#this sector last data
                        print("this sector last data\r\n")
                        send_data_info[step] = send_data_info[step][0:3]
                        send_data_info[step][2] = self.Srv36_index
                        send_data_info[step].extend(list(bytes.fromhex(self.Current_file_data[0:(self.Srv36_File_Sector_Size*2)])))
                        #print("Transmit2 data{0} datasize:{1} Srv36_File_Sector_Size{2}".format(send_data_info[step],len(send_data_info[step]),self.Srv36_File_Sector_Size))
                        self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
                        File_data.File_Send_Size += self.Srv36_File_Sector_Size
                        print("Send_data_size2:{0}\r\n".format(File_data.File_Send_Size))
                        self.Current_file_data = self.Current_file_data[(self.Srv36_File_Sector_Size*2):]
                        #print("self.Current_file_data2:{0} len:{1}".format(self.Current_file_data,len(self.Current_file_data)))
                        self.Srv36_File_Sector_Size = 0
                        self.Srv36_index = 1
                        self.Srv36_File_Sector_Num -= 1
                        #self.UDS_Tester_Send_Request(Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD)
        elif step == Uds_Tester_Step.UDS_STEP_SECURITY1_SEND_KEY:
            ret = self.seed_to_key(self.req_seed)
            send_data_info[step][3] = ret[0]
            send_data_info[step][4] = ret[1]
            send_data_info[step][5] = ret[2]
            send_data_info[step][6] = ret[3]
            self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
        elif step == Uds_Tester_Step.UDS_STEP_ERASE_MEMORY:
            print("########ERASE MEMORY#########:File_Type:{0}\r\n".format(self.Srv36_File_Type))
            if self.Srv36_File_Type == 0:#driver file
                if len(File_data.DRV_start_address_record)!=0:
                                  
                    pass
                else:
                    self.Srv36_File_Type = 1
                    
            if self.Srv36_File_Type == 1:#App File
                if len(File_data.APP_start_address_record) != 0:
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][6] = (File_data.APP_start_address_record[0] & 0xFF000000)>>24
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][7] = (File_data.APP_start_address_record[0] & 0x00FF0000)>>16
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][8] = (File_data.APP_start_address_record[0] & 0x0000FF00)>>8
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][9] = (File_data.APP_start_address_record[0] & 0x000000FF)
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][10] = ((File_data.APP_End_address_record[-1] - File_data.APP_start_address_record[0]+1) & 0xFF000000)>>24
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][11] = ((File_data.APP_End_address_record[-1] - File_data.APP_start_address_record[0]+1) & 0x00FF0000)>>16
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][12] = ((File_data.APP_End_address_record[-1] - File_data.APP_start_address_record[0]+1) & 0x0000FF00)>>8
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][13] = ((File_data.APP_End_address_record[-1] - File_data.APP_start_address_record[0]+1) & 0x000000FF)
                    self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
                else:
                    self.Srv36_File_Type = 2
                    
            if self.Srv36_File_Type == 2:#Cal File
                if len(File_data.CAL_start_address_record) != 0:
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][6] = (File_data.CAL_start_address_record[0] & 0xFF000000)>>24
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][7] = (File_data.CAL_start_address_record[0] & 0x00FF0000)>>16
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][8] = (File_data.CAL_start_address_record[0] & 0x0000FF00)>>8
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][9] = (File_data.CAL_start_address_record[0] & 0x000000FF)
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][10] = ((File_data.CAL_End_address_record[-1] - File_data.CAL_start_address_record[0]+1) & 0xFF000000)>>24
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][11] = ((File_data.CAL_End_address_record[-1] - File_data.CAL_start_address_record[0]+1) & 0x00FF0000)>>16
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][12] = ((File_data.CAL_End_address_record[-1] - File_data.CAL_start_address_record[0]+1) & 0x0000FF00)>>8
                    send_data_info[Uds_Tester_Step.UDS_STEP_ERASE_MEMORY][13] = ((File_data.CAL_End_address_record[-1] - File_data.CAL_start_address_record[0]+1) & 0x000000FF)
                    self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
                else:
                    self.Srv36_File_Type = 3
                    
            if self.Srv36_File_Type == 3:#No more file send，download over
                self.UDS_Tester_Step = 0x17
                
                self.CAN_Transmit.Tp_Transmit(send_data_info[updata_flow[self.UDS_Tester_Step]][1:], temp_ID)
        elif step == Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY:
            
            if self.Srv36_File_Type == 0:#driver file
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][5] = (File_data.DCM_Driver_File_CRC & 0xFF000000)>>24
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][6] = (File_data.DCM_Driver_File_CRC & 0x00FF0000)>>16
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][7] = (File_data.DCM_Driver_File_CRC & 0x0000FF00)>>8
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][8] = (File_data.DCM_Driver_File_CRC & 0x000000FF)
                print("send_data_info:{0},,,{1}".format(send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][5],File_data.DCM_Driver_File_CRC))
            elif self.Srv36_File_Type == 1:#App File
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][5] = (File_data.DCM_App_File_CRC & 0xFF000000)>>24
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][6] = (File_data.DCM_App_File_CRC & 0x00FF0000)>>16
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][7] = (File_data.DCM_App_File_CRC & 0x0000FF00)>>8
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][8] = (File_data.DCM_App_File_CRC & 0x000000FF)
            elif self.Srv36_File_Type == 2:#Cal File
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][5] = (File_data.DCM_Cal_File_CRC & 0xFF000000)>>24
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][6] = (File_data.DCM_Cal_File_CRC & 0x00FF0000)>>16
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][7] = (File_data.DCM_Cal_File_CRC & 0x0000FF00)>>8
                send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][8] = (File_data.DCM_Cal_File_CRC & 0x000000FF)
            else:
                pass
            print("+++++++++++++++CRC+++++++++++file_type:{0},data:{1}".format(self.Srv36_File_Type,send_data_info[Uds_Tester_Step.UDS_STEP_CHECK_PROG_INTEGRITY][1:]))
            self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
            pass
        elif step == Uds_Tester_Step.UDS_STEP_ECU_RESET:
            
            self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
            time.sleep(0.1)
        elif step == Uds_Tester_Step.UDS_STEP_WRITER_FINGER:
            date = datetime.datetime.now()
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][4] = int((((date.year)%100)//10*16)+(date.year%10))
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][5] = int((((date.month)//10)*16)+((date.month)%10))
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][6] = int((((date.day)//10)*16)+((date.day)%10))

            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][7] = 0x12
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][8] = 0x34
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][9] = 0x56
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][10] = 0x78
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][11] = 0x9A
            send_data_info[Uds_Tester_Step.UDS_STEP_WRITER_FINGER][12] = 0xBC

            self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
        else:
            self.CAN_Transmit.Tp_Transmit(send_data_info[step][1:], temp_ID)
            #print("request ID:{0} request Key:{1} step:{2} value:{3}\r\n".format(hex(request_ID[id_key]),id_key,send_data_info[step],File_data.FUN_ID))
        #print("tp send data:{0}".format(send_data_info[step][:]))
    def run(self):
        print("UDS Mainfunction Runing\n")

        while self.uds_running:
            time.sleep(0.0005)
            self.Dcm_RxIndication()
            if self.UDS_Tester_Send_Or_Receive_Ctrl == Uds_Tester_Send_Rec.UDS_IDLE:
                pass
            elif self.UDS_Tester_Send_Or_Receive_Ctrl == Uds_Tester_Send_Rec.UDS_SEND:
                if updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_SECURITY1_SEND_KEY:
                    pass
                elif updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD:

                    pass
                elif updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_TRANSFER_DATA:
                    pass
                elif updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_ERASE_MEMORY:

                    print("###ERASE MEMORY File Type:{0} Step:{1}".format(self.Srv36_File_Type,self.UDS_Tester_Step))
                else:
                    pass
                
                if updata_flow[self.UDS_Tester_Step] != Uds_Tester_Step.UDS_STEP_IDLE:
                    self.UDS_Tester_Send_Request(updata_flow[self.UDS_Tester_Step])
                    self.UDS_Tester_Send_Or_Receive_Ctrl = Uds_Tester_Send_Rec.UDS_RECV
                else:
                    self.UDS_Tester_Send_Or_Receive_Ctrl = Uds_Tester_Send_Rec.UDS_IDLE
                
            elif self.UDS_Tester_Send_Or_Receive_Ctrl == Uds_Tester_Send_Rec.UDS_RECV:
                if self.DCM_receive_flag == 1:
                    #print("data:{0} compare:{1} step:{2}".format(self.DCM_receive_Data,send_data_info[updata_flow[self.UDS_Tester_Step]],self.UDS_Tester_Step))
                    if updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_SECURITY1_REQ_SEED:
                        pass
                    elif updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_REQ_DOWNLOAD:
                        pass
                    elif updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_TRANSFER_DATA:
                        pass
                    else:
                        pass
                    if self.DCM_receive_Data[0] == send_data_info[updata_flow[self.UDS_Tester_Step]][1]+0x40:
                        self.UDS_Tester_Send_Or_Receive_Ctrl = Uds_Tester_Send_Rec.UDS_SEND
                        
                        if send_data_info[updata_flow[self.UDS_Tester_Step]][1] == 0x34:
                            self.Srv36_Block_Size = self.DCM_receive_Data[2]*256+self.DCM_receive_Data[3]
                            print("Srv 36 Block Size:{0}".format(self.Srv36_Block_Size))
                        else:
                            pass
                        if send_data_info[updata_flow[self.UDS_Tester_Step]][1] == 0x27:
                            print("cmd:{0},step:{1}\n".format(send_data_info[updata_flow[self.UDS_Tester_Step]][1],self.UDS_Tester_Step))
                            if updata_flow[self.UDS_Tester_Step] == Uds_Tester_Step.UDS_STEP_SECURITY1_REQ_SEED:
                                self.req_seed = self.DCM_receive_Data[2:6]
                                print("request seed:{0}\n".format(self.req_seed))
                            else:
                                pass
                        else:
                            pass
                        if send_data_info[updata_flow[self.UDS_Tester_Step]][1] != 0x36:
                            self.UDS_Tester_Step += 1
                            print("current srv:{0}".format(hex(send_data_info[updata_flow[self.UDS_Tester_Step]][1])))
                        else:
                            if self.Srv36_File_Sector_Num == 0:
                                self.UDS_Tester_Step += 1
                            else:
                                if self.Srv36_File_Sector_Size != 0:
                                    pass
                                else:
                                    self.UDS_Tester_Step -= 1
                                pass
                        print("Positive response next:{0}\r\n".format(self.UDS_Tester_Step))
                    elif self.DCM_receive_Data[0] == 0x7F and self.DCM_receive_Data[2] == 0x78:
                        print("Pendding\r\n")
                    else:
                        self.UDS_Tester_Step = 0xFF
                        self.UDS_Tester_Send_Or_Receive_Ctrl = Uds_Tester_Send_Rec.UDS_IDLE
                    #self.DCM_receive_Data.pop(0)
                    #if len(self.DCM_receive_Data) != 0:
                    #    pass
                    #else:
                    self.DCM_receive_flag = 0
                        #self.CAN_Transmit.CanIf_Clear_Indica_To_Dcm_Flag()#maybe lost data
                else:
                    pass
    def Set_Uds_Tester_Step(self,step):
        print("send_recv:{0}\n".format(self.UDS_Tester_Send_Or_Receive_Ctrl))
        if self.UDS_Tester_Send_Or_Receive_Ctrl == Uds_Tester_Send_Rec.UDS_IDLE:
            self.UDS_Tester_Step = step
            self.UDS_Tester_Send_Or_Receive_Ctrl = Uds_Tester_Send_Rec.UDS_SEND
            print("set Uds_Tester_step:{0}\r\n".format(self.UDS_Tester_Step))
            self.return_status = 0
            if len(File_data.DRV_start_address_record)!=0:
                self.Srv36_File_Type = 0
            elif len(File_data.APP_start_address_record)!=0:
                self.Srv36_File_Type = 1
            elif len(File_data.CAL_start_address_record)!=0:
                self.Srv36_File_Type = 2
            else:
                self.Srv36_File_Type = 3
            print("Srv36_File_Type:##{0}##\r\n".format(self.Srv36_File_Type))
        else:
            self.return_status = 1
        return self.return_status

    def reset(self):
        self.__init__()
        self.CAN_Transmit.__init__()
    def terminate(self):
        self.uds_running = False
        self.CAN_Transmit.terminate()
        self.CAN_Transmit.join(timeout=1)
        self.join(timeout=1)
    def seed_to_key(self,data):
        '''
        MASK = 0xE26662B7
        wLSBit = 0
        key_byte = [0,1,2,3]
        seed_temp = data[0]<<24 | data[1]<<16 | data[2]<<8 | data[3]
        #print("seed temp:{0}".format(hex(seed_temp)))
        wSeed = seed_temp
        wLastSeed = wSeed
        temp = ((MASK & 0x00000800)>>10) | ((MASK & 0x00200000)>>21)
        if temp == 0:
            wTemp = ((wSeed | 0xFF000000)>>24)
        elif temp == 1:
            wTemp = ((wSeed | 0x00FF0000)>>16)
        elif temp == 2:
            wTemp = ((wSeed | 0x0000FF00)>>8)
        else:
            wTemp = ((wSeed | 0x000000FF))                               

        SB1 = ((MASK & 0x000003Fc)>>2)
        SB2 = (((MASK & 0x7F800000)>>23)^0xA5)
        SB3 = (((MASK & 0x001FE000)>>13)^0x5A)
        iterations = (((wTemp | SB1)^SB2)+SB3)
        #print("sb1:{0}sb2:{1}sb3:{2}iterations:{3}".format(hex(SB1),hex(SB2),hex(SB3),iterations))
        for jj in range(0,iterations):
            wTemp = (((wLastSeed^0x40000000)//0x40000000)^((wLastSeed & 0x01000000)//0x01000000)^((wLastSeed & 0x1000)//0x1000)^((wLastSeed & 0x04)//0x04))&0xFFFFFFFF
            wLSBit = wTemp ^ 0x00000001
            wLastSeed = (wLastSeed << 1)&0xFFFFFFFF
            wTop31Bits = wLastSeed ^ 0xFFFFFFFE
            wLastSeed = wTop31Bits | wLSBit
            #print("wLastSeed:{0}".format(hex(wLastSeed)))
        if MASK & 0x00000001:
            wTop31Bits = ((wLastSeed & 0x00FF0000)>>16)|((wLastSeed^0xFF000000)>>8)|((wLastSeed^0x000000FF)<<8)|((wLastSeed ^ 0x0000FF00)<<16)
        else:
            wTop31Bits = wLastSeed
        #print("wTop31Bits:{0}".format(hex(wTop31Bits)))
        wTop31Bits = wTop31Bits ^ MASK
        key_byte[0] = (wTop31Bits & 0xFF000000)>>24
        key_byte[1] = (wTop31Bits & 0x00FF0000)>>16                                                                                                         
        key_byte[2] = (wTop31Bits & 0x0000FF00)>>8
        key_byte[3] = (wTop31Bits & 0x000000FF)
        '''
        key = 0
        key_byte = [0,1,2,3]
        seed_temp = data[0]<<24 | data[1]<<16 | data[2]<<8 | data[3]
        if(seed_temp != 0):
            for i in range(0,35):
                if(seed_temp & 0x80000000):
                    if(seed_temp & 0x00000002):
                        seed_temp = ((seed_temp << 1)&0xFFFFFFFF)
                        seed_temp = (seed_temp^0xE1D5C303)&0xFFFFFFFF
                    else:
                        seed_temp = (seed_temp << 1)&0xFFFFFFFF
                        seed_temp = seed_temp^0x656777E9
                else:
                    seed_temp = (seed_temp << 1)&0xFFFFFFFF
            key_byte[0] = (seed_temp & 0xFF000000)>>24
            key_byte[1] = (seed_temp & 0x00FF0000)>>16                                                                                                         
            key_byte[2] = (seed_temp & 0x0000FF00)>>8
            key_byte[3] = (seed_temp & 0x000000FF)
        return key_byte
    def UDS_Send_Data(self,data):
        self.CAN_Transmit.Tp_Transmit(data,File_data.PHY_ID)

if __name__=="__main__":
    test_uds = Uds()
    a=[0x0b,0x8A,0x90,0x7D]
    ret = test_uds.seed_to_key(a)
    print("test_uds:{0}".format(list(map(hex,ret))))
