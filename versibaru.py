import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import streamlit as st
import textwrap
import zipfile
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread

st.set_page_config("Sukses Jaya - Versi3 - Create Photos")

# -----------------------------
# Get data from Google Sheet
# -----------------------------
@st.cache_data
def get_data_from_google():
    SERVICE_ACCOUNT_FILE = 'api.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    client = gspread.authorize(credentials)
    
    # Database sheet (uploaded files info)
    sheet = client.open_by_key("18t23AKiAQmK4A4dmkwqYTOGj4gNuFMEAsBpY50zJLNY")
    database_sheet = sheet.sheet1
    database = pd.DataFrame(database_sheet.get_all_records())
    
    # Catalogue sheet (master product data)
    catalogue_sheet = sheet.worksheet('CatalogueUpdate')
    catalogue = pd.DataFrame(catalogue_sheet.get_all_records())
    catalogue['ItemCode'] = catalogue['ItemCode'].astype(str)
    
    return database, catalogue

database, catalogue = get_data_from_google()

# -----------------------------
# Upload Excel
# -----------------------------
st.title("Sukses Jaya - Versi3")
st.write("Upload Excel dengan 3 kolom: `ItemCode`, `List`, `HargaBaruLusin`, `HargaBaruKoli`")
file_upload = st.file_uploader("Upload file", type=["xlsx", "xls", "csv"])

if file_upload:
    try:
        if file_upload.name.endswith(('.xls', '.xlsx')):
            file_user = pd.read_excel(file_upload)
        else:
            file_user = pd.read_csv(file_upload)
        file_user['ItemCode'] = file_user['ItemCode'].astype(str).str.upper()
        start_button = st.button("Start Now")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    st.warning("Please upload an Excel file with ItemCode, List, HargaBaruLusin, HargaBaruKoli.")
    st.stop()

# -----------------------------
# Select old price type
# -----------------------------
price_options = ['Harga Under', 'HargaLusin', 'HargaSpecial']
select_price = st.selectbox("Select Old Price Column", price_options)

