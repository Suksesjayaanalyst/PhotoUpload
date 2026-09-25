import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import streamlit as st
import textwrap
import zipfile
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread
import os

def load_all_images(base_folder):
    image_dict = {}

    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                item_code = os.path.splitext(file)[0].upper()
                full_path = os.path.join(root, file)
                image_dict[item_code] = full_path

    return image_dict

IMAGE_FOLDER = r"C:\Testing picture"
image_index = load_all_images(IMAGE_FOLDER)

st.set_page_config("Sukses Jaya - Create Photos")

# ===================== Google Sheets Data =====================
@st.cache_data
def get_data_from_google():
    with st.spinner("Getting data from Google Sheets..."):
        SERVICE_ACCOUNT_FILE = 'api.json'
        SCOPES = ['https://www.googleapis.com/auth/drive']

        credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('drive', 'v3', credentials=credentials)
        client = gspread.authorize(credentials)

        sheet = client.open_by_key("1YECf6N_v0AflBMMBjIEIW9Ckc15NJqqooz0tmnSsaJY")
        database = pd.DataFrame(sheet.sheet1.get_all_records())

        catalogue = pd.DataFrame(sheet.worksheet('CatalogueUpdate').get_all_records())
        catalogue['ItemCode'] = catalogue['ItemCode'].astype(str)
        return database, catalogue

# st.session_state.database = get_data_from_google()[0]
st.session_state.catalogue = get_data_from_google()[1]

# database = st.session_state.database
file_catalogue = st.session_state.catalogue
file_catalogue['U_Kategori'] = file_catalogue['U_Kategori'].astype(str)

# ===================== User File Upload =====================
st.title("Hai Everyone! made by: V")
st.write("Ini versi pake list, bikin List excel dengan:")
st.write("judul Column1 = 'ItemCode' (isinya list ItemCode yang ingin dibuat fotonya)")
st.write("judul Column2 = 'List' (ini akan menjadi nama foldernya) ")
st.warning("Update Photo memerlukan ± 10 menit (tergantung internet)")

file_upload = st.file_uploader("Upload File", type=["xlsx", "xls", "csv"])

if file_upload:
    try:
        if file_upload.name.endswith(('.xls', '.xlsx')):
            file_user = pd.read_excel(file_upload)
        else:
            file_user = pd.read_csv(file_upload)

        file_user['ItemCode'] = file_user['ItemCode'].astype(str)
        start2 = st.button("Start Now")
    except Exception as e:
        st.error(f"Error reading files: {e}")
        st.stop()
else:
    st.warning("Please Upload all files.")
    st.stop()

# ===================== Select Price Option =====================
selectprice = st.selectbox(
    "Select", options=['Harga Under', 'HargaLusin', 'HargaSpecial']
)

# ===================== Image Creation Functions =====================
font_path = "./Poppins-Regular.ttf"
font_harga = ImageFont.truetype("./Poppins-SemiBold.ttf", size=20)
current_font = ImageFont.truetype(font_path, size=20)

if selectprice == 'Harga Under':
    colour = (255,163,208)  # Pink
elif selectprice == 'HargaLusin':
    colour = (250, 225, 135)  # Orange
elif selectprice == 'HargaSpecial':
    colour = (154,210,172)  # Green

def wrap_text(text, font, max_width):
    wrapped_text = textwrap.fill(
        text, width=max_width // (font.getbbox('a')[2] - font.getbbox('a')[0])
    )
    return wrapped_text.splitlines()

