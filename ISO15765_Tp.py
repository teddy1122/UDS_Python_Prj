#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.07.24

import CAN_If
# import UDS 
import time
from enum import IntEnum, Enum
import threading
import File_data
import copy

class CanTpMessageType(IntEnum):
    SINGLE_FRAME = 0
    FIRST_FRAME = 1
    CONSECUTIVE_FRAME = 2
    FLOW_CONTROL = 3

class CanTpState(Enum):
    IDLE = 0
    SEND_SINGLE_FRAME = 1
    SEND_FIRST_FRAME = 2
    SEND_CONSECUTIVE_FRAME = 3
    SEND_FLOW_CONTROL = 4
    WAIT_FLOW_CONTROL = 5
    WAIT_STMIN_TIMEOUT = 6
    WAIT_WAIT_TIMEOUT = 7
    RECEIVING_CONSECUTIVE_FRAME = 8
    RECEIVED_SINGLE_FARME = 9
    RECEIVED_FIRST_FRAME = 10
    BUSY = 255

class CAN_Tp(threading.Thread):
    def __init__(self):
        super().__init__()
        self.CAN_TP_Rx_Status = CanTpState.IDLE
        self.CAN_TP_Tx_Status = CanTpState.IDLE
        self.First_frame_len = 0
        self.CAN_TP_Num_of_Bock_Size = 0
        self.CAN_TP_Tx_Data = []
        self.CAN_TP_Tx_Data_Id = []
        self.CAN_TP_Tx_Data_Temp = []
        self.CAN_TP_Tx_Data_Id_Temp = []
        self.CAN_TP_Tx_Data_len_Temp = 0
        self.CAN_TP_Multi_Fram_Inedex = 0
        self.CanIf_Receive_Flag = 0
        self.CAN_TP_Rx_Data = []
        self.CAN_To_DCM_Data = []
        self.CAN_TP_Wait_Flow_Control_Flag = 0
        self.CAN_TP_Wait_Flow_Control_count = 0
        self.Tp_running = True
        self.tptxdata = []
        print("CAN_Tp Init\n")
    def run(self):
        print("Tp_MainFunction Running\n")
        while self.Tp_running:
            time.sleep(0.0005)
            self.Rx_MainFunction()
            self.Tx_MainFunction()
    def Rx_MainFunction(self):
        #CAN_TP_Rx_Data = []
        receive_data = CAN_If.CAN_Device.can_read()
        if self.CAN_TP_Rx_Status == CanTpState.IDLE:
            if receive_data!=None and receive_data[0] == File_data.RES_ID:#RES ID
                #print("Rx data:{0}".format(receive_data[2]))
                receive_frame_type = (receive_data[2][0] & 0xF0) >> 4
                if receive_frame_type == CanTpMessageType.SINGLE_FRAME:#singe frame
                    self.CAN_TP_Rx_Data.append(receive_data[2][1:])
                    #print("Rx Append:{0}".format(self.CAN_TP_Rx_Data))
                    #UDS.Uds.Dcm_RxIndication(UDS,CAN_TP_Rx_Data)
                    self.CAN_To_DCM_Data = copy.deepcopy(self.CAN_TP_Rx_Data)
                    self.CAN_TP_Rx_Data.clear()
                    self.CanIf_Receive_Flag = 1
