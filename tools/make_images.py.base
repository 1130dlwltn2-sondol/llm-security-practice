#!/usr/bin/env python3
"""Cursor 실전 가이드 책용 이미지 생성 스크립트 (PIL 기반)."""
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
    d.ellipse([-180, -180, 320, 320], outline=(129, 140, 248, 90), width=3)
    d.ellipse([-120, -120, 260, 260], outline=(192, 132, 252, 70), width=2)
    d.ellipse([760, 980, 1180, 1400], outline=(45, 212, 191, 80), width=3)
    d.ellipse([820, 1040, 1120, 1340], outline=(129, 140, 248, 60), width=2)
    for i in range(6):
        x = 700 + i * 45
        d.line([(x, 0), (x + 220, 420)], fill=(255, 255, 255, 14), width=2)

    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    text_center(d, W / 2, 66, "W I K I D O C S   T E C H   B O O K", fr(26), INDIGO)
    d.line([(120, 128), (880, 128)], fill=LINE, width=2)

    text_center(d, W / 2, 210, "Cursor", fb(110), WHITE)
    text_center(d, W / 2, 345, "실전 가이드", fb(96), INDIGO)

    text_center(d, W / 2, 520, "에디터 안에서 끝내는", fb(44), WHITE)
    text_center(d, W / 2, 586, "AI 코딩 실전서", fb(44), WHITE)

    rrect(d, [160, 690, 840, 758], 34, PANEL, outline=LINE, width=2)
    text_center(d, W / 2, 706, "타이핑하는 에디터가 아니라 일을 맡기는 에디터", fb(31), WHITE)

    topics = [
        "Tab 자동완성, Chat, Composer, 에이전트",
        "@ 멘션으로 코드베이스 전체 참조",
        "Rules로 팀 코딩 스타일 고정",
        "MCP 연동과 디버깅·테스트 자동화",
        "VS Code 마이그레이션 가이드",
    ]
    y = 810
    text_center(d, W / 2, y, "이 책에서 다루는 내용", fr(26), MUTED)
    y += 44
    for i, t in enumerate(topics):
        rrect(d, [170, y, 830, y + 46], 23, (24, 26, 62), outline=(70, 82, 140), width=1)
        d.ellipse([194, y + 11, 228, y + 45], fill=INDIGO)
        fnum = fb(26)
        num = str(i + 1)
        bb = d.textbbox((0, 0), num, font=fnum)
        d.text((211 - (bb[2] - bb[0]) / 2 - bb[0], y + 13), num, font=fnum, fill=(255, 255, 255))
        d.text((244, y + 15), t, font=fr(24), fill=WHITE)
        y += 56

    d.line([(120, 1130), (880, 1130)], fill=LINE, width=2)
    text_center(d, W / 2, 1158, "저자  이준수", fr(30), MUTED)
    text_center(d, W / 2, 1202, "기준일  2026-10-09", fr(26), MUTED)

    img.save(os.path.join(ASSETS, "cover.png"))
    print("cover.png saved")


# ------------------------------------------------- Tab 자동완성 흐름 1500x560
def make_tab_flow():
    W, H = 1500, 560
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    text_center(d, W / 2, 24, "Tab: Predict and Complete", fb(40), INK)
    text_center(d, W / 2, 78, "커서를 움직이면 다음 편집을 미리 예측한다",
                fr(26), SUB)

    steps = [
        ("입력", "코드 타이핑\n커서 이동", INDIGO),
        ("예측", "주변 맥락 분석\n다음 편집 추론", VIOLET),
        ("제안", "회색 텍스트로\n변경 미리 표시", TEAL),
        ("수락", "Tab으로 수락\n부분 수락도 가능", CORAL),
    ]
    x0, bw, gap = 60, 320, 30
    y0 = 170
    for i, (t, desc, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 200], 20, (255, 255, 255),
              outline=CARD_LINE, width=2)
        d.rectangle([x, y0, x + bw, y0 + 12], fill=color)
        text_center(d, x + bw / 2, y0 + 34, t, fb(32), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 84 + j * 38, line, fr(24), SUB)
        if i < 3:
            arrow(d, x + bw + 5, y0 + 100, x + bw + gap - 5, y0 + 100,
                  fill=(148, 163, 184), width=5)

    text_center(d, W / 2, 450, "제안이 마음에 안 들면 Esc, 마음에 들면 Tab",
                fr(26), SUB)
    img.save(os.path.join(ASSETS, "fig-tab-flow.png"))
    print("fig-tab-flow.png saved")


