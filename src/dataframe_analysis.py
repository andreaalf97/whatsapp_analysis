import pandas as pd

from src import misc
from src.misc import print_separator_line
import datetime as dt
import matplotlib.pyplot as plt
import wordcloud
from stop_words import get_stop_words
import emojis
from operator import add


def df_general_info(df: pd.DataFrame):

    counts = {author: len(frame) for author, frame in df.groupby(df["author"])}

    print("There are", len(counts), "different authors in this chat")

    for author in counts:
        print(author, "has written", counts[author], "messages")

    print_separator_line()

    print("You have exchanged", str(len(df)), " messages between ", str(df.iloc[0].datetime), "and", str(df.iloc[-1].datetime))

    print_separator_line()

    print(len(df[df.isMedia == False]), "text objects")
    print(len(df[df.isMedia == True]), "media objects")


def df_length_info(df: pd.DataFrame):
    index_longest = df.length.sort_values().index[-1]
    index_shortest = df.length.sort_values().index[0]

    print("Shortest message is #" + str(index_shortest) + " with a length of " + str(
        len(df.iloc[index_shortest].message)) + ":")
    print(df.iloc[index_shortest].message)

    print_separator_line()

    print("Longest message is #" + str(index_longest) + " with a length of " + str(
        len(df.iloc[index_longest].message)) + ":")
    print(df.iloc[index_longest].message)


def bar(x: list, y: list, xlabel, ylabel, color='b', rotation='vertical'):

    if type(y[0])==list:
        for i in range(len(y)):
            plt.bar(x, y[i], align='center')
    else:
        plt.bar(x, y, align='center', color=color)
    plt.xticks(rotation='vertical')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def df_plot_month_year(df: pd.DataFrame, start="01-2000", end="12-2050", auto=False):

    if auto:
        max_size = 0
        for year, frame in df.groupby(df["datetime"].dt.year):
            if len(frame) > max_size:
                max_size = len(frame)
                max_year = int(year)
        start = "06-" + str(max_year-1)
        end = "06-" + str(max_year+1)
        print("Max year is", max_year)

    start = dt.datetime.strptime(start, "%m-%Y")
    end = dt.datetime.strptime(end, "%m-%Y")

    dates = []
    counts = []

    for frame in df.groupby([df["datetime"].dt.year, df["datetime"].dt.month]):

        if frame[1].iloc[0]["datetime"] < start or frame[1].iloc[0]["datetime"] > end:
            continue

        # frame[0] contains (year, month)
        # frame[1] contains the full dataframe with those years and months only
        dates.append(str(frame[0][0]) + "-" + str(frame[0][1]))
        counts.append(len(frame[1]))

    bar(dates, counts, "Date", "Total number of messages", color='r')


def df_plot_year(df: pd.DataFrame):
    dates = []
    counts_per_author = {}

    for author in df_get_author_list(df):
        counts_per_author[author] = []

    for year, year_frame in df.groupby(df["datetime"].dt.year):
        dates.append(str(year))
        for author, frame in year_frame.groupby(year_frame["author"]):
            counts_per_author[author].append(len(frame))

    tots = [0 for x in dates]
    for author in counts_per_author:
        counts_per_author[author] = list(map(add, counts_per_author[author], tots))
        tots = counts_per_author[author]
        plt.bar(dates, counts_per_author[author], label=author)

    plt.xlabel("Year")
    plt.ylabel("Total number of messages")
    plt.legend()
    plt.show()


def df_emojis(df: pd.DataFrame, n=5):

    print("EMOJI ANALYSIS")

    author_counters = {}
    all_emojis = {}

    for author in df_get_author_list(df):
        author_counters[author] = {}

    for row in df.iterrows():
        emoji_list = row[1]["emojis"]
        author = row[1]["author"]

        if emoji_list:
            for emoji in emoji_list:
                if emoji in author_counters[author]:
                    author_counters[author][emoji] += 1
                else:
                    author_counters[author][emoji] = 1
                if emoji in all_emojis:
                    all_emojis[emoji] += 1
                else:
                    all_emojis[emoji] = 1

    all_emojis = {k: v for k, v in sorted(all_emojis.items(), reverse=True, key=lambda item: item[1])}
    print("OVERALL:")
    i = 1
    for emoji in all_emojis:
        if i > n:
            break
        print(emoji, "--", all_emojis[emoji])
        i += 1

    bar(
        [emojis.decode(k) for k in list(all_emojis.keys())[:(n*2)]],
        [all_emojis[k] for k in list(all_emojis.keys())[:(n*2)]],
        "Emojis",
        "Number of times used",
        rotation=''
    )

    for author in author_counters:
        author_counters[author] = {k: v for k, v in sorted(author_counters[author].items(), reverse=True, key=lambda item: item[1])}
        print(author)
        i = 1
        for emoji in author_counters[author]:
            if i > n:
                break
            print(emoji, "--", author_counters[author][emoji])
            i += 1


