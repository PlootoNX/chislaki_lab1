import csv
import json
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'results'
OUTPUT = ROOT / 'report.pdf'


def load_csv(name):
    with (RESULTS / name).open(encoding='utf-8') as file:
        return list(csv.DictReader(file))


def load_json(name):
    with (RESULTS / name).open(encoding='utf-8') as file:
        return json.load(file)


regular_font = os.environ.get('DAIMON_CJK_FONT_REGULAR')
bold_font = os.environ.get('DAIMON_CJK_FONT_BOLD')
if not regular_font or not bold_font:
    raise RuntimeError('Не найдены управляемые шрифты')

pdfmetrics.registerFont(TTFont('LabFont', regular_font))
pdfmetrics.registerFont(TTFont('LabFont-Bold', bold_font))
pdfmetrics.registerFontFamily(
    'LabFont',
    normal='LabFont',
    bold='LabFont-Bold',
    italic='LabFont',
    boldItalic='LabFont-Bold',
)

styles = getSampleStyleSheet()
body = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='LabFont',
    fontSize=10.5,
    leading=15.5,
    alignment=TA_JUSTIFY,
    spaceAfter=7,
)
title = ParagraphStyle(
    'TitleLab',
    parent=styles['Title'],
    fontName='LabFont-Bold',
    fontSize=20,
    leading=25,
    alignment=TA_CENTER,
    spaceAfter=12,
)
subtitle = ParagraphStyle(
    'SubtitleLab',
    parent=body,
    fontSize=12,
    leading=17,
    alignment=TA_CENTER,
    textColor=colors.HexColor('#555555'),
    spaceAfter=18,
)
h1 = ParagraphStyle(
    'H1Lab',
    parent=styles['Heading1'],
    fontName='LabFont-Bold',
    fontSize=15,
    leading=19,
    spaceBefore=12,
    spaceAfter=8,
    keepWithNext=True,
)
h2 = ParagraphStyle(
    'H2Lab',
    parent=styles['Heading2'],
    fontName='LabFont-Bold',
    fontSize=12,
    leading=16,
    spaceBefore=9,
    spaceAfter=6,
    keepWithNext=True,
)
caption = ParagraphStyle(
    'CaptionLab',
    parent=body,
    fontSize=9,
    leading=12,
    alignment=TA_CENTER,
    textColor=colors.HexColor('#555555'),
    spaceAfter=8,
)
formula = ParagraphStyle(
    'FormulaLab',
    parent=body,
    fontSize=11,
    leading=17,
    alignment=TA_CENTER,
    spaceBefore=5,
    spaceAfter=9,
)
small = ParagraphStyle(
    'SmallLab',
    parent=body,
    fontSize=8.5,
    leading=11,
    alignment=TA_CENTER,
    spaceAfter=0,
)
small_header = ParagraphStyle(
    'SmallHeaderLab',
    parent=small,
    fontName='LabFont-Bold',
)


def p(text, style=body):
    return Paragraph(text, style)


def cell(value, header=False):
    return Paragraph(str(value), small_header if header else small)


def add_table(story, caption_text, header, rows, widths=None, font_size=8.5):
    story.append(p(caption_text, caption))
    data = [[cell(value, True) for value in header]]
    data.extend([[cell(value) for value in row] for row in rows])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign='CENTER')
    table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1.2, colors.HexColor('#222222')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.7, colors.HexColor('#222222')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.2, colors.HexColor('#222222')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))
    story.append(table)
    story.append(Spacer(1, 9))


def add_image(story, filename, caption_text, width=16*cm, height=9*cm):
    story.append(Image(str(RESULTS / filename), width=width, height=height))
    story.append(p(caption_text, caption))


def fmt(value):
    value = float(value)
    if value < 0.001:
        return f'{value:.2e}'
    if value < 1:
        return f'{value:.6f}'
    return f'{value:.4f}'


def fmt_num(value):
    return f'{float(value):.6g}'


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFont('LabFont', 8.5)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(2.5*cm, height - 1.35*cm, 'Лабораторная работа №1')
    canvas.drawRightString(width - 2*cm, height - 1.35*cm, 'Число обусловленности')
    canvas.line(2.5*cm, height - 1.55*cm, width - 2*cm, height - 1.55*cm)
    canvas.drawCentredString(width / 2, 1.25*cm, str(doc.page))
    canvas.restoreState()


