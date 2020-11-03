import pandas as pd
import os
from os import path
import datetime as dt

from src.dataframe_analysis import df_setup
from src.misc import print_separator_line


def file_to_csv_format(file_path: str, is_apple: bool) -> str:
    out_file_path = file_path.replace(".txt", ".tmp")

    with open(file_path, "r") as in_file:
        with open(out_file_path, "w") as out_file:

            this_line = in_file.readline()
            next_line = in_file.readline()

            out_file.write("datetime|author|message\n")

            if is_apple:
                while next_line:

                    if "‎" in this_line:
                        this_line = next_line
                        next_line = in_file.readline()
                        continue

                    valid_next_line: bool = (
                            next_line.count("[") == 1 and
                            next_line.count("]") == 1 and
                            next_line.split("] ", 1)[0].count(":") == 2
                    )

                    if not valid_next_line:
                        this_line = this_line.replace("\n", "__n__") + next_line.replace("\n", "__n__") + "\n"
                        next_line = in_file.readline()
                        continue

                    this_line = this_line.replace("|", "__x__")
                    this_line = this_line.replace("*", "__a__")
                    this_line = this_line.replace('"', "__vv__")
                    this_line = this_line.replace("'", "__v__")
                    this_line = this_line.replace("“", "__vv__")

                    if "PM" in this_line.split("] ", 1)[0]:
                        hour_str = this_line.split(", ", 1)[1].split(":", 1)[0]
                        hour = int(hour_str)
                        if hour != 12:
                            hour += 12

                        this_line = this_line.split(", ", 1)[0] + ", " + str(hour) + ":" + this_line.split(":", 1)[1]
                        this_line = this_line.replace("PM", "AM", 1)

                    this_line = this_line.replace("[", "", 1) \
                        .replace(", ", " ", 1)\
                        .replace(" AM] ", "|", 1)\
                        .replace(": ", "|", 1)

                    out_file.write(this_line)

                    this_line = next_line
                    next_line = in_file.readline()
            else:
                while next_line:

                    if "‎" in this_line or this_line.count(":") < 2 or "Hai cambiato l'oggetto da “" in this_line:
                        this_line = next_line
                        next_line = in_file.readline()
                        continue

                    valid_next_line: bool = (
                            next_line.split(",", 1)[0].count("/") == 2
                    )

                    if not valid_next_line:
                        this_line = this_line.replace("\n", "__n__") + next_line.replace("\n", "__n__") + "\n"
                        next_line = in_file.readline()
                        continue

                    this_line = this_line.replace("|", "__x__")
                    this_line = this_line.replace("*", "__a__")
                    this_line = this_line.replace('"', "__vv__")
                    this_line = this_line.replace("“", "__vv__")
                    this_line = this_line.replace("'", "__v__")

                    this_line = this_line.replace(", ", " ", 1) \
                        .replace(" - ", ":00|", 1) \
                        .replace(": ", "|", 1)

                    out_file.write(this_line)

                    this_line = next_line
                    next_line = in_file.readline()
    return out_file_path


def load_data_frame(file_path: str, is_apple: bool) -> pd.DataFrame:

    # If the backup .frames folder does not exist, I create one
    if not path.isdir("../chats/.frames"):
        os.mkdir("../chats/.frames")

    # The backup file has the same name as the original but is .zip file and is
    # saved in the .frames folder
    dataframe_file_path = file_path.replace(".txt", "") + ".zip"
    dataframe_file_path = dataframe_file_path.replace("chats/", "chats/.frames/")

    if path.isfile(dataframe_file_path):  # if the file exists it needs to be pickled

        print("LOADING BACKUP..")
        beginning = dt.datetime.now()
        df = pd.read_pickle(dataframe_file_path)
        print("It took", (dt.datetime.now() - beginning).microseconds / 1000, "ms to load the pickled dataset")

        beginning = dt.datetime.now()
        print("It took", (dt.datetime.now() - beginning).microseconds / 1000, "ms to create the df_info dictionary")

        print("BACKUP LOADED")

    else:  # Otherwise, we have to create the dataframe and store is as a pickle file

        print("CREATING CSV FORMATTED FILE")
        beginning = dt.datetime.now()
        temp_file_path = file_to_csv_format(file_path, is_apple)  # Transforms the input file into a csv file
        print("It took", (dt.datetime.now() - beginning).microseconds / 1000, "ms to create the CSV file")

        print("LOADING DATAFRAME FROM CSV")
        beginning = dt.datetime.now()
        df = pd.read_csv(temp_file_path, sep="|")  # Reads the csv into a dataframe
        print("It took", (dt.datetime.now() - beginning).microseconds / 1000, "ms to create the CSV file")

        df = df_setup(df)

        os.remove(temp_file_path)  # Deletes the csv file because it's not helpful anymore

        beginning = dt.datetime.now()
        df.to_pickle(dataframe_file_path)  # Pickles the dataframe into a zip file and saves it
        print("It took", (dt.datetime.now() - beginning).microseconds /1000, "ms to pickle the dataframe")

        print("BACKUP SAVED AT", dataframe_file_path)

    print("FRAME LOADED")
    print_separator_line()
    print_separator_line()
    return df


def print_example(file_path: str, n: int):
    print("An example of the dataframe")
    with open(file_path, "r") as file:
        i = 0
        for i in range(n):
            print(file.readline())
