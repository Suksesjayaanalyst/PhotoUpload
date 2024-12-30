import streamlit as st
import pandas as pd
from io import BytesIO

#SetupPage
byfile = st.Page(
     page="byfile.py",
     title="Versi 2",
     icon="📁",

)


bylist = st.Page(
     page="bylist.py",
     title="Versi 1",
     icon="📃",
     default=True,
)


pg = st.navigation({
    "Choose": [bylist, byfile],

})




pg.run()