def df_words(df: pd.DataFrame, title=""):

    full_string = " ".join([str(row[1]["message"]).replace("\n", " ").lower() for row in df.iterrows() if row[1]["message"]!="<Media omessi>"])
    authors = df_get_author_list(df)

    full_string_authors = {}
    for author in authors:
        full_string_authors[author] = " ".join([str(row[1]["message"]).replace("<Media omessi>", "").replace("\n", " ").lower() for row in df.iterrows() if row[1]["author"] == author])

    stopwords = get_stop_words("it")

    wc = wordcloud.WordCloud(
        stopwords=stopwords,
        # width=1000,
        # height=500,
        background_color="white"
    )

    wc.generate(full_string)
    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    plt.title(title + " | " + "OVERALL")
    plt.show()

    for author in full_string_authors:
        wc.generate(full_string_authors[author])
        plt.axis("off")
        plt.imshow(wc, interpolation="bilinear")
        plt.title(title + " | " + author)
        plt.show()


def df_setup(df: pd.DataFrame) -> pd.DataFrame:

    # Creates the 'isMedia' column
    df["message"] = df["message"].astype(str)
    beginning = dt.datetime.now()
    df["isMedia"] = df.apply(lambda row: row["message"].find("<Media omessi>") != -1, axis=1)
    print((dt.datetime.now() - beginning).microseconds / 1000, "ms to create the isMedia column")

    # 14/06/15 12:52:00
    beginning = dt.datetime.now()
    df["datetime"] = pd.to_datetime(df["datetime"], format="%d/%m/%y %H:%M:%S")
    print((dt.datetime.now() - beginning).microseconds / 1000, "ms to convert 'datetime' from string")

    beginning = dt.datetime.now()
    df["isMedia"] = df["isMedia"].astype(bool)
    df["author"] = df["author"].astype(str)
    print((dt.datetime.now() - beginning).microseconds / 1000, "ms to convert column types")

    beginning = dt.datetime.now()
    df["message"] = df.apply(lambda row:
                             row["message"].replace("__x__", "|")
                             .replace("__a__", "*")
                             .replace("__vv__", '"')
                    .replace("__v__", "'"), axis=1
                             )
    print((dt.datetime.now() - beginning).microseconds / 1000, "ms to reformat the 'message' column")

    beginning = dt.datetime.now()
    df["emojis"] = df.apply(lambda row: emojis.get(row["message"]), axis=1)
    print((dt.datetime.now() - beginning).microseconds / 1000, "ms to create the 'emojis' column")

    beginning = dt.datetime.now()
    df["length"] = df.apply(lambda row: len(row["message"]), axis=1)
    print((dt.datetime.now() - beginning).microseconds / 1000, "ms to create the 'length' column")

    return df


def df_month_analysis(df, month="0", year="0"):

    if month == '0' and year == '0':
        max_size = 0
        for date_i, frame_i in df.groupby([df["datetime"].dt.year, df["datetime"].dt.month]):
            if len(frame_i) > max_size:
                max_size = len(frame_i)
                month = date_i[1]
                year = date_i[0]
                frame = frame_i
        print("The month you talked the most is " + str(month) + "-" + str(year))
    else:
        frame = df[
            (df["datetime"].dt.year==int(year)) &
            (df["datetime"].dt.month==int(month))
            ]
        print("There have been", len(frame), "messages in " + month + "-" + year)

    df_words(frame, title="What you talked about on " + str(month) + "-" + str(year))


def df_filter(df: pd.DataFrame,
              words=[],
              words_or=[],
              authors=[],
              start_date="30/03/2000 18:00",
              end_date="30/03/2050 18:00") -> pd.DataFrame:

    condition = ((df["datetime"] > dt.datetime.strptime(start_date, "%d/%m/%Y %H:%M")) &
                (df["datetime"] < dt.datetime.strptime(end_date, "%d/%m/%Y %H:%M")))

    if words:
        for word in words:
            condition = ((condition) & df["message"].str.contains(word))
    if words_or:
        words_condition = 0
        for word in words_or:
            words_condition = ((words_condition) | (df["message"].str.contains(word)))
        condition = (condition) & (words_condition)

    if authors:
        author_condition = 0
        for author in authors:
            author_condition = (author_condition) | (df["author"].str.contains(author))
        condition = (condition) & (author_condition)

    return df[condition]


def df_plot_days(df, start="01/03/2020", end="01/04/2020", auto=False):

    if auto:
        max_len = 0
        for (year, month), frame in df.groupby([df["datetime"].dt.year, df["datetime"].dt.month]):
            if len(frame) > max_len:
                max_len = len(frame)
                max_year = year
                max_month = month
        print("Max month is " + str(max_month) + "-" + str(max_year))
        last_day = misc.get_last_day_of_month(max_month)
        start = "01/" + str(max_month) + "/" + str(max_year)
        end = str(last_day) + "/" + str(max_month) + "/" + str(max_year)
    # 23/03/2020

    start = dt.datetime.strptime(start, "%d/%m/%Y")
    end = dt.datetime.strptime(end, "%d/%m/%Y")

    filtered_df = df_filter(
        df,
        start_date=start.strftime("%d/%m/%Y %H:%M"),
        end_date=end.strftime("%d/%m/%Y %H:%M")
    )

    dates = []
    counts = []
    for date, frame in filtered_df.groupby([df["datetime"].dt.year, df["datetime"].dt.month, df["datetime"].dt.day]):
        dates.append(str(date[2]) + "-" + str(date[1]))
        counts.append(len(frame))

    bar(dates, counts, "Day", "Total number of messages")


def df_get_author_list(df: pd.DataFrame) -> list:
    return [author for author in df["author"].value_counts().index]
