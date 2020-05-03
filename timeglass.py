import rumps
import sys
import icon_manager
from datetime import timedelta
import timekeeper
import os

# pyinstaller --onefile -w --add-data "Icons/:Icons" --icon="Icons/timeglass.png" --clean timeglass.spec

# rumps.debug_mode(True)

class TimerApp(rumps.App):
    def __init__(self, initial_seconds):
        super(TimerApp, self).__init__("")
        self.mode = "hourglass"
        self.timekeeper = timekeeper.Timer(initial_seconds)
        self.im = icon_manager.Icon_manager(initial_seconds)
        self.change_icon()        
        self.remaining_sec = rumps.MenuItem(self.timekeeper.get_remaining_string())
        self.menu = [self.remaining_sec]
        self.next_icon_change = self.im.icon_interval
        self.rumps_timer = rumps.Timer(self.tick,0.5)
        self.rumps_timer.callback(self.tick)
        self.invert_counter = 0

    def change_icon(self):
        #self.im.draw_icon(frame)
        print("frame:", self.im.icon_counter)
        self.icon = self.im.get_icon_path()

    def change_remaining(self):
        self.remaining_sec.title = self.timekeeper.get_remaining_string()

    def tick(self, _):
        if self.timekeeper.tick():
            self.notDone = True
            self.invert_counter = 0
            self.change_remaining()
            if self.timekeeper.elapsed >= self.next_icon_change:
                self.im.icon_counter = int(self.timekeeper.elapsed/self.im.icon_interval) + 1 #1-89
                self.change_icon()
                self.next_icon_change += self.im.icon_interval
                print(self.timekeeper.elapsed)
                print(self.timekeeper.elapsed/self.im.icon_interval)
                print(int(self.timekeeper.elapsed/self.im.icon_interval))

        if self.timekeeper.done:
            self.im.active = False
            self.change_icon()
            if self.notDone:
                self.icon = self.im.invert()
                self.invert_counter += 1
                if self.invert_counter > 5:
                    self.notDone = False
                    self.rumps_timer.stop()
                    self.reset()
                    #self.pause()
                

    @rumps.clicked("Start")
    def pause(self, sender):
        if sender.title == "Pause":
            self.timekeeper.pause_timer()
            # self.timekeeper.pause = True
            # self.timekeeper.active = False
            self.rumps_timer.stop()
            sender.title = "Start"
        elif sender.title == "Start":
            self.timekeeper.start()
            self.im.active = True
            self.change_icon()
            self.rumps_timer.start()
            sender.title = "Pause"

    @rumps.clicked("Reset")
    def reset_button(self, sender):
        self.reset()
        self.menu["Start"].title = "Start"

    def reset(self):
        self.timekeeper.reset()
        self.rumps_timer.stop()
        self.im.active = False
        self.im.reset()
        self.change_icon()
        self.change_remaining()
        self.next_icon_change = self.im.icon_interval
        self.menu["Start"].title = "Start"

    def string_to_sec(self, text):
        nums = text.split(":")
        nums.reverse()
        seconds = 0
        for i,n in enumerate(nums):
            if i == 0:
                seconds += int(n)
            else:
                seconds += (60**i) * int(n)
                print((i * 60) * int(n))
                #print(f"{i} {n} {seconds}")
        return seconds

    def validate_input(self, text):
        texts = text.split(":")
        if len(texts)>3: return False
        for s in texts:
            try:
                int(s)
            except:
                return False
        return True

    @rumps.clicked("Set time")
    def set_time(self, _):
        response = rumps.Window("Enter time: (hours:minutes:seconds)").run()
        if response.clicked:
            if not self.validate_input(response.text):
                skip = True
                rumps.alert("Does not compute! Please try again.")

            else:
                seconds = self.string_to_sec(response.text)
                print(seconds)
                skip = False
            
            if not skip:
                self.rumps_timer.stop()
                self.timekeeper.set_time(seconds)
                self.im.set_icon_interval(seconds)
                self.im.reset()
                self.im.active = False
                self.next_icon_change = self.im.icon_interval
                self.change_icon()
                self.change_remaining()
                self.menu["Start"].title = "Start"

if __name__ == "__main__":
    default_secounds = 60 * 60
    TimerApp(default_secounds).run()