def add_image(img_path, row):
    template = Image.new("RGBA", (800, 1200), "white")
    img = Image.open(img_path).convert("RGBA").resize((750, 750))
    image_x = (template.width - img.width) // 2
    image_y = 25

    # Add logo for specific categories
    if row['U_Kategori'] == 'AKSESORIS RAMBUT KAMINO':
        image_y = 100
        logo = Image.open("./logo-kamino-for-web-new.png").convert("RGBA").resize((200, 100))
        template.paste(logo, ((template.width - logo.width)//2, 0), logo)

    if row['U_Kategori'] == 'LOLI & MOLI':
        image_y = 100
        logo = Image.open("./Lolimoli Logo-02.png").convert("RGBA").resize((150, 75))
        template.paste(logo, ((template.width - logo.width)//2, 15), logo)

    template.paste(img, (image_x, image_y))
    return template

def add_text(template, draw, row, font, selectprice):
    item_code = row['ItemCode']
    item_name = row['ItemName']
    try:
        price = float(row[selectprice])
        harga_jual = f"Rp. {price:,.0f} / {row['Uom']}"
    except:
        harga_jual = f"Rp. {row[selectprice]} / {row['Uom']}"
    ctn = f"Isi Karton: {int(row['IsiCtn'])} {row['Uom']}" if pd.notna(row['IsiCtn']) else "N/A"

    lines_item_code = wrap_text(item_code, font, max_width=450)
    lines_item_name = wrap_text(item_name, font, max_width=450)
    lines_harga_jual = wrap_text(harga_jual, font, max_width=450)
    lines_ctn = wrap_text(ctn, font, max_width=450)
    all_lines = lines_item_code + lines_item_name + lines_harga_jual + lines_ctn

    background_width = 735
    background_margin = 10
    corner_radius = 15
    x_position = 32.5
    y_start = 825 if row['U_Kategori'] not in ['AKSESORIS RAMBUT KAMINO', 'LOLI & MOLI'] else 900

    total_text_height = sum(draw.textbbox((0,0), line, font=font)[3] for line in all_lines)
    total_height = total_text_height + (len(all_lines)+1) * 2 * background_margin

    draw.rounded_rectangle(
        [(x_position-background_margin, y_start), (x_position+background_width+background_margin, y_start+total_height)],
        fill=colour,
        radius=corner_radius
    )

    y_offset = y_start + background_margin
    for line in all_lines:
        if line in lines_item_code or line in lines_harga_jual:
            fnt = font_harga
        else:
            fnt = current_font

        text_width, text_height = draw.textbbox((0,0), line, font=fnt)[2:4]
        text_x = x_position + (background_width - text_width)//2
        draw.text((text_x, y_offset), line, font=fnt, fill="black")
        y_offset += text_height + 2 * background_margin

# ===================== Start Image Generation =====================
if start2:
    with st.spinner("Processing data..."):
        file_user['ItemCode'] = file_user['ItemCode'].astype(str).str.upper()

        selected_df = pd.merge(
            file_user,
            file_catalogue[['ItemCode','ItemName','Uom','IsiCtn','U_Kategori',
                            'Harga Under','HargaLusin','HargaKoli','HargaSpecial']],
            on='ItemCode', how='left'
        )

        df_kosong = selected_df[~selected_df['ItemCode'].apply(
            lambda x: x in image_index
        )]

        selected_df = selected_df[selected_df['ItemCode'].apply(
            lambda x: x in image_index
        )]

        st.write("Yang dibuat:")
        st.dataframe(selected_df)
        st.write("Yang Tidak ada di Google Drive:")
        st.dataframe(df_kosong)

    with st.spinner("Creating images..."):
        category_dict = {}
        image_paths = []

        for _, row in selected_df.iterrows():
            img_path = image_index.get(row['ItemCode'])
            if not os.path.exists(img_path):
                st.warning(f"Image not found: {row['ItemCode']}")
                continue

            img_template = add_image(img_path, row)
            draw = ImageDraw.Draw(img_template)
            add_text(img_template, draw, row, current_font, selectprice)

            buf = BytesIO()
            img_template.save(buf, format='PNG')
            buf.seek(0)

            file_name = f"{row['ItemCode']}.jpg"
            image_paths.append((file_name, buf.getvalue()))
            category = row['List']
            category_dict.setdefault(category, []).append((file_name, buf.getvalue()))

        if image_paths:
            st.image(image_paths[0][1])

    with st.spinner("Creating ZIP file..."):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for category, files in category_dict.items():
                for file_name, image_data in files:
                    zipf.writestr(f"{category}/{file_name}", image_data)

        zip_buffer.seek(0)
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="Ready_to_Upload.zip",
            mime="application/zip"
        )