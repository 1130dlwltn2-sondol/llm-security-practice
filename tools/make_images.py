#!/usr/bin/env python3
"""LLM 보안 실전 책용 이미지 생성 스크립트 (PIL 기반).

디자인 시스템은 make_images.py.base(Cursor 실전 가이드)와 동일.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

BG = (17, 18, 42)
PANEL = (30, 32, 74)
INDIGO = (129, 140, 248)
VIOLET = (192, 132, 252)
CORAL = (251, 146, 128)
TEAL = (45, 212, 191)
BLUE = (96, 165, 250)
WHITE = (245, 247, 250)
MUTED = (154, 167, 199)
LINE = (74, 88, 160)
LIGHT_BG = (250, 251, 253)
INK = (30, 41, 59)
SUB = (100, 116, 139)
CARD_LINE = (203, 213, 225)
DARK = (30, 41, 59)


def font(path, size):
    return ImageFont.truetype(path, size, index=1)


def text_center(d, cx, y, s, f, fill):
    bb = d.textbbox((0, 0), s, font=f)
    w = bb[2] - bb[0]
    d.text((cx - w / 2 - bb[0], y), s, font=f, fill=fill)


def rrect(d, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(d, x1, y1, x2, y2, fill=VIOLET, width=4):
    d.line([x1, y1, x2, y2], fill=fill, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    sz = 14
    for da in (2.6, -2.6):
        d.line([x2, y2, x2 + sz * math.cos(ang + da), y2 + sz * math.sin(ang + da)],
               fill=fill, width=width)


def diagram_header(d, W, title, subtitle):
    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)
    text_center(d, W / 2, 24, title, fb(40), INK)
    text_center(d, W / 2, 78, subtitle, fr(26), SUB)


def dashed_rect(d, box, fill_outline, width=3, dash=(14, 10)):
    x1, y1, x2, y2 = box
    def seg(xa, ya, xb, yb):
        length = math.hypot(xb - xa, yb - ya)
        n = max(1, int(length / sum(dash)))
        for i in range(n):
            t0 = i * sum(dash) / length
            t1 = min(1.0, (i * sum(dash) + dash[0]) / length)
            d.line([(xa + (xb - xa) * t0, ya + (yb - ya) * t0),
                    (xa + (xb - xa) * t1, ya + (yb - ya) * t1)],
                   fill=fill_outline, width=width)
    seg(x1, y1, x2, y1)
    seg(x2, y1, x2, y2)
    seg(x2, y2, x1, y2)
    seg(x1, y2, x1, y1)


# ---------------------------------------------------------------- 표지 1000x1300
def make_cover():
    W, H = 1000, 1300
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(17 + (38 - 17) * t)
        g = int(18 + (42 - 18) * t)
        b = int(42 + (88 - 42) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    # 회로 모티프: 노드와 연결선
    nodes = [(90, 700), (160, 620), (250, 660), (90, 900), (180, 960),
             (910, 420), (840, 350), (750, 400), (930, 560)]
    edges = [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7), (5, 8), (2, 8)]
    for a, b in edges:
        d.line([nodes[a], nodes[b]], fill=(74, 88, 160), width=3)
    for x, y in nodes:
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(30, 32, 74),
                  outline=(129, 140, 248), width=3)

    # 자물쇠 모티프
    lx, ly, lw, lh = 430, 675, 140, 120
    d.arc([lx + 25, ly - 45, lx + lw - 25, ly + 55], start=180, end=360,
          fill=(45, 212, 191), width=18)
    rrect(d, [lx, ly, lx + lw, ly + lh], 22, (30, 32, 74),
          outline=(45, 212, 191), width=4)
    kx = lx + lw / 2
    d.ellipse([kx - 14, ly + 34, kx + 14, ly + 62], fill=(45, 212, 191))
    d.rectangle([kx - 7, ly + 50, kx + 7, ly + 88], fill=(45, 212, 191))

    text_center(d, W / 2, 66, "W I K I D O C S   T E C H   B O O K", fr(26), INDIGO)
    d.line([(120, 128), (880, 128)], fill=LINE, width=2)

    text_center(d, W / 2, 200, "LLM", fb(110), WHITE)
    text_center(d, W / 2, 335, "보안 실전", fb(110), INDIGO)

    text_center(d, W / 2, 512, "OWASP LLM Top 10 2026으로 배우는", fb(40), WHITE)
    text_center(d, W / 2, 574, "에이전트 시대의 LLM 방어 실무", fb(40), WHITE)

    text_center(d, W / 2, 815, "공격 원리부터 방어 코드까지, 실무로 익히는 LLM 보안", fb(30), WHITE)

    topics = [
        "프롬프트 인젝션과 EchoLeak 사례 분석",
        "RAG 권한 설계와 검색 전 권한 확인",
        "과도한 에이전시 3근원과 권한 최소화",
        "공급망 무결성: 해시·서명·격리 실행",
        "가드레일 파이프라인 설계와 레드팀 평가",
    ]
    y = 880
    text_center(d, W / 2, y, "이 책에서 다루는 내용", fr(26), MUTED)
    y += 44
    for i, t in enumerate(topics):
        rrect(d, [170, y, 830, y + 42], 21, (24, 26, 62), outline=(70, 82, 140), width=1)
        d.ellipse([194, y + 9, 226, y + 41], fill=INDIGO)
        fnum = fb(24)
        num = str(i + 1)
        bb = d.textbbox((0, 0), num, font=fnum)
        d.text((210 - (bb[2] - bb[0]) / 2 - bb[0], y + 10), num, font=fnum, fill=(255, 255, 255))
        d.text((240, y + 11), t, font=fr(23), fill=WHITE)
        y += 52

    d.line([(120, 1198), (880, 1198)], fill=LINE, width=2)
    text_center(d, W / 2, 1222, "저자  순돌", fr(30), MUTED)

    img.save(os.path.join(ASSETS, "cover.png"))
    print("cover.png saved")


# ------------------------------------------------- LLM 앱 공격 표면 1200x800
def make_threat_surface():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "LLM 앱의 공격 표면",
                   "다섯 개 지점 모두 신뢰 경계 밖에 있다")

    cx, cy, cw, ch = 480, 350, 240, 170
    rrect(d, [cx, cy, cx + cw, cy + ch], 24, DARK)
    text_center(d, cx + cw / 2, cy + 42, "LLM 앱", font(BOLD, 36), WHITE)
    text_center(d, cx + cw / 2, cy + 92, "모델 + 파이프라인", font(REG, 26),
                (203, 213, 225))

    sources = [
        ("사용자 입력", "직접 인젝션의 진입점", 60, 180, BLUE),
        ("RAG 문서", "문서 속 숨겨진 지시", 60, 520, TEAL),
        ("도구 결과", "외부 텍스트가 컨텍스트로", 940, 180, INDIGO),
        ("외부 API", "플러그인·MCP 서버", 940, 520, VIOLET),
        ("벡터 DB", "오염된 문서 주입", 500, 620, CORAL),
    ]
    for t, desc, x, y, color in sources:
        rrect(d, [x, y, x + 200, y + 110], 18, (255, 255, 255),
              outline=color, width=3)
        text_center(d, x + 100, y + 18, t, font(BOLD, 26), INK)
        text_center(d, x + 100, y + 58, desc, font(REG, 20), SUB)
        arrow(d, x + 100, y + (110 if y < cy else 0),
              cx + cw / 2, cy + (0 if y < cy else ch),
              fill=color, width=5)

    text_center(d, W / 2, 740, "믿을 수 있는 것은 시스템 프롬프트와 개발자가 통제하는 코드뿐",
                font(REG, 24), SUB)
    img.save(os.path.join(ASSETS, "llm-threat-surface.png"))
    print("llm-threat-surface.png saved")


# ------------------------------------------------- OWASP 2026 순위 변화 1200x800
def make_owasp_changes():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "OWASP LLM Top 10 2026 순위 변화",
                   "실제 사고 사례 코퍼스를 가중한 첫 번째 순위표")

    rows = [
        ("LLM01", "프롬프트 인젝션", "Prompt Injection", 1, 1, "유지", None),
        ("LLM02", "민감 정보 노출", "Sensitive Information Disclosure", 2, 2, "유지", None),
        ("LLM03", "과도한 에이전시", "Excessive Agency", 3, 6, "상승 3계단", "up"),
        ("LLM04", "공급망", "Supply Chain", 4, 3, "하락 1계단", "down"),
        ("LLM05", "데이터·모델 포이즈닝", "Data and Model Poisoning", 5, 4, "하락 1계단", "down"),
        ("LLM06", "무제한 소비", "Unbounded Consumption", 6, 10, "상승 4계단", "up"),
        ("LLM07", "허위정보", "Misinformation", 7, 9, "상승 2계단", "up"),
        ("LLM08", "히든 컨텍스트 노출", "Hidden Context Exposure", 8, 7, "개명·확장", "rename"),
        ("LLM09", "벡터·임베딩 취약점", "Vector and Embedding", 9, 8, "하락 1계단", "down"),
        ("LLM10", "부적절한 출력 처리", "Improper Output Handling", 10, 5, "하락 5계단", "down"),
    ]
    y0, rh = 130, 58
    for i, (code, ko, en, r26, r25, change, kind) in enumerate(rows):
        y = y0 + i * rh
        bg = (255, 255, 255) if i % 2 == 0 else (241, 245, 249)
        d.rectangle([40, y, 1160, y + 56], fill=bg)
        d.ellipse([60, y + 8, 112, y + 48], fill=DARK)
        text_center(d, 86, y + 13, str(r26), font(BOLD, 24), WHITE)
        d.text((126, y + 14), code, font=font(REG, 22), fill=SUB)
        d.text((216, y + 10), ko, font=font(BOLD, 24), fill=INK)
        d.text((500, y + 18), en, font=font(REG, 18), fill=SUB)
        d.text((840, y + 18), "2025년 %d위" % r25, font=font(REG, 20), fill=SUB)
        if kind == "up":
            d.text((975, y + 10), "▲ %s" % change, font=font(BOLD, 23),
                   fill=(220, 38, 38))
        elif kind == "down":
            d.text((975, y + 10), "▼ %s" % change, font=font(BOLD, 23),
                   fill=(37, 99, 235))
        elif kind == "rename":
            d.text((975, y + 10), "◆ %s" % change, font=font(BOLD, 23),
                   fill=(124, 58, 237))
        else:
            d.text((975, y + 10), "— %s" % change, font=font(BOLD, 23), fill=SUB)

    text_center(d, W / 2, 722, "모델이 말하는 시대의 위험에서, 모델이 행동하는 시대의 위험으로",
                font(REG, 24), SUB)
    img.save(os.path.join(ASSETS, "owasp-2026-changes.png"))
    print("owasp-2026-changes.png saved")


# ------------------------------------------------- 위협 모델링 개념도 1200x800
def make_threat_model():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "LLM 앱 위협 모델링 개념도",
                   "신뢰 경계 · 자산 · 공격 표면을 한 장에 그린다")

    bx1, by1, bx2, by2 = 380, 170, 1020, 600
    d.rectangle([bx1, by1, bx2, by2], fill=(239, 246, 255))
    dashed_rect(d, [bx1, by1, bx2, by2], (37, 99, 235), width=3)
    text_center(d, (bx1 + bx2) / 2, by1 + 16, "신뢰 영역 (경계 안)",
                font(BOLD, 26), (37, 99, 235))

    trusted = [
        ("시스템 프롬프트", "버전 관리되는 지시", 395, 250, 185, 100, BLUE),
        ("개발자 지시", "배포 파이프라인", 615, 250, 185, 100, BLUE),
        ("앱 코드", "검증 로직 포함", 835, 250, 185, 100, BLUE),
        ("자산: 데이터", "개인정보 · 사내문서\nAPI 키 · 비밀값", 395, 420, 185, 140, TEAL),
        ("자산: 행동", "에이전트 도구 권한\n발송 · 삭제 · 결제", 615, 420, 185, 140, TEAL),
        ("자산: 비용·신뢰", "API 사용량 · 예산\n출력 신뢰", 835, 420, 185, 140, TEAL),
    ]
    for t, desc, x, y, w, hh, color in trusted:
        rrect(d, [x, y, x + w, y + hh], 16, (255, 255, 255), outline=color, width=3)
        text_center(d, x + w / 2, y + 16, t, font(BOLD, 24), INK)
        if "\n" in desc:
            for j, line in enumerate(desc.split("\n")):
                text_center(d, x + w / 2, y + 56 + j * 32, line, font(REG, 20), SUB)
        else:
            text_center(d, x + w / 2, y + 56, desc, font(REG, 20), SUB)

    untrusted = [
        ("사용자 입력", 60, 190, CORAL),
        ("외부 문서", 60, 330, CORAL),
        ("도구 결과", 60, 470, CORAL),
        ("외부 API 응답", 60, 610, CORAL),
    ]
    for t, x, y, color in untrusted:
        rrect(d, [x, y, x + 260, y + 88], 16, (255, 255, 255),
              outline=color, width=3)
        text_center(d, x + 130, y + 26, t, font(BOLD, 26), INK)
        text_center(d, x + 130, y + 58, "신뢰 경계 밖", font(REG, 20), SUB)
        arrow(d, x + 260, y + 44, bx1 - 4, y + 44, fill=(148, 163, 184), width=4)

    text_center(d, W / 2, 700, "경계를 넘는 데이터는 전부 검증과 정화의 대상",
                font(REG, 24), SUB)
    img.save(os.path.join(ASSETS, "threat-model.png"))
    print("threat-model.png saved")


# ------------------------------------------------- 간접 인젝션(EchoLeak) 흐름 1200x800
def make_indirect_injection():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "EchoLeak: 간접 인젝션 공격 흐름",
                   "CVE-2025-32711, Microsoft 365 Copilot 사례")

    steps = [
        ("1. 유인", "공격자가 숨겨진\n지시문을 담은\n이메일을 발송", CORAL),
        ("2. 질문", "피해자의\n일상적인 질문\nCopilot에 전달", BLUE),
        ("3. 오염", "검색 엔진이\n공격자 이메일을\n컨텍스트에 포함", INDIGO),
        ("4. 수집", "지시문 발동\n민감 데이터 수집\n메일박스·클라우드", VIOLET),
        ("5. 유출", "프록시 경유 URL로\n공격자 서버에\n데이터 전송", CORAL),
    ]
    x0, bw, gap = 30, 206, 26
    y0 = 170
    for i, (t, desc, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 260], 20, (255, 255, 255),
              outline=CARD_LINE, width=2)
        d.rectangle([x, y0, x + bw, y0 + 14], fill=color)
        text_center(d, x + bw / 2, y0 + 36, t, font(BOLD, 28), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 90 + j * 38, line, font(REG, 22), SUB)
        if i < 4:
            arrow(d, x + bw + 4, y0 + 130, x + bw + gap - 4, y0 + 130,
                  fill=(148, 163, 184), width=5)

    rrect(d, [60, 510, 1140, 640], 18, DARK)
    text_center(d, 600, 528, "핵심 원리: 모델은 지시와 데이터를 구분하지 못한다", font(BOLD, 28), WHITE)
    text_center(d, 600, 572, "시스템 프롬프트·사용자 입력·검색 결과·문서 내용이 하나의 텍스트 흐름으로 합쳐진다",
                font(REG, 24), (203, 213, 225))
    text_center(d, 600, 684, "방어의 출발점: 출처 태그로 신뢰도를 코드 구조에 새긴다",
                font(REG, 24), SUB)
    img.save(os.path.join(ASSETS, "indirect-injection.png"))
    print("indirect-injection.png saved")


# ------------------------------------------------- 권한 확인 후 검색 RAG 1200x800
def make_rag_access_control():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "검색 전 권한 확인 RAG 아키텍처",
                   "권한 필터가 벡터 검색보다 앞에 위치한다")

    steps = [
        ("사용자 질문", "질문 + 사용자 ID", BLUE, 60),
        ("권한 필터", "볼 수 있는 문서 집합\n먼저 확정", TEAL, 310),
        ("벡터 검색", "허용된 집합 안에서만\n유사도 검색", INDIGO, 560),
        ("모델 답변", "권한 없는 문서는\n컨텍스트에 없음", VIOLET, 810),
    ]
    y0 = 170
    for t, desc, color, x in steps:
        bw = 220
        rrect(d, [x, y0, x + bw, y0 + 210], 20, (255, 255, 255),
              outline=color, width=3)
        text_center(d, x + bw / 2, y0 + 30, t, font(BOLD, 28), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 80 + j * 38, line, font(REG, 23), SUB)
        if x < 810:
            arrow(d, x + bw + 4, y0 + 105, x + bw + (810 - x - bw) / 2 + 4 - 13,
                  y0 + 105, fill=(148, 163, 184), width=5)

    rrect(d, [310, 450, 780, 560], 18, (254, 242, 242), outline=CORAL, width=3)
    d.line([(340, 470), (390, 540)], fill=(220, 38, 38), width=6)
    d.line([(340, 540), (390, 470)], fill=(220, 38, 38), width=6)
    d.text((410, 470), "권한 없는 문서", font=font(BOLD, 28), fill=INK)
    d.text((410, 512), "벡터 검색 대상에서 제외", font=font(REG, 23), fill=SUB)
    arrow(d, 545, 450, 545, 384, fill=(220, 38, 38), width=4)

    rrect(d, [60, 610, 1140, 700], 18, DARK)
    text_center(d, 600, 630, "원칙: 모델이 모르는 데이터는 유출할 수 없다",
                font(BOLD, 27), TEAL)
    img.save(os.path.join(ASSETS, "rag-access-control.png"))
    print("rag-access-control.png saved")


# ------------------------------------------------- 과도한 에이전시 3근원 삼각 1200x800
def make_excessive_agency():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "과도한 에이전시의 3근원",
                   "하나라도 과하면 사고, 겹치면 대형 사고")

    nodes = [
        ("과도한 기능", "필요 없는 도구를\n쥐여 주는 것", 470, 210, INDIGO),
        ("과도한 권한", "도구 실행 범위가\n지나치게 넓은 것", 160, 560, CORAL),
        ("과도한 자율성", "승인 없이 스스로\n판단·실행하는 것", 780, 560, VIOLET),
    ]
    centers = []
    for t, desc, x, y, color in nodes:
        bw, bh = 260, 150
        rrect(d, [x, y, x + bw, y + bh], 20, (255, 255, 255),
              outline=color, width=3)
        text_center(d, x + bw / 2, y + 20, t, font(BOLD, 28), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y + 64 + j * 36, line, font(REG, 23), SUB)
        centers.append((x + bw / 2, y + bh / 2))

    for a, b in [(0, 1), (1, 2), (2, 0)]:
        d.line([centers[a], centers[b]], fill=(148, 163, 184), width=4)

    d.ellipse([510, 440, 690, 620], fill=DARK)
    text_center(d, 600, 480, "위험", font(BOLD, 30), CORAL)
    text_center(d, 600, 522, "세 축이 겹치는\n지점이 사고", font(REG, 23), (203, 213, 225))

    text_center(d, 600, 690, "처방: 최소 권한 — 목적에 딱 맞는 도구와 범위만",
                font(REG, 24), SUB)
    img.save(os.path.join(ASSETS, "excessive-agency.png"))
    print("excessive-agency.png saved")


# ------------------------------------------------- 공급망 무결성 검증 파이프라인 1200x800
def make_supply_chain():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "공급망 무결성 검증 파이프라인",
                   "받아 쓰는 모든 구성 요소가 기대한 그것인지 확인한다")

    steps = [
        ("1. 다운로드", "모델 파일·패키지·\nMCP 서버 받기", BLUE),
        ("2. 해시 검증", "게시자가 공개한 해시와\n대조, 불일치 시 중단", INDIGO),
        ("3. 서명 확인", "게시자 개인 키 서명\n확인으로 신뢰 고정", TEAL),
        ("4. 격리 실행", "샌드박스에서 로드·\n실행 후 실제 투입", VIOLET),
    ]
    x0, bw, gap = 60, 252, 30
    y0 = 170
    for i, (t, desc, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 210], 20, (255, 255, 255),
              outline=CARD_LINE, width=2)
        d.rectangle([x, y0, x + bw, y0 + 14], fill=color)
        text_center(d, x + bw / 2, y0 + 36, t, font(BOLD, 28), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 88 + j * 38, line, font(REG, 23), SUB)
        if i < 3:
            arrow(d, x + bw + 4, y0 + 105, x + bw + gap - 4, y0 + 105,
                  fill=(148, 163, 184), width=5)

    items = [
        ("모델 파일", "수 GB 바이너리, 역직렬화 공격 주의", 60, 440, BLUE),
        ("패키지", "해시 고정 설치(--require-hashes)", 420, 440, TEAL),
        ("MCP 서버", "허용 목록 대조 후에만 연결", 780, 440, INDIGO),
    ]
    for t, desc, x, y, color in items:
        rrect(d, [x, y, x + 340, y + 110], 16, (255, 255, 255), outline=color, width=3)
        text_center(d, x + 170, y + 18, t, font(BOLD, 26), INK)
        text_center(d, x + 170, y + 58, desc, font(REG, 20), SUB)

    rrect(d, [60, 600, 1140, 690], 18, DARK)
    text_center(d, 600, 620, "검증은 로드보다 먼저", font(BOLD, 28), WHITE)
    text_center(d, 600, 658, "해시 검증 없이 모델 파일을 여는 것은 출처 불명의 실행 파일을 여는 것과 같다",
                font(REG, 22), (203, 213, 225))
    img.save(os.path.join(ASSETS, "supply-chain-integrity.png"))
    print("supply-chain-integrity.png saved")


# ------------------------------------------------- 가드레일 파이프라인 1200x800
def make_guardrail():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "가드레일 파이프라인: 탐지 · 판단 · 조치",
                   "입력과 출력 단계에 각각 게이트를 둔다")

    stages = [
        ("1. 탐지", "패턴 매칭\n분류기\n휴리스틱", INDIGO, 60),
        ("2. 판단", "차단 / 수정 / 통과\n위험 점수 + 정책", VIOLET, 470),
        ("3. 조치", "로깅 · 알림\n폴백 응답", TEAL, 880),
    ]
    y0 = 170
    bw = 260
    for t, desc, color, x in stages:
        rrect(d, [x, y0, x + bw, y0 + 240], 20, (255, 255, 255),
              outline=color, width=3)
        text_center(d, x + bw / 2, y0 + 30, t, font(BOLD, 30), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 88 + j * 40, line, font(REG, 23), SUB)
        if x < 880:
            arrow(d, x + bw + 6, y0 + 120, x + bw + 144, y0 + 120,
                  fill=(148, 163, 184), width=5)

    branches = [
        ("로깅", "탐지 신호 · 판단 근거 · 조치 내용 구조화 기록", 120, 480, BLUE),
        ("알림", "고위험 차단 시 담당자에게 알림, 임계값 관리", 460, 480, CORAL),
        ("사람 승인", "애매한 요청은 승인 큐로, 네 번째 조치 옵션", 800, 480, VIOLET),
    ]
    for t, desc, x, y, color in branches:
        rrect(d, [x, y, x + 320, y + 110], 16, (255, 255, 255), outline=color, width=3)
        text_center(d, x + 160, y + 14, t, font(BOLD, 26), INK)
        text_center(d, x + 160, y + 54, desc, font(REG, 19), SUB)

    rrect(d, [60, 630, 1140, 720], 18, DARK)
    text_center(d, 600, 648, "이진 판정 대신 위험 점수와 근거를 남긴다",
                font(BOLD, 27), WHITE)
    text_center(d, 600, 686, "왜 차단했는지를 설명할 수 있어야 임계값을 조정할 수 있다",
                font(REG, 22), (203, 213, 225))
    img.save(os.path.join(ASSETS, "guardrail-pipeline.png"))
    print("guardrail-pipeline.png saved")


# ------------------------------------------------- 안전한 사내 문서 도우미 방어 아키텍처 1200x800
def make_secure_doc_assistant():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    diagram_header(d, W, "실전 프로젝트: 안전한 사내 문서 도우미",
                   "네 가지 방어 계층이 결합된 전체 아키텍처")

    layers = [
        ("입력 검증", "질문 · 문서 정화\n출처 태그 부착", INDIGO),
        ("검색 (권한 강제)", "검색 전 권한 확인\n허용 집합만 검색", BLUE),
        ("가드레일", "탐지 · 판단 · 조치\n입출력 이중 게이트", TEAL),
        ("사람 승인", "위험 행동은 승인 큐\n실행 전 사람 확인", VIOLET),
    ]
    x0, bw, gap = 40, 252, 30
    y0 = 160
    for i, (t, desc, color) in enumerate(layers):
        x = x0 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 220], 20, (255, 255, 255),
              outline=color, width=3)
        text_center(d, x + bw / 2, y0 + 30, t, font(BOLD, 27), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 84 + j * 38, line, font(REG, 23), SUB)
        if i < 3:
            arrow(d, x + bw + 5, y0 + 110, x + bw + gap - 5, y0 + 110,
                  fill=(148, 163, 184), width=5)

    arrow(d, 40 - 25, y0 + 110, 40 - 5, y0 + 110, fill=INDIGO, width=5)
    d.text((6, y0 + 70), "요청", font=font(BOLD, 24), fill=INK)
    arrow(d, x0 + 3 * (bw + gap) + bw + 5, y0 + 110,
          x0 + 3 * (bw + gap) + bw + 25, y0 + 110, fill=VIOLET, width=5)
    d.text((1140, y0 + 70), "응답", font=font(BOLD, 24), fill=INK)

    rrect(d, [40, 450, 1160, 560], 18, DARK)
    text_center(d, 600, 468, "어느 계층을 우회하는 경로가 있는지가 설계 리뷰의 핵심 질문",
                font(BOLD, 27), WHITE)
    text_center(d, 600, 508, "검증 · 최소 권한 · 가드레일 · 사람 승인을 겹겹이 쌓는다",
                font(REG, 23), (203, 213, 225))

    text_center(d, 600, 620, "믿을 수 있음: 권한 검증 래퍼 · 가드레일 · 승인 절차",
                font(REG, 24), SUB)
    text_center(d, 600, 660, "믿을 수 없음: 사용자 질문 · 위키 문서 · 검색 결과 스니펫",
                font(REG, 24), SUB)
    img.save(os.path.join(ASSETS, "secure-doc-assistant.png"))
    print("secure-doc-assistant.png saved")


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    make_cover()
    make_threat_surface()
    make_owasp_changes()
    make_threat_model()
    make_indirect_injection()
    make_rag_access_control()
    make_excessive_agency()
    make_supply_chain()
    make_guardrail()
    make_secure_doc_assistant()
