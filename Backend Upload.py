import streamlit as st
import pandas as pd
from io import BytesIO

#SetupPage
Versi1 = st.Page(
     page="Upload foto bagus.py",
     title="Versi 1",
     icon="📃",
     default=True,
)

Versi2 = st.Page(
     page="Upload foto KT.py",
     title="Versi 1.1 (Foto KT)",
     icon="📃",
)

pg = st.navigation({
     "Choose": [Versi1, Versi2],
})

pg.run()