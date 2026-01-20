모터드라이버(L9110S) 제어 실습: 정/역회전 및 PWM 속도 제어🎯 실습 목표ESP32가 L9110S 모터 드라이버에 신호를 주어 DC 모터를 정방향 → 정지 → 역방향 → 정지로 제어하고, **PWM(펄스 폭 변조)**을 이용해 모터의 **속도(세기)**를 조절하는 방법을 익힌다.🛠 준비물ESP32 (DevKit)L9110S 모터드라이버TT 기어드 모터 1개AA 배터리팩 (4개 = 6V 권장)점퍼선 (M-M, M-F)미니 브레드보드🔌 배선도 (모터 A채널 기준)⚠️ 핵심 주의사항:배터리(-), L9110S GND, ESP32 GND는 **반드시 공통 접지(Common Ground)**로 연결해야 합니다. 기준 전위가 다르면 모터가 오작동하거나 신호가 들어가지 않습니다.연결 목적출발 (부품/핀)도착 (부품/핀)설명모터 전원 (+)배터리팩 (+)L9110S VCC (VM)모터 구동용 외부 전원모터 전원 (-)배터리팩 (-)L9110S GND모터 전원 접지공통 접지 (필수)ESP32 GNDL9110S GND제어 신호 기준점 공유방향/속도 제어 1ESP32 GPIO 25L9110S A-IAPWM 신호 입력 A방향/속도 제어 2ESP32 GPIO 26L9110S A-IBPWM 신호 입력 B모터 출력 1L9110S OA1TT모터 단자 1모터 연결모터 출력 2L9110S OA2TT모터 단자 2모터 연결✅ 연결 체크 포인트모터가 반대로 돌면: OA1 ↔ OA2 선의 위치를 서로 바꾼다.모터가 전혀 안 돌면: **GND(공통 접지)**가 잘 연결되었는지 가장 먼저 확인한다.낮은 속도(PWM)에서 안 돌면: 모터의 기동 토크 부족일 수 있다. (실습 2-1 참고)📂 코드 파일 목록실습 1: lab1_forward_reverse_stop.py (기본 방향 제어)실습 2: lab2_pwm_3step_speed.py (3단 속도 제어)실습 2-1: lab2_1_pwm_min_start_test.py (최소 기동값 찾기)실습 3: lab3_pwm_ramp_up_down.py (가감속 램프 제어)실습 1) 정·역·정지 (기본 방향 제어)1. 코드 흐름설정: GPIO 25, 26번 핀을 PWM 모드로 설정 (주파수 20kHz).함수 정의: stop(), forward(speed), reverse(speed) 함수를 만들어 제어를 단순화.루프: 정방향(3초) → 정지(1초) → 역방향(3초) → 정지(1초)를 무한 반복.2. 주요 코드 (lab1_forward_reverse_stop.py)Pythonfrom machine import Pin, PWM
import time

# 1. PWM 핀 설정 (주파수 20kHz = 20000Hz)
# 주파수를 높게 잡으면 모터의 '삐-' 하는 고주파 소음을 줄일 수 있음
IA = PWM(Pin(25), freq=20000)
IB = PWM(Pin(26), freq=20000)

# 2. 제어 함수 정의
def stop():
    """모터 정지 (둘 다 0)"""
    IA.duty(0)
    IB.duty(0)

def forward(speed):
    """정방향 회전 (speed: 0~1023)"""
    IB.duty(0)      # 한쪽은 LOW
    IA.duty(speed)  # 다른 쪽은 PWM

def reverse(speed):
    """역방향 회전 (speed: 0~1023)"""
    IA.duty(0)      # 반대로 설정
    IB.duty(speed)

# 3. 메인 루프
print("[실습1] 정·역·정지 테스트 시작")

while True:
    print("FWD (정방향)")
    forward(900)
    time.sleep(3)

    print("STOP (정지)")
    stop()
    time.sleep(1)

    print("REV (역방향)")
    reverse(900)
    time.sleep(3)

    print("STOP (정지)")
    stop()
    time.sleep(1)
