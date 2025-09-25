from datetime import datetime
from threading import Thread

import cv2
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.graphics.texture import Texture
from kivy.properties import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatIconButton
from kivymd.uix.screen import MDScreen

from FaceDetector import FaceDetector

# Set the font path
font_path = 'BMHANNAPro.ttf'

Window.size = (1920, 1080)


class MainScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.app = app

        # 배경 이미지 추가
        self.background_image = Image(source="KakaoTalk_20231126_185622471_01.png", allow_stretch=False,
                                      keep_ratio=False)
        self.add_widget(self.background_image)

        # 버튼 크기 조정
        self.button = MDRectangleFlatIconButton(
            text="같이 여정을 떠나볼까요?",
            icon="camera",
            font_name="BMHANNAPro.ttf",
            font_size=40,
            line_color=(0, 0, 0, 1),
            pos_hint={"center_x": .5, "center_y": .57},
            on_release=self.show_welcome_screen
        )

        self.add_widget(self.button)

    def show_welcome_screen(self, instance):
        self.app.screen_manager.previous = self.app.screen_manager.current
        self.app.screen_manager.current = "welcome"


class WelcomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        self.face_detector = FaceDetector()
        self.capture = cv2.VideoCapture(0)
        self.is_capturing = False
        self.app = app
        self.paused = False
        self.start_time = datetime.now()
        self.all_layout = BoxLayout(orientation="vertical")

        # 배경 색상 지정
        with self.all_layout.canvas.before:
            self.background_color = Color(1, 1, 1, 1)  # 기본 배경 흰색으로 지정
            self.rect = Rectangle(size=self.all_layout.size, pos=self.all_layout.pos)

        # 이게 있어야 색상 나옵니다..
        self.all_layout.bind(size=lambda instance, value: setattr(self.rect, 'size', value))
        self.all_layout.bind(pos=lambda instance, value: setattr(self.rect, 'pos', value))

        self.top_layout = BoxLayout(orientation="horizontal")
        top_child = BoxLayout(size=(570, 300))
        top_child2 = BoxLayout(size=(640, 300))
        top_child3 = BoxLayout(size=(570, 300))

        self.top_layout.add_widget(top_child)
        # welcome_image와 exit_button 추가
        welcome_image = Image(
            source="KakaoTalk_20231126_185622471.png",  # 이미지 파일의 경로로 바꾸세요
            size_hint_y=None,
            height=100,
            pos_hint={"center": 1, "top": 1},  # 상단 가운데 배치
            size_hint=(1, 1)
        )
        top_child2.add_widget(welcome_image)
        self.top_layout.add_widget(top_child2)

        exit_button = MDRectangleFlatIconButton(
            text="나가기",
            icon="exit-to-app",
            font_name="BMHANNAPro.ttf",
            font_size=50,
            pos_hint={"right": 1, "top": 1},  # 상단 오른쪽 배치
            on_release=self.exit_screen,
            size_hint=(0.7, 1),
            md_bg_color=get_color_from_hex("#2196F3"),  # Set the background color to blue
            text_color=(1, 1, 1, 1),  # Set the font color to white
            icon_color=(1, 1, 1, 1)
        )

        self.top_layout.add_widget(top_child3)

        self.all_layout.add_widget(self.top_layout)

        # 두번째 부모 레이아웃
        self.center_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), size=(1920, 1000),
                                       pos_hint={"top": 1}, )
        center_child = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        self.image = Image()
        center_child.add_widget(self.image)
        self.center_layout.add_widget(center_child)
        self.all_layout.add_widget(self.center_layout)

        # 세번째 부모 레이아웃
        self.bottom_layout = BoxLayout(orientation="horizontal", padding=10, spacing=10)
        child_layout1 = BoxLayout(orientation="horizontal", padding=10, spacing=10)
        child_layout2 = BoxLayout(orientation="horizontal", padding=10, spacing=10)
        child_layout3 = BoxLayout(orientation="horizontal", padding=10, spacing=10)

        self.pause_button = MDRectangleFlatIconButton(
            text="일시정지",
            icon="pause",
            font_name="BMHANNAPro.ttf",
            font_size=50,
            size=(200, 100),
            on_release=self.toggle_pause,
            size_hint=(1, 1),
            pos_hint={"center": 1},
            md_bg_color=get_color_from_hex("#2196F3"),  # Set the background color to blue
            text_color=(1, 1, 1, 1),  # Set the font color to white
            icon_color=(1, 1, 1, 1)
        )
        child_layout1.add_widget(self.pause_button)

        self.time_label = Label(
            text="주행시간: 00:00:00",
            font_name="BMHANNAPro.ttf",
            font_size=50,
            color=(0, 0, 0, 1),
            size_hint=(1, 1),  # size_hint를 설정하여 세로 크기를 bottom_layout에 맞춤
            halign='center'
        )
        child_layout2.add_widget(self.time_label)

        child_layout3.add_widget(exit_button)

        self.bottom_layout.add_widget(child_layout1)
        self.bottom_layout.add_widget(child_layout2)
        self.bottom_layout.add_widget(child_layout3)

        self.all_layout.add_widget(self.bottom_layout)

        self.add_widget(self.all_layout)

        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def back_to_main(self, instance):
        self.app.screen_manager.current = self.app.screen_manager.previous

    def toggle_camera(self, *args):
        if not self.is_capturing:
            self.start_capturing()  # 캡처 시작
        else:
            self.stop_capturing()  # 캡처 중지

    def toggle_pause(self, instance):
        if self.paused:
            self.start_time += datetime.now() - self.pause_time  # Resume tracking from where it left off
            self.start_capturing()
            instance.icon = "pause"  # Change the icon to "pause" when resuming
            instance.text = "일시정지"  # Change the text to "일시정지" when resuming
        else:
            self.pause_time = datetime.now()  # Record the time when pausing
            self.stop_capturing()
            instance.icon = "play"  # Change the icon to "play" when pausing
            instance.text = "재생"  # Change the text to "재생" when pausing

        self.paused = not self.paused

    def start_capturing(self, dt=0):
        self.is_capturing = True
        self.face_detector.start_average_eye_distace = None
        self.face_detector.start_average_both_eye_distace = None
        self.face_detector.Sound_Playing = False
        self.face_detector.previous_yawn_state = False
        self.face_detector.previous_forward_focus = False
        self.face_detector.previous_sleep_state = False
        self.face_detector.is_playing = False
        self.face_detector.yawn_start_time = None
        self.face_detector.sleep_start_time = None
        self.face_detector.forward_focus_start_time = None
        Thread(target=self.update, daemon=True).start()

    def stop_capturing(self):
        self.is_capturing = False
        self.face_detector.start_average_eye_distace = None
        self.face_detector.start_average_both_eye_distace = None
        self.face_detector.Sound_Playing = False
        self.face_detector.previous_yawn_state = False
        self.face_detector.previous_forward_focus = False
        self.face_detector.previous_sleep_state = False
        self.face_detector.is_playing = False
        self.face_detector.yawn_start_time = None
        self.face_detector.sleep_start_time = None
        self.face_detector.forward_focus_start_time = None

    def on_pre_enter(self, *args):
        # 화면이 표시되기 전에 호출되는 이벤트
        # 카메라가 꺼진 상태에서 화면으로 돌아왔을 때 켜지도록 처리
        if self.app.screen_manager.current == self.name:  # 현재 화면이 WelcomeScreen인 경우에만 실행
            self.start_capturing() if not self.is_capturing else None

    def exit_screen(self, instance):
        self.stop_capturing()
        self.app.screen_manager.current = self.app.screen_manager.previous

        # Stop the current Kivy application
        self.app.stop()

        # Restart the application by creating a new instance and running it
        new_app_instance = Example()
        new_app_instance.run()

    def update(self, dt):
        if self.is_capturing:
            _, frame = self.capture.read()
            self.face_detector.detect_face(frame, frame.shape[1], frame.shape[0], False, 0, False, 0)
            self.face_detector.Yawn()
            self.face_detector.FoucusFoward()
            self.face_detector.Drowsiness()
            self.update_texture(frame)
            # 주행시간 측정 라벨
            elapsed_time = datetime.now() - self.start_time
            elapsed_time_str = str(elapsed_time).split(".")[0]
            self.time_label.text = f"주행시간: {elapsed_time_str}"

    def update_texture(self, frame):
        buf = cv2.flip(frame, -1).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture


class Example(MDApp):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.previous = "main"

        main_screen = MainScreen(self, name="main")
        welcome_screen = WelcomeScreen(self, name="welcome")

        self.screen_manager.add_widget(main_screen)
        self.screen_manager.add_widget(welcome_screen)

        # WelcomeScreen을 Example 클래스의 속성으로 추가
        self.welcome_screen = welcome_screen

        return self.screen_manager


if __name__ == '__main__':
    app = Example()
    app.run()
