# coding:utf-8

'''
xrandrコマンドをクリック操作で実行できるようにするインジケータアプレット

Copyright (c) 2016, ASHIJANKEN

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
    * Neither the name of the <ORGANIZATION> nor the names of its
contributors may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
Created on 2016/09/27

version 1.0   (2016/09/28)
version 1.0.1 (2017/01/17) brightness.txtに関するバグ修正
'''

import appindicator
import gtk
import subprocess
import re
import os.path

#明るさのチェック間隔(sec)
CHECK_INTERVAL_SEC = 5

class XrandrIndicator():
    def __init__(self):
        self.ind = appindicator.Indicator("user-XRandR-indicator",
                    os.path.dirname(os.path.realpath(__file__)) + "/notification-display-brightness-full.svg", 
                    appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        
        #明るさ情報をファイルから読み込み
	f = open(os.path.dirname(os.path.realpath(__file__)) + "/brightness.txt", "r")
        self.curr_brightness = float(f.read())
	f.close()
        #下の文がないと起動時に現在の明るさを表す黒丸が表示されない(小数の桁でも変わるのか？)
        self.curr_brightness = int(self.curr_brightness * 10) * 0.1

        #XRandR起動
        subprocess.call(["xrandr","--output", "DVI-D-0", "--brightness", str(self.curr_brightness)])

        #コンテキストメニュー 設定
        self.menu_setup()
        self.ind.set_menu(self.menu)
                
    def menu_setup(self):
        self.menu = gtk.Menu()
        
        #明るさ選択部
        for i in range(10,2,-1):
            i2 = i * 0.1
            buf = "%3.1f" % i2
            if i2 == self.curr_brightness:
                buf = u"%3.1f \u2022" % i2

            menu_items = gtk.MenuItem(buf)
            menu_items.show()
            menu_items.connect("activate", self.change_brightness, i2)
            self.menu.append(menu_items)
        
        #仕切り線
        breaker = gtk.SeparatorMenuItem()
        breaker.show()
        self.menu.append(breaker)
        
        #Aboutメニュー
        show_about_item = gtk.MenuItem("About GUI_XRandR")
        show_about_item.connect("activate", self.menu_about_dlg)
        show_about_item.show()
        self.menu.append(show_about_item)
        
        #終了メニュー
        quit_item = gtk.ImageMenuItem("Quit")
        quit_item.set_image(gtk.image_new_from_stock('gtk-quit', gtk.ICON_SIZE_MENU))
        quit_item.connect("activate", self.menu_quit)
        quit_item.show()
        self.menu.append(quit_item)
     
    #スライドの値をコマンドで送信  
    def change_brightness(self, w, recv_val):
        #recv_val = int(widget.get_value())
        #スライダから受け取った値を以下の変数としておく
        subprocess.call(["xrandr","--output", "DVI-D-0", "--brightness", str(recv_val)])
        if recv_val != self.curr_brightness:
            self.curr_brightness = recv_val
            f = open(os.path.dirname(os.path.realpath(__file__)) + "/brightness.txt", "w")
            f.write(str(self.curr_brightness))
            f.close()
            self.menu_setup()
            self.ind.set_menu(self.menu)
        
    #メニュー ： Aboutダイアログ
    def menu_about_dlg(self, widget):
        dlg = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format='GUI_XRandR')
        dlg.format_secondary_text('クリック操作でxrandrコマンドを送信できるソフトです。\n画面の照度調整が簡単にできます。')
        dlg.run()
        dlg.destroy()
        
    #メニュー ： プログラム終了
    def menu_quit(self, widget, data=None):
        gtk.main_quit()
        
    #メイン関数（タイマー設定を行う）
    def main(self):
        # タイマー設定（定期的に chk_brightness 関数を実行する）
        gtk.timeout_add(CHECK_INTERVAL_SEC*1000, self.chk_brightness)
        gtk.main()
        
    #現在のbrightnessが、設定したbrightnessと同じになっているか確かめる。
    #同じになっていなければコマンドを送って設定したbrightnessにする。    
    def chk_brightness(self):
        if self.explr_brightness("DVI-D-0") != self.curr_brightness:
            subprocess.call(["xrandr","--output", "DVI-D-0", "--brightness", str(self.curr_brightness)])
        return True
        
    #引数で指定されたディスプレイの明るさを調べる。返り値は明るさ(float)
    def explr_brightness(self, display):
        #「xrandr --verbose」で情報を取得
        info_xrandr = subprocess.check_output(["xrandr", "--verbose"])
        #引数で指定したディスプレイの明るさ情報を抽出
        #指定のディスプレイについてのセクションの先頭行を抽出
        splt_output = re.split("\n", info_xrandr)
        for keyline in splt_output:
            if keyline.find(display) >= 0:
                break
        keylinenum = splt_output.index(keyline)
        #生成したリストではkeyline要素の5個後ろにbrightnessが記述された文の要素がくる
        brightness = re.findall(r"\d\.\d+",splt_output[keylinenum+5])
        return float(brightness[0])

if __name__ == '__main__':
    indicator = XrandrIndicator()
    indicator.main()
