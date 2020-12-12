#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.07.25
import File_data
import copy
import time,datetime
class Visual_Device():
    def __init__(self):
        self.tx_data = []
        self.rx_data_flag = 0
        self.rx_data = []
        self.flow_control = 0
        self.flow_control_count = 0
        self.UDS_Service = 0
        self.UDS_Service_index = 0
        self.Rx_Continuous_Frame_total_length = 0
        self.Rx_Continuous_Frame_count_length = 0
        self.flow_control_data = [0x30,0x08,0x00,0x00,0x00,0x00,0x00,0x00]
        self.Tx_conf = 0
    def Open_Device(self,Visual_Device_Handle):
        return 0
    def Close_Device(self):
        return 0
    def Init_Can(self,Visual_Baud,Device_handle):
        return 0
    def Start_Can(self):
        return 0
    def Reset_Can(self):
        return 0
    def Transmit(self,tx_data,tx_id,tx_len):
        self.tx_data = copy.deepcopy(tx_data)
        self.rx_data = [0x30,0x08,0x00,0x00,0x00,0x00,0x00,0x00]
        #print("ID:{0} Len:{1} Data:{2}".format(tx_id,tx_len,tx_data))
        #print("ID:{0} TX data:{1}".format(hex(tx_id),tx_data))
        #temp_data = copy.deepcopy(tx_data)
        #print("can if txata:{0}".format(temp_data))
        #c=copy.deepcopy(list(map(hex,temp_data)))
        #c.insert(0,"TX:")
        #c.insert(1,hex(tx_id))
        #c.insert(2,str(datetime.datetime.now()))
        #File_data.Log_Info.append(c)
        if len(self.tx_data)!=0:
            frame_type = (self.tx_data[0]&0xF0) >> 4
            self.Tx_conf = 1
        else:
            pass
        if frame_type == 0:#receive single frame
            self.rx_data = self.tx_data
            self.rx_data[1] += 0x40
            print("Visual Can receive single frame\n")
            self.rx_data_flag = 1
            
        elif frame_type == 1:#receive first frame
            self.rx_data = [0x30,0x08,0x00,0x00,0x00,0x00,0x00,0x00]
            self.UDS_Service = self.tx_data[2]
            self.UDS_Service_index = self.tx_data[3]
            #print("self.UDS_Service:{0} {1}\n".format(self.UDS_Service,self.tx_data[1]))
            self.Rx_Continuous_Frame_total_length = (self.tx_data[0]&0x0F)*256+self.tx_data[1]
            self.Rx_Continuous_Frame_count_length += 6
            #print("self.UDS_Service:{0} Frame length:{1} now:{2}\n".format(hex(self.UDS_Service),self.Rx_Continuous_Frame_total_length,self.Rx_Continuous_Frame_count_length))
            print("Visual Can receive First frame\n")
            self.flow_control = 1
            self.rx_data_flag = 0
        elif frame_type == 2:#continuous frame
            self.flow_control = 0
            self.rx_data_flag = 0
            self.flow_control_count += 1
            self.Rx_Continuous_Frame_count_length += 7
            if self.Rx_Continuous_Frame_count_length >= self.Rx_Continuous_Frame_total_length:#continuous receive over
                self.Rx_Continuous_Frame_count_length = 0
                #self.tx_data.clear()
                #print("self.UDS_Service:{0} \n".format(hex(self.UDS_Service)))
                if self.UDS_Service == 0x34:
                    self.rx_data[0] = 0x4
                    self.rx_data[1] = 0x74
                    self.rx_data[2] = 0x20
                    self.rx_data[3] = 0x04
                    self.rx_data[4] = 0x02
                elif self.UDS_Service == 0x36:
                    self.rx_data[0] = 0x2
                    self.rx_data[1] = 0x76
                    self.rx_data[2] = self.UDS_Service_index
                elif self.UDS_Service == 0x2E:
                    self.rx_data[0] = 0x3
                    self.rx_data[1] = 0x6E
                    self.rx_data[2] = 0xF1
                    self.rx_data[3] = 0x84
                elif self.UDS_Service == 0x31:
                    self.rx_data[0] = 0x5
                    self.rx_data[1] = 0x71
                    self.rx_data[2] = 0xF1
                    self.rx_data[3] = 0x84
                else:
                    pass
                self.flow_control_count = 0
                print("Visual Can receive continuous frame over:{0}\n".format(self.rx_data))
                self.rx_data_flag = 1
            else:
                if self.flow_control_count >= 8:
                    self.flow_control_count = 0
                    self.flow_control =1
                    self.rx_data = [0x30,0x08,0x00,0x00,0x00,0x00,0x00,0x00]
                #print("Visual Can receive continuous frame:{0}".format(self.flow_control_count))
        else:
            pass
        
    def Receive_data(self):
#         print("flow:{0} flag:{1} ".format(self.flow_control,self.rx_data_flag))
        #time.sleep(0.002)
        if self.flow_control == 1 or self.rx_data_flag == 1:
            self.Tx_conf = 0
            self.flow_control = 0
            #return (File_data.RES_ID,8,self.flow_control_data)
        #elif self.rx_data_flag == 1: 
            self.rx_data_flag = 0
            
            return (File_data.RES_ID,8,self.rx_data)
        else:
            return (None,0,[0,0])
    def Error_Info(self):
        pass
    def Tx_confirm(self):
        return self.Tx_conf