correctness = load_csv('correctness.csv')
conditions = load_csv('condition_numbers.csv')
zero_rows = load_csv('zero_to_positive.csv')
research = load_json('mini_research.json')
full_timings = load_json('full_timings.json')
metrics = load_json('derived_metrics.json')
sparse_correctness = load_csv('sparse_correctness.csv')
sparse_timings = load_json('sparse_timings.json')
sparse_conditions = load_csv('sparse_condition_numbers.csv')
special = load_csv('sparse_special_case.csv')
c_rows = load_csv('c_perturbations.csv')
a_rows = load_csv('a_perturbations.csv')
b_rows = load_csv('b_perturbations.csv')


doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    topMargin=2.2*cm,
    bottomMargin=2*cm,
    leftMargin=2.5*cm,
    rightMargin=2*cm,
    title='Лабораторная работа №1',
    author='Студент',
    subject='Число обусловленности и чувствительность на дискретной модели',
)
story = []

story.append(p('Лабораторная работа №1', title))
story.append(p('Число обусловленности и чувствительность на дискретной модели:<br/>число решений уравнения a<sup>y</sup> ≡ c (mod b)', subtitle))
story.append(p('<b>Цель работы</b> — сравнить наивную, бинарную и итеративную реализации подсчёта числа решений, исследовать их сложность и изучить чувствительность дискретной модели к малым изменениям параметров.'))
story.append(p('<b>Исполнитель:</b> ____________________'))
story.append(Spacer(1, 8))

story.append(p('1. Постановка задачи', h1))
story.append(p('Рассматривается сравнение a<sup>y</sup> ≡ c (mod b), где b ≥ 2, a и c принадлежат диапазону от 0 до b−1, а y пробегает значения от 0 до b−1. Используется соглашение 0<sup>0</sup> = 1.'))
story.append(p('N(a,b,c) = #{y ∈ {0, …, b−1}: a<sup>y</sup> ≡ c (mod b)}.', formula))
story.append(p('Выходом модели является не само решение y, а количество таких решений. Параметры модели образуют точку p = (a,b,c).'))

story.append(p('2. Реализации и проверка корректности', h1))
story.append(p('<b>count_naive</b> вычисляет каждую степень заново с помощью y последовательных модульных умножений. <b>count_fastpow</b> применяет собственную реализацию бинарного возведения в степень. <b>count_iter</b> последовательно получает следующую степень из предыдущей одним умножением. Во всех реализациях промежуточные результаты сокращаются по модулю b.'))
add_table(
    story,
    'Таблица 1. Проверка совпадения результатов',
    ('a', 'b', 'c', 'N', 'naive', 'fastpow', 'iter'),
    [(r['a'], r['b'], r['c'], r['expected'], r['naive'], r['fastpow'], r['iter']) for r in correctness],
)
story.append(p('Пояснения к значениям: для (2,7,4) подходят y = 2 и 5; для (2,7,3) решений нет; для (3,11,1) подходят y = 0, 5 и 10; для (0,7,0) подходят y = 1,…,6; для (0,7,1) подходит только y = 0.'))
story.append(p('<b>Замечание к условию.</b> В проверочной таблице исходного PDF для (3,11,1) и (0,7,0) указаны значения 1. Они противоречат определению модели: непосредственный перебор даёт соответственно 3 и 6. В работе использованы значения, следующие из определения.'))

story.append(p('3. Анализ сложности', h1))
add_table(
    story,
    'Таблица 2. Число модульных умножений по порядку роста',
    ('Реализация', 'Полный диапазон', 'Разреженный набор, |Y| = k'),
    [
        ('count_naive', 'O(b²)', 'O(k·b)'),
        ('count_fastpow', 'O(b log b)', 'O(k log b)'),
        ('count_iter', 'O(b)', 'O(b), сканирование всего диапазона'),
    ],
    widths=[4*cm, 4*cm, 7*cm],
)
story.append(p('На полном диапазоне итеративная реализация асимптотически лучше: каждый переход к следующему y требует одного умножения. На разреженном наборе она по-прежнему сканирует все b значений, поэтому при b ≫ k log b проигрывает бинарному возведению только для k выбранных точек.'))

