#!/usr/bin/env python3
"""
Icon Konverter für DRX Trading Tracker
Konvertiert PNG zu ICO für Windows
"""

from PIL import Image
import os
from pathlib import Path

def create_ico_from_png():
    """PNG zu ICO konvertieren"""
    
    # Größtes PNG finden
    iconset_dir = Path("iconset_for_icns")
    png_files = list(iconset_dir.glob("icon_*.png"))
    
    if not png_files:
        print("❌ Keine PNG-Dateien gefunden!")
        return False
    
    # 256x256 oder größtes verfügbares nehmen
    target_files = [
        iconset_dir / "icon_256x256.png",
        iconset_dir / "icon_512x512.png", 
        iconset_dir / "icon_128x128.png"
    ]
    
    source_png = None
    for target in target_files:
        if target.exists():
            source_png = target
            break
    
    if not source_png:
        source_png = png_files[0]
    
    print(f"📷 Verwende: {source_png}")
    
    try:
        # PNG laden
        img = Image.open(source_png)
        
        # ICO erstellen mit mehreren Größen
        icon_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
        ico_images = []
        
        for size in icon_sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(resized)
        
        # ICO speichern
        ico_path = Path("icon.ico")
        ico_images[0].save(
            ico_path, 
            format='ICO', 
            sizes=icon_sizes,
            append_images=ico_images[1:]
        )
        
        print(f"✅ ICO erstellt: {ico_path}")
        return True
        
    except Exception as e:
        print(f"❌ Konvertierung fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🎨 DRX Icon Konverter")
    print("=" * 30)
    
    success = create_ico_from_png()
    if success:
        print("✅ Icon bereit für Windows!")
    else:
        print("❌ Konvertierung fehlgeschlagen!")