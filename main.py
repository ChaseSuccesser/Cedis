#coding=utf-8
from redis_util import RedisUtil
from conf.redis_conf import RedisConf
import tkinter as tk
import tkinter.messagebox
import os
import json
__author__ = 'lgx'


class Main(object):

    def __init__(self):
        pass

    def main_frame(self):
        """
        主界面
        :return:
        """
        root = tk.Tk()
        root.title('Cedis--Redis客户端工具')
        # root.wm_iconbitmap(os.getcwd()+'\image\\redis.ico')

        #-------------------创建顶层下拉下拉菜单-------------
        top_menu = tk.Menu(root)
        option_menu = tk.Menu(top_menu, tearoff=0)
        option_menu.add_command(label='连接', command=self.open_conn_dialog)
        option_menu.add_separator()
        option_menu.add_command(label='退出', command=root.quit)
        top_menu.add_cascade(label='选项', menu=option_menu)

        root.config(menu=top_menu)

        #-------------------数据库下拉菜单-------------
        self.db_index = tk.StringVar(root)
        self.db_index.set("选择数据库")

        self.all_db = []
        for index in range(0,16):
            self.all_db.append(str(index))

        om = tk.OptionMenu(root, self.db_index, *self.all_db)
        om.config(width=9)
        om.grid(row=0,column=0)

        #-------------------数据类型下拉菜单-------------
        self.type_variable = tk.StringVar(root)
        self.type_variable.set('选择数据类型')

        type_om = tk.OptionMenu(root, self.type_variable, "选择数据类型", "string","list","set","hash")
        type_om.config(width=9)
        type_om.grid(row=0,column=1)


        #-------------------查询条件输入框-------------
        query_condition = tk.Label(root, text='key:')
        query_condition.grid(row=0, column=2, sticky=tk.E)

        self.input_value = tk.StringVar(root)

        input = tk.Entry(root, textvariable=self.input_value)
        input.grid(row=0,column=3)


        #---------------------查询按钮-------------
        button = tk.Button(root, text='查询', command=self.query_cache_info)
        button.grid(row=0,column=4)
        #---------------------返回按钮-------------
        button = tk.Button(root, text='返回', command=self.back)
        button.grid(row=0,column=5)


        #---------------------创建滚动条-------------
        listbox_scrollbar_vertical = tk.Scrollbar(root, orient=tk.VERTICAL)
        listbox_scrollbar_vertical.grid(row=1, column=6, sticky=tk.N+tk.S)
        listbox_scrollbar_horizontal = tk.Scrollbar(root, orient=tk.HORIZONTAL)
        listbox_scrollbar_horizontal.grid(row=2,column=0,columnspan=6, sticky=tk.E+tk.W)

        #---------------------列表框（显示查询结果）-------------
        self.cache_info_lb = tk.Listbox(root,selectmode=tk.SINGLE, bd=1, width=80, height=30,
                        yscrollcommand=listbox_scrollbar_vertical.set,
                        xscrollcommand=listbox_scrollbar_horizontal.set)
        self.cache_info_lb.config(fg='blue')
        self.cache_info_lb.grid(row=1,column=0,columnspan=6)
        self.cache_info_lb.bind('<<ListboxSelect>>', self.print_key_value)
        self.cache_info_lb.bind('<Button-3>', self.pop_menu)  #绑定鼠标右键点击事件

        #---------------------配置滚动条-------------
        listbox_scrollbar_vertical['command'] = self.cache_info_lb.yview
        listbox_scrollbar_horizontal['command'] = self.cache_info_lb.xview


        #---------------------创建鼠标右键菜单-------------
        self.right_click_menu = tk.Menu(root, tearoff=0)
        self.right_click_menu.add_command(label="删除", command=self.delete_item)



        tk.Label(root, text='详细信息').grid(row=0,column=7,columnspan=3)

        json_pretty_button = tk.Button(root, text='json格式化', fg='blue', command=self.json_pretty)
        json_pretty_button.grid(row=0, column=10, sticky=tk.E)

        #---------------------创建滚动条-------------
        text_scrollbar_vertical = tk.Scrollbar(root, orient=tk.VERTICAL)
        text_scrollbar_vertical.grid(row=1, column=11, sticky=tk.N+tk.S)

        #---------------------创建Text组件（显示缓存内容）-------------
        self.cache_content_text = tk.Text(root, width=80, height=41,relief="sunken",
                                     yscrollcommand=text_scrollbar_vertical.set)
        self.cache_content_text.grid(row=1, column=7, columnspan=4)

        #---------------------配置滚动条-------------
        text_scrollbar_vertical['command'] = self.cache_content_text.yview


        tk.Button(root, text='退出', fg='red', command=root.quit).grid(row=2,column=12)


        # w = 1200  # width of the root
        # h = 610  # height of the root
        #
        #
        # ws = root.winfo_screenwidth()  # width of the screen
        # hs = root.winfo_screenheight() # height of the screen
        #
        # x = (ws - w) / 2
        # y = (hs - h) / 2
        #
        # root.geometry("+%d+%d" % (x, y))
        root.mainloop()


    tmp_list = []  #作用是临时保存数据

    def query_cache_info(self):
        """
        按查询条件查询缓存
        :return:
        """
        if self.db_index.get() in self.all_db:
            redis = RedisUtil(int(self.db_index.get()))
        else:
            tk.messagebox.showerror('错误', '参数不正确：没有选择数据库')
            return

        type_variable_value = self.type_variable.get()
        query_condition_key = self.input_value.get()

        self.cache_content_text.delete('1.0', tk.END)
        self.cache_info_lb.delete(0,tk.END)

        #2.按指定的key类型和key名称查询数据
        if type_variable_value in ['string','list','set','hash'] and \
                self.check_none(query_condition_key):
            try:
                cache_info = redis.get_key_value(type_variable_value, query_condition_key, None)
            except ConnectionError:
                tk.messagebox.showerror('错误', '没有连接Redis')
                return

            #如果数据类型是hash或者set，则在Listbox中显示hash或set的所有field
            if type_variable_value in ['hash','set']:
                self.fillin_listbox(type_variable_value, query_condition_key, cache_info)
                return

            #如果数据类型是string，则在Text中显示value,在Listbox中显示key
            self.cache_info_lb.delete(0,tk.END)
            try:
                key_info_tuple = redis.get_key_info(query_condition_key)
                result = query_condition_key+'   '+type_variable_value+'   超时时间:'+key_info_tuple[1]
            except ConnectionError:
                tk.messagebox.showerror('错误', '没有连接Redis')
                return
            self.cache_info_lb.insert(tk.END, result)
            self.cache_content_text.insert(tk.INSERT, str(cache_info))

        #1.查询当前数据库中所有的key信息：key名称、key类型、key超时时间，在Listbox组件显示
        elif type_variable_value=='选择数据类型':
            try:
                cache_info = redis.get_all_keys()
            except ConnectionError:
                tk.messagebox.showerror('错误', '没有连接Redis')
                return

            for item in cache_info:
                self.tmp_list.clear()
                self.tmp_list.append(item)       #临时保存数据
                self.cache_info_lb.insert(tk.END, item)


    def print_key_value(self,event):
        """
        点击Listbox组件中一条缓存条目，查看对应数据
        :param event:
        :return:None
        """
        self.cache_content_text.delete('1.0', tk.END)

        #获取Listbox中选中的item的数据
        key_info_list = self.cache_info_lb.get(self.cache_info_lb.curselection()).split('   ')
        key_id = key_info_list[0]
        key_type = key_info_list[1]
        third_value = key_info_list[2]  #超时时间 or field_name(hash/set)

        redis = RedisUtil(int(self.db_index.get()))

        #如果数据类型是hash或者set，则在Listbox中显示hash或set的所有field
        if key_type in ['hash','set']:
            try:
                cache_info = redis.get_key_value(key_type, key_id, None)
            except ConnectionError:
                tk.messagebox.showerror('错误', '没有连接Redis')
                return
            self.fillin_listbox(key_type, key_id, cache_info)
        elif key_type in ['string','list','hash_field','set_field']:
            try:
                key_value = redis.get_key_value(key_type, key_id, third_value)
            except ConnectionError:
                tk.messagebox.showerror('错误', '没有连接Redis')
                return
            self.cache_content_text.insert(tk.INSERT, str(key_value))


    def fillin_listbox(self, type_variable_value, query_condition_key, cache_info):
        """
        将hash/set集合中的key在Listbox中显示
        :param type_variable_value:
        :param query_condition_key:
        :param cache_info:
        :return:
        """
        if type_variable_value == 'hash':
            self.cache_info_lb.delete(0,tk.END)
            for hash_field_item in cache_info:
                self.cache_info_lb.insert(tk.END, query_condition_key+'   '+
                                                  'hash_field   '+
                                                  hash_field_item)
        elif type_variable_value == 'set':
            self.cache_info_lb.delete(0,tk.END)
            for set_field_item in cache_info:
                self.cache_info_lb.insert(tk.END, query_condition_key+'   '+
                                                  'set_field   '+
                                                  set_field_item)


    def delete_item(self):
        """
        删除缓存
        :return:
        """
        key_info_list = self.cache_info_lb.get(self.cache_info_lb.curselection()).split('   ')
        key_id = key_info_list[0]
        result = tk.messagebox.askquestion('删除', '确定删除key为'+key_id+'的缓存?', icon='warning')
        if result == 'yes':
            re_result = tk.messagebox.askquestion('删除', '你刚才点了删除，真的要删除吗?', icon='warning')
            if re_result == 'yes':
                redis = RedisUtil(int(self.db_index.get()))
                try:
                    redis.del_key(key_id)
                except ConnectionError:
                    tk.messagebox.showerror('错误', '没有连接Redis')
            else:
                pass
        else:
            pass


    def json_pretty(self):
        """
        如果Text组件的内容是json，则美化它
        :return:None
        """
        #获取Text组件中的内容
        cache_data = self.cache_content_text.get('1.0', tk.END)
        #格式化json
        try:
            parse_data = json.loads(cache_data)
            cache_pretty_data = json.dumps(parse_data, indent=2, ensure_ascii=False, sort_keys=True)
        except Exception:
            tk.messagebox.showwarning('警告','不是标准格式json数据')
            return

        self.cache_content_text.delete('1.0', tk.END)
        self.cache_content_text.insert(tk.INSERT, cache_pretty_data)


    def back(self):
        if len(self.tmp_list)>0:
            self.cache_info_lb.delete(0,tk.END)
            for item in self.tmp_list:
                self.cache_info_lb.insert(tk.END, item)


    def pop_menu(self, event):
        """
        鼠标右键点击Listbox，弹出菜单
        :param event:
        :return:
        """
        self.right_click_menu.post(event.x_root, event.y_root)

    def conn_redis(self):
        env = self.env_value.get()
        host = self.host_value.get()
        port = self.port_value.get()
        password = self.password_value.get()

        is_Connection_success = RedisUtil(None).testConnection(host=host, port=port, password=password)
        if is_Connection_success:
            self.top_level.destroy()      #销毁Toplevel窗口
            conf_file_path = os.getcwd()+'\\conf\\redis_conf.cfg'
            RedisConf().write_cfg(file_path=conf_file_path, env=env, host=host,
                                  port=port, password=password)
            tk.messagebox.showinfo('连接成功', '连接Redis成功!')
        else:
            tk.messagebox.showwarning('连接失败', '连接Redis失败!')

    def open_conn_dialog(self):
        self.top_level = tk.Toplevel()
        self.top_level.geometry('200x140')
        self.top_level.title('连接Redis')

        env_label = tk.Label(self.top_level, text='Env')
        env_label.grid(row=0, column=0, sticky=tk.W+tk.N+tk.S)

        self.env_value = tk.StringVar()
        env_input = tk.Entry(self.top_level, textvariable=self.env_value)
        env_input.grid(row=0, column=1)

        host_label = tk.Label(self.top_level, text='Host')
        host_label.grid(row=1, column=0, sticky=tk.W+tk.N+tk.S)

        self.host_value = tk.StringVar()
        host_input = tk.Entry(self.top_level, textvariable=self.host_value)
        host_input.grid(row=1, column=1)

        port_label = tk.Label(self.top_level, text='Port')
        port_label.grid(row=2, column=0, sticky=tk.W+tk.N+tk.S)

        self.port_value = tk.StringVar()
        port_input = tk.Entry(self.top_level, textvariable=self.port_value)
        port_input.grid(row=2, column=1)

        password_lable = tk.Label(self.top_level, text='Password')
        password_lable.grid(row=3, column=0, sticky=tk.W+tk.N+tk.S)

        self.password_value = tk.StringVar()
        password_input = tk.Entry(self.top_level, textvariable=self.password_value)
        password_input.grid(row=3, column=1)

        ok = tk.Button(self.top_level, text='连接', command=self.conn_redis)
        ok.grid(row=4,column=1)

        self.top_level.focus_set()


    def check_none(self, str):
        return (len(str)!=0 and str is not None)


if __name__ == '__main__':
    Main().main_frame()