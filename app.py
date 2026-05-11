import streamlit as st

# ページ設定（タイトルやアイコン）
st.set_page_config(
    page_title="サービス終了のお知らせ",
    page_icon="⚠️",
    initial_sidebar_state="collapsed"
)

# CSSで中央寄せとデザイン調整
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding-top: 50px;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
        font-size: 20px;
        padding: 10px 30px;
        border-radius: 8px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# メインコンテンツ
st.container()
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.error("### ⚠️ サービス終了のお知らせ")
    
    st.markdown("""
    #### こちらのサイトはサービスを終了いたしました。
    ご利用誠にありがとうございました。
    
    現在は新しいサイトにてサービスを提供しております。 
    詳しくは、作者のTwitter(zawasow_vd)をご確認ください。 
    """)
    
    #st.write("") # スペース用
    
    # 新サイトのURLを指定
    # new_site_url = "https://your-new-site-url.streamlit.app" # ここを新しいURLに書き換えてください
    
    # ボタン形式のリンク

# 念のためフッターにコピーライトなど
st.divider()
st.caption("© 2026 Zawasow_lab")