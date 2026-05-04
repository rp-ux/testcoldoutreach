from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

# Styles
styles = doc.styles

def set_font(run, size=11, bold=False, color=None, italic=False):
    run.font.name = 'Calibri'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    if level == 1:
        set_font(run, size=16, bold=True, color=(30, 90, 160))
    elif level == 2:
        set_font(run, size=13, bold=True, color=(20, 70, 130))
    elif level == 3:
        set_font(run, size=11, bold=True, color=(40, 40, 40))
    return p

def add_para(text, bold=False, italic=False, size=11, color=None, space_before=2, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_font(run, size=size, bold=bold, color=color, italic=italic)
    return p

def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        set_font(r1, bold=True)
        r2 = p.add_run(text)
        set_font(r2)
    else:
        run = p.add_run(text)
        set_font(run)
    return p

def shade_cell(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        shade_cell(cell, '1E5AA0')
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_font(run, bold=True, color=(255, 255, 255), size=10)

    # Data rows
    for ri, row in enumerate(rows):
        tr = table.rows[ri + 1]
        bg = 'EEF4FB' if ri % 2 == 0 else 'FFFFFF'
        for ci, cell_text in enumerate(row):
            cell = tr.cells[ci]
            shade_cell(cell, bg)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(cell_text))
            # Highlight totals
            is_bold = str(cell_text).startswith('**') or str(cell_text).startswith('Итого')
            clean = str(cell_text).replace('**', '')
            p.runs[0].text = clean
            set_font(run, size=10, bold=is_bold)

    # Column widths
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)

    doc.add_paragraph()
    return table

# ─── TITLE ───────────────────────────────────────────────────────────────────
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(4)
run = p.add_run('Коммерческое предложение для Qzino.com')
set_font(run, size=20, bold=True, color=(30, 90, 160))

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p2.paragraph_format.space_after = Pt(16)
run2 = p2.add_run('Перформанс-маркетинг на CPA-модели: Meta Ads + Google Ads + SEO')
set_font(run2, size=12, italic=True, color=(80, 80, 80))

doc.add_paragraph()

# ─── О НАС ───────────────────────────────────────────────────────────────────
add_heading('О нас', 1)
add_para(
    'Специализируемся на перформанс-маркетинге для crypto-casino и iGaming. '
    'Работаем через платные каналы (Meta Ads, Google Ads) и органику (SEO), '
    'с фокусом на FTD-конверсии в крипто-казино сегменте. Ниже — реальные кейсы в вашей нише.'
)

# ─── КЕЙСЫ ───────────────────────────────────────────────────────────────────
add_heading('Релевантные кейсы', 1)

add_heading('Кейс 1 — Crypto Casino, Meta Ads, Азия → 4 100% ROI', 2)
add_para('Задача: продвижение крипто-казино на азиатских рынках через Meta Ads в условиях жёстких ограничений платформы.')
add_bullet('136 первых депозитов (FTD)')
add_bullet('$45 222 выручки')
add_bullet('ROI 4 100%')
add_bullet('Подход: compliance-first запуск + performance-ориентированные креативы + точный таргетинг по аудиториям')
add_para(
    'Доказывает: даже в ограниченных категориях Meta даёт масштабируемый результат при правильном техническом исполнении.',
    italic=True, color=(80, 80, 80)
)

add_heading('Кейс 2 — Crypto Casino, SEO + Google AI Overview, Индия и Малайзия', 2)
add_para('Задача: органическое доминирование по high-intent запросам на двух крупных крипто-рынках без платного трафика.')
add_bullet('Топ-3 в Google AI Overview')
add_bullet('Попадание в Google Top Stories')
add_bullet('$0 рекламного бюджета')
add_bullet('Устойчивые позиции по конкурентным запросам crypto casino в Индии и Малайзии')
add_para(
    'Доказывает: SEO + авторитетные медиаразмещения дают топовую видимость в долгосрочной перспективе.',
    italic=True, color=(80, 80, 80)
)

add_heading('Кейс 3 — iGaming, Multi-channel', 2)
add_bullet('5X рост FTD через 9+ каналов')
add_bullet('$3 629 112 суммарной выручки (GA4)')
add_bullet('6.40 общий ROAS, пиковый до 7.5 в Google Ads')
add_bullet('5M+ рекламных показов')

# ─── СТРАТЕГИЯ ───────────────────────────────────────────────────────────────
add_heading('Стратегия тестового периода', 1)