#                     self.CAN_TP_Rx_Data.clear()
                    self.CAN_TP_Rx_Status = CanTpState.IDLE
                elif receive_frame_type == CanTpMessageType.FIRST_FRAME:#首帧
                    self.First_frame_len = ((receive_data[2][0]&0x0F)*256 + receive_data[2][1])
                    self.CAN_TP_Rx_Data.append(receive_data[2][2:])
                    self.First_frame_len -= 6
                    self.CAN_TP_Tx_Status = CanTpState.SEND_FLOW_CONTROL
                    self.CAN_TP_Rx_Status = CanTpState.BUSY#wait for send flow control
                elif receive_frame_type == CanTpMessageType.CONSECUTIVE_FRAME:#连续�?
                    #self.CAN_TP_Rx_Status = CanTpState.RECEIVING_CONSECUTIVE_FRAME
                    if self.First_frame_len <= 7:
                        self.CAN_TP_Rx_Data.append(receive_data[2][1:(self.First_frame_len+1)])
                        self.CAN_TP_Rx_Status = CanTpState.IDLE
                        #UDS.Uds.Dcm_RxIndication(UDS,CAN_TP_Rx_Data)
                        self.CAN_To_DCM_Data = copy.deepcopy(self.CAN_TP_Rx_Data)
                        self.CAN_TP_Rx_Data.clear()
                        self.CanIf_Receive_Flag = 1
                    else:
                        self.CAN_TP_Rx_Data.append(receive_data[2][1:8])
                        self.First_frame_len -= 7
                elif receive_frame_type == CanTpMessageType.FLOW_CONTROL:#流控
                    if self.CAN_TP_Tx_Status == CanTpState.WAIT_FLOW_CONTROL or self.CAN_TP_Tx_Status == CanTpState.SEND_CONSECUTIVE_FRAME:
                        self.CAN_TP_Tx_Status = CanTpState.SEND_CONSECUTIVE_FRAME
                        self.CAN_TP_Num_of_Bock_Size = receive_data[2][1]
                        #self.CAN_TP_Multi_Fram_Inedex = 0
                        self.CAN_TP_Wait_Flow_Control_Flag = 0
                        #print("ISOTP receive flow control frame:block:{0} state:{1}\n".format(self.CAN_TP_Num_of_Bock_Size,self.CAN_TP_Tx_Status))
                else:
                    pass
            else:
                pass
        elif self.CAN_TP_Rx_Status == CanTpState.BUSY:
            pass
        else:
            pass
    def Tx_MainFunction(self):
        pdu_data = [0xAA,0xAA,0xAA,0xAA,0xAA,0xAA,0xAA,0xAA]
