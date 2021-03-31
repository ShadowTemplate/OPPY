#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
import seaborn as sns

from datetime import datetime, timedelta
from time import gmtime, strftime

OSPA_PLAYLIST_CSV_FILE = 'one_song_per_artist_latest.csv'
# OSPA_PLAYLIST_CSV_FILE = 'one_song_per_artist_instrumental_latest.csv'
PLAYLIST_DURATION_FIELD_CSV = 'Duration (ms)'
# PLAYLIST_DURATION_FIELD_CSV = 'Track Duration (ms)'  # before 2021 use this
PLAYLIST_ADDED_FIELD_CSV = 'Added At'
PLAYLIST_DATE_FORMAT_CSV = '%Y-%m-%dT%H:%M:%S%fZ'
SPOTIFY_GREEN_RBG = '#1db954'
GROUP_EVERY_DAY = 50
X_AXIS_DATE_FORMAT = '%d-%m-%Y'


def main(ospa_playlist_csv_file, duration_field_name_csv, added_field_name_csv, date_format_csv):
    print(f'Processing file {ospa_playlist_csv_file}...')
    with open(ospa_playlist_csv_file, newline='') as csv_f:
        csv_reader = csv.reader(csv_f, delimiter=',')
        header = next(csv_reader)
        print(f'{header}')
        duration_field_index = header.index(duration_field_name_csv)
        added_field_index = header.index(added_field_name_csv)
        print(f'{duration_field_name_csv}: [{duration_field_index}]\n{added_field_name_csv}: [{added_field_index}]')
        tracks = [
            (int(row[duration_field_index]), _to_millis(row[added_field_index], date_format_csv)) for row in csv_reader
        ]
        draw_cumulative_chart(tracks)


def _to_millis(date, date_format):
    utc_time = datetime.strptime(date, date_format)
    return (utc_time - datetime(1970, 1, 1)) // timedelta(milliseconds=1)


def _print_array_overview(array, rows):
    for i in range(rows):
        print(f"Track[{i}]: {array[i]} with types ({', '.join((str(type(t)) for t in array[i]))})")


def _get_songs_number_for_duration(values, threshold):
    try:
        return next(idx for idx, value in enumerate(values, start=0) if value >= threshold)
    except StopIteration:
        return len(values)


def draw_cumulative_chart(tracks):
    fig = plt.gcf()
    fig.set_size_inches(10.5, 10.5)

    print(f'Tracks number: {len(tracks)}')
    tracks.sort(key=lambda x: x[1])  # tracks may be already sorted by added time, but sort them anyway for safety
    tracks = np.array(tracks)
    _print_array_overview(tracks, 3)

    print('Cumulative values:')
    cumulative_data = tracks.cumsum(axis=0)
    _print_array_overview(cumulative_data, 3)

    data = {
        'Date': [t[1] for t in tracks],
        'Duration (h)': [t[0] / 1000 / 60 / 60 for t in cumulative_data]
    }
    sns.set(style='darkgrid')
    ax = sns.lineplot(x='Date', y='Duration (h)', data=data, color=SPOTIFY_GREEN_RBG)

    # customize (x, y1, y2) axes and labels
    day_in_millis = 1000 * 60 * 60 * 24
    regular_interval_locator = plticker.MultipleLocator(base=day_in_millis * GROUP_EVERY_DAY)
    ax.xaxis.set_major_locator(regular_interval_locator)
    ax.set(ylabel='Duration (hours)')
    ax.set_xticklabels([strftime(X_AXIS_DATE_FORMAT, gmtime(tm / 1000.0)) for tm in ax.get_xticks()], rotation=50)
    second_ax = ax.secondary_yaxis('right')
    second_ax.set(ylabel='Songs')
    second_ax.set_yticklabels([_get_songs_number_for_duration(data['Duration (h)'], tm) for tm in ax.get_yticks()])
    second_ax.yaxis.set_tick_params(length=0)

    # draw info box
    m, s = divmod(cumulative_data[-1][0] // 1000, 60)
    h, m = divmod(m, 60)
    box_text = f'Duration: {h} h {m} m {s} s\nSongs: {len(tracks)}'
    properties = dict(boxstyle='round', facecolor=SPOTIFY_GREEN_RBG, alpha=0.5)
    ax.text(0.05, 0.95, box_text, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=properties)

    plt.show()
    ax.figure.savefig('plot.png')


if __name__ == '__main__':
    main(OSPA_PLAYLIST_CSV_FILE, PLAYLIST_DURATION_FIELD_CSV, PLAYLIST_ADDED_FIELD_CSV, PLAYLIST_DATE_FORMAT_CSV)