add_heading('Гео: Бразилия (старт) → Канада / Worldwide', 2)
add_para(
    'Бразилия — один из сильнейших рынков одновременно по крипте, беттингу и казино: '
    'высокий органический спрос, относительно низкий CPM, быстрый цикл до депозита. '
    'После отработки связки масштабируемся на Канаду и другие Worldwide гео.'
)

add_heading('Каналы (приоритет)', 2)
add_bullet('Facebook / Meta Ads', bold_prefix='')
add_bullet('Google Ads (via cloaking)', bold_prefix='')
add_bullet('SEO — подключается по результатам теста', bold_prefix='')

add_heading('Тестовые связки', 2)
add_table(
    ['Связка', 'Аудитория', 'Формат'],
    [
        ['Crypto + Casino', 'крипто-аудитория, casual gamers', 'видео + статика'],
        ['Crypto + Betting', 'крипто-аудитория, sports fans', 'видео + статика'],
    ],
    col_widths=[5, 7, 5]
)

add_para(
    'Важное условие успешного теста: весь путь пользователя должен быть корректно собран — '
    'целевой креатив → целевые игры → PWA → post-reg flow → понятный путь к депозиту и игре. '
    'Без этого тест даёт искажённую картину, а не реальную эффективность канала.',
    italic=True, color=(160, 60, 0)
)

# ─── БЮДЖЕТ ──────────────────────────────────────────────────────────────────
add_heading('Бюджет тестового периода (~30 дней)', 1)
add_table(
    ['Статья', 'Сумма'],
    [
        ['Трафик (Meta + Google)', '$6 800'],
        ['Креативы (20–40 вариантов)', '$500–$1 000'],
        ['Техническая часть (PWA, постбэки, tracking)', '$450–$600'],
        ['Аккаунты и расходники', '$550–$650'],
        ['Запуск, тесты, оптимизация (фикс команды)', '$1 500'],
        ['Итого', '~$9 500–$10 500'],
    ],
    col_widths=[11, 6]
)
add_para(
    'Рыночный бенчмарк для Бразилии: стоимость FTD в сегменте Casino+Betting — $90–$200 на холодном трафике.',
    italic=True, color=(80, 80, 80)
)

# ─── CPA-УСЛОВИЯ ─────────────────────────────────────────────────────────────
add_heading('CPA-условия (тестовый период)', 1)
add_table(
    ['Параметр', 'Условие'],
    [
        ['Событие', 'FTD (First Time Deposit)'],
        ['Минимальный депозит', 'уточняется на стороне Qzino'],
        ['Hold', '7–14 дней'],
        ['Трекинг', 'ваша платформа или согласованный трекер (постбэк)'],
        ['Длительность теста', '30 дней'],
        ['Отчётность', 'еженедельные срезы: CPL, CPA, CTR, ROAS'],
        ['Масштабирование', 'по результатам теста, с вашего подтверждения'],
    ],
    col_widths=[7, 10]
)

# ─── GOOGLE ADS ──────────────────────────────────────────────────────────────
add_heading('Условия запуска Google Ads', 1)

add_heading('Структура затрат', 2)
add_table(
    ['Статья', 'Стоимость'],
    [
        ['Сервисная комиссия', '$5 500 / мес'],
        ['Инфраструктура (Tier 2–3, напр. Бразилия)', '$3 500 / мес'],
        ['Инфраструктура (Tier 1, напр. Канада)', '$4 500 / мес'],
    ],
    col_widths=[10, 7]
)
add_para(
    'Инфраструктура включает: cloaking-ПО, Google Ads аккаунты, white page домены + контент, '
    'хостинг, антидетект-браузер, прокси.',
    italic=True, color=(80, 80, 80)
)

add_heading('Надбавка по объёму трафика', 2)
add_table(
    ['Бюджет на трафик', 'Надбавка к инфраструктуре'],
    [
        ['$1 000 – $3 000', 'без надбавки (базовая инфраструктура)'],
        ['$3 001 – $6 000', '+ $1 000'],
        ['$6 001 – $9 000', '+ $2 000'],
    ],
    col_widths=[8, 9]
)

add_heading('Платёжная комиссия', 2)
add_table(
    ['Параметр', 'Условие'],
    [
        ['Комиссия на трафик-бюджет', '+10% (уникальные платёжные методы для аккаунтов)'],
        ['НДС', 'большинство аккаунтов VAT-free'],
    ],
    col_widths=[7, 10]
)
add_para('Сервисная и инфраструктурная комиссии невозвратны (non-refundable).', italic=True, color=(160, 60, 0))

add_heading('Пример расчёта: Бразилия, трафик $6 800', 2)
add_table(
    ['Статья', 'Сумма'],
    [
        ['Сервисная комиссия', '$5 500'],
        ['Инфраструктура (Tier 2–3)', '$3 500'],
        ['Надбавка (трафик $6 001–$9 000)', '$2 000'],
        ['Трафик', '$6 800'],
        ['Платёжная комиссия (10%)', '$680'],
        ['Итого за месяц', '$18 480'],
    ],
    col_widths=[11, 6]
)

# ─── META VS GOOGLE ───────────────────────────────────────────────────────────
add_heading('Meta Ads vs Google Ads — сравнение по метрикам', 1)

add_heading('Бразилия (Tier 2–3)', 2)
add_table(
    ['Метрика', 'Meta Ads', 'Google Ads'],
    [
        ['CPM', '$4–8', '$6–12'],
        ['CTR', '1.5–3.5%', '3–6% (search)'],
        ['CPL (регистрация)', '$8–18', '$12–25'],
        ['CPA (FTD)', '$90–160', '$120–200'],
        ['ROAS (ожид.)', '4–6x', '3–5x'],
        ['Скорость выхода на результат', '7–14 дней', '10–21 день'],
        ['Объём аудитории', 'очень высокий', 'высокий'],
        ['Уровень конкуренции', 'высокий', 'очень высокий'],
    ],
    col_widths=[7, 6, 6]
)

add_heading('Канада (Tier 1)', 2)
add_table(
    ['Метрика', 'Meta Ads', 'Google Ads'],
    [
        ['CPM', '$12–22', '$18–35'],
        ['CTR', '1.0–2.5%', '3–7% (search)'],
        ['CPL (регистрация)', '$20–40', '$30–60'],
        ['CPA (FTD)', '$150–280', '$180–350'],
        ['ROAS (ожид.)', '3–5x', '2.5–4x'],
        ['Скорость выхода на результат', '10–21 день', '14–28 дней'],
        ['Объём аудитории', 'средний', 'средний'],
        ['Уровень конкуренции', 'очень высокий', 'критически высокий'],
    ],
    col_widths=[7, 6, 6]
)

add_heading('Сводное сравнение каналов', 2)
add_table(
    ['Параметр', 'Meta Ads', 'Google Ads'],
    [
        ['Тип трафика', 'холодный, широкий', 'тёплый, intent-based'],
        ['Качество FTD', 'среднее → высокое при оптимизации', 'высокое (пользователь сам ищет)'],
        ['Масштабируемость', 'высокая', 'ограничена объёмом запросов'],
        ['Сложность запуска', 'средняя', 'высокая (cloaking обязателен)'],
        ['Стоимость инфраструктуры', 'ниже', 'выше'],
        ['Рекомендация', 'основной канал', 'дополнительный канал'],
    ],
    col_widths=[6, 7, 7]
)
add_para(
    'Оптимальное распределение бюджета на трафик: ~60% Meta / ~40% Google на старте, '
    'с перераспределением после первых 2 недель по реальным данным.',
    bold=True, color=(30, 90, 160)
)

# ─── ИНФЛЮЕНСЕРЫ ─────────────────────────────────────────────────────────────
add_heading('Инфлюенсеры и стримеры', 1)
add_para(
    'У вашей команды есть отдельный департамент по этому направлению — уважаем это разграничение. '
    'Если появится необходимость в стримерах или авторах, с которыми ваша команда ещё не работала, '
    'готовы предложить релевантные контакты. Финальное решение — на вашей стороне.'
)

# ─── СЛЕДУЮЩИЙ ШАГ ───────────────────────────────────────────────────────────
add_heading('Следующий шаг', 1)
add_para('Для выхода на финальные CPA-ставки и подписания условий теста просим подтвердить:')
add_bullet('Минимальный размер депозита, засчитываемого как FTD')
add_bullet('Приоритетное гео для старта (Бразилия / Канада / другое)')
add_bullet('Наличие готовой PWA и настроенного post-reg flow')
add_bullet('Предпочтения по трекеру / постбэк-интеграции')
add_para('Готовы провести короткий звонок для согласования деталей в удобное для вас время.', bold=True)

doc.save('/home/user/testcoldoutreach/qzino-cpa-offer.docx')
print('Done')