story.append(p('4. Замеры времени на полном диапазоне', h1))
story.append(p('Замеры выполнены при a = 2 и c = 1. Для каждого запуска бралось медианное время трёх повторов.'))
add_table(
    story,
    'Таблица 3. Время работы полной модели, секунды',
    ('b', 'count_naive', 'count_fastpow', 'count_iter'),
    [(r['b'], fmt(r['naive']), fmt(r['fastpow']), fmt(r['iter'])) for r in full_timings],
)
add_image(story, 'full_time.png', 'Рисунок 1. Зависимость времени от b в логарифмических осях', height=10*cm)
story.append(p(f"Наклоны логарифмических графиков: naive ≈ {metrics['slopes']['naive']:.2f}, fastpow ≈ {metrics['slopes']['fastpow']:.2f}, iter ≈ {metrics['slopes']['iter']:.2f}. Это согласуется с порядками O(b²), O(b log b) и O(b): наклон бинарной реализации близок к единице, а множитель log b проявляется как небольшое превышение."))
story.append(p(f"При b = 10<sup>4</sup> наивная реализация медленнее итеративной примерно в {metrics['naive_iter_ratio_b_10000']:.0f} раз. Экстраполяция по закону O(b²) для b = 10<sup>5</sup> даёт {metrics['naive_estimate_b_100000_seconds']:.1f} с, то есть около 3,2 минуты. Поэтому прямой замер не проводился."))
story.append(p('Асимптотику следует отличать от константы реализации. Встроенный Python pow(a,y,b) выполнен в C и может обгонять Python-код в десятки раз, но его сложность остаётся O(log y), а не O(1). В данной работе использован собственный binpow.'))

story.append(PageBreak())
story.append(p('5. Чувствительность и число обусловленности', h1))
story.append(p('Для исходной точки p и возмущённой точки p′ используется регуляризованная чувствительность:'))
story.append(p('S = (|N(p′) − N(p)| / max(N(p),1)) / max<sub>i</sub>(|p′<sub>i</sub> − p<sub>i</sub>| / max(|p<sub>i</sub>|,1)).', formula))
story.append(p('Знаменатель является максимальным относительным изменением параметров. Допустимые возмущения: a → (a±1) mod b, c → (c±1) mod b и b → b±1 при b′ ≥ 2; в последнем случае a и c приводятся по новому модулю. Оценка κ<sub>lab</sub> — максимум S по всем допустимым возмущениям.'))

story.append(p('5.1. Изменение параметров a, b и c', h2))
add_table(
    story,
    'Таблица 4. Примеры скачков N при изменении c на +1',
    ('a', 'b', 'c', 'N до', 'N после'),
    [(r['a'], r['b'], r['c'], r['N'], r['N_c_plus']) for r in c_rows if r['N'] != r['N_c_plus']][:3],
)
add_table(
    story,
    'Таблица 5. Примеры изменений N при возмущении a',
    ('a', 'b', 'c', 'N', 'a+1', 'a−1'),
    [(r['a'], r['b'], r['c'], r['N'], r['N_a_plus'], r['N_a_minus']) for r in a_rows if r['N'] != r['N_a_plus'] or r['N'] != r['N_a_minus']][:3],
)
add_table(
    story,
    'Таблица 6. Примеры изменений N при возмущении b',
    ('a', 'b', 'c', 'N', 'b+1', 'b−1'),
    [(r['a'], r['b'], r['c'], r['N'], r['N_b_plus'], r['N_b_minus']) for r in b_rows if r['N'] != r['N_b_plus'] or r['N'] != r['N_b_minus']][:3],
)
story.append(p('В полных таблицах по 144 строки изменение результата обнаружено в 60 строках для c, 132 строках для a и 104 строках для b. Возмущение b особенно значимо, поскольку b одновременно задаёт модуль вычислений и размер диапазона перебора y.'))

