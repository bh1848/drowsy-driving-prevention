# Drowsy Driving Prevention (졸음운전 방지 시스템)

## 📌 프로젝트 개요
이 프로젝트는 운전자의 눈 움직임(EAR, 깜빡임 패턴)을 실시간으로 분석하여  
졸음 징후가 감지되면 차량 핸들에 장착된 Arduino 진동 모듈에 즉시 경고 신호를 보내는   
졸음운전 방지 프로토타입 시스템입니다.

카메라 영상 분석 → 졸음 판정 → 하드웨어 경고까지 이어지는  
엔드 투 엔드(End-to-End) 구조를 Python 기반으로 직접 구현했습니다.

---

## 🛠 Tech Stack
- **Language**: Python 3.8+
- **Computer Vision**: OpenCV, face landmark detection, EAR(Eye Aspect Ratio)
- **Machine Learning**: MediaPipe / Custom ONNX model 기반 눈 감김 감지
- **Hardware Interface**: pyserial 기반 Arduino 통신
- **Runtime**: Webcam + Local Python + Arduino vibration device
- **Optional**: Flask 기반 로깅/대시보드, Docker

---

## ⚙️ 시스템 아키텍처

1. **Webcam**  
   - 운전자의 얼굴·눈 영역을 실시간으로 캡처

2. **Python CV 모듈**  
   - 얼굴/눈 랜드마크 검출  
   - EAR(Blink Ratio) 계산  
   - 일정 시간 이상 임계값 이하 → “졸음 감지”

3. **알림 전송 모듈**  
   - 졸음 발생 시 Arduino에 `'1'` 등의 신호 전송  
   - 통신 방식: pyserial (USB Serial)

4. **Arduino Module**  
   - Python에서 전달된 신호 수신  
   - 핸들 진동 모터 On/Off 제어

5. **Monitoring/Logging**  
   - 졸음 이벤트 발생 기록  
   - Flask 기반 상태 모니터링 페이지 구성 가능

---

## 🌟 주요 기능

### ✔ 실시간 얼굴·눈 인식  
- OpenCV 기반 랜드마크 검출  
- 눈 거리 기반 EAR 계산(눈 감김 정도 측정)  
- 깜빡임 빈도 분석(blink rate)

### ✔ 졸음 판정 알고리즘  
- EAR < threshold 지속 판단  
- 다중 조건(EAR + Blink interval) 조합 판정  
- 오탐 줄이기 위한 smoothing 적용

### ✔ Arduino 진동 경고  
- pyserial로 즉시 신호 송신  
- 전송 프로토콜 설계 (경고 시작/해제)  
- 아두이노의 하드웨어 동작은 팀원이 구현

### ✔ 실시간 UI + 디버깅 화면  
- OpenCV 창에 다음 정보 오버레이  
  - EAR 값  
  - 눈 감김 상태  
  - 졸음 여부  
  - 시리얼 통신 상태  

---

## 👤 My Role (방혁)

본 프로젝트에서 Python 기반 AI/시스템 통합을 전담했습니다.

### Computer Vision / AI
- EAR 기반 졸음 감지 알고리즘 직접 구현  
- 눈 랜드마크 검출 및 안정화  
- 임계값 튜닝 및 false-positive 감소 로직 개선

### 실시간 UI·영상 처리
- OpenCV로 실시간 스트리밍 환경 구축  
- UI(오버레이), 연산, 시리얼 통신을 한 프로세스에서 동시 처리  
- Thread 기반 비동기 구조 설계

### Arduino와 연동
- Python → Arduino 시리얼 통신 구현  
- 졸음 상태 변화에 따른 이벤트 신호 전송  
- 팀원의 아두이노 모터 제어 코드와 연동 테스트

---

## ✔ Summary

이 프로젝트는 Python 기반으로  
실시간 영상 처리 + AI 분석 + UI + 하드웨어 연동이 결합된 복합 구조였습니다.

특히 다음이 어려웠습니다:

- AI(컴퓨터 비전) 경험 없이 EAR 알고리즘을 직접 구현해야 했던 점  
- Python 내부에서 영상 처리·알고리즘·UI·시리얼 통신을 동시에 처리해야 했던 점  
- 외부 장치(Arduino)와의 실시간 연동 안정성 확보  

이 경험을 통해 실시간 시스템 처리 능력과  
하드웨어 연동 기반 애플리케이션 구조에 대해 이해하게 됐습니다.
