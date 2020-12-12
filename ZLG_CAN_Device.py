#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.07.20
import ctypes
import platform
from _overlapped import NULL
from _ctypes import Structure, byref
from ctypes import c_ulong, c_ubyte, c_uint, c_ushort ,c_char
import File_data

#1.ZLGCAN系列接口卡信息的数据类型
class VCI_BOARD_INFO(Structure):
    _fields_ = [
        ("hw_Version",c_ushort),
        ("fw_Version",c_ushort),
        ("dr_Version",c_ushort),
        ("in_Version",c_ushort),
        ("irq_Num",c_ushort),
        ("can_Num",c_ubyte),
        ("str_Serial_Num",c_char * 20),
        ("str_hw_Type",c_char * 40),
        ("Reserved",c_ushort * 4)
        ]

#2.定义CAN信息帧的数据类型
class VCI_CAN_OBJ(Structure):
    _fields_ = [
        ("Id",c_uint),
        ("TimeStamp",c_uint),
        ("TimeFlag",c_ubyte),
        ("SendType",c_ubyte),
        ("RemoteFlag",c_ubyte),#是否是远程帧
        ("EcternFlag",c_ubyte),#是否是扩展帧
        ("DataLen",c_ubyte),
        ("Data",c_ubyte * 8),
        ("Reserved",c_ubyte * 3)#Reserved[0] 第0位表示特殊的空行或者高亮帧
        ]

#5.定义初始化CAN的数据类型
class VCI_INIT_CONFIG(Structure):
    _fields_ = [
        ("AccCode",c_ulong),
        ("AccMaxk",c_ulong),
        ("Reserved",c_ulong),
        ("Fiter",c_ubyte),
        ("Timing0",c_ubyte),
        ("Timing1",c_ubyte),
        ("Mode",c_ubyte)
        ]

#new add struct for filter
class VCI_FILTER_RECORD(Structure):
    _fields_ = [
        ("ExtFrame",c_ulong),
        ("Start",c_ulong),
        ("End",c_ulong)
        ]


