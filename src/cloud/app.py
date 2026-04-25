import streamlit as st
import os
from datetime import datetime

# Konfiguration
UPLOAD_DIR = "data/"
PASSWORD = "koto873400" # Ändere das hier!

# Sicherstellen, dass der Ordner existiert
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def main():
    st.title("📸 Purchases Upload")

    # --- 1. Passwort Abfrage ---
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        password_input = st.text_input("Bitte Passwort eingeben", type="password")
        if st.button("Login"):
            if password_input == PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return

    # --- 2. Kamera Input ---
    st.write("Mache ein Foto deines Belegs:")
    img_file = st.camera_input("Kamera öffnen")

    if img_file is not None:
        # Einzigartigen Dateinamen generieren
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"receipt_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)

        # --- 3. Speichern auf dem Server ---
        with open(filepath, "wb") as f:
            f.write(img_file.getbuffer())
        
        st.success(f"Bild erfolgreich gespeichert als {filename}")
        st.balloons()

if __name__ == "__main__":
    main()