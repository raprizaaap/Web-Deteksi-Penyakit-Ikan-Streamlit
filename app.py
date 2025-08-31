import streamlit as st
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
from datetime import datetime
import plotly.express as px

# ======================
# Konfigurasi Halaman Utama
# ======================
st.set_page_config(
    page_title="IkanCheck",
    page_icon="🐟",
    layout="wide"
)

# ======================
# CSS Kustom untuk Tampilan
# ======================
st.markdown("""
    <style>
    /* CSS untuk layout full-width */
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100% !important;
    }
    /* CSS untuk Card di Halaman Beranda */
    .card {
        background-color: #262730;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        border: 1px solid #4D4D4D;
    }
    .card h2, .card h3 {
        color: #FFFFFF;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# ======================
# Pemuatan Model & Konfigurasi Awal
# ======================
MODEL_PATH = "model999.h5"
model = load_model(MODEL_PATH)

class_labels = {
    "Bacterial Red disease": 0,
    "Bacterial diseases - Aeromoniasis": 1,
    "Bacterial gill disease": 2,
    "Fungal diseases Saprolegniasis": 3,
    "Healthy Fish": 4,
    "Parasitic diseases": 5,
    "Viral diseases White tail disease": 6
}
idx_to_class = {v: k for k, v in class_labels.items()}

HISTORY_DIR = "riwayat_upload"
os.makedirs(HISTORY_DIR, exist_ok=True)

# ======================
# Database Teks (Saran & Edukasi)
# ======================
saran_pengobatan = {
    "Bacterial Red disease": """
        **Penyebab:** Bakteri *Aeromonas hydrophila* atau *Pseudomonas sp.*, sering dipicu oleh stres atau kualitas air yang buruk.
        **Gejala Umum:** Bercak merah atau borok pada tubuh, sirip, atau ekor. Ikan menjadi lesu dan kehilangan nafsu makan.
        **Saran Pengobatan:**
        1.  **Karantina:** Segera pisahkan ikan yang sakit untuk mencegah penularan.
        2.  **Perbaikan Kualitas Air:** Lakukan penggantian air sekitar 30-50% dan pastikan parameter air (pH, amonia) stabil.
        3.  **Pengobatan:** Gunakan antibiotik yang sesuai seperti Oxytetracycline atau Enrofloxacin yang dicampurkan ke dalam pakan atau air sesuai dosis yang dianjurkan.
        4.  **Garam Ikan:** Tambahkan garam ikan (non-yodium) sekitar 1-3 gram per liter air untuk membantu mengurangi stres osmotik pada ikan.
    """,
    "Bacterial diseases - Aeromoniasis": """
        **Penyebab:** Infeksi bakteri *Aeromonas*, biasanya menyerang ikan yang sedang stres atau terluka.
        **Gejala Umum:** Perut kembung (dropsy), mata menonjol (pop-eye), borok pada kulit.
        **Saran Pengobatan:**
        1.  Segera karantina ikan yang terinfeksi.
        2.  Gunakan antibiotik seperti Kanamycin atau Metronidazole. Konsultasikan dosis dengan ahli.
        3.  Jaga kebersihan akuarium secara maksimal.
    """,
    "Bacterial gill disease": """
        **Penyebab:** Bakteri seperti *Flavobacterium branchiophilum*. Sering terjadi di akuarium padat dengan kualitas air rendah.
        **Gejala Umum:** Insang terlihat bengkak, pucat, atau tertutup lendir. Ikan kesulitan bernapas dan sering megap-megap di permukaan.
        **Saran Pengobatan:**
        1.  Tingkatkan aerasi dan kualitas air.
        2.  Lakukan perendaman dengan larutan garam ikan.
        3.  Gunakan pengobatan antibakteri seperti Acriflavine atau Formalin sesuai petunjuk.
    """,
    "Fungal diseases Saprolegniasis": """
        **Penyebab:** Jamur *Saprolegnia sp.*, biasanya menyerang jaringan tubuh ikan yang sudah ada luka sebelumnya.
        **Gejala Umum:** Tumbuh lapisan seperti kapas berwarna putih atau keabu-abuan pada kulit, sirip, atau mata ikan.
        **Saran Pengobatan:**
        1.  Gunakan anti-jamur seperti Malachite Green atau Methylene Blue.
        2.  Jaga suhu air tetap stabil dan bersih.
        3.  Pindahkan ikan ke tank karantina selama pengobatan.
    """,
    "Parasitic diseases": """
        **Penyebab:** Parasit eksternal seperti *Ichthyophthirius multifiliis* (White Spot) atau kutu ikan (*Argulus*).
        **Gejala Umum:** Bintik-bintik putih di seluruh tubuh (White Spot), ikan sering menggesekkan tubuhnya ke benda, atau terlihat parasit menempel di kulit.
        **Saran Pengobatan:**
        1.  Naikkan suhu air secara bertahap (untuk White Spot) ke 28-30°C untuk mempercepat siklus hidup parasit.
        2.  Gunakan obat anti-parasit yang mengandung Malachite Green dan Formalin.
        3.  Jaga kebersihan dasar akuarium karena beberapa parasit berkembang biak di substrat.
    """,
    "Viral diseases White tail disease": """
        **Penyebab:** Infeksi virus. Penyakit ini sangat menular dan seringkali sulit diobati.
        **Gejala Umum:** Muncul warna putih buram atau seperti susu pada bagian pangkal hingga ujung ekor.
        **Saran Pengobatan:**
        1.  Saat ini belum ada obat antivirus yang efektif untuk ikan.
        2.  Fokus utama adalah **pencegahan**: jaga kualitas air, berikan nutrisi terbaik untuk meningkatkan imun ikan.
        3.  Segera pisahkan ikan yang terinfeksi untuk mencegah wabah.
    """,
    "Healthy Fish": "Ikan Anda terlihat sehat! Terus jaga kualitas air dan berikan pakan yang baik."
}

edukasi_lengkap = {
    "Bacterial Red disease": {
        "img": "image/bacterial.jpg",
        "nama_lain": "Penyakit Bercak Merah, *Epizootic Ulcerative Syndrome (EUS)*",
        "penyebab": "Umumnya disebabkan oleh infeksi bakteri seperti *Aeromonas hydrophila* atau *Pseudomonas sp.*. Seringkali dipicu oleh stres, kualitas air yang buruk, atau luka pada tubuh ikan.",
        "gejala_umum": """
        - Munculnya bercak merah, ruam, atau luka borok (ulkus) pada kulit, sirip, atau pangkal ekor.
        - Sirip terlihat geripis atau rusak.
        - Ikan menjadi lesu, kehilangan nafsu makan, dan sering menyendiri.
        - Pada kasus parah, dapat terjadi pendarahan di beberapa bagian tubuh.
        """,
        "penanganan_dan_pengobatan": """
        1.  **Karantina**: Segera pisahkan ikan yang sakit ke dalam tangki karantina untuk mencegah penularan.
        2.  **Perbaikan Kualitas Air**: Lakukan penggantian air parsial (30-50%) secara rutin. Pastikan parameter air seperti pH, amonia, dan nitrit berada pada level yang aman.
        3.  **Penggunaan Antibiotik**: Lakukan perendaman atau campurkan antibiotik seperti *Oxytetracycline* atau *Enrofloxacin* ke dalam pakan. Selalu ikuti dosis dan petunjuk penggunaan.
        4.  **Pemberian Garam Ikan**: Tambahkan garam ikan (non-yodium) dengan dosis 1-3 gram per liter air di tangki karantina untuk membantu proses penyembuhan dan mengurangi stres osmotik.
        """,
        "pencegahan": """
        - Jaga kebersihan akuarium dan filter secara rutin.
        - Hindari kepadatan populasi ikan yang berlebihan.
        - Berikan pakan yang berkualitas dan bervariasi.
        """
    },
    "Bacterial diseases - Aeromoniasis": {
        "img": "image/aeromon.png",
        "nama_lain": "Penyakit Sisik Nanas (*Dropsy*), Mata Bengkak (*Pop-eye*)",
        "penyebab": "Infeksi bakteri dari genus *Aeromonas* yang menyerang organ dalam. Biasanya menyerang ikan dengan sistem imun yang lemah akibat stres atau kualitas air yang buruk.",
        "gejala_umum": """
        - Perut ikan membengkak secara tidak normal (seperti buah nanas, karena sisik terangkat).
        - Mata terlihat menonjol keluar.
        - Munculnya luka atau borok pada tubuh.
        - Ikan kehilangan keseimbangan saat berenang.
        """,
        "penanganan_dan_pengobatan": """
        1.  **Karantina Segera**: Penyakit ini bisa menular.
        2.  **Pengobatan Internal**: Campurkan antibiotik seperti *Metronidazole* atau *Kanamycin* ke dalam pakan ikan.
        3.  **Perendaman Garam Epsom**: Garam Epsom (Magnesium Sulfat) dapat membantu mengurangi pembengkakan cairan di tubuh ikan. Lakukan perendaman sesuai dosis yang dianjurkan.
        """,
        "pencegahan": "Manajemen kualitas air adalah kunci utama. Hindari perubahan suhu yang drastis dan jaga kebersihan akuarium."
    },
    "Bacterial gill disease": {
        "img": "image/gill.jpg",
        "nama_lain": "Penyakit Insang Bakterial",
        "penyebab": "Bakteri seperti *Flavobacterium sp.* yang menginfeksi filamen insang. Sering terjadi di akuarium yang padat dan kadar oksigen rendah.",
        "gejala_umum": """
        - Insang terlihat bengkak, pucat, atau terkikis.
        - Sering tertutup oleh lapisan lendir yang berlebihan.
        - Ikan kesulitan bernapas, sering megap-megap di permukaan air.
        - Gerakan operkulum (tutup insang) menjadi sangat cepat.
        """,
        "penanganan_dan_pengobatan": """
        1.  **Tingkatkan Oksigen**: Segera tambah aerasi di dalam akuarium.
        2.  **Perbaikan Kualitas Air**: Lakukan penggantian air untuk mengurangi kadar amonia dan nitrit.
        3.  **Pengobatan Eksternal**: Lakukan perendaman jangka pendek dengan *Potassium Permanganate (PK)* atau Formalin. Lakukan dengan hati-hati dan sesuai dosis.
        """,
        "pencegahan": "Jangan terlalu padat mengisi akuarium dan pastikan sistem filtrasi dan aerasi berjalan dengan baik."
    },
    "Fungal diseases Saprolegniasis": {
        "img": "image/fungal.jpg",
       "nama_lain": "Penyakit Jamur Kapas",
        "penyebab": "Infeksi jamur dari genus *Saprolegnia*. Jamur ini bersifat oportunistik, artinya hanya menyerang ikan yang sudah lemah, stres, atau memiliki luka terbuka.",
        "gejala_umum": "Tumbuhnya lapisan seperti gumpalan kapas berwarna putih, abu-abu, atau kecoklatan pada kulit, sirip, mata, atau mulut ikan.",
        "penanganan_dan_pengobatan": """
        1.  **Karantina**: Pisahkan ikan yang terinfeksi.
        2.  **Gunakan Anti-Jamur**: Obati dengan produk anti-jamur yang mengandung *Malachite Green* atau *Methylene Blue*.
        3.  **Perendaman Garam Ikan**: Mandikan ikan dalam larutan garam ikan dengan dosis yang lebih tinggi untuk perendaman jangka pendek.
        """,
        "pencegahan": "Hindari melukai ikan saat memindahkannya dan jaga kualitas air agar ikan tidak stres."
    },
    "Healthy Fish": {
        "img": "image/healty.jpg",
        "nama_lain": "Ikan Sehat",
        "penyebab": "Kondisi ideal yang dicapai melalui perawatan yang baik.",
        "gejala_umum": """
        - Berenang aktif dan responsif.
        - Warna tubuh cerah, cerah, dan tidak kusam.
        - Sirip dan ekor mengembang sempurna dan tidak ada sobekan.
        - Mata jernih, tidak berkabut atau menonjol.
        - Tidak ada bintik, bercak, luka, atau lapisan lendir aneh pada tubuh.
        - Bernapas dengan tenang dan memiliki nafsu makan yang baik.
        """,
        "penanganan_dan_pengobatan": "Tidak diperlukan pengobatan. Teruskan perawatan yang baik.",
        "pencegahan": "Kualitas air, pakan bergizi, dan lingkungan bebas stres adalah tiga pilar utama untuk menjaga ikan tetap sehat."
    },
    "Parasitic diseases": {
        "img": "image/parasit.jpg",
       "nama_lain": "Penyakit Parasit (Contoh: White Spot, Kutu Ikan)",
        "penyebab": "Organisme parasit yang hidup di kulit, insang, atau organ internal ikan.",
        "gejala_umum": """
        - **White Spot (Ich)**: Bintik-bintik putih kecil seperti butiran garam di seluruh tubuh dan sirip.
        - **Kutu Ikan (Argulus)**: Terlihat parasit pipih transparan yang menempel erat pada kulit ikan.
        - Ikan sering menggesek-gesekkan tubuhnya pada dekorasi atau dinding akuarium (*flashing*).
        """,
        "penanganan_dan_pengobatan": """
        1.  **Gunakan Obat Anti-Parasit**: Gunakan produk yang mengandung *Malachite Green*, Formalin, atau *Copper Sulfate* (hati-hati untuk beberapa jenis ikan).
        2.  **Naikkan Suhu (khusus White Spot)**: Menaikkan suhu air secara perlahan ke 28-30°C dapat mempercepat siklus hidup parasit *Ich*, membuatnya lebih rentan terhadap obat.
        3.  **Jaga Kebersihan Substrat**: Sedot kotoran di dasar akuarium secara rutin karena beberapa parasit berkembang biak di sana.
        """,
        "pencegahan": "Karantina ikan baru sebelum dimasukkan ke akuarium utama. Hindari memberikan pakan hidup yang tidak terjamin kebersihannya."
    },
    "Viral diseases White tail disease": {
        "img": "image/white.jpg",
        "nama_lain": "Penyakit Ekor Putih",
        "penyebab": "Infeksi virus yang sangat menular. Seringkali fatal dan sulit diobati.",
        "gejala_umum": "Munculnya warna putih buram atau seperti susu yang dimulai dari pangkal ekor (peduncle) dan menyebar ke seluruh sirip ekor.",
        "penanganan_dan_pengobatan": "Saat ini belum ada obat antivirus yang efektif untuk ikan. Pengobatan biasanya tidak berhasil. Langkah terbaik adalah melakukan eutanasia (mematikan ikan secara manusiawi) pada ikan yang terinfeksi parah untuk mencegah penyebaran ke ikan lain.",
        "pencegahan": "Pencegahan adalah satu-satunya cara yang efektif. Jaga kualitas air pada tingkat tertinggi, berikan pakan bernutrisi tinggi untuk meningkatkan sistem imun ikan, dan segera karantina ikan baru atau ikan yang menunjukkan gejala."
    }
}


# ======================
# Fungsi Prediksi
# ======================
def model_prediction(img):
    img = img.resize((299, 299))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0) / 255.0
    preds = model.predict(x)
    return np.argmax(preds), np.max(preds)

# ======================
# Sidebar Navigasi
# ======================
st.sidebar.title("🧭 Navigasi")
page = st.sidebar.selectbox("Pilih Halaman", ["🏠 Beranda", "🔍 Deteksi Penyakit", "📚 Edukasi Penyakit", "📝 Riwayat", "ℹ️ Tentang"])


# ======================
# ----- HALAMAN BERANDA -----
# ======================
if page == "🏠 Beranda":
    st.title("🐟 Selamat Datang di IkanCheck")
    st.subheader("Sistem Deteksi Penyakit Ikan Air Tawar Berbasis CNN Xception")
    st.markdown("---")

    # --- Card 1: Apa itu IkanCheck? ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            img = Image.open("bgikan.jpg")
            st.image(img, caption="IkanCheck", use_container_width=True)
        except FileNotFoundError:
            st.error("Gambar bgikan.jpg tidak ditemukan!")
    with col2:
        st.markdown("""
            <h2>🎯 Apa itu IkanCheck?</h2>
            <p>IkanCheck adalah aplikasi berbasis <b>AI (Convolutional Neural Network - Xception)</b> 
            yang dapat mendeteksi penyakit pada ikan air tawar hanya dengan menggunakan <b>gambar</b>.</p>
            <ul>
                <li>🔹 Mudah digunakan</li>
                <li>🔹 Cepat & akurat</li>
                <li>🔹 Edukasi lengkap penyakit ikan</li>
            </ul>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Card 2: Statistik Singkat ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 Statistik Singkat</h3>", unsafe_allow_html=True)
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.metric("Jenis Penyakit", "6+1")
    stat_col2.metric("Algoritma", "CNN Xception")
    stat_col3.metric("Dataset", "Kaggle")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Card 3: Tips Cepat ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💡 Tips Cepat</h3>", unsafe_allow_html=True)
    st.markdown("""
        <ol>
            <li>Jaga kualitas air tetap bersih</li>
            <li>Berikan pakan bergizi</li>
            <li>Amati perubahan perilaku ikan</li>
        </ol>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br><center>✨ Dibuat dengan ❤️ menggunakan Streamlit ✨</center>", unsafe_allow_html=True)


# ======================
# ----- HALAMAN DETEKSI (REVISI UKURAN GAMBAR) -----
# ======================
elif page == "🔍 Deteksi Penyakit":
    st.title("🔍 Deteksi Penyakit Ikan")
    st.info("Unggah gambar ikan Anda untuk memulai deteksi. Untuk hasil terbaik, ikuti tips di samping.")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("Pilih atau seret gambar ikan ke sini", 
                                         type=["jpg", "jpeg", "png"])

    with col2:
        st.subheader("💡 Tips Foto Akurat")
        st.markdown("""
        - **Gunakan Cahaya Cukup:** Pastikan ikan terlihat jelas.
        - **Fokus Jelas:** Hindari gambar yang buram.
        - **Tampilkan Gejala:** Arahkan kamera pada bagian tubuh ikan yang aneh.
        - **Satu Ikan per Foto:** Fokus pada satu ikan untuk hasil terbaik.
        """)

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        with col1:
            # --- [PERUBAHAN DI SINI] ---
            # Ganti 'use_container_width=True' dengan 'width=500'
            st.image(img, caption="Gambar yang akan dideteksi", width=500) 
            
            if st.button("Deteksi Sekarang"):
                # (Sisa kode di bawah ini tetap sama seperti sebelumnya)
                with st.spinner('Menganalisis gambar...'):
                    pred_class, confidence = model_prediction(img)
                    label = idx_to_class[pred_class]
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = os.path.join(HISTORY_DIR, f"{timestamp}_{label}.jpg")
                    img.save(save_path)
                    
                    import pandas as pd
                    preds = model.predict(np.expand_dims(np.array(img.resize((299,299)))/255.0, axis=0))[0]
                    df = pd.DataFrame({
                        'Kelas': list(class_labels.keys()),
                        'Probabilitas': preds
                    }).sort_values(by='Probabilitas', ascending=False)
                    
                    fig = px.bar(
                        df, x='Probabilitas', y='Kelas', orientation='h',
                        title="Grafik Keyakinan per Kelas",
                        labels={'Probabilitas': 'Tingkat Keyakinan', 'Kelas': 'Jenis Penyakyt'},
                        text_auto='.2%'
                    )
                    fig.update_layout(xaxis_range=[0,1])
                    
                    with col2:
                        col2.empty() 
                        st.plotly_chart(fig, use_container_width=True)

                st.divider()
                st.success(f"Hasil Deteksi: **{label}**")
                st.info(f"Tingkat Keyakinan: {confidence*100:.2f}%")
                
                saran = saran_pengobatan.get(label, "Tidak ada saran spesifik.")
                with st.expander("🔬 **Lihat Detail dan Saran Penanganan**"):
                    st.markdown(saran)
    else:
        # (Bagian 'else' untuk menampilkan contoh gambar tetap sama)
        st.divider()
        st.subheader("Contoh Gambar Deteksi")
        ex_col1, ex_col2, ex_col3 = st.columns(3)
        # ... kode untuk menampilkan contoh gambar ...

# ======================
# ----- HALAMAN EDUKASI (VERSI DETAIL) -----
# ======================
elif page == "📚 Edukasi Penyakit":
    st.title("📚 Penjelasan Penyakit Ikan")
    st.markdown("Pelajari lebih lanjut tentang berbagai kondisi yang dapat mempengaruhi ikan air tawar, mulai dari penyebab, gejala, hingga cara penanganan dan pencegahannya.")

    # Membuat daftar nama tab yang lebih pendek agar rapi
    nama_penyakit_list = list(edukasi_lengkap.keys())
    nama_tabs = ["Red Disease", "Aeromoniasis", "Gill Disease", "Saprolegniasis", "Sehat", "Parasit", "White Tail"]
    
    # Membuat Tabs
    tabs = st.tabs(nama_tabs)

    # Mengisi konten untuk setiap tab
    for i, tab in enumerate(tabs):
        with tab:
            nama_full = nama_penyakit_list[i]
            konten = edukasi_lengkap[nama_full]
            
            st.header(nama_full)
            
            # Layout 2 kolom: gambar di kiri, deskripsi di kanan
            col1, col2 = st.columns([1, 2])
            
            with col1:
                try:
                    st.image(konten["img"], use_container_width=True)
                except FileNotFoundError:
                    st.warning(f"Gambar {konten['img']} tidak ditemukan.")

            with col2:
                if "nama_lain" in konten:
                    st.markdown(f"**Nama Lain:** *{konten['nama_lain']}*")
                st.markdown(f"**Penyebab:** {konten['penyebab']}")

            st.divider()

            # Bagian Detail di bawah gambar
            st.subheader("Gejala Umum")
            st.markdown(konten["gejala_umum"])
            
            st.subheader("Penanganan dan Pengobatan")
            st.markdown(konten["penanganan_dan_pengobatan"])

            st.subheader("Tips Pencegahan")
            st.markdown(konten["pencegahan"])

# ======================
# ----- HALAMAN RIWAYAT -----
# ======================
elif page == "📝 Riwayat":
    st.title("📝 Riwayat Deteksi")
    st.markdown("Berikut adalah riwayat gambar yang pernah Anda deteksi. Arahkan kursor ke gambar untuk melihat opsi hapus.")

    try:
        files = sorted(
            [f for f in os.listdir(HISTORY_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))],
            reverse=True
        )
    except FileNotFoundError:
        files = []

    if not files:
        st.info("Belum ada riwayat deteksi.")
    else:
        JUMLAH_KOLOM = 4
        cols = st.columns(JUMLAH_KOLOM)

        for i, file_name in enumerate(files):
            with cols[i % JUMLAH_KOLOM]:
                
                # --- [BAGIAN YANG DIPERBAIKI] ---
                # Logika parsing nama file yang lebih baik
                try:
                    parts = file_name.split('_')
                    timestamp_str = f"{parts[0]}_{parts[1]}"
                    # Gabungkan sisa bagian nama file, lalu hapus ekstensi .jpg/.png
                    label_part = "_".join(parts[2:])
                    label = os.path.splitext(label_part)[0]
                    
                    dt_object = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    formatted_time = dt_object.strftime("%d %B %Y, %H:%M")
                
                except (ValueError, IndexError):
                    # Jika format nama file tidak sesuai, tampilkan nama file tanpa ekstensi
                    label = os.path.splitext(file_name)[0]
                    formatted_time = "Tidak diketahui"

                # Gunakan CSS card
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                
                image_path = os.path.join(HISTORY_DIR, file_name)
                st.image(image_path, use_container_width=True)
                
                # Tampilkan informasi yang sudah diparsing dengan benar
                st.markdown(f"**Hasil:** `{label}`")
                st.caption(f"Waktu: {formatted_time}")
                
                if st.button("Hapus", key=file_name):
                    os.remove(image_path)
                    st.rerun() 

                st.markdown(f'</div>', unsafe_allow_html=True)

# ======================
# ----- HALAMAN TENTANG -----
# ======================
elif page == "ℹ️ Tentang":
    st.title("ℹ️ Tentang Aplikasi")
    st.markdown("""
        Aplikasi **IkanCheck** ini dikembangkan untuk membantu deteksi dini penyakit pada ikan air tawar menggunakan teknologi kecerdasan buatan.
        
        - **Model**: *Convolutional Neural Network* (CNN) dengan arsitektur Xception.
        - **Dataset**: Dilatih menggunakan dataset *'Fresh Water Fish Disease'* dari Kaggle.
        - **Framework**: Dibuat dengan menggunakan Streamlit.
        
        Semoga aplikasi ini dapat bermanfaat!
    """)