# -----------------------------
# Start processing
# -----------------------------
if start_button:
    with st.spinner("Preparing data..."):
        database['ItemCode'] = database['ItemCode'].astype(str).str.upper()
        database['Upload Date'] = pd.to_datetime(database['Upload Date'], errors='coerce')
        # Keep latest image per ItemCode
        database = database.loc[database.groupby('ItemCode')['Upload Date'].idxmax()]
        # Merge uploaded Excel with database to get image links
        merged_df = pd.merge(file_user, database[['ItemCode','Link']], on='ItemCode', how='left')
        missing = merged_df[merged_df['Link'].isna()]
        merged_df = merged_df[~merged_df['Link'].isna()]
        # Merge with catalogue for product info & old price
        merged_df = pd.merge(merged_df, catalogue[['ItemCode','ItemName','Uom','IsiCtn','U_Kategori', 'U_KonversiBeli', 'Harga Under','HargaLusin','HargaKoli','HargaSpecial']], on='ItemCode', how='left')
        st.write("Items to be created:")
        st.dataframe(merged_df)
        if not missing.empty:
            st.write("Items not found in Google Drive:")
            st.dataframe(missing)

    # -----------------------------
    # Fonts & Colors
    # -----------------------------
    font_path = "./Poppins-Regular.ttf"
    font_harga = ImageFont.truetype("./Poppins-SemiBold.ttf", size=18)
    current_font = ImageFont.truetype(font_path, size=18)
    font = ImageFont.truetype(font_path, size=18)
    colour = (214,225,242)  # Background color

    # -----------------------------
    # Functions for images
    # -----------------------------
    def wrap_text(text, font, max_width):
        wrapped = textwrap.fill(text, width=max_width // (font.getbbox('a')[2]-font.getbbox('a')[0]))
        return wrapped.splitlines()

    def add_image(img_url, row):
        try:
            template = Image.new("RGBA", (800,1050), "white")
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            img = img.resize((750,750))
            image_x = (template.width - img.width)//2
            image_y = 25
            if row['U_Kategori'] == 'AKSESORIS RAMBUT KAMINO':
                image_y = 100
                logo = Image.open("./logo-kamino-for-web-new.png").convert("RGBA").resize((200,100))
                template.paste(logo, ((template.width - logo.width)//2, 0), logo)
            if row['U_Kategori'] == 'LOLI & MOLI':
                image_y = 100
                logo = Image.open("./Lolimoli Logo-02.png").convert("RGBA").resize((150,75))
                template.paste(logo, ((template.width - logo.width)//2, 15), logo)
            template.paste(img, (image_x, image_y))
            return template
        except Exception as e:
            st.error(f"Error loading image: {e} ({row['ItemCode']})")
            return None

    def add_text(template, draw, row):
        # -----------------------------
        # Fonts & layout
        # -----------------------------
        label_font = current_font
        value_font = current_font
        price_font = font_harga

        x_pos = 32.5
        y_start = 825
        if row['U_Kategori'] in ['AKSESORIS RAMBUT KAMINO', 'LOLI & MOLI']:
            y_start = 900

        label_x = x_pos + 10
        line_spacing = 10

        # -----------------------------
        # Prepare text data
        # -----------------------------
        rows = []

        # Item code (full width, no colon)
        rows.append({
            "type": "full",
            "text": row['ItemCode'],
            "font": price_font
        })

        # Nama Barang
        rows.append({
            "type": "pair",
            "label": "Nama Barang",
            "value": row['ItemName'],
            "font": value_font
        })

        # Harga Grosir
        if pd.notna(row['HargaLusin']):
            old_price = f"Rp. {float(row['HargaLusin']):,.0f}/{row['Uom']}"
            new_price = f"Rp. {float(row['HargaBaruLusin']):,.0f}/{row['Uom']} isi {row['U_KonversiBeli']} pcs"
            rows.append({
                "type": "pair",
                "label": "Harga Grosir",
                "value": f"{old_price} => {new_price}",
                "font": value_font,
                "strike": old_price
            })

        # Harga Koli
        if pd.notna(row['HargaKoli']):
            old_price = f"Rp. {float(row['HargaKoli']):,.0f}/{row['Uom']}"
            new_price = f"Rp. {float(row['HargaBaruKoli']):,.0f}/{row['Uom']} isi {row['U_KonversiBeli']} pcs"
            rows.append({
                "type": "pair",
                "label": f"1 Koli = {row['IsiCtn']} Set",
                "value": f"{old_price} => {new_price}",
                "font": value_font,
                "strike": old_price
            })

        # Note
        rows.append({
            "type": "full",
            "text": "Variasi warna tampak pada gambar",
            "font": value_font
        })

        # -----------------------------
        # Calculate dynamic colon tab stop
        # -----------------------------
        max_label_width = max(
            draw.textlength(r["label"], font=r["font"])
            for r in rows if r["type"] == "pair"
        )

        colon_x = label_x + max_label_width + 50
        value_x = colon_x + 15

        # -----------------------------
        # Calculate background height
        # -----------------------------
        total_height = 0
        wrapped_rows = []

        for r in rows:
            if r["type"] == "full":
                lines = wrap_text(r["text"], r["font"], 700)
                wrapped_rows.append((r, lines))
                for line in lines:
                    total_height += draw.textbbox((0, 0), line, font=r["font"])[3] + line_spacing
            else:
                lines = wrap_text(r["value"], r["font"], 700)
                wrapped_rows.append((r, lines))
                for line in lines:
                    total_height += draw.textbbox((0, 0), line, font=r["font"])[3] + line_spacing

        margin = 15
        bg_width = 735
        rect_coords = [
            (x_pos, y_start),
            (x_pos + bg_width, y_start + total_height + margin)
        ]

        # draw.rounded_rectangle(
        #     rect_coords,
        #     fill=colour,
        #     radius=15
        # )

        # -----------------------------
        # Draw text
        # -----------------------------
        y_offset = y_start + margin

        for r, lines in wrapped_rows:
            if r["type"] == "full":
                for line in lines:
                    draw.text((label_x, y_offset), line, font=r["font"], fill="black")
                    y_offset += draw.textbbox((0, 0), line, font=r["font"])[3] + line_spacing
            else:
                # Draw label & colon once
                draw.text((label_x, y_offset), r["label"], font=r["font"], fill="black")
                draw.text((colon_x, y_offset), ":", font=r["font"], fill="black")

                for i, line in enumerate(lines):
                    draw.text((value_x, y_offset), line, font=r["font"], fill="black")

                    # Strike-through old price (only first line)
                    if i == 0 and "strike" in r:
                        strike_width = draw.textlength(r["strike"], font=r["font"])
                        text_height = draw.textbbox((0, 0), line, font=r["font"])[3]
                        line_y = y_offset + text_height // 2

                        draw.line(
                            [value_x, line_y, value_x + strike_width, line_y],
                            fill="red",
                            width=2
                        )

                    y_offset += draw.textbbox((0, 0), line, font=r["font"])[3] + line_spacing

    # -----------------------------
    # Generate images & ZIP
    # -----------------------------
    with st.spinner("Creating images..."):
        category_dict = {}
        image_paths = []

        for _, row in merged_df.iterrows():
            img = add_image(row['Link'], row)
            if img is None:
                continue
            draw = ImageDraw.Draw(img)
            add_text(img, draw, row)
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            file_name = f"{row['ItemCode']}.jpg"
            category = row['List']
            if category not in category_dict:
                category_dict[category] = []
            category_dict[category].append((file_name, buf.getvalue()))
            image_paths.append((file_name, buf.getvalue()))

        if image_paths:
            st.image(image_paths[0][1])

    # -----------------------------
    # Create ZIP for download
    # -----------------------------
    with st.spinner("Creating ZIP file..."):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for category, files in category_dict.items():
                for file_name, data in files:
                    zipf.writestr(f"{category}/{file_name}", data)
        zip_buffer.seek(0)

        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="Ready_to_Upload_Versi3.zip",
            mime="application/zip"
        )