story.append(p('5.2. Оценки κ<sub>lab</sub> для десяти точек', h2))
add_table(
    story,
    'Таблица 7. Число решений и оценка числа обусловленности',
    ('a', 'b', 'c', 'N', 'κ_lab'),
    [(r['a'], r['b'], r['c'], r['N'], fmt_num(r['kappa'])) for r in conditions],
)
story.append(p('Наибольшее значение в выбранном наборе получено в точке (6,15,5): N = 0, κ<sub>lab</sub> = 70. Для точки (5,17,3) с N = 1 оценка равна 17, а для (2,7,3) с N = 0 — 6. Нулевое исходное N не означает отсутствие чувствительности: благодаря регуляризации изменение до положительного значения даёт конечную оценку.'))

story.append(p('5.3. Переходы из N = 0 в N > 0', h2))
add_table(
    story,
    'Таблица 8. Три различные исходные точки с переходом из нуля',
    ('p', 'p′', 'N(p)', 'N(p′)', 'S'),
    [
        (f"({r['a']},{r['b']},{r['c']})", f"({r['a_new']},{r['b_new']},{r['c_new']})", r['N'], r['N_new'], r['S'])
        for r in zero_rows
    ],
    widths=[3*cm, 3*cm, 2*cm, 2*cm, 2*cm],
)
story.append(p('В строгой относительной формуле во всех трёх случаях делитель равен |N(p)| = 0, а числитель положителен. Поэтому строгая относительная чувствительность равна +∞. Замена |N(p)| на max(N(p),1) устраняет деление на ноль и даёт конечные значения 1, 0,5 и 2.'))

story.append(p('6. Мини-исследование при b ≤ 50', h1))
story.append(p(f"Перебраны все {research['total_count']} точек: для каждого b от 2 до 50 значения a и c пробегают диапазон 0,…,b−1. Получено {research['zero_count']} точек с N = 0 и {research['multi_count']} точек с N ≥ 2."))
story.append(p(f"Максимальная оценка κ<sub>lab</sub> = {research['max_kappa']:.0f} найдена в точке {tuple(research['max_point'])}. В ней N = 0, а при переходе b = 49 → 50 получается N = 48. Относительное изменение параметров равно 1/49, откуда S = 48/(1/49) = 2352."))
story.append(p(f"Пример устойчивой точки: {tuple(research['stable_point'])}. Для неё N = 0, и все шесть допустимых возмущений сохраняют N = 0, поэтому κ<sub>lab</sub> = 0."))
add_image(story, 'n_histogram.png', 'Рисунок 2. Гистограмма распределения N по всем точкам при b ≤ 50', height=8*cm)
add_image(story, 'change_fraction.png', 'Рисунок 3. Доля точек, где хотя бы одно возмущение меняет N', height=10*cm)
story.append(p('Доля чувствительных точек остаётся высокой во всём диапазоне: среднее значение около 0,836, минимум около 0,635 при b = 45. Колебания связаны с дискретной и периодической структурой сравнений.'))

story.append(PageBreak())
story.append(p('7. Разреженная модель', h1))
story.append(p('Фиксируется k = 500. Набор Y(b) состоит из значений floor(i(b−1)/(k−1)), i = 0,…,k−1. Подсчитываются только y ∈ Y(b). Поскольку выбранные y не являются соседними, итеративная реализация вынуждена сканировать полный диапазон и проверять принадлежность y набору Y(b).'))
story.append(p('7.1. Проверка корректности', h2))
add_table(
    story,
    'Таблица 9. Совпадение разреженных реализаций',
    ('a', 'b', 'c', 'naive', 'fastpow', 'iter'),
    [(r['a'], r['b'], r['c'], r['naive'], r['fastpow'], r['iter']) for r in sparse_correctness],
)
story.append(p('Все три функции совпали на наборах с b ≤ 10<sup>5</sup>, включая a = 0, a = 1 и малые b, где набор Y(b) может содержать повторяющиеся индексы до приведения к множеству.'))

