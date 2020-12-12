#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.07.27

from ZLG_CAN_Device import ZLG_Device
from Vector_CAN_Device import Vector_Device
from Visual_CAN_Device import Visual_Device
import File_data
import copy
import datetime

class Device_can_if():
    def __init__(self):
        self.Can_Dev = Visual_Device()
        pass
    def select_device(self,device):
        if 'USB-CAN' in device:
            self.Can_Dev = ZLG_Device()
            print('zlg can')
        elif 'Vector'in device:
            self.Can_Dev = Vector_Device()
        else:
            self.Can_Dev = Visual_Device()
            print('Visual can')
    def can_init(self,device_handle,baud):
            print("CAN_IF Device Handle:{0}".format(device_handle))
            ret_value = self.Can_Dev.Open_Device(device_handle)
            if ret_value == 0:
                ret_value = self.Can_Dev.Init_Can(baud,device_handle)
                if ret_value == 0:
                    ret_value = self.Can_Dev.Start_Can()
                    if ret_value == 0:
                        return_state = 0
                    else:
                        return_state = 1
                else:
                    return_state = 1
            else:
                return_state = 1
            return return_state
    def can_write(self,wwdata,ID,Len):
        rr_data = []
        r = []
        self.Can_Dev.Transmit(wwdata,ID,8)
        rr_data = copy.deepcopy(wwdata)
        c = list(map(hex,rr_data))
        #d = list(map(str,c))
        e = list(map(str.upper,c))
        for i in range(0,len(e)):
            if len(e[i]) == 3:
                e[i] = e[i].replace("0X","0x0")
            else:
                e[i] = e[i].replace("0X","0x")
        f=" ".join(e)
        #print("e:{0}\nd:{1}".format(e,d))
        r.insert(4,f)
        r.insert(0,"TX:")
        r.insert(1,hex(ID))
        r.insert(2,str(datetime.datetime.now()))
        r.insert(3,"#  ")
        File_data.Log_Info.append(r)
    def can_read(self):
        receive_data = self.Can_Dev.Receive_data()
        if receive_data[0] == File_data.RES_ID :
            tt_data = []
            d = []
            tt_data = copy.deepcopy(receive_data[2])
            #d=list(map(hex,tt_data))
            
            m = list(map(hex,tt_data))
            
            n = list(map(str.upper,m))

            for i in range(0,len(n)):
                if len(n[i]) == 3:
                    n[i] = n[i].replace("0X","0x0")
                else:
                    n[i] = n[i].replace("0X","0x")
            o=" ".join(n)
            
            d.insert(4,o)
            
            d.insert(0,"RX:")
            d.insert(1,hex(receive_data[0]))
            d.insert(2,str(datetime.datetime.now()))
            d.insert(3,"#  ")
            File_data.Log_Info.append(d)
        else:
            if receive_data[0] != None:
                print("Receive:{0}\n".format(receive_data[0]))
        return receive_data
    def can_close(self):
        return self.Can_Dev.Close_Device()
    def can_Tx_confirmation(self):
        self.Can_Dev.Tx_confirm()
CAN_Device = Device_can_if()
