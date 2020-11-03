import src.dataframe_analysis as analysis
from src.file_handler import print_example, load_data_frame
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':

    pd.set_option('display.max_colwidth', 300)

    # Reading the file path from the user input
    # file_path: str = input("Insert the name of the chat you want to analyze:")
    # file_path = "../chats/" + file_path + ".txt"
    # while not path.isfile(file_path):
    #     print("NOT AN EXISTING PATH")
    #     file_path: str = input("Insert the name of the chat you want to analyze:")
    #     file_path = "../chats/" + file_path + ".txt"
    #
    # # Reading if the file is a iOS file from the user input
    # is_apple_input: str = input("Is the chat file generated from an iOS device?")
    # is_apple: bool = (is_apple_input == "y" or is_apple_input == "Y" or is_apple_input == "1")

    file_path = "../chats/Sara_Gotti.txt"
    is_apple = False

    df = load_data_frame(file_path, is_apple)

    # filtered = analysis.filter(df, words_or=["hu", "Hu", "HU"])
    # print(filtered[["author", "message"]])

    analysis.df_general_info(df)
    # analysis.df_length_info(df)
    # analysis.df_plot_month_year(df, start="03-2015", end="12-2015")
    # analysis.df_plot_month_year(df, auto=True)
    analysis.df_plot_year(df)
    # analysis.df_plot_days(df, auto=True)
    # analysis.df_emojis(df)
    # analysis.df_words(df)

    # analysis.df_month_analysis(df, month="5", year="2020")
