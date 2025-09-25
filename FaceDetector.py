import threading
import time

import cv2
import mediapipe as mp
import numpy as np
from playsound import playsound
import serial


class FaceDetector:
    def __init__(self):
        self.is_playing = False
        self.start_average_eye_distace = None  # 초기 양쪽 눈 위아래 거리 평균값
        self.start_average_both_eye_distace = None  # 초기 양쪽 눈 사이 거리

        self.faceMesh = mp.solutions.face_mesh.FaceMesh(False, 1, True, 0.5, 0.5)
        self.mpDraw = mp.solutions.drawing_utils
        self.drawSpecCircle = self.mpDraw.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))
        self.drawSpecLine = self.mpDraw.DrawingSpec(thickness=1, circle_radius=1, color=(255, 0, 0))
        self.previous_sleep_state = False
        self.sleep_start_time = None
        self.previous_forward_focus = False
        self.forward_focus_start_time = None
        self.label = None
        self.left_eye_top = None
        self.yaw = None
        self.roll = None
        self.pitch = None
        self.lip_vertical_distance = None
        self.average_eye_distance = None
        self.threshold_distance = None
        self.previous_yawn_state = False
        self.yawn_start_time = None
        self.ser = serial.Serial('COM3', 9600)
        self.serial_lock = threading.Lock()

        self.Sound_Playing = False

    def set_label(self, label):
        self.label = label

    def detect_face(self, frame, width, height, previous_sleep_state, sleep_start_time, previous_forward_focus,
                    forward_focus_start_time):
        width, height = frame.shape[1], frame.shape[0]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.faceMesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for faceLandmarks in results.multi_face_landmarks:
                self.mpDraw.draw_landmarks(frame, faceLandmarks, mp.solutions.face_mesh.FACEMESH_TESSELATION,
                                           landmark_drawing_spec=self.mpDraw.DrawingSpec(thickness=1, circle_radius=1,
                                                                                         color=(0, 255, 0)),
                                           connection_drawing_spec=self.mpDraw.DrawingSpec(thickness=1, circle_radius=1,
                                                                                           color=(255, 0, 0)))

                left_eye_landmarks = [133, 173, 157, 158, 159, 160, 161, 246, 33, 130, 7, 163, 144, 145, 153, 154,
                                      155, ]
                right_eye_landmarks = [362, 382, 381, 380, 374, 373, 390, 249, 359, 263, 466, 388, 387, 386, 385, 384,
                                       398, ]

                left_eye_points = [faceLandmarks.landmark[idx] for idx in left_eye_landmarks]
                right_eye_points = [faceLandmarks.landmark[idx] for idx in right_eye_landmarks]

                # 눈의 위아래 좌표 구하기
                self.left_eye_top = min(left_eye_points, key=lambda point: point.y)
                left_eye_bottom = max(left_eye_points, key=lambda point: point.y)
                right_eye_top = min(right_eye_points, key=lambda point: point.y)
                right_eye_bottom = max(right_eye_points, key=lambda point: point.y)

                # 위아래 거리 계산
                left_eye_distance = abs(self.left_eye_top.y - left_eye_bottom.y)
                right_eye_distance = abs(right_eye_top.y - right_eye_bottom.y)

                # 두 눈꺼풀의 거리 평균 계산
                self.average_eye_distance = (left_eye_distance + right_eye_distance) / 2 * 500
                if self.start_average_eye_distace is None:
                    self.start_average_eye_distace = self.average_eye_distance

                self.threshold_distance = self.start_average_eye_distace * 0.6  # 초기 값보다 40% 이상 작아지면 졸음

                rotation_vector = faceLandmarks.landmark[10].x - faceLandmarks.landmark[234].x, \
                                  faceLandmarks.landmark[10].y - faceLandmarks.landmark[234].y, \
                                  faceLandmarks.landmark[10].z - faceLandmarks.landmark[234].z

                rotation_matrix = cv2.Rodrigues(np.array(rotation_vector))[0]

                self.roll = np.arctan2(rotation_matrix[2][1], rotation_matrix[2][2]) * 100  # 상하 각도
                self.pitch = np.arctan2(-rotation_matrix[2][0],
                                        np.sqrt(rotation_matrix[2][1] ** 2 + rotation_matrix[2][
                                            2] ** 2)) * -100  # 좌우 각도
                self.yaw = np.arctan2(rotation_matrix[1][0], rotation_matrix[0][0]) * -100  # 회전 각도

                # 입술 Landmark 좌표
                upper_lip_landmarks = [61, 185, 40, 39, 37, 0, 267, 270]
                lower_lip_landmarks = [146, 91, 181, 84, 17, 314, 405, 321]

                # 입술 Landmark 좌표 추출
                upper_lip_points = [faceLandmarks.landmark[idx] for idx in upper_lip_landmarks]
                lower_lip_points = [faceLandmarks.landmark[idx] for idx in lower_lip_landmarks]

                # 입술 위아래 거리 계산
                upper_lip_y = min(upper_lip_points, key=lambda point: point.y).y
                lower_lip_y = max(lower_lip_points, key=lambda point: point.y).y

                self.lip_vertical_distance = abs(upper_lip_y - lower_lip_y) * height  # 입술 사이의 세로 길이 계산

    # 졸음감지
    def Drowsiness(self):
        if self.average_eye_distance is not None: # None 으로 예외처리
            if self.average_eye_distance < self.threshold_distance and not self.is_playing:
                if not self.previous_sleep_state:
                    self.sleep_start_time = time.time()
                    self.previous_sleep_state = True
                else:
                    if time.time() - self.sleep_start_time >= 3:
                        print("졸음운전은 위험합니다")
                        if not self.Sound_Playing:
                            self.Sound_Playing = True

                            def play_music():
                                playsound("C:/teamproject/last_project/Drowsiness_Bomin.mp3")
                                self.Sound_Playing = False  # 사운드 재생이 끝난 후에 False로 설정

                            threading.Thread(target=play_music).start()
                        self.is_playing = True  # 재생 중 표시
                        self.previous_sleep_state = False
            elif self.average_eye_distance >= self.threshold_distance:
                self.previous_sleep_state = False
                self.is_playing = False  # 재생 중이 아님을 표시

    # 전방주시감지
    def FoucusFoward(self):
        if (self.roll is not None and self.yaw is not None) and (
                int(self.roll) < 8 or int(self.yaw) < 8) and not self.is_playing:
            if not self.previous_forward_focus:
                self.forward_focus_start_time = time.time()
                self.previous_forward_focus = True
            else:
                if time.time() - self.forward_focus_start_time >= 4:
                    print('전방을 주시하세요')
                    if not self.Sound_Playing:
                        self.Sound_Playing = True

                        def play_music():
                            playsound("C:/teamproject/last_project/FocusForward_Bomin.mp3")
                            self.Sound_Playing = False  # 사운드 재생이 끝난 후에 False로 설정

                        threading.Thread(target=play_music).start()
                    self.is_playing = True  # 재생 중 표시
                    self.previous_forward_focus = False
        elif (self.roll is not None and self.yaw is not None and # None 으로 예외처리
              int(self.roll) >= 8 and int(self.yaw) >= 8):
            self.previous_forward_focus = False
            self.is_playing = False  # 재생 중이 아님을 표시

    # 하품 감지
    def Yawn(self):
        if (self.lip_vertical_distance is not None and
                self.lip_vertical_distance > 100 and not self.is_playing):
            if not self.previous_yawn_state:
                self.yawn_start_time = time.time()
                self.previous_yawn_state = True
            else:
                if time.time() - self.yawn_start_time >= 2:
                    print('쉬어가세요')
                    # 음성 파일 재생 로직 추가
                    if not self.Sound_Playing:
                        self.Sound_Playing = True

                        def play_music():
                            playsound("C:/teamproject/last_project/Yawn_Air_Bomin.mp3")
                            self.Sound_Playing = False  # 사운드 재생이 끝난 후에 False로 설정

                        threading.Thread(target=play_music).start()
                    self.is_playing = True  # 재생 중 표시
                    self.previous_yawn_state = False
        elif (self.lip_vertical_distance is not None and
              self.lip_vertical_distance <= 100):
            self.previous_yawn_state = False
            self.is_playing = False  # 재생 중이 아님을 표시

    def play_sound(self, file_path):
        playsound(file_path)

    def send_to_arduino(self, value):
        with self.serial_lock:
            self.ser.write(str(value).encode())

    def Vibration(self):
        if self.Sound_Playing:
            value_to_send = 1
            self.send_to_arduino(value_to_send)
        else:
            value_to_send = 0
            self.send_to_arduino(value_to_send)