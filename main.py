from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import threading
import re

# Library untuk akses fitur native Android (Bluetooth)
from jnius import autoclass

class BMSAndroidApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        self.is_connected = False
        self.stream = None
        
        # Screen Utama
        screen = MDScreen()
        
        # Layout Utama
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # --- Bagian Atas: Input & Koneksi ---
        conn_box = MDCard(orientation='vertical', padding=15, size_hint=(1, 0.3), elevation=2)
        self.status_label = MDLabel(text="Status: DISCONNECTED", halign="center", theme_text_color="Secondary")
        
        input_box = BoxLayout(spacing=10)
        self.v_up = MDTextField(hint_text="V-High", text="14.4", input_filter="float")
        self.v_low = MDTextField(hint_text="V-Low", text="10.5", input_filter="float")
        input_box.add_widget(self.v_up)
        input_box.add_widget(self.v_low)
        
        self.btn_conn = MDRaisedButton(text="CONNECT BLUETOOTH", pos_hint={'center_x': .5})
        self.btn_conn.bind(on_release=self.toggle_bluetooth)
        
        conn_box.add_widget(self.status_label)
        conn_box.add_widget(input_box)
        conn_box.add_widget(self.btn_conn)
        
        # --- Bagian Tengah: Dashboard Data ---
        data_box = MDGridLayout(cols=2, spacing=10, size_hint=(1, 0.5))
        
        self.v_card = self.create_data_card("VOLTAGE", "0.00 V", "lightning-bolt", "#60a5fa")
        self.i_card = self.create_data_card("CURRENT", "0.000 A", "amperage", "#f87171")
        self.soc_card = self.create_data_card("SoC", "0.0 %", "battery-60", "#34d399")
        self.st_card = self.create_data_card("STATE", "IDLE", "state-machine", "#ffffff")
        
        data_box.add_widget(self.v_card)
        data_box.add_widget(self.i_card)
        data_box.add_widget(self.soc_card)
        data_box.add_widget(self.st_card)
        
        # --- Bagian Bawah: Control ---
        ctrl_box = BoxLayout(spacing=20, size_hint=(1, 0.2))
        self.btn_start = MDRaisedButton(text="START TEST", md_bg_color="#059669")
        self.btn_start.bind(on_release=self.send_start)
        
        self.btn_stop = MDRaisedButton(text="STOP", md_bg_color="#dc2626")
        self.btn_stop.bind(on_release=self.send_stop)
        
        ctrl_box.add_widget(self.btn_start)
        ctrl_box.add_widget(self.btn_stop)
        
        layout.add_widget(conn_box)
        layout.add_widget(data_box)
        layout.add_widget(ctrl_box)
        
        screen.add_widget(layout)
        return screen

    def create_data_card(self, title, value, icon, color):
        card = MDCard(orientation='vertical', padding=10, elevation=1, line_color=(0.2, 0.2, 0.2, 1))
        card.add_widget(MDLabel(text=title, font_style="Caption", halign="center"))
        lbl = MDLabel(text=value, font_style="H5", halign="center", theme_text_color="Custom", text_color=color)
        card.value_label = lbl # Simpan referensi untuk update
        card.add_widget(lbl)
        return card

    # --- LOGIKA BLUETOOTH ANDROID ---
    def toggle_bluetooth(self, *args):
        if not self.is_connected:
            threading.Thread(target=self.do_connect).start()
        else:
            self.do_disconnect()

    def do_connect(self):
        try:
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            adapter = BluetoothAdapter.getDefaultAdapter()
            paired_devices = adapter.getBondedDevices().toArray()
            
            target_device = None
            for device in paired_devices:
                if device.getName() == "BMS_Monitor_S3":
                    target_device = device
                    break
            
            if target_device:
                uuid = autoclass('java.util.UUID').fromString("00001101-0000-1000-8000-00805F9B34FB")
                self.socket = target_device.createRfcommSocketToServiceRecord(uuid)
                self.socket.connect()
                self.stream = self.socket.getInputStream()
                self.output = self.socket.getOutputStream()
                
                self.is_connected = True
                Clock.schedule_once(lambda dt: self.update_status("CONNECTED", "#059669"))
                threading.Thread(target=self.listen_data).start()
            else:
                Clock.schedule_once(lambda dt: self.update_status("DEVICE NOT PAIRED", "#dc2626"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_status(f"ERROR: {str(e)}", "#dc2626"))

    def listen_data(self):
        buffer = ""
        while self.is_connected:
            try:
                if self.stream.available() > 0:
                    char = chr(self.stream.read())
                    if char == '\n':
                        self.parse_line(buffer)
                        buffer = ""
                    else:
                        buffer += char
            except:
                break

    def parse_line(self, line):
        if "STATE=" in line:
            # Gunakan Regex untuk ambil data
            v = re.search(r"V=([\d\.]+)", line)
            i = re.search(r"I=([\d\.\-]+)", line)
            soc = re.search(r"SoC=([\d\.]+)", line)
            st = re.search(r"STATE=(\w+)", line)
            
            if v and i and soc and st:
                Clock.schedule_once(lambda dt: self.update_ui(v.group(1), i.group(1), soc.group(1), st.group(1)))

    def update_ui(self, v, i, soc, st):
        self.v_card.value_label.text = f"{v} V"
        self.i_card.value_label.text = f"{i} A"
        self.soc_card.value_label.text = f"{soc} %"
        self.st_card.value_label.text = st

    def update_status(self, text, color):
        self.status_label.text = f"Status: {text}"
        self.btn_conn.text = "DISCONNECT" if self.is_connected else "CONNECT BLUETOOTH"

    def send_start(self, *args):
        if self.is_connected:
            cmd = f"START|VUP={self.v_up.text}|VLOW={self.v_low.text}\n"
            self.output.write(cmd.encode())

    def send_stop(self, *args):
        if self.is_connected:
            self.output.write(b"STOP\n")

if __name__ == "__main__":
    from kivy.uix.gridlayout import MDGridLayout # Fix import missing
    BMSAndroidApp().run()
