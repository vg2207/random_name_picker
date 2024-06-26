import streamlit as st
import pandas as pd
import time
import random
from io import BytesIO
import xlsxwriter
from streamlit_option_menu import option_menu 


def lowerify_and_upperify_cols(data, lower, upper) :
    lowerify_cols = [col for col in data if col in lower]
    upperify_cols = [col for col in data if col in upper]
    data[lowerify_cols] = data[lowerify_cols].apply(lambda x: x.astype(str).str.lower())
    data[upperify_cols] = data[upperify_cols].apply(lambda x: x.astype(str).str.upper())
    return data

def remove_duplicate(data, drop_col) :
    data = data.drop_duplicates(subset=[drop_col], keep="last")
    return data



st.set_page_config(layout="wide")





user_input_excel = st.sidebar.file_uploader("Upload an excel", type=['csv','xlsx'], accept_multiple_files=False, key='file_uploader')


if user_input_excel is not None:
    if user_input_excel.name.endswith('.csv'):
        df=pd.read_csv(user_input_excel)
        st.sidebar.success('File Uploaded Successfully!')
        # st.sidebar.write(df)
        lower_col = []
        upper_col = ['ID Karyawan', 'Nama Lengkap']
        df = lowerify_and_upperify_cols(df, lower_col, upper_col)
        df = remove_duplicate(df, drop_col='ID Karyawan')
    elif user_input_excel.name.endswith('.xlsx'):
        df=pd.read_excel(user_input_excel)
        st.sidebar.success('File Uploaded Successfully!')
        # st.sidebar.write(df)
        lower_col = []
        upper_col = ['ID Karyawan', 'Nama Lengkap']
        df = lowerify_and_upperify_cols(df, lower_col, upper_col)
        df = remove_duplicate(df, drop_col='ID Karyawan')
    else:
        st.sidebar.warning('You need to upload a csv or an excel file')
    
    # with st.sidebar:
    # selected_main_menu = option_menu(menu_title = None, #"Main Menu"
    #                 options = ["Settings", "Run Apps"],
    #                 icons = ["gear", "caret-right-square"],
    #                 menu_icon = "cast",
    #                 default_index = 0,
    #                 orientation = "horizontal"
    #             )
        

    ## --- TAB 

    tab1, tab2 = st.tabs(["Setting", "Run Apps"])
    with tab1 :
    # if selected_main_menu == "Settings" :

        with st.container():
            user_input_seed = st.number_input("Pick random seed number", 1)
        col_1, col_2 = st.columns(2)
        with st.container():
            with col_1:
                user_input_winner = st.number_input("Pick number of winner(s)", 1, len(df))
        with st.container():
            with col_2:
                user_input_prize = st.number_input("Pick number of prize(s) in Rupiah", 0, 1000000000, step=50000, format='%g')


        data = {
        "Number of Winner(s)": [],
        "Prize": []
        }


        if 'df1' not in st.session_state:
            df1 = pd.DataFrame(data)
            st.session_state.df1 = df1

        df1 = st.session_state.df1


        col_5, col_6, col_7 = st.columns(3)
        with col_5 :
            button_clicked_5 = st.button("Save", type="secondary", use_container_width=True)
        with col_6 :
            button_clicked_6 = st.button("Resets", type="secondary", use_container_width=True)
        with col_7 :
            button_clicked_7 = st.button("Submit", type="primary", use_container_width=True)

        if button_clicked_5 :
            new_row = pd.DataFrame({"Number of Winner(s)": [user_input_winner],"Prize": [user_input_prize]})
            st.session_state.df1 = pd.concat([st.session_state.df1, new_row])
            st.sidebar.write(st.session_state.df1)

        if button_clicked_6 :
            st.session_state.df1 = pd.DataFrame(data)



        if button_clicked_7 :

            st.session_state.user_input_seed = user_input_seed

            st.sidebar.markdown(f"Random seed = {st.session_state.user_input_seed}")


            df2 = st.session_state.df1.copy().reset_index(drop=True)
            
            st.session_state.df2 = df2
            # df2 = st.session_state.df2

            st.sidebar.write(st.session_state.df2)
            # df2.to_csv('winner_parameter.csv')

            


    with tab2 :
    # else :
        
        if 'count' not in st.session_state:
            st.session_state.count = 0

        def increment_counter():
            st.session_state.count += 1

        def reset_counter():
            st.session_state.count -= st.session_state.count
        
        try :
            df2 = st.session_state.df2
            t = 30
            df3 = df.copy()
            winners_name_all = []

            random.seed(st.session_state.user_input_seed)
            for i in range(len(df2)):
                winners_row = random.sample(range(len(df3)),int(df2["Number of Winner(s)"][i]))
                winners_name = df3.iloc[winners_row]
                prize = df2["Prize"][i]
                # st.markdown(f'won {prize}')
                # st.write(winners_name)
                df3 = df3.drop(winners_row).reset_index(drop=True)
                # st.write(df3)
                winners_name_all.append(winners_name)


            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer: 
                for i in range(len(df2)) :
                    sheetname = 'Round ' + str(int(i+1)) + ' - Winner Rp ' + str(int(df2.loc[i, 'Prize']))
                    winners_data = winners_name_all[i].reset_index(drop=True)
                    winners_data.index = winners_data.index + 1
                    winners = winners_data.to_excel(writer, sheet_name=sheetname)
                    

            # col_3, col_4, col_8 = st.columns([1,1,1])
            col_3, col_4 = st.columns([1,1])
            with col_3 :
                button_clicked = st.button("Start", type="primary", use_container_width=True, on_click=increment_counter)
            with col_4 :
                button_clicked_2 = st.button("Reset", type="secondary", use_container_width=True, on_click=reset_counter)
            # with col_8 :
            #     button_clicked_8 = st.download_button(label=':cloud: Download winners', type="secondary", data=output.getvalue(),file_name='winners.xlsx')
            button_clicked_8 = st.sidebar.download_button(label=':cloud: Download winners', type="secondary", data=output.getvalue(),file_name='winners.xlsx')

            

            if button_clicked: 
                
                if st.session_state.count <= len(df2) :
                    with st.empty():
                        while t :
                            if t > 0 :
                                with st.empty():
                                    name_show = df.iloc[random.randint(1, len(df)) - 1]
                                    
                                    st.markdown(f"<h1 style='text-align: center;'>{str(name_show['Nama Lengkap'])}</h1>", unsafe_allow_html=True)
                                time.sleep(0.1)
                                t -= 1
                                st.empty()
                    row_number_to_show = st.session_state.count - 1
                    data_to_show = winners_name_all[row_number_to_show].reset_index(drop=True)
                    data_to_show.index += 1
                    prize_to_choose = st.session_state.df2.copy()
                    prize_to_show = prize_to_choose.loc[st.session_state.count-1, 'Prize']
                    st.markdown(f"<h1 style='text-align: center;'>Pemenang Hadiah Senilai Rp {str(int(prize_to_show))} adalah</h1>", unsafe_allow_html=True)
                    # st.header(f"Pemenang Hadiah Senilai Rp {str(int(prize_to_show))} adalah")
                    with st.container():
                        st.dataframe(data_to_show[["ID Karyawan", "Nama Lengkap", "Perusahaan"]], use_container_width=True)

                    # for m in range(len(data_to_show)) :
                    #     st.text_area("", 
                    #     f"""
                    #     {str(data_to_show.loc[m+1, 'ID Karyawan'])}
                    #     {str(data_to_show.loc[m+1, 'Nama Lengkap'])}
                    #     {str(data_to_show.loc[m+1, 'Perusahaan'])}""",
                    #     height = 150)
                    # # for m in range(len(data_to_show)//5) :
                    # # acol1, acol2, acol3, acol4, acol5 = st.columns(1)
                    # with st.container() :
                        
                    #     st.markdown("""
                    #     <html>
                    #     <head>
                    #     <style>
                    #     .grid-container {
                    #     display: grid;
                    #     grid-template-columns: auto auto auto auto auto;
                    #     background-color: #2196F3;
                    #     padding: 10px;
                    #     }

                    #     .grid-item {
                    #     background-color: rgba(255, 255, 255, 0.8);
                    #     border: 1px solid rgba(0, 0, 0, 0.8);
                    #     padding: 20px;
                    #     font-size: auto;
                    #     text-align: center;
                    #     }
                    #     </style>
                    #     </head>
                    #     <body>

                    #     <div class="grid-container">
                    #     <div class="grid-item">{{ data_to_show.loc[1,'Nama Lengkap'] }}</div>
                    #     <div class="grid-item">2</div>
                    #     <div class="grid-item">3</div>  
                    #     <div class="grid-item">4</div>
                    #     <div class="grid-item">5</div>
                    #     <div class="grid-item">6</div>  
                    #     <div class="grid-item">7</div>
                    #     <div class="grid-item">8</div>
                    #     <div class="grid-item">9</div>
                    #     <div class="grid-item">10</div>  
                    #     <div class="grid-item">{}</div>
                    #     <div class="grid-item">12</div>
                    #     <div class="grid-item">13</div>  
                    #     <div class="grid-item">14</div>
                    #     <div class="grid-item">15</div>
                    #     <div class="grid-item">16</div>  
                    #     <div class="grid-item">17</div>
                    #     <div class="grid-item">18</div>
                    #     <div class="grid-item">19</div>
                    #     <div class="grid-item">20</div>
                    #     </div>

                    #     </body>
                    #     </html>

                    #     """, unsafe_allow_html=True)
                        

                else :
                    with st.empty():
                        st.markdown(f"<h1 style='text-align: center;'>CONGRATS TO ALL THE WINNERS!</h1>", unsafe_allow_html=True)

                
                # st.write('Count = ', st.session_state.count)
                st.balloons()
        except :
            st.error('You need to submit the number of winners and prize')
        
        



else :
    st.error("You have to upload a csv or an excel file in the sidebar")