# ------------------------------------------------- 코드베이스 인덱싱 1400x600
def make_codebase():
    W, H = 1400, 600
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    text_center(d, W / 2, 24, "Codebase Indexing + Chat", fb(40), INK)
    text_center(d, W / 2, 78, "열지 않은 파일까지 통째로 이해하고 답변한다",
                fr(26), SUB)

    files = [
        (80, 170, "auth.py", "인증 로직", BLUE),
        (330, 170, "payment.py", "결제 로직", TEAL),
        (990, 170, "api.py", "API 라우트", INDIGO),
        (1120, 170, "...", "나머지 파일", VIOLET),
    ]
    for x, y, t, desc, color in files:
        rrect(d, [x, y, x + 180, y + 110], 16, (255, 255, 255), outline=color, width=3)
        text_center(d, x + 90, y + 22, t, fb(24), INK)
        text_center(d, x + 90, y + 58, desc, fr(20), SUB)
        arrow(d, x + 90, y + 110, 700, 360, fill=(148, 163, 184), width=3)

    rrect(d, [520, 340, 880, 460], 22, (30, 41, 59))
    text_center(d, 700, 366, "Codebase Index", fb(32), WHITE)
    text_center(d, 700, 408, "임베딩 · 심볼 그래프", fr(24), (203, 213, 225))

    arrow(d, 700, 465, 700, 505, fill=VIOLET, width=5)
    rrect(d, [420, 505, 980, 565], 18, (255, 255, 255), outline=VIOLET, width=3)
    text_center(d, 700, 520, "질문 하나에 관련 파일 5개를 함께 읽고 답변", fr(24), INK)
    img.save(os.path.join(ASSETS, "fig-codebase.png"))
    print("fig-codebase.png saved")


# ------------------------------------------------- 에이전트 루프 1500x600
def make_agent_loop():
    W, H = 1500, 600
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    text_center(d, W / 2, 24, "Agent Mode Working Loop", fb(40), INK)
    text_center(d, W / 2, 78, "지시 하나로 탐색부터 실행·검증까지",
                fr(26), SUB)

    steps = [
        ("지시", "목표와 제약\n조건을 문장으로", INDIGO),
        ("탐색", "@ 멘션 없이도\n코드베이스 읽기", VIOLET),
        ("계획", "수정 계획 수립\ndiff 미리 확인", TEAL),
        ("실행", "파일 수정\n터미널 명령", BLUE),
        ("검증", "테스트 실행\n결과 보고", CORAL),
    ]
    x0, bw, gap = 40, 252, 30
    y0 = 170
    for i, (t, desc, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 210], 20, (255, 255, 255),
              outline=CARD_LINE, width=2)
        d.rectangle([x, y0, x + bw, y0 + 12], fill=color)
        text_center(d, x + bw / 2, y0 + 34, t, fb(32), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 84 + j * 38, line, fr(24), SUB)
        if i < 4:
            arrow(d, x + bw + 5, y0 + 105, x + bw + gap - 5, y0 + 105,
                  fill=(148, 163, 184), width=5)

    text_center(d, W / 2, 490, "에디터를 떠나지 않고 결과물의 diff를 보고 승인한다",
                fr(26), SUB)
    img.save(os.path.join(ASSETS, "fig-agent-loop.png"))
    print("fig-agent-loop.png saved")


# ------------------------------------------------- Rules 계층 1400x600
def make_rules():
    W, H = 1400, 600
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    text_center(d, W / 2, 24, "Rules: Layered Instructions", fb(40), INK)
    text_center(d, W / 2, 78, "매번 설명하지 말고 규칙으로 고정한다",
                fr(26), SUB)

    layers = [
        (120, 170, "사용자 규칙", "모든 프로젝트에 공통 적용", INDIGO),
        (520, 170, "프로젝트 규칙", ".cursor/rules, 항상 적용", VIOLET),
        (920, 170, "조건부 규칙", "파일 패턴에 따라 자동 적용", TEAL),
    ]
    for x, y, t, desc, color in layers:
        rrect(d, [x, y, x + 360, y + 140], 20, (255, 255, 255), outline=color, width=3)
        text_center(d, x + 180, y + 32, t, fb(28), INK)
        text_center(d, x + 180, y + 74, desc, fr(23), SUB)
        if x > 120:
            arrow(d, x - 80, y + 70, x - 10, y + 70, fill=(148, 163, 184), width=5)

    rrect(d, [120, 400, 1280, 520], 18, (30, 41, 59))
    text_center(d, 700, 422, "예: 이 프로젝트는 테스트 없이 함수를 만들지 않는다", fb(26), WHITE)
    text_center(d, 700, 464, "규칙을 써 두면 Tab, Chat, Agent 모두 같은 스타일로 동작한다",
                fr(24), (203, 213, 225))
    img.save(os.path.join(ASSETS, "fig-rules.png"))
    print("fig-rules.png saved")