실습 2) PWM 속도 3단 (LOW / MID / HIGH)1. 코드 흐름forward(speed) 함수 하나만 사용하여 speed 값(Duty Cycle)만 변경한다.LOW(저속) → MID(중속) → HIGH(고속) → STOP(정지) 순서로 동작한다.2. 주요 코드 (lab2_pwm_3step_speed.py)Pythonfrom machine import Pin, PWM
import time

IA = PWM(Pin(25), freq=20000)
IB = PWM(Pin(26), freq=20000)

def stop():
    IA.duty(0)
    IB.duty(0)

def forward(speed):
    IB.duty(0)
    IA.duty(speed)

print("[실습2] PWM 속도 3단 제어")

while True:
    # 1단: 저속 (너무 낮으면 안 돌 수 있음)
    print("LOW Speed (450)")
    forward(450)
    time.sleep(3)

    # 2단: 중속
    print("MID Speed (750)")
    forward(750)
    time.sleep(3)

    # 3단: 고속 (최대 1023)
    print("HIGH Speed (1023)")
    forward(1023)
    time.sleep(3)

    print("STOP")
    stop()
    time.sleep(2)
실습 2-1) “최소 기동 PWM” 찾기1. 실습 목적모터는 정지 상태에서 움직이기 시작하려면 일정 수준 이상의 힘(토크)이 필요하다. 이를 기동 임계값이라고 한다. 이 값보다 낮은 PWM을 주면 전기는 흐르지만 모터는 돌지 않는다. 내 모터가 PWM 몇부터 돌기 시작하는지 찾아내는 코드다.2. 주요 코드 (lab2_1_pwm_min_start_test.py)Pythonfrom machine import Pin, PWM
import time

IA = PWM(Pin(25), freq=20000)
IB = PWM(Pin(26), freq=20000)

def stop():
    IA.duty(0)
    IB.duty(0)

def forward(speed):
    IB.duty(0)
    IA.duty(speed)

print("[실습2-1] 최소 기동 PWM 찾기")
stop()
time.sleep(1)

# 0부터 1023까지 50단위로 올리면서 테스트
for s in range(0, 1024, 50):
    print(f"Current PWM: {s}")
    forward(s)
    time.sleep(2) # 2초간 상태 유지 후 다음 단계로

stop()
print("Test Done. 모터가 처음 돌기 시작한 값을 기록하세요.")
실습 3) PWM 램프 (서서히 가속/감속)1. 코드 흐름가속 (Ramp Up): for문을 이용해 PWM을 0에서 1023까지 부드럽게 올린다.유지 (Hold): 최대 속도에서 잠시 머무른다.감속 (Ramp Down): PWM을 1023에서 0까지 부드럽게 내린다.급출발/급정지가 아닌 부드러운 주행감을 구현할 때 사용한다.2. 주요 코드 (lab3_pwm_ramp_up_down.py)Pythonfrom machine import Pin, PWM
import time

IA = PWM(Pin(25), freq=20000)
IB = PWM(Pin(26), freq=20000)

def stop():
    IA.duty(0)
    IB.duty(0)

def forward(speed):
    IB.duty(0)
    IA.duty(speed)

print("[실습3] Soft Start & Stop (Ramp)")

while True:
    print("RAMP UP (가속)")
    # 0 -> 1023 까지 40씩 증가
    for s in range(0, 1024, 40):
        forward(s)
        time.sleep(0.05) # 0.05초 간격으로 속도 증가

    print("HOLD (최대 속도 유지)")
    forward(1023)
    time.sleep(2)

    print("RAMP DOWN (감속)")
    # 1023 -> 0 까지 40씩 감소
    for s in range(1023, -1, -40):
        forward(s)
        time.sleep(0.05)

    print("STOP")
    stop()
    time.sleep(2)
💡 자주 발생하는 문제 해결 (Troubleshooting)모터가 웅~ 소리만 나고 안 돌아요.PWM 값이 너무 낮습니다. (기동 토크 부족)배터리 전압이 부족할 수 있습니다.코드를 실행했는데 아무 반응이 없어요.**공통 접지(GND)**가 끊어졌을 확률이 90%입니다. ESP32 GND와 배터리(-)가 연결되어 있는지 확인하세요.한쪽 방향으로만 돌아요.점퍼선 중 하나가 접촉 불량이거나 빠져 있을 수 있습니다.
