import sys
from pathlib import Path
 
sys.path.append(str(Path(__file__).parent))
 
import flet as ft
from views.catalogue_view import activities_page  # ← use what exists
from utils.constants import BG
 
def main(page: ft.Page):
    page.title      = "Grand Blue"
    page.bgcolor    = BG
    page.padding    = 0
    page.window.width       = 550
    page.window.height      = 900
    page.window.resizable   = False
    page.window.maximizable = False
 
    page.add(activities_page(page))
 
ft.app(main, assets_dir="assets")