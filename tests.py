from controller import Controller
import os, shutil

class Tests:
    def __init__(self):
        self.controller = Controller()
        self.run_all_tests()

    def test_search_album(self):
        band_name = "Yes"
        album_title = "Close To The Edge"
        results = self.controller.search_album(band_name, album_title)
        assert(len(results) != 0)

        for result in results:
            lowercase_album_title = result['title'].lower().replace("̲", "")
            assert(band_name.lower() in lowercase_album_title and album_title.lower() in lowercase_album_title and "full album" in lowercase_album_title)

        print("Album search test passed.")

    def test_download_album(self):
        try:
            if os.path.exists("./downloads"):
                shutil.rmtree("./downloads")
            os.mkdir("downloads")
            os.chdir("./downloads")
            self.controller.download_youtube_video("Nails", "Unsilent Death")
            assert(os.listdir() == ["Nails_-_Unsilent_Death.mp3"])
            os.remove("Nails_-_Unsilent_Death.mp3")
            os.chdir("..")
            shutil.rmtree("./downloads")
            print("Album downloading test passed.")
        except Exception as e:
            print(e)
            assert(False)

    def test_create_search_query(self):
        search_query = self.controller.create_search_query("  Rush     ", "    Moving  pictures  ")
        assert(search_query == "https://www.discogs.com/search/?q=rush+moving+pictures&type=all")
        print("Search query creation test passed.")

    def test_get_album_links_from_discogs(self):
        album_links = self.controller.get_album_links_from_discogs(" Asylum party  ", "borderline  ")
        assert(album_links[0] == "https://www.discogs.com/Asylum-Party-Borderline/master/11882")
        print("Album link scraping test passed.")

    def test_get_album_tracklist(self):
        links = self.controller.get_album_links_from_discogs("King Crimson", "Red")
        (song_titles, song_durations) = self.controller.get_album_tracklist(links[0])
        assert(song_titles == ['Red', 'Fallen Angel', 'One More Red Nightmare', 'Providence', 'Starless'])
        assert(song_durations == ['6:20', '6:00', '7:07', '8:08', '12:18'])
        print("Album tracklist extraction test passed.")

    def test_download_into_directory(self):
        self.controller.download_into_directory("Warsaw", "Warsaw")
        os.chdir("./downloads")
        assert("Warsaw_-_Warsaw" in os.listdir())
        os.chdir("..")
        print("Directory path download test passed.")

    def test_string_timestamp_conversion_to_ints(self):
        timestamp = self.controller.convert_timestamp_string_to_ints("9:52")
        assert(timestamp["minutes"] == 9 and timestamp["seconds"] == 52)
        print("String timestamp conversion test passed.")

    def test_split_audio_in_tracks__average_case(self):
        self.controller.split_audio_in_tracks("Pink Floyd", "Meddle")
        assert(set(os.listdir("./downloads/Pink_Floyd_-_Meddle")) == set(['Seamus.mp3', 'A_Pillow_Of_Winds.mp3', 'San_Tropez.mp3', 'Fearless.mp3', 'Echoes.mp3', 'One_Of_These_Days.mp3']))
        print("Audio splitting test (average case) passed.")

    def test_split_audio_in_tracks__no_song_lengths_in_the_first_link(self):
        shutil.rmtree("./downloads")
        os.mkdir("./downloads")
        self.controller.split_audio_in_tracks("Jethro Tull", "Aqualung")
        assert(set(os.listdir("./downloads/Jethro_Tull_-_Aqualung")) == set(['Aqualung.mp3', 'Cross-Eyed_Mary.mp3', 'Cheap_Day_Return.mp3', 'Mother_Goose.mp3', "Wond_ring_Aloud.mp3", 'Up_To_Me.mp3', "My_God.mp3", "Hymn_43.mp3", "Slipstream.mp3", "Locomotive_Breath.mp3", "Wind-Up.mp3"]))
        print("Audio splitting test (no song lengths in link) passed.")

    def run_all_tests(self):
        """
        self.test_search_album()
        self.test_download_album()
        self.test_create_search_query()
        self.test_get_album_links_from_discogs()
        self.test_get_album_tracklist()
        self.test_download_into_directory()
        self.test_string_timestamp_conversion_to_ints()
        self.test_split_audio_in_tracks__average_case()
        """
        self.test_split_audio_in_tracks__no_song_lengths_in_the_first_link()