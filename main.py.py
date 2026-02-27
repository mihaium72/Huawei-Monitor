from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from pymodbus.client import ModbusTcpClient
import time

class HuaweiApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        self.lbl = Label(
            text="HUAWEI SUN2000\nPronto per la lettura", 
            halign="center",
            font_size='20sp'
        )
        
        btn = Button(
            text="LEGGI POTENZA", 
            size_hint=(1, 0.4),
            background_color=(0.1, 0.6, 1, 1)
        )
        btn.bind(on_press=self.read_solar)
        
        layout.add_widget(self.lbl)
        layout.add_widget(btn)
        return layout

    def read_solar(self, instance):
        client = ModbusTcpClient('192.168.1.75', port=502) 
        try:
            self.lbl.text = "Tentativo di lettura..."
            if client.connect():
                self.lbl.text = "Connesso..."
                # Nelle versioni 3.x, l'unico modo per non avere l'errore 
                # "2 positional arguments but 3 given" è nominare il count.
                # Se 'slave' fallisce ancora, proveremo a non metterlo affatto.
                try:
                    # Questo è lo standard Pymodbus 3.1+
                    rr = client.read_holding_registers(32080, count=2, slave=1)
                except TypeError:
                    # Se 'slave' non è accettato, la tua versione lo chiama 'slave' 
                    # ma forse è cambiato il modulo. Proviamo senza ID (usa default 1)
                    rr = client.read_holding_registers(32080, count=2)

                if rr and not rr.isError():
                    # Calcolo Potenza 32 bit
                    res = (rr.registers[0] << 16) + rr.registers[1]
                    if res > 2147483647: res -= 4294967296
                    self.lbl.text = f"POTENZA ATTUALE:\n{res} W"
                else:
                    self.lbl.text = "Inverter connesso ma\nha rifiutato i dati."
                client.close()
            else:
                self.lbl.text = "Inverter non trovato.\nControlla IP 192.168.1.75"
        except Exception as e:
            self.lbl.text = f"Errore Tecnico:\n{str(e)}"

if __name__ == "__main__":
    HuaweiApp().run()