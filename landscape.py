import streamlit as st
import pandas as pd
from io import BytesIO

#SetupPage
byfile = st.Page(
     page="byfile.py",
     title="Versi 2",
     icon="📁",
)

byfile2 = st.Page(
     page="byfile2_fotocustom.py",
     title="Versi 2.1",
     icon="📁",
)

discount = st.Page(
     page="discount.py",
     title="Discount",
     icon="💸",
)

bylist = st.Page(
     page="bylist.py",
     title="Versi 1",
     icon="📃",
     default=True,
)

salessuport = st.Page(
     page="salessupport.py",
     title="Sales Support",
     icon="📈",
)

TasKarung = st.Page(
     page="bylist3.py",
     title="Versi Tas&Karung",
     icon="📁",
)

FotoKT = st.Page(
     page="bylist2_fotokt.py",
     title="Versi 1.1 (Foto KT)",
     icon="📃",
)

Reqabdul = st.Page(
     page="bylist4.py",
     title="Versi 1.2 (3 Harga)",
     icon="📃",
)

pg = st.navigation({
     "Choose": [bylist, FotoKT, Reqabdul, byfile, byfile2, discount, TasKarung],
})

pg.run()