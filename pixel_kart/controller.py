from pixel_kart.gui import PixelKartGUI
from pixel_kart.player import HumanPlayer

class PixelKartController:
    def __init__(self, parent):
        self.gui = PixelKartGUI(parent)
        self.gui.pack(expand=True, fill="both")