# ------------------------------------------------- MCP 연동 1400x620
def make_mcp_cursor():
    W, H = 1400, 620
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    text_center(d, W / 2, 24, "Cursor + MCP", fb(40), INK)
    text_center(d, W / 2, 78, "설정에서 MCP 서버를 등록하면 도구가 된다",
                fr(26), SUB)

    rrect(d, [550, 170, 850, 320], 22, (30, 41, 59))
    text_center(d, 700, 196, "Cursor", fb(34), WHITE)
    text_center(d, 700, 242, "필요할 때 도구를 골라 호출", fr(24), (203, 213, 225))

    servers = [
        (80, 400, "DB 서버", "데이터 조회", BLUE),
        (400, 400, "이슈 트래커", "티켓 조회", TEAL),
        (880, 400, "문서 서버", "사내 문서 검색", INDIGO),
        (1080, 400, "브라우저", "웹 페이지 조회", VIOLET),
    ]
    for x, y, t, desc, color in servers:
        rrect(d, [x, y, x + 240, y + 110], 18, (255, 255, 255), outline=color, width=3)
        text_center(d, x + 120, y + 18, t, fb(26), INK)
        text_center(d, x + 120, y + 56, desc, fr(22), SUB)
        arrow(d, 700, 325, x + 120, y - 5, fill=color, width=3)

    text_center(d, W / 2, 560, "읽기 전용부터 시작, 작업에 필요한 것만 연결한다",
                fr(26), SUB)
    img.save(os.path.join(ASSETS, "fig-mcp-cursor.png"))
    print("fig-mcp-cursor.png saved")


# ------------------------------------------------- 실전 프로젝트 1500x640
def make_project():
    W, H = 1500, 640
    img = Image.new("RGB", (W, H), LIGHT_BG)
    d = ImageDraw.Draw(img)
    fb = lambda s: font(BOLD, s)
    fr = lambda s: font(REG, s)

    text_center(d, W / 2, 24, "Agent Project: 5 Steps", fb(40), INK)
    text_center(d, W / 2, 78, "에이전트 모드로 기능 하나 통째로 만들기",
                fr(26), SUB)

    steps = [
        ("1. 준비", "규칙 작성\nMCP 연결", INDIGO),
        ("2. 계획", "Agent Plan\n계획 검토·수정", VIOLET),
        ("3. 구현", "파일 생성·수정\ndiff 확인", TEAL),
        ("4. 테스트", "테스트 작성\n직접 실행 확인", BLUE),
        ("5. 정리", "커밋 메시지\n변경 요약", CORAL),
    ]
    x0, bw, gap = 40, 252, 30
    y0 = 170
    for i, (t, desc, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 200], 20, (255, 255, 255),
              outline=CARD_LINE, width=2)
        d.rectangle([x, y0, x + bw, y0 + 12], fill=color)
        text_center(d, x + bw / 2, y0 + 34, t, fb(28), INK)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, x + bw / 2, y0 + 80 + j * 36, line, fr(24), SUB)
        if i < 4:
            arrow(d, x + bw + 5, y0 + 100, x + bw + gap - 5, y0 + 100,
                  fill=(148, 163, 184), width=5)

    rrect(d, [40, 450, 1460, 570], 18, (30, 41, 59))
    text_center(d, 750, 470, "각 단계의 결과물은 사람이 눈으로 확인한다", fb(28), VIOLET)
    text_center(d, 750, 512, "과정에서 만든 Rules와 설정은 팀의 자산으로 남는다",
                fr(24), (203, 213, 225))

    img.save(os.path.join(ASSETS, "fig-project-cursor.png"))
    print("fig-project-cursor.png saved")


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    make_cover()
    make_tab_flow()
    make_codebase()
    make_agent_loop()
    make_rules()
    make_mcp_cursor()
    make_project()
