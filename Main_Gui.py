#!/usr/bin/python
#coding=utf-8
#junfeng.luan 2019.07.20
from tkinter import *
from tkinter import messagebox
import threading
from tkinter.filedialog import askopenfilename
from tkinter import scrolledtext
from tkinter import ttk
from CAN_If import CAN_Device
from Hex_File_analyze import Hex_File_analyze
import os
import time
import UDS
import File_data
# import ISO15765_Tp

class Uds_Gui(threading.Thread):
    def __init__(self):
        #super(Uds_Gui,self).__init__()#Thread.__init__()
        super().__init__()
        self.PHY_ID = "732"
        self.FUN_ID = "7DF"
        self.RES_ID = "7B2"
        self.return_value={0:'success',1:'error'}
        self.show_file_type = {0:"驱动文件信息",1:"应用文件信息",2:"标定文件信息"}
        self.device={"USB-CAN-E":3,"USB-CAN-2E":4,"Vector Can":22,"Visual Bus":23}
        self.baud={"500k":0x060007,"250k":0x1C0008,"125k":0x1C0011}
        self.device_handle = 'USB-CAN-E'
        self.baud_value = 0x060007
        self.root = Tk()
        self.root.title("Simple FBL Demo")
        self.root.geometry("986x650")
        self.root.resizable(False,False)
        #self.root.attributes('-alpha',0.9)
        self.hirain_pic = r"./favicon.ico"
        self.root.iconbitmap(self.hirain_pic)
        self.imgpath = r".\back_pic.png"
        self.test_ptoto = PhotoImage(file=self.imgpath)
        self.canvas = Canvas(self.root,width=986,height=650,bd=0)
        self.canvas.create_image(493,325,image = self.test_ptoto)
        self.canvas.pack()

        self.Gui_running = True
        self.my_UDS = UDS.Uds()
        self.my_UDS.daemon = True
        self.my_UDS.start()
        
        File_data.PHY_ID = int(self.PHY_ID,16)
        File_data.FUN_ID = int(self.FUN_ID,16)
        File_data.RES_ID = int(self.RES_ID,16)

        self.First_start_flag = 0;

        self.PHY_ID_Var = StringVar()
        self.FUN_ID_Var = StringVar()
        self.RES_ID_Var = StringVar()
        self.PHY_ID_Var.set(self.PHY_ID)
        self.FUN_ID_Var.set(self.FUN_ID)
        self.RES_ID_Var.set(self.RES_ID)
        
        self.Entry_Phy_Var = Entry(self.root,textvariable=self.PHY_ID_Var,width=5,font=('Verdana',12))
        self.Entry_Phy_Var.pack()
        self.Entry_Phy_Var.bind('<FocusOut>', self.get_Phy_ID)
        self.Phy_Label = Label(self.root,text="物理 ID:0x",font=('Arial',12))
        self.Phy_Label.pack()
        
        self.Entry_Fun_Var = Entry(self.root,textvariable=self.FUN_ID_Var,width=5,font=('Verdana',12))
        self.Entry_Fun_Var.pack()
        self.Entry_Fun_Var.bind('<FocusOut>', self.get_Fun_ID)
        self.Fun_Label = Label(self.root,text="功能 ID:0x",font=('Arial',12))
        self.Fun_Label.pack()
        
        self.Entry_Res_Var = Entry(self.root,textvariable=self.RES_ID_Var,width=5,font=('Verdana',12))
        self.Entry_Res_Var.pack()
        self.Entry_Res_Var.bind('<FocusOut>', self.get_Res_ID)
        self.Res_Label = Label(self.root,text="应答 ID:0x",font=('Arial',12))
        self.Res_Label.pack()
        
        self.Driver_file_path = StringVar()
        self.text_driver = Text(self.root,font=('verdana',12),width=50,height=1)
        self.text_driver.config(state=DISABLED)
        self.text_driver.pack()
        self.Driver_file_Label = Label(self.root,text='驱动文件',font=('Arial',12),background='yellow')
        self.Driver_file_Label.pack()
        self.Button_Driver = Button(self.root,text='../..',command=self.select_driver_file)
        self.Button_Driver.pack()
        
        self.APP_file_path = StringVar()
        self.text_app = Text(self.root,font=('verdana',12),width=50,height=1)
        self.text_app.config(state=DISABLED)
        self.text_app.pack()
        self.APP_file_Label = Label(self.root,text='应用文件',font=('Arial',12),background='yellow')
        self.APP_file_Label.pack()
        self.Button_APP = Button(self.root,text='../..',command=self.select_app_file)
        self.Button_APP.pack()
        
        self.CAL_file_path = StringVar()
        self.text_cal = Text(self.root,font=('verdana',12),width=50,height=1)
        self.text_cal.config(state=DISABLED)
        self.text_cal.pack()
        self.CAL_file_Label = Label(self.root,text='标定文件',font=('Arial',12),background='yellow')
        self.CAL_file_Label.pack()
        self.Button_CAL = Button(self.root,text='../..',command=self.select_cal_file)
        self.Button_CAL.pack()
        
        self.text_log = scrolledtext.ScrolledText(self.root,wrap=WORD,font=('Consolas',10))
        self.text_log.tag_config("Red_error", foreground="red")
        self.text_log.tag_config("Green_pass",foreground="green")
        self.text_log.tag_config("Warning",foreground="blue")
        self.text_log.tag_config("default",foreground="black")
        self.text_log.bind('<<Modified>>',self.modified)
        ##self.text_log.config(state=DISABLED)
        self.text_log.pack()
        
        self.Open_Device_button = Button(self.root,text="打开设备",command=self.open_device_function)
        self.Open_Device_button.pack()
        
        self.Close_Device_button = Button(self.root,text="关闭设备",command=self.close_device_function)
        self.Close_Device_button.config(state=DISABLED)
        self.Close_Device_button.pack()
        
        self.Start_button = Button(self.root,text="Start",command=self.start_button_fun)
        self.Start_button.config(state=DISABLED)
        self.Start_button.pack()
        

        self.Send_Data_button = Button(self.root,text="发送TP数据",command=self.send_data_function)
        self.Send_Data_button.config(state=DISABLED)
        self.Send_Data_button.pack()

        self.device_select_label=Label(self.root,text="设备",font=('Arial',12))
        self.device_select_label.pack()
        self.device_select_list = ttk.Combobox(self.root,values=tuple(self.device.keys()),width=50)
        self.device_select_list.set('USB-CAN-E')
        self.device_select_list.pack()
        self.device_select_list.bind('<<ComboboxSelected>>',self.get_device)
        
        self.baud_set_label = Label(self.root,text='速率',font=('Arial',12))
        self.baud_set_label.pack()
        self.baud_set_list = ttk.Combobox(self.root,values=tuple(self.baud.keys()),width=50)
        self.baud_set_list.set('500k')
        self.baud_set_list.pack()
        self.baud_set_list.bind('<<ComboboxSelected>>',self.get_baud)
        
        self.Clear_button = Button(self.root,text="Clear log",background="lightblue",command=self.Clear_function)
        self.Clear_button.pack()
        
        self.send_data_path = StringVar()
        self.text_send_data = Text(self.root,font=('verdana',12),width=50,height=1)
        #self.text_send_data.config(state=DISABLED)
        self.text_send_data.pack()

        self.Processbar_var = ttk.Progressbar(self.root,length=700)
        self.Processbar_var.pack()
        
        self.canvas.create_window(70,110,width = 100,height = 30,window = self.Phy_Label)
        self.canvas.create_window(220,110,width = 180,height = 30,window = self.Entry_Phy_Var)
        self.canvas.create_window(400,110,width = 100,height = 30,window = self.Fun_Label)
        self.canvas.create_window(550,110,width = 180,height = 30,window = self.Entry_Fun_Var)
        self.canvas.create_window(730,110,width = 100,height = 30,window = self.Res_Label)
        self.canvas.create_window(880,110,width = 180,height = 30,window = self.Entry_Res_Var)
        
        self.canvas.create_window(70,150,width = 80,height = 30,window = self.Driver_file_Label)
        self.canvas.create_window(470,150,width = 700,height = 30,window = self.text_driver)
        self.canvas.create_window(850,150,width = 40,height = 30,window = self.Button_Driver)
        
        self.canvas.create_window(70,190,width = 80,height = 30,window = self.APP_file_Label)
        self.canvas.create_window(470,190,width = 700,height = 30,window = self.text_app)
        self.canvas.create_window(850,190,width = 40,height = 30,window = self.Button_APP)
        
        self.canvas.create_window(70,230,width = 80,height = 30,window = self.CAL_file_Label)
        self.canvas.create_window(470,230,width = 700,height = 30,window = self.text_cal)
        self.canvas.create_window(850,230,width = 40,height = 30,window = self.Button_CAL)
        
        self.canvas.create_window(440,420,width = 700,height = 330,window = self.text_log)
        
        self.canvas.create_window(890,320,width = 100,height = 30,window = self.Open_Device_button)
        self.canvas.create_window(890,360,width = 100,height = 30,window = self.Close_Device_button)
        self.canvas.create_window(890,400,width = 100,height = 30,window = self.Start_button)
        
        self.canvas.create_window(840,440,width = 40,height = 30,window = self.device_select_label)
        self.canvas.create_window(920,440,width = 100,height = 30,window = self.device_select_list)
        
        self.canvas.create_window(840,480,width = 40,height = 30,window = self.baud_set_label)
        self.canvas.create_window(920,480,width = 100,height = 30,window = self.baud_set_list)
        
        self.canvas.create_window(890,520,width = 100,height = 30,window = self.Clear_button)
        
        self.canvas.create_window(440,600,width = 700,height = 20,window = self.Processbar_var)

        self.canvas.create_window(860,630,width = 100,height = 20,window = self.Send_Data_button)

        self.canvas.create_window(440,630,width = 700,height = 20,window = self.text_send_data)
        #self.root.wm_attributes('-transparentcolor','white') 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_device(self,event):
        self.device_handle = self.device_select_list.get()
        if(self.device_handle):
            self.device_value = self.device[self.device_handle]
            self.log_output("选择设备:"+str(self.device_handle))
        else:
            self.device_select_list.set('USB-CAN-E')
    def get_baud(self,event):
        self.baud_handle = self.baud_set_list.get()
        if(self.baud_handle):
            self.baud_value = self.baud[self.baud_handle]
            self.log_output('设置波特率:'+str(self.baud_handle))
        else:
            self.baud_set_list.set('500k')
    def get_Phy_ID(self,event):
        self.PHY_ID=self.Entry_Phy_Var.get()
        self.log_output('设置物理  ID 0x:'+ self.PHY_ID)
        File_data.PHY_ID = int(self.PHY_ID,16)
    def get_Fun_ID(self,event):
        self.FUN_ID=self.Entry_Fun_Var.get()
        self.log_output('设置功能 ID 0x:'+ self.FUN_ID)
        File_data.FUN_ID = int(self.FUN_ID,16)
    def get_Res_ID(self,event):
        self.RES_ID=self.Entry_Res_Var.get()
        self.log_output('设置应答 ID 0x:'+ self.RES_ID)
        File_data.RES_ID = int(self.RES_ID,16)
    def select_driver_file(self):
        self.text_driver.config(state = NORMAL)
        self.driver_file_handle = askopenfilename()
        self.text_driver.delete(1.0,END)
        self.text_driver.insert(INSERT, self.driver_file_handle)
        self.text_driver.config(state = DISABLED)
        self.show_file_info(0,self.driver_file_handle)
    def select_app_file(self):
        self.text_app.config(state = NORMAL)
        self.app_file_handle = askopenfilename()
        self.text_app.delete(1.0,END)
        self.text_app.insert(INSERT, self.app_file_handle)
        self.text_app.config(state = DISABLED)
        self.show_file_info(1,self.app_file_handle)
    def select_cal_file(self):
        self.text_cal.config(state = NORMAL)
        self.cal_file_handle = askopenfilename()
        self.text_cal.delete(1.0,END)
        self.text_cal.insert(INSERT, self.cal_file_handle)
        self.text_cal.config(state = DISABLED)
        self.show_file_info(2,self.cal_file_handle)
    def modified(self,event):
        pass
    
    def open_device_function(self):
        CAN_Device.select_device(self.device_handle)
        ret = CAN_Device.can_init(self.device[self.device_handle], self.baud_value)
        self.log_output('Device open '+self.return_value[ret])
        if ret==0:
            self.Start_button.config(state = NORMAL)
            self.Close_Device_button.config(state=NORMAL)
            self.Send_Data_button.config(state=NORMAL)
            self.device_select_list.config(state = DISABLED)
            self.baud_set_list.config(state = DISABLED)
    def close_device_function(self):
        self.my_UDS.reset()
        self.log_output("Device close "+self.return_value[CAN_Device.can_close()])
        self.Start_button.config(state = DISABLED)
        self.Close_Device_button.config(state=DISABLED)
        self.device_select_list.config(state = NORMAL)
        self.baud_set_list.config(state = NORMAL)
    def start_button_fun(self):
        File_data.File_Send_Size=0