story.append(p('7.2. Замеры и экстраполяция', h2))
b_values = (1000, 100000, 10000000, 1000000000, 10**12, 10**15)
timing_rows = []
for b in b_values:
    key = str(b)
    row = [f'{b:,}'.replace(',', ' ')]
    for name in ('naive', 'fastpow', 'iter'):
        measured = sparse_timings['measured'][name]
        estimates = sparse_timings['estimates'][name]
        if key in measured:
            row.append(fmt(measured[key]))
        else:
            row.append(f"не выполнять<br/>≈ {estimates[key]:.3g} с")
    timing_rows.append(row)
add_table(
    story,
    'Таблица 10. Время разреженной модели; для пропущенных запусков указана оценка',
    ('b', 'count_sp_naive', 'count_sp_fastpow', 'count_sp_iter'),
    timing_rows,
    widths=[2.5*cm, 4.2*cm, 4.2*cm, 4.2*cm],
)
story.append(p('Для count_sp_naive после b = 10<sup>5</sup> использована линейная экстраполяция по b, поскольку при фиксированном k средний показатель y растёт пропорционально b. Уже при b = 10<sup>7</sup> оценка превышает 60 секунд. Для count_sp_iter после фактического замера 59,28 с при b = 10<sup>9</sup> также применена линейная экстраполяция; запуски при b = 10<sup>12</sup> и 10<sup>15</sup> не выполнялись.'))
add_image(story, 'sparse_time.png', 'Рисунок 4. Измеренное время разреженных реализаций', height=10*cm)
story.append(p('Результаты подтверждают вывод из анализа сложности: при больших b быстрое возведение для 500 выбранных точек занимает миллисекунды, тогда как полное сканирование диапазона быстро становится непрактичным.'))

story.append(p('7.3. Обусловленность разреженной модели', h2))
add_table(
    story,
    'Таблица 11. Оценки κ_lab при a = 2, c = 1',
    ('a', 'b', 'c', 'N_sp', 'κ_lab'),
    [(r['a'], r['b'], r['c'], r['N_sp'], fmt_num(r['kappa'])) for r in sparse_conditions],
)
story.append(p('Оценка при b = 10<sup>6</sup> значительно выше, чем при b = 10<sup>9</sup> и 10<sup>12</sup>. Это показывает, что рост b сам по себе не гарантирует монотонного изменения обусловленности: результат зависит от дискретной структуры набора Y(b) и от конкретных возмущений.'))

story.append(p('7.4. Частный случай b = 10¹², c = 1', h2))
story.append(p('Для a = 2 получается N<sub>sp</sub> = 1: решение даёт y = 0, поскольку 2<sup>0</sup> = 1, а остальные элементы Y(b) решений не дают. Аналогичный результат получен для a = 0 и a = 3.'))
add_table(
    story,
    'Таблица 12. Проверка утверждения для разных a',
    ('a', 'b', 'c', 'N_sp'),
    [(r['a'], r['b'], r['c'], r['N_sp']) for r in special],
)
story.append(p('<b>Замечание к условию.</b> Утверждение «N<sub>sp</sub>(a,b,c) = 1 для любого a» при b = 10<sup>12</sup> и c = 1 неверно без дополнительных ограничений. При a = 1 все 500 выбранных y являются решениями, поскольку 1<sup>y</sup> = 1; при a = b−1 получено 265 решений. Корректная формулировка должна относиться к рассмотренному a = 2 или к отдельно оговорённому классу значений a.'))

story.append(p('8. Общие выводы', h1))
story.append(p('Все три реализации полной и разреженной моделей дают одинаковые результаты при соблюдении соглашений задачи. Итеративный метод наиболее эффективен для полного диапазона, а бинарное возведение — для разреженного набора при больших b. Наивный метод пригоден для проверки и небольших входов, но его квадратичный рост быстро делает вычисления дорогими.'))
story.append(p('Чувствительность дискретной модели нельзя анализировать производной: выход N изменяется скачками. Поэтому число обусловленности оценивается перебором допустимых возмущений. Регуляризация max(N,1) позволяет сравнивать точки с нулевым числом решений, хотя строгая относительная чувствительность в таких переходах бесконечна.'))
story.append(p('Исходный код находится в файлах main.py, gen.py, sparse.py и run_experiments.py. Таблицы результатов сохранены в каталоге results; повторный запуск выполняется командой python3 run_experiments.py.'))

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(OUTPUT)