#         print("TX Main:{0}".format(self.CAN_TP_Tx_Data))
        if self.CAN_TP_Tx_Status == CanTpState.IDLE:
            if len(self.CAN_TP_Tx_Data) != 0:
                #print("Tx Main data1:{0}\r\n".format(self.CAN_TP_Tx_Data))
                self.CAN_TP_Tx_Data_Temp = self.CAN_TP_Tx_Data.pop(0)
                self.CAN_TP_Tx_Data_len_Temp = len(self.CAN_TP_Tx_Data_Temp)
                self.CAN_TP_Tx_Data_Id_Temp = self.CAN_TP_Tx_Data_Id.pop(0)
                #print("Tx Main data2:{0}\r\n".format(self.CAN_TP_Tx_Data))
                if self.CAN_TP_Tx_Data_len_Temp <= 7:#单帧发�?
                    self.CAN_TP_Tx_Status = CanTpState.SEND_SINGLE_FRAME
                else:#多帧发送�?�帧
                    self.CAN_TP_Tx_Status = CanTpState.SEND_FIRST_FRAME
            else:
                pass
        if self.CAN_TP_Tx_Status == CanTpState.SEND_FLOW_CONTROL:
            data = (0x30,0x00,0x00,0x00,0x00,0x00,0x00,0x00)
            CAN_If.CAN_Device.can_write(data, self.CAN_TP_Tx_Data_Id_Temp, 8)
            self.CAN_TP_Rx_Status = CanTpState.IDLE
            self.CAN_TP_Tx_Status = CanTpState.IDLE
        elif self.CAN_TP_Tx_Status == CanTpState.SEND_SINGLE_FRAME:
            pdu_data[0] = self.CAN_TP_Tx_Data_len_Temp
            pdu_data[1:(self.CAN_TP_Tx_Data_len_Temp+1)] = self.CAN_TP_Tx_Data_Temp[0:self.CAN_TP_Tx_Data_len_Temp]
            CAN_If.CAN_Device.can_write(pdu_data, self.CAN_TP_Tx_Data_Id_Temp, self.CAN_TP_Tx_Data_len_Temp+1)
            self.CAN_TP_Tx_Status = CanTpState.IDLE
            self.Canif_Tp_Tx_over = 1
            print('Single frame send\n')
        elif self.CAN_TP_Tx_Status == CanTpState.SEND_FIRST_FRAME:
            pdu_data[0] = 0x10 | (self.CAN_TP_Tx_Data_len_Temp//256)
            pdu_data[1] = self.CAN_TP_Tx_Data_len_Temp%256
            pdu_data[2:8] = self.CAN_TP_Tx_Data_Temp[0:6]
            self.CAN_TP_Tx_Data_Temp = self.CAN_TP_Tx_Data_Temp[6:]
            self.CAN_TP_Multi_Fram_Inedex = 1
            self.CAN_TP_Tx_Data_len_Temp -= 6
            CAN_If.CAN_Device.can_write(pdu_data, self.CAN_TP_Tx_Data_Id_Temp, 8)
            self.CAN_TP_Tx_Status = CanTpState.WAIT_FLOW_CONTROL
            #record time
            print('First frame send\n')
        elif self.CAN_TP_Tx_Status == CanTpState.SEND_CONSECUTIVE_FRAME:
            if ((self.CAN_TP_Num_of_Bock_Size != 0) and (self.CAN_TP_Wait_Flow_Control_Flag == 1)):
                #self.CAN_TP_Tx_Status = CanTpState.WAIT_FLOW_CONTROL
                #print("Tx MultiFram wait for flow control:{0}\n".format(self.CAN_TP_Multi_Fram_Inedex))
                pass
            else:
                if CAN_If.CAN_Device.can_Tx_confirmation() != 1:
                    
                    if self.CAN_TP_Tx_Data_len_Temp <= 7:
                        pdu_data[0] = 0x20|(self.CAN_TP_Multi_Fram_Inedex%16)
                        pdu_data[1:self.CAN_TP_Tx_Data_len_Temp+1] = self.CAN_TP_Tx_Data_Temp[0:self.CAN_TP_Tx_Data_len_Temp]
                        self.CAN_TP_Tx_Status = CanTpState.IDLE
                        self.CAN_TP_Multi_Fram_Inedex = 0
                        self.CAN_TP_Wait_Flow_Control_count = 0
                        CAN_If.CAN_Device.can_write(pdu_data, self.CAN_TP_Tx_Data_Id_Temp, 8)
                        print("Multi frame send end\n")
                        self.Canif_Tp_Tx_over = 1
                    else:
                        pdu_data[0] = 0x20|(self.CAN_TP_Multi_Fram_Inedex%16)
                        pdu_data[1:8] = self.CAN_TP_Tx_Data_Temp[0:7]
                        self.CAN_TP_Tx_Data_Temp = self.CAN_TP_Tx_Data_Temp[7:]
                        self.CAN_TP_Tx_Data_len_Temp -= 7
                        self.CAN_TP_Multi_Fram_Inedex += 1

                        self.CAN_TP_Tx_Status = CanTpState.SEND_CONSECUTIVE_FRAME
                        CAN_If.CAN_Device.can_write(pdu_data, self.CAN_TP_Tx_Data_Id_Temp, 8)
                        #print("continuous frame:{0}\n".format(self.CAN_TP_Multi_Fram_Inedex))
                    
                    if (self.CAN_TP_Num_of_Bock_Size != 0) and ((self.CAN_TP_Wait_Flow_Control_count)%(self.CAN_TP_Num_of_Bock_Size) == 0) and (self.CAN_TP_Wait_Flow_Control_count != 0):
                        self.CAN_TP_Wait_Flow_Control_count = 0
                        self.CAN_TP_Wait_Flow_Control_Flag = 1
                    else:
                        pass
                    self.CAN_TP_Wait_Flow_Control_count+=1
                else:
                    pass
        elif self.CAN_TP_Tx_Status == CanTpState.WAIT_FLOW_CONTROL:
            #time out ?
            print("Tx MultiFram wait for flow control:{0}\r\n".format(self.CAN_TP_Tx_Status))
            pass
        else:
            pass
    def Tp_Transmit(self,data,Fun_Phy):
        self.tptxdata = copy.deepcopy(data)
        self.CAN_TP_Tx_Data.append(self.tptxdata)
        self.CAN_TP_Tx_Data_Id.append(Fun_Phy)
        #print("Tp Transmit:{0} len:{1} ID:{2} Len:{3}".format(self.CAN_TP_Tx_Data,len(self.CAN_TP_Tx_Data[0]),self.CAN_TP_Tx_Data_Id,len(self.CAN_TP_Tx_Data_Id)))
    def CanIf_Indication_To_Dcm(self):
        if self.CanIf_Receive_Flag == 1:
            #print("flag:{0} data;{1}".format(self.CanIf_Receive_Flag,self.CAN_To_DCM_Data))
            ret = copy.deepcopy(self.CAN_To_DCM_Data.pop(0))
            #print("ret:{0}".format(ret))
            return (self.CanIf_Receive_Flag,ret)
        
        else:
            return (0,0)
    def CanIf_Clear_Indica_To_Dcm_Flag(self):
        #print("flagaa:{0} dataaa:{1}".format(self.CanIf_Receive_Flag,self.CAN_To_DCM_Data))
        if len(self.CAN_To_DCM_Data) == 0:
            self.CanIf_Receive_Flag = 0
        else:
            self.CanIf_Receive_Flag = 1
        #self.CAN_TP_Rx_Data.clear()
    def CanIf_Tx_Over_To_DCM(self):
        return self.Canif_Tp_Tx_over
    def CanIf_Tx_Flag_Clear(self):
        self.Canif_Tp_Tx_over = 0
    def terminate(self):
        self.Tp_running = False
