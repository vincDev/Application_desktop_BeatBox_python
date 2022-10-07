from kivy import Config
Config.set('graphics', 'width', '780')
Config.set('graphics', 'height', '360')
Config.set('graphics', 'minimum_width', '650')
Config.set('graphics', 'minimum_height', '300')

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from audio_engine import AudioEngine
from sound_kit_service import SoundKitService
from track import TrackWidget

Builder.load_file('track.kv')
Builder.load_file('play_indicator.kv')

TRACK_NB_STEPS = 16
MIN_BPM = 80
MAX_BPM = 160


class VerticalSpacingWidget(Widget):
    pass


class MainWidget(RelativeLayout):
    tracks_layout = ObjectProperty()
    play_indicator_widget = ObjectProperty()
    TRACK_STEPS_LEFT_ALIGN = NumericProperty(dp(120))
    step_index = 0
    bpm = NumericProperty(115)
    nb_tracks = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.sound_kit_service = SoundKitService()

        self.nb_tracks = self.sound_kit_service.get_nb_tracks()
        # kick_sound = self.sound_kit_service.get_sound_at(0)
        all_sound = self.sound_kit_service.soundkit.get_all_samples()

        self.audio_engine = AudioEngine()
        # self.audio_engine.play_sound(kick_sound.samples)
        
        # self.audio_engine.create_track(kick_sound.samples, 120)
        
        self.mixer = self.audio_engine.create_mixer(all_sound, self.bpm, TRACK_NB_STEPS, self.on_mixer_current_step_changed, MIN_BPM)

    def on_parent(self, widget, parent):
        self.play_indicator_widget.set_nb_steps(TRACK_NB_STEPS)
        # self.play_indicator_widget.set_current_step_index(0)
        for i in range(0, self.sound_kit_service.get_nb_tracks()):
            sound = self.sound_kit_service.get_sound_at(i)
            self.tracks_layout.add_widget(VerticalSpacingWidget())
            self.tracks_layout.add_widget(TrackWidget(sound, self.audio_engine, TRACK_NB_STEPS, self.mixer.tracks[i],
                                                      self.TRACK_STEPS_LEFT_ALIGN))
        self.tracks_layout.add_widget(VerticalSpacingWidget())

    def on_mixer_current_step_changed(self, step_index):
        # print(f'on_mixer_current_step_changed {step_index}')
        self.step_index = step_index
        Clock.schedule_once(self.update_play_indicator_cbk, 0)

    def update_play_indicator_cbk(self, dt):
        if self.play_indicator_widget is not None:
            self.play_indicator_widget.set_current_step_index(self.step_index)

    def on_play_button_pressed(self):
        self.mixer.audio_play()

    def on_stop_button_pressed(self):
        self.mixer.audio_stop()

    def on_bpm(self, widget, value):
        # print(f'BPM : {str(value)}')
        if value < MIN_BPM:
            self.bpm = MIN_BPM
            return
        if value > MAX_BPM:
            self.bpm = MAX_BPM
            return

        self.mixer.set_bpm(self.bpm)


class MrBeatApp(App):
    pass


MrBeatApp().run()