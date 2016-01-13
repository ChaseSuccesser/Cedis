#coding=utf-8
from redis_util import RedisUtil
import tkinter as tk
import tkinter.messagebox
import os
import json
__author__ = 'lgx'


#----------------------------------事件函数--------------------------
all_db = []
for index in range(1,17):
    all_db.append(str(index))

tmp_list = []  #作用是临时保存数据

def queryCacheInfo():
    """
    按查询条件查询缓存
    :return:
    """
    if db_index.get() in all_db:
        redis = RedisUtil(int(db_index.get()))
    else:
        tk.messagebox.showerror('错误', '参数不正确：没有选择数据库')
        return

    query_condition_value = input_value.get()
    type_variable_value = type_variable.get()

    cache_content_text.delete('1.0',tk.END)
    cache_info_lb.delete(0,tk.END)

    #2.按指定的key类型和key名称查询数据
    if type_variable_value in ['string','list','set','hash'] and checkNone(query_condition_value):
        cache_info = redis.getKeyValue(type_variable_value, query_condition_value, None)

        #如果数据类型是hash或者set，则在Listbox中显示hash或set的所有field
        if type_variable_value in ['hash','set']:
            fillinListbox(type_variable_value, query_condition_value, cache_info)
            return
        #如果数据类型是string，则在Text中显示key的值
        cache_content_text.insert(tk.INSERT, str(cache_info))

    #1.查询当前数据库中所有的key信息：key名称、key类型、key超时时间，在Listbox组件显示
    elif type_variable_value=='选择数据类型':
        cache_info = redis.getAllKeys()
        print(len(cache_info))
        for item in cache_info:
            tmp_list.append(item)       #临时保存数据
            cache_info_lb.insert(tk.END, item)


def printKeyValue(event):
    """
    点击Listbox组件中一条缓存条目，查看对应数据
    :param event:
    :return:None
    """
    cache_content_text.delete('1.0', tk.END)

    #获取Listbox中选中的item的数据
    key_info_list = cache_info_lb.get(cache_info_lb.curselection()).split('   ')
    key_id = key_info_list[0]
    key_type = key_info_list[1]
    third_value = key_info_list[2]  #超时时间 or field_name(hash/set)

    redis = RedisUtil(int(db_index.get()))

    #如果数据类型是hash或者set，则在Listbox中显示hash或set的所有field
    if key_type in ['hash','set']:
        cache_info = redis.getKeyValue(key_type, key_id, None)
        fillinListbox(key_type, key_id, cache_info)
    elif key_type in ['string','list','hash_field','set_field']:
        key_value = redis.getKeyValue(key_type, key_id, third_value)
        cache_content_text.insert(tk.INSERT, str(key_value))


def fillinListbox(type_variable_value, query_condition_value, cache_info):
    if type_variable_value == 'hash':
        cache_info_lb.delete(0,tk.END)
        for hash_field_item in cache_info:
            cache_info_lb.insert(tk.END, query_condition_value+'   '+'hash_field   '+hash_field_item)
    elif type_variable_value == 'set':
        cache_info_lb.delete(0,tk.END)
        for set_field_item in cache_info:
            cache_info_lb.insert(tk.END, query_condition_value+'   '+'set_field   '+set_field_item)


def deleteItem():
    """
    删除缓存
    :return:
    """
    key_info_list = cache_info_lb.get(cache_info_lb.curselection()).split('   ')
    key_id = key_info_list[0]
    result = tk.messagebox.askquestion('删除', '确定删除key为'+key_id+'的缓存?', icon='warning')
    if result == 'yes':
        re_result = tk.messagebox.askquestion('删除', '你刚才点了删除，真的要删除吗?', icon='warning')
        if re_result == 'yes':
            redis = RedisUtil(int(db_index.get()))
            redis.delKey(key_id)
        else:
            pass
    else:
        pass


def jsonPretty():
    """
    如果Text组件的内容是json，则美化它
    :return:None
    """
    #获取Text组件中的内容
    cache_data = cache_content_text.get('1.0', tk.END)
    #格式化json
    try:
        parse_data = json.loads(cache_data)
        cache_pretty_data = json.dumps(parse_data, indent=2, ensure_ascii=False, sort_keys=True)
    except Exception:
        tk.messagebox.showwarning('警告','不是标准格式json数据')

    cache_content_text.delete('1.0', tk.END)
    cache_content_text.insert(tk.INSERT, cache_pretty_data)


