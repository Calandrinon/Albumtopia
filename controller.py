import requests
import datetime
from bs4 import BeautifulSoup
from youtube_search import YoutubeSearch
from youtube_dl import YoutubeDL
from pydub import AudioSegment
from difflib import SequenceMatcher
import re, os, eyed3, sys, urllib, unidecode

class Controller:
    def __init__(self):
        self.album_link = ""
        self.new_directory_name = ""
        self.path_to_image = ""


    def search_album(self, band_name, album_name):
        band_name, album_name = band_name.lower(), album_name.lower()
        search_string = band_name + " " + album_name + " full album"
        results = YoutubeSearch(search_string, max_results=20).to_dict()
        valid_results = []

        for result in results:
            lowercase_result_title = result['title'].lower().replace("̲", "").replace("̶", "")
            if band_name in lowercase_result_title and album_name in lowercase_result_title and "full" in lowercase_result_title:
                valid_results.append(result)

        return valid_results


    def download_youtube_video(self, band_name, album_name):
        results = self.search_album(band_name, album_name)
        video_url = "https://www.youtube.com" + results[0]['url_suffix']
        video_info = YoutubeDL().extract_info(url=video_url, download=False)
        filename = (band_name + " - " + album_name + ".mp3").replace(" ", "_")
        options = {
            'format': 'bestaudio/best', 'keepvideo': False, 'outtmpl': filename,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]}

        with YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

    
    def create_file_structure(self, band_name, album_title):
        if not os.path.exists("./downloads"):
            os.mkdir("downloads")
        os.chdir("./downloads")
        self.new_directory_name = ("./" + band_name + " - " + album_title + "/").replace(" ", "_")
        if not os.path.exists(self.new_directory_name):
            os.mkdir(self.new_directory_name)
        os.chdir(self.new_directory_name)


    def download_into_directory(self, band_name, album_title):
        self.create_file_structure(band_name, album_title)
        self.download_youtube_video(band_name, album_title)
        os.chdir("../../")


    def create_search_query(self, band_name, album_title):
        search_term = (band_name + " " + album_title).strip().lower()
        search_term = re.sub(r" \s+", " ", search_term).replace(" ", "+")
        request_url = "https://www.discogs.com/search/?q=" + search_term + "&type=all"
        return request_url


    def get_album_links_from_discogs(self, band_name, album_title):
        band_name = band_name.strip().lower()
        album_title = album_title.strip().lower()
        search_query = self.create_search_query(band_name, album_title)
        result = requests.get(search_query)
        page_source = result.content
        soup = BeautifulSoup(page_source, "lxml")
        links = soup.find_all("a", "search_result_title")
        if len(links) == 0:
            print("No search found on Discogs! Unfortunately, the album cannot be tagged.")
            return 404

        valid_links = []
        for index in range(0, len(links)):
            tokens = album_title.strip().lower().split(" ")
            valid = True
            link = links[index].attrs["href"].lower()
            for token in tokens:
                if (token not in link and token not in str(links[index]).lower()) or ("artist" in link) or ("label" in link):
                    valid = False
                    break

            if valid:
                valid_links.append("https://www.discogs.com" + links[index].attrs["href"])

        return valid_links


    def get_album_tracklist(self, album_link):
        result = requests.get(album_link)
        tracklist_page = result.content
        soup = BeautifulSoup(tracklist_page, "lxml")
        tracklist_span_titles = soup.find_all("span", "tracklist_track_title")
        tracklist_without_subtracks = list(filter((lambda x: "subtrack" not in x.parent.parent["class"]), tracklist_span_titles))
        tracklist_durations = soup.find_all("td", "tracklist_track_duration")
        song_titles = list(map(lambda x: x.getText(), tracklist_without_subtracks))
        song_durations = list(map(lambda x: x.find("span").getText(), tracklist_durations))
        return (song_titles, song_durations)


    def convert_timestamp_string_to_ints(self, timestamp):
        timestamp_dictionary = {}
        time_units = list(map(lambda x: int(x), timestamp.split(":")))
        if len(time_units) == 3:
            timestamp_dictionary["hours"] = time_units[0]
            timestamp_dictionary["minutes"] = time_units[1]
            timestamp_dictionary["seconds"] = time_units[2]
        elif len(time_units) == 2:
            timestamp_dictionary["minutes"] = time_units[0]
            timestamp_dictionary["seconds"] = time_units[1]
        return timestamp_dictionary


    def check_tracklength_validity(self, song_durations):
        for song_duration in song_durations:
            if len(song_duration) > 0:
                return True
        return False


    def download_album_cover_art(self, band_name, album_title):
        result = requests.get(self.album_link)
        page_source = result.content
        soup = BeautifulSoup(page_source, "lxml")
        links = soup.find_all("img")
        image_link = ""
        for link in links:
            if "album cover" in str(link):
                image_link = link.attrs["src"]
                break

        self.path_to_image = (os.getcwd() + "/" + band_name + album_title).replace(" ", "_")
        urllib.request.urlretrieve(image_link, self.path_to_image)


    def add_tags_to_track(self, path_to_track, band_name, album_title, song_title, track_num):
        song = eyed3.load(path_to_track)
        song.tag.artist = band_name
        song.tag.album = album_title
        song.tag.album_artist = band_name
        song.tag.title = song_title
        song.tag.track_num = track_num
        song.tag.images.set(3, open(self.path_to_image, 'rb').read(), 'image/jpeg')
        song.tag.save()


    def sanitize_filename(self, filename):
        characters = [' ', '(', ')', ',', ';', ':', '"', '\'', '&', '.', '/']
        for char in characters:
            if char in filename:
                filename = filename.replace(char, "_")
        filename += ".mp3"
        return filename


    def split_audio_in_tracks(self, band_name, album_title):
        filename = band_name + "_-_" + album_title
        filename = self.sanitize_filename(filename)
        self.download_into_directory(band_name, album_title)
        os.chdir("./downloads/" + self.new_directory_name[2:])
        total_time = datetime.timedelta(minutes=0, seconds=0)
        invalid_song_durations = True
        album_links = self.get_album_links_from_discogs(band_name, album_title)

        if album_links == 404:
            return

        while invalid_song_durations:
            album_link = album_links[0]
            (song_titles, song_durations) = self.get_album_tracklist(album_link)
            song_durations = list(filter((lambda x: x != ''), song_durations))
            if self.check_tracklength_validity(song_durations) == False:
                del album_links[0]
                continue

            self.album_link = album_link
            self.download_album_cover_art(band_name, album_title)
            invalid_song_durations = False
            for song_index in range(0, len(song_titles)):
                if song_durations[song_index] == "":
                    continue
                song_durations[song_index] = song_durations[song_index].replace("(", "").replace(")", "")
                song_length_tokens = song_durations[song_index].split(":")
                song_length_tokens = list(map(lambda x: int(x), song_length_tokens))
                song_duration_in_seconds = song_length_tokens[0] * 60 + song_length_tokens[1]

                timestamp = self.convert_timestamp_string_to_ints(song_durations[song_index])
                current_duration = datetime.timedelta(minutes=timestamp["minutes"], seconds=timestamp["seconds"])
                start_time = total_time.total_seconds()
                total_time += current_duration

                song_title = self.sanitize_filename(song_titles[song_index])
                os.system("ffmpeg -t {} -ss {} -i {} {} -hide_banner -loglevel panic".format(song_duration_in_seconds, start_time, filename, song_title))
                self.add_tags_to_track(song_title, band_name, album_title, song_titles[song_index], song_index + 1)

        os.remove(filename)
        os.chdir("../../")


    def sanitize_string(self, string):
        characters = ['(', ')', ',', ';', ':', '"', '\'', '&', '.', '/']
        for char in characters:
            if char in string:
                string = string.replace(char, "")
        return string


    def get_string_similarity_percentage(self, string_a, string_b):
        return SequenceMatcher(None, string_a, string_b).ratio() 


    def search_track(self, band_name, track_title):
        band_name, track_title = band_name.lower(), self.sanitize_string(track_title.lower())
        search_string = band_name + " " + track_title 
        results = YoutubeSearch(search_string, max_results=20).to_dict()
        valid_results = []

        for result in results:
            channel_name = result["channel"].lower()
            lowercase_result_title = result['title'].lower().replace("̲", "").replace("̶", "")
            lowercase_result_title = self.sanitize_string(lowercase_result_title)

            if (band_name in lowercase_result_title or band_name in channel_name) and \
                (track_title in lowercase_result_title or self.get_string_similarity_percentage(track_title, lowercase_result_title) >= 0.5)\
                and "full" not in lowercase_result_title and "album" not in lowercase_result_title:
                valid_results.append(result)
            else:
                lowercase_result_title_without_accents = unidecode.unidecode(lowercase_result_title) 
                band_name_without_accents = unidecode.unidecode(band_name) 
                track_title_without_accents = unidecode.unidecode(track_title) 
                channel_name_without_accents = unidecode.unidecode(channel_name)
                if (band_name_without_accents in lowercase_result_title_without_accents or band_name_without_accents in channel_name_without_accents)\
                    and (track_title_without_accents in lowercase_result_title_without_accents or self.get_string_similarity_percentage(track_title, lowercase_result_title) >= 0.9)\
                    and "full" not in lowercase_result_title:
                    valid_results.append(result)

        return valid_results


    def download_track(self, band_name, track_title):
        try:
            results = self.search_track(band_name, track_title)
            filename = self.sanitize_filename(track_title)
            video_url = "https://www.youtube.com" + results[0]['url_suffix']
            video_info = YoutubeDL().extract_info(url=video_url, download=False)
            options = {
                'format': 'bestaudio/best', 'keepvideo': False, 'outtmpl': filename,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]}

            with YoutubeDL(options) as ydl:
                ydl.download([video_info['webpage_url']])
            
            return True
        except Exception as e:
            print("ERROR: Couldn't download \"{}\". The song was most likely not found on Youtube.".format(track_title))
            print(e)
            return False


    def download_track_into_directory(self, band_name, album_title, track_title):
        self.create_file_structure(band_name, album_title)
        successful = self.download_track(band_name, track_title)
        os.chdir("../../")
        return successful

    
    def download_tracks_separately(self, band_name, album_title): 
        album_links = self.get_album_links_from_discogs(band_name, album_title)
        if album_links == 404:
            return
        self.album_link = album_links[0]
        (song_titles, song_durations) = self.get_album_tracklist(self.album_link)
        track_index = 0
        self.create_file_structure(band_name, album_title)
        self.download_album_cover_art(band_name, album_title)
        os.chdir("../../")

        for song_title in song_titles:
            song_title = song_title.replace("\"", "")
            track_index += 1
            successful = self.download_track_into_directory(band_name, album_title, song_title) 
            if not successful:
                continue
            filename = self.sanitize_filename(song_title)
            path = (os.getcwd() + "/downloads/" + band_name + " - " + album_title + "/" + filename).replace(" ", "_")
            
            """ This solves the issue with the eyed3 tagging of the file.
                Although the file should be an mp3 (as the youtube-dl downloads it as mp3), the eyed3 module does not recognize it.
                Converting the file to mp3 solves the issue.
            """
            song = AudioSegment.from_file(path)
            song.export(path, "mp3")

            self.add_tags_to_track(path, band_name, album_title, song_title, track_index)