#         self.log_output('start warning')
        if self.First_start_flag == 0:
            self.First_start_flag = 1
        else:
            File_data.File_Total_Size = 0
            try:
                self.driver_file_handle
            except :
                pass
            else:
                self.show_file_info(0,self.driver_file_handle)
            try:
                self.app_file_handle
            except :
                pass
            else:
                self.show_file_info(1,self.app_file_handle)
            try:
                self.cal_file_handle
            except :
                pass
            else:
                self.show_file_info(2,self.cal_file_handle)
        ret = self.my_UDS.Set_Uds_Tester_Step(UDS.Uds_Tester_Step.UDS_STEP_EXT_SESSION)
        self.log_output('start '+self.return_value[ret])
    def Clear_function(self):
        self.text_log.config(state=NORMAL)
        self.text_log.delete(1.0,END)
#         self.text_log.config(state=DISABLED)
    def log_output(self,str_info):
        #self.text_log.config(state=NORMAL)
        if 'error' in str_info:
            self.text_log.insert(END,str_info+'\n','Red_error')
        elif 'success' in str_info:
            self.text_log.insert(END,str_info+'\n','Green_pass')
        elif 'warning' in str_info:
            self.text_log.insert(END,str_info+'\n','Warning')
        elif 'RX' in str_info:
            self.text_log.insert(END,str_info+'\n','Warning')
        else:
            self.text_log.insert(END,str_info+'\n','default')
        #self.text_log.see(END)
        #self.text_log.config(state = DISABLED)
    def send_data_function(self):
        contents = self.text_send_data.get(1.0, "end")
        print("read data:{0}\r\n".format(list(map(hex,list(bytes.fromhex(contents))))))
        self.my_UDS.UDS_Send_Data(list(bytes.fromhex(contents)))
        
        pass
    def run(self):

        process_update_var_new = 0
        process_update_var_old = 0
        count = 0
        while self.Gui_running:
            time.sleep(0.001)
            if len(File_data.Log_Info) != 0:
                log = File_data.Log_Info.pop(0)
                self.log_output(" ".join(log))
                count += 1
                if count > 1000:
                    count = 0
                    self.text_log.see(END)
            else:
                pass
            if File_data.File_Total_Size != 0:
                process_update_var_new = (round(File_data.File_Send_Size*100/File_data.File_Total_Size,1))
            else:
                pass

            if process_update_var_new != process_update_var_old:
                print("process:{0}".format(process_update_var_new))
                process_update_var_old = process_update_var_new
                self.Processbar_var.config(value = process_update_var_new)#进度条
                self.Processbar_var.update()
            else:
                pass
             
    def show_file_info(self,file_type,file_handle):
        total_size= 0
        
        file_Exname = os.path.splitext(file_handle)[-1]
        if file_Exname == '.hex' or file_Exname == '.HEX':
            file_process = Hex_File_analyze()
        else:
            r = messagebox.showerror('消息类型','暂不支持的文件类型:{0}'.format(file_Exname))
            print("不支持的文件类型{0}\r\n".format(r))
            return
        self.text_log.config(state = NORMAL)
        self.text_log.insert(END,self.show_file_type[file_type]+':\r\n',"Green_pass")
        self.text_log.insert(END,"文件名称：{0}\r\n".format(os.path.basename(file_handle)))
        t = os.path.getmtime(file_handle)
        self.text_log.insert(END,"修改时间：{0}\r\n".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t))),'Red_error')
        file_info = file_process.file_analyze(file_type, file_handle)
        for i in range(len(file_info[0])):
            self.text_log.insert(END,"block start:{0}  block end:{1}  size:{2}\r\n".format(hex(file_info[0][i]),hex(file_info[1][i]),file_info[1][i]-file_info[0][i]+1))
            total_size += file_info[1][i]-file_info[0][i]+1
        self.text_log.insert(END,"文件总大小：{0}(bytes) 约:{1}Kb \r\n".format(total_size,round(total_size/1024,2)))
        self.text_log.insert(END,"文件CRC：{0}\r\n".format(hex(file_info[3])))
        self.text_log.see(END)
        #self.text_log.config(state = DISABLED)
    def on_closing(self):
        self.Gui_running = False
        self.root.destroy()
        print("root destory\n")
        self.my_UDS.terminate()
        print("Uds terminate\n")
        my_gui.join(timeout = 1)
        print("gui join\n")
        
if __name__=="__main__":
    
    my_gui = Uds_Gui()
    my_gui.daemon = True
    my_gui.start()
    
    my_gui.root.mainloop()
    
    