class ZLG_Device():
    def __init__(self):
        self.Python_Info = platform.architecture()
        print(self.Python_Info)
        if(self.Python_Info[0] == '64bit'):
            self.DLL_PATH = r".\ZLG_Dll_64\ControlCAN.dll"
        else:
            self.DLL_PATH = r".\ZLG_Dll_32\ControlCAN.dll"
        print(self.DLL_PATH)   
        self.ZLG_USB_CAN_Dll = ctypes.windll.LoadLibrary(self.DLL_PATH)
        self.ZLGDeviceHandle = 0
        self.Open_Device_Handle=0
        self.Tx_conf = 0
    def Open_Device(self,ZLG_Device_Handle):
        
        self.ZLGDeviceHandle = ZLG_Device_Handle
        print("ZLG CAN Handle:{0}".format(ZLG_Device_Handle))
        self.Open_Device_Handle = self.ZLG_USB_CAN_Dll.OpenDevice(self.ZLGDeviceHandle,0,0)
        if(self.Open_Device_Handle == 0):
            print('Device open failed\r\n')
            self.open_device_state = 1
        else:
            print("Device open success\r\n")
            self.open_device_state = 0
        return self.open_device_state
    def Close_Device(self):
        self.CloseDevice = self.ZLG_USB_CAN_Dll.CloseDevice(self.Open_Device_Handle,0)
        if(self.CloseDevice == 1):
            print("Device Close Success!\r\n")
            self.close_device_state = 0
        else:
            print("Device Close Error\r\n")
            self.close_device_state = 1
        return self.close_device_state
    def Init_Can(self,ZLG_Baud,Device_handle):
        self.Baud = ZLG_Baud
        self.ZLGDeviceHandle = Device_handle
        print("ZLG baud:{0}".format(hex(self.Baud)))
        print("ZLG device handle:{0}".format(self.ZLGDeviceHandle))
        ZLG_USB_CAN_Info = VCI_BOARD_INFO()
        ZLG_USB_CAN_Info_P = byref(ZLG_USB_CAN_Info)
        self.ZLG_USB_CAN_Dll.ReadBoardInfo(self.ZLGDeviceHandle,0,ZLG_USB_CAN_Info_P)#read info
        print("HW:%#x\n"%ZLG_USB_CAN_Info.hw_Version)
        print("FW:%#x\n"%ZLG_USB_CAN_Info.fw_Version)
        print("DR:%#x\n"%ZLG_USB_CAN_Info.dr_Version)
        print("IN:%#x\n"%ZLG_USB_CAN_Info.in_Version)
        print("IRQ:%#d\n"%ZLG_USB_CAN_Info.irq_Num)
        print("CAN_NUM:%#d\n"%ZLG_USB_CAN_Info.can_Num)
        print("STR_serial:%s\n"%ZLG_USB_CAN_Info.str_Serial_Num)
        print("Str_Hw_NUM:%s\n"%ZLG_USB_CAN_Info.str_hw_Type)
        ZLG_USB_CAN_INIT = VCI_INIT_CONFIG()
        ZLG_USB_CAN_INIT.AccCode = 0x00000000
        ZLG_USB_CAN_INIT.AccMaxk = 0x00FFFFFF
        ZLG_USB_CAN_INIT.Mode = 0
        ZLG_USB_CAN_INIT.Fiter = 1
        ZLG_USB_CAN_INIT.Timing0=0
        ZLG_USB_CAN_INIT.Timing1=0x1c
        ZLG_USB_CAN_INIT_P = byref(ZLG_USB_CAN_INIT)
        print(ZLG_USB_CAN_INIT.Mode)
        print(type(self.Baud))
        baud_value = ctypes.c_int32(self.Baud)
        print("ZLG baud value:{0}".format((baud_value)))
        set_can_reference = self.ZLG_USB_CAN_Dll.SetReference(self.ZLGDeviceHandle,0,0,0,ctypes.byref(baud_value))
        if(set_can_reference == 1):
            print("can set reference ok\r\n")
            init_can = self.ZLG_USB_CAN_Dll.InitCAN(self.ZLGDeviceHandle,0,0,ZLG_USB_CAN_INIT_P)#init can
            if(init_can == 1):
                self.set_can_state = 0
                print("CAN init success\r\n")
                ZLG_USB_CAN_FILTER = VCI_FILTER_RECORD()
                if File_data.RES_ID & 0xFFFFF000 != 0:#扩展帧
                    ZLG_USB_CAN_FILTER.ExtFrame = 1
                else:
                    ZLG_USB_CAN_FILTER.ExtFrame = 0
                ZLG_USB_CAN_FILTER.Start = File_data.RES_ID
                ZLG_USB_CAN_FILTER.End = File_data.RES_ID
                ZLG_USB_CAN_FILTER_P = byref(ZLG_USB_CAN_FILTER)
                set_fielter = self.ZLG_USB_CAN_Dll.SetReference(self.ZLGDeviceHandle,0,0,1,ZLG_USB_CAN_FILTER_P)
                if set_fielter == 1:
                    print("set fielter success:{0}".format(File_data.RES_ID))
                else:
                    pass
            else:
                print("CAN init error\r\n")
                self.set_can_state = 1
        else:
            print("can set reference error\r\n")
            self.set_can_state = 1
        return self.set_can_state
    def Start_Can(self):
        clear_buffer = self.ZLG_USB_CAN_Dll.ClearBuffer(self.ZLGDeviceHandle,0,0)
        if(clear_buffer == 1):
            self.can_start_state = 0
            print('clear buffer ok\r\n')
            init_can = self.ZLG_USB_CAN_Dll.StartCAN(self.ZLGDeviceHandle,0,0)
            if(init_can == 1):
                print('can start ok\r\n')
                self.can_start_state = 0
            else:
                self.can_start_state = 1
        else:
            self.can_start_state = 1
            print('clear buffer error\r\n')
        return self.can_start_state
    def Reset_Can(self):
        pass
    def Transmit(self,tx_data,tx_id,tx_len):
        VCI_CAN_OBJ_Info = VCI_CAN_OBJ()
        VCI_CAN_OBJ_Info.TimeStamp = 0
        VCI_CAN_OBJ_Info.TimeFlag = 0
        VCI_CAN_OBJ_Info.SendType = 0
        VCI_CAN_OBJ_Info.RemoteFlag = 0
        if tx_id & 0xFFFFF000 != 0:
            VCI_CAN_OBJ_Info.ExternFlag = 1
        else:
            VCI_CAN_OBJ_Info.ExternFlag = 0
        VCI_CAN_OBJ_Info.DataLen = tx_len
        VCI_CAN_OBJ_Info.Id = tx_id
        VCI_CAN_OBJ_Info.Data = tuple(tx_data[0:8])
        VCI_CAN_OBJ_Info_P = byref(VCI_CAN_OBJ_Info)
        self.ZLG_USB_CAN_Dll.Transmit(self.ZLGDeviceHandle,0,0,VCI_CAN_OBJ_Info_P,1)
        self.Tx_conf = 1
        #print("TX:{0} {1}".format(hex(tx_id),tx_data[0:8]))
    def Receive_data(self):
        return_data = []
        return_len = 0
        VCI_CAN_OBJ_Info = VCI_CAN_OBJ()
        VCI_CAN_OBJ_Info.TimeStamp = 0
        VCI_CAN_OBJ_Info.TimeFlag = 0
        VCI_CAN_OBJ_Info.SendType = 0
        VCI_CAN_OBJ_Info.RemoteFlag = 0
        VCI_CAN_OBJ_Info.ExternFlag = 0
        VCI_CAN_OBJ_Info.DataLen = 0
        VCI_CAN_OBJ_Info_P = byref(VCI_CAN_OBJ_Info)
        self.receive_frame_num = self.ZLG_USB_CAN_Dll.GetReceiveNum(self.ZLGDeviceHandle,0,0)
        if(self.receive_frame_num != 0):
            ret_data = self.ZLG_USB_CAN_Dll.Receive(self.ZLGDeviceHandle,0,0,VCI_CAN_OBJ_Info_P,1,0)
            if ret_data != 0xFFFFFFFF:
                self.Tx_conf = 0
                return_len = VCI_CAN_OBJ_Info.DataLen
                return_ID = VCI_CAN_OBJ_Info.Id
                
                #if return_ID == 0x72e:
                
                for i in (range(0,return_len)):
                    return_data.append(VCI_CAN_OBJ_Info.Data[i])
                #print("receive ID:{0}".format(list(map(hex,return_data))))
            else:
                return_ID = None
        else:
            return_ID = None
        return (return_ID,return_len,return_data)
    def Error_Info(self):
        pass
    def Tx_confirm(self):
        return self.Tx_conf
