from controller import Controller
import os, shutil, eyed3

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
            assert(band_name.lower() in lowercase_album_title and album_title.lower() in lowercase_album_title and "full" in lowercase_album_title)

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


    def test_get_album_tracklist__subtrack_filtering(self):
        links = self.controller.get_album_links_from_discogs("Edge Of Sanity", "Unorthodox")
        (song_titles, song_durations) = self.controller.get_album_tracklist(links[0])
        assert(song_titles == ['The Unorthodox', 'Enigma', 'Incipience To The Butchery', 'In The Veins/Darker Than Black', 'Everlasting (Epidemic Reign Part III)', 'After Afterlife', 'Beyond The Unknown', 'Nocturnal', 'A Curfew For The Damned (...Blind Belief)', 'Cold Sun (Epidemic Reign Part IV)', 'The Day Of Maturity', 'Requiscon By Page (Instrumental)', 'Dead But Dreaming', 'When All Is Said'])
        print("Subtrack filtering test passed.")


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
        expected_result = set(['Seamus.mp3', 'A_Pillow_Of_Winds.mp3', 'San_Tropez.mp3', 'Fearless.mp3', 'Echoes.mp3', 'One_Of_These_Days.mp3']) 
        actual_result = set(os.listdir("./downloads/Pink_Floyd_-_Meddle"))
        assert(expected_result.issubset(actual_result))
        print("Audio splitting test (average case) passed.")


    def test_split_audio_in_tracks__no_song_lengths_in_the_first_link(self):
        shutil.rmtree("./downloads")
        os.mkdir("./downloads")
        self.controller.split_audio_in_tracks("Jethro Tull", "Aqualung")
        expected_result = set(['Aqualung.mp3', 'Cross-Eyed_Mary.mp3', 'Cheap_Day_Return.mp3', 'Mother_Goose.mp3', "Wond_ring_Aloud.mp3", 'Up_To_Me.mp3', "My_God.mp3", "Hymn_43.mp3", "Slipstream.mp3", "Locomotive_Breath.mp3", "Wind-Up.mp3"]) 
        actual_result = set(os.listdir("./downloads/Jethro_Tull_-_Aqualung"))
        assert(expected_result.issubset(actual_result))
        print("Audio splitting test (no song lengths in link) passed.")


    def test_split_audio_in_tracks__validate_based_on_tokens(self):
        shutil.rmtree("./downloads")
        os.mkdir("./downloads")
        self.controller.split_audio_in_tracks("Drowning The Light", "Oceans Of Eternity")
        expected_result = set(['Oceans_Of_Eternity.mp3', 'Oppression___Tyranny.mp3', 'The_Key_Still_Not_Found.mp3', 'As_The_Shadows_At_Dusk_Reach_Our_Enemies_Throats.mp3', 'The_Lunatic_Tide.mp3', 'The_Poison_Kiss.mp3', 'The_Runes_Are_Thrown___The_Bones_Are_Spread__A_Hymn_To_The_Apocalypse_.mp3', 'Drifting_Away_In_A_Sea_Of_Sorrow__Part_II_.mp3', 'The_Cataclysmic_Cycle_Of_Renewal.mp3']) 
        actual_result = set(os.listdir("./downloads/Drowning_The_Light_-_Oceans_Of_Eternity"))
        assert(expected_result.issubset(actual_result))
        print("Audio splitting test 3 (token validation) passed.")


    def test_split_audio_in_tracks__sanitize_dots(self):
        shutil.rmtree("./downloads")
        os.mkdir("./downloads")
        self.controller.split_audio_in_tracks("Drowning The Light", "Catacombs Of Blood")
        expected_result = set(['Autumn_Mourning.mp3', '___Such_Cruelty_Never_Rests.mp3', 'Eyes_Of_Onyx__Carrion_For_The_Worms_.mp3', 'As_Plague_Upon_The_Sheep__Poison_In_Redemption_.mp3', 'Entrance_To_Illumination.mp3', 'Fragmented___Unrealisable.mp3', 'This_Darkest_Hour.mp3', 'Requiem_Of_Honour___Glory.mp3', 'Pact_Of_The_Black_Templars.mp3', 'Burial_In_The_Rain.mp3', 'Torn_Away_By_The_Shadows.mp3'])
        actual_result = set(os.listdir("./downloads/Drowning_The_Light_-_Catacombs_Of_Blood"))
        assert(expected_result.issubset(actual_result))
        print("Audio splitting test 4 (filename sanitization) passed.")


    def test_split_audio_in_tracks__sanitize_tracklength(self):
        shutil.rmtree("./downloads")
        os.mkdir("./downloads")
        self.controller.split_audio_in_tracks("Yes", "Close To The Edge")
        expected_result = set(['And_You_And_I.mp3', 'Close_To_The_Edge.mp3', 'Siberian_Khatru.mp3'])
        actual_result = set(os.listdir("./downloads/Yes_-_Close_To_The_Edge"))
        assert(expected_result.issubset(actual_result))
        print("Audio splitting test 4 (tracklength sanitization) passed.")


    def test_split_audio_in_tracks__sanitize_youtube_title(self):
        shutil.rmtree("./downloads")
        os.mkdir("./downloads")
        self.controller.split_audio_in_tracks("The Smiths", "The Queen Is Dead")
        expected_result = set(['Never_Had_No_One_Ever.mp3', 'Frankly__Mr__Shankly.mp3', 'The_Boy_With_The_Thorn_In_His_Side.mp3', 'There_Is_A_Light_That_Never_Goes_Out.mp3', 'Vicar_In_A_Tutu.mp3', 'Cemetry_Gates.mp3', 'Bigmouth_Strikes_Again.mp3', 'The_Queen_Is_Dead__Take_Me_Back_To_Dear_Old_Blighty__Medley__.mp3', 'Some_Girls_Are_Bigger_Than_Others.mp3', 'I_Know_It_s_Over.mp3'])
        actual_result = set(os.listdir("./downloads/The_Smiths_-_The_Queen_Is_Dead"))
        assert(expected_result.issubset(actual_result))
        print("Audio splitting test 5 (youtube title sanitization) passed.")
        

    def test_add_tags_to_track(self):
        shutil.rmtree("./downloads")
        os.mkdir("./downloads")
        self.controller.split_audio_in_tracks("Decomposed", "The Funeral Obsession")
        os.chdir("./downloads/Decomposed_-_The_Funeral_Obsession")
        song = eyed3.load("At_Rest.mp3")
        assert(song.tag.artist == "Decomposed")
        assert(song.tag.album == "The Funeral Obsession")
        assert(song.tag.title == "At Rest")
        assert(song.tag.track_num[0] == 1)
        os.chdir("../../")
        print("Automatic track tags test passed.")


    def test_track_searching(self):
        results = self.controller.search_track("Ahab", "Below The Sun")
        assert(len(results) > 0 and "Below The Sun" in results[0]["title"])
        print("Track searching test passed.")
    

    def test_track_downloading(self):
        self.controller.download_track("Ahab", "Below The Sun")
        assert("Below_The_Sun.mp3" in os.listdir())
        os.remove("Below_The_Sun.mp3")
        print("Track downloading test passed.")


    def test_track_downloading_into_directory(self):
        self.controller.download_track_into_directory("Ahab", "The Call of the Wretched Sea", "Below The Sun")
        assert("Below_The_Sun.mp3" in os.listdir("./downloads/Ahab_-_The_Call_of_the_Wretched_Sea"))
        print("Track downloading in directory test passed.")


    def test_separate_track_downloading_1(self):
        self.controller.download_tracks_separately("Melvins", "Houdini")
        assert(set(os.listdir("./downloads/Melvins_-_Houdini")) == set(['Hag_Me.mp3', 'Night_Goat.mp3', 'Spread_Eagle_Beagle.mp3', 'Teet.mp3', 'Copache.mp3', 'MelvinsHoudini', 'Lizzy.mp3', 'Honey_Bucket.mp3', 'Joan_Of_Arc.mp3', 'Pearl_Bomb.mp3', 'Hooch.mp3', 'Going_Blind.mp3', 'Sky_Pup.mp3', 'Set_Me_Straight.mp3']))
        print("Separate track downloading test 1 passed.")


    def test_separate_track_downloading_2(self):
        self.controller.download_tracks_separately("Megadeth", "Rust In Peace")
        assert(set(os.listdir("./downloads/Megadeth_-_Rust_In_Peace")) == set(['Rust_In_Peace___Polaris.mp3', 'Take_No_Prisoners.mp3', 'Poison_Was_The_Cure.mp3', 'Five_Magics.mp3', 'Hangar_18.mp3', 'Lucretia.mp3', 'MegadethRust_In_Peace', 'Holy_Wars___The_Punishment_Due.mp3', 'Dawn_Patrol.mp3', 'Tornado_Of_Souls.mp3']))
        print("Separate track downloading test 2 passed.")
    

    def test_separate_track_downloading_3__diacritics_and_long_mp3_handling(self):
        self.controller.download_tracks_separately("Progresiv TM", "Puterea Muzicii")
        assert(set(os.listdir("./downloads/Progresiv_TM_-_Puterea_Muzicii")) == set(['Pas_Candid_Către_Realitate.mp3', 'Opțiune_Pentru_Pace.mp3', 'Oameni_Și_Fapte.mp3', 'Puterea_Muzicii.mp3', 'Sete_De_Pădure.mp3', 'Progresiv_TMPuterea_Muzicii', 'Legămînt.mp3', 'Gînd_Curat.mp3']))
        print("Separate track downloading test 3 passed.")

    
    def test_separate_track_downloading_4__string_similarity_last_case(self):
        self.controller.download_tracks_separately("Edge Of Sanity", "Unorthodox")
        expected_result = set(['The_Day_Of_Maturity.mp3', 'Requiscon_By_Page__Instrumental_.mp3', 'Cold_Sun__Epidemic_Reign_Part_IV_.mp3', 'Enigma.mp3', 'The_Unorthodox.mp3', 'Nocturnal.mp3', 'After_Afterlife.mp3', 'Beyond_The_Unknown.mp3', 'When_All_Is_Said.mp3', 'Dead_But_Dreaming.mp3', 'Edge_Of_SanityUnorthodox', 'Incipience_To_The_Butchery.mp3', 'Everlasting__Epidemic_Reign_Part_III_.mp3', 'A_Curfew_For_The_Damned_____Blind_Belief_.mp3', 'In_The_Veins_Darker_Than_Black.mp3'])
        actual_result = set(os.listdir("./downloads/Edge_Of_Sanity_-_Unorthodox"))
        assert(actual_result.issubset(expected_result))
        print("Separate track downloading test (string similarity) passed.")


    def test_get_album_links_from_discogs__ignore_record_label_links(self):
        links = self.controller.get_album_links_from_discogs("Epitaph", "Epitaph")
        correct_link = links[0] 
        assert(correct_link == "https://www.discogs.com/Epitaph-Epitaph/master/277822")
        print("Ignoring record label links test passed.")


    def run_all_tests(self):
        self.test_search_album()
        self.test_download_album()
        self.test_create_search_query()
        self.test_get_album_links_from_discogs()
        self.test_get_album_tracklist()
        self.test_get_album_tracklist__subtrack_filtering()
        self.test_download_into_directory()
        self.test_string_timestamp_conversion_to_ints()
        self.test_split_audio_in_tracks__average_case()
        self.test_split_audio_in_tracks__no_song_lengths_in_the_first_link()
        self.test_split_audio_in_tracks__validate_based_on_tokens()
        self.test_split_audio_in_tracks__sanitize_dots()
        self.test_split_audio_in_tracks__sanitize_tracklength()
        self.test_split_audio_in_tracks__sanitize_youtube_title()
        self.test_add_tags_to_track()

        self.test_track_searching()
        self.test_track_downloading()
        self.test_track_downloading_into_directory()
        self.test_separate_track_downloading_1()
        self.test_separate_track_downloading_2()
        self.test_separate_track_downloading_3__diacritics_and_long_mp3_handling()
        self.test_separate_track_downloading_4__string_similarity_last_case()
        self.test_get_album_links_from_discogs__ignore_record_label_links()