def back():
    if len(tmp_list)>0:
        cache_info_lb.delete(0,tk.END)
        for item in tmp_list:
            cache_info_lb.insert(tk.END, item)


def popMenu(event):
    """
    鼠标右键点击Listbox，弹出菜单
    :param event:
    :return:
    """
    right_click_menu.post(event.x_root, event.y_root)

def checkNone(str):
    return (len(str)!=0 and str is not None)


root = tk.Tk()
root.title('Cedis--Redis客户端工具')
# img = tk.PhotoImage(file=os.getcwd()+'\image\\redis.ico')
# root.tk.call('wm', 'iconphoto', root._w, img)
# root.wm_iconbitmap(os.getcwd()+'\image\\redis.ico')

#-------------------数据库下拉菜单-------------
db_index = tk.StringVar(root)
db_index.set("选择数据库")

om = tk.OptionMenu(root, db_index,
              "1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16")
om.config(width=9)
om.grid(row=0,column=0)

#-------------------数据类型下拉菜单-------------
type_variable = tk.StringVar(root)
type_variable.set('选择数据类型')

type_om = tk.OptionMenu(root, type_variable, "选择数据类型", "string","list","set","hash")
type_om.config(width=9)
type_om.grid(row=0,column=1)


#-------------------查询条件输入框-------------
query_condition = tk.Label(root, text='key:')
query_condition.grid(row=0, column=2, sticky=tk.E)

input_value = tk.StringVar(root)

input = tk.Entry(root, textvariable=input_value)
input.grid(row=0,column=3)


#---------------------查询按钮-------------
button = tk.Button(root, text='查询', command=queryCacheInfo)
button.grid(row=0,column=4)
#---------------------返回按钮-------------
button = tk.Button(root, text='返回', command=back)
button.grid(row=0,column=5)


#---------------------创建滚动条-------------
listbox_scrollbar_vertical = tk.Scrollbar(root, orient=tk.VERTICAL)
listbox_scrollbar_vertical.grid(row=1, column=6, sticky=tk.N+tk.S)
listbox_scrollbar_horizontal = tk.Scrollbar(root, orient=tk.HORIZONTAL)
listbox_scrollbar_horizontal.grid(row=2,column=0,columnspan=6, sticky=tk.E+tk.W)

#---------------------列表框（显示查询结果）-------------
cache_info_lb = tk.Listbox(root,selectmode=tk.SINGLE, bd=1, width=80, height=30,
                yscrollcommand=listbox_scrollbar_vertical.set,
                xscrollcommand=listbox_scrollbar_horizontal.set)
cache_info_lb.config(fg='blue')
cache_info_lb.grid(row=1,column=0,columnspan=6)
cache_info_lb.bind('<<ListboxSelect>>', printKeyValue)
cache_info_lb.bind('<Button-3>', popMenu)  #绑定鼠标右键点击事件

#---------------------配置滚动条-------------
listbox_scrollbar_vertical['command'] = cache_info_lb.yview
listbox_scrollbar_horizontal['command'] = cache_info_lb.xview


#---------------------创建鼠标右键菜单-------------
right_click_menu = tk.Menu(root, tearoff=0)
right_click_menu.add_command(label="删除", command=deleteItem)



tk.Label(root, text='详细信息').grid(row=0,column=7,columnspan=3)

tk.Button(root, text='json格式化', fg='blue', command=jsonPretty).grid(row=0, column=10, sticky=tk.E)

#---------------------创建滚动条-------------
text_scrollbar_vertical = tk.Scrollbar(root, orient=tk.VERTICAL)
text_scrollbar_vertical.grid(row=1, column=11, sticky=tk.N+tk.S)

#---------------------创建Text组件（显示缓存内容）-------------
cache_content_text = tk.Text(root, width=80, height=41,relief="sunken",
                             yscrollcommand=text_scrollbar_vertical.set)
cache_content_text.grid(row=1, column=7, columnspan=4)

#---------------------配置滚动条-------------
text_scrollbar_vertical['command'] = cache_content_text.yview


tk.Button(root, text='退出', fg='red', command=root.quit).grid(row=2,column=12)


root.mainloop()