from tkinter import Tk, Canvas
from random import randint
from math import sin, cos, pi

# https://habr.com/ru/post/172827/ - сайт, на котором брал информацию

amount_needles = 10

# Параметры полотна:
CANVAS_OPTIONS = {
    'width': 1220,
    'height': 400,
    'bg': 'black'
}

# Параметры иголок:
NEEDLES_OPTIONS = {
    'fill': '#87939A',
    'width': 1,
    'length': 20
}

CHART_OPTIONS = {
    'fill': 'lime',
    'width': 2,
    'tags': ('for clean',)
}

chart = None  # список для сохранения дескрипторов диаграммы
chart_factor = 1
stop_process = None  # глобальная переменная, которая в последствии станет экземпляром класса

drawed_needles = 0
overlapped_needles = set()

needles_ids = []  # список для сохранения дескрипторов иголок
lines_ids = []  # список для сохранения дескрипторов линий
data_ids = []  # список для хранения дескрипторов текста, который будет выводится на полотно
middle_line_ids = []  # список для сохранения дескриптора средней линии

list_overlapping = []  # список для сохранения координат пересечения
list_values_pi = [0.0]  # список для сохранения всех значений вероятности (каждой итерации)


def draw_lines(distance_bet_lines=NEEDLES_OPTIONS['length']):
    """
    Рисует вертикальные линии на полотне (их кол-во зависит от расстояния между ними).
    *Все линии рисуются в пределах полотна.
    Args:
        distance_bet_lines: расстояние между прямыми (по умолчанию оно равно длине иглы)
    """
    global lines_ids
    for coord_x in range(distance_bet_lines, CANVAS_OPTIONS['width'], distance_bet_lines):
        lines_ids.append(canvas.create_line(coord_x, 0, coord_x, CANVAS_OPTIONS['height'], fill='gray',
                                            width=1))


def draw_needles():
    """
    "Разбрасывает" иголки по полотну. Количество бросаемых иголок зависит от величины
    amount_needles (7 строка кода)
    """
    global needles_ids
    global drawed_needles

    for amount_iterations in range(amount_needles):
        coord_x = randint(0, CANVAS_OPTIONS['width'])
        coord_y = randint(0, CANVAS_OPTIONS['height'])
        random_angle = randint(0, 360)
        drawed_needles += 1
        needles_ids.append(canvas.create_line(coord_x, coord_y,
                                              coord_x - cos(random_angle * pi / 180) * NEEDLES_OPTIONS['length'],
                                              coord_y - sin(random_angle * pi / 180) * NEEDLES_OPTIONS['length'],
                                              fill=NEEDLES_OPTIONS['fill'], width=NEEDLES_OPTIONS['width'],
                                              tags=('for clean',)))
        while len(needles_ids) > 500:
            canvas.delete(needles_ids.pop(0))


def paint_needles():
    """
    Перекрашивает иголки, которые пересеклись с линиями
    """
    global overlapped_needles

    for line in lines_ids:
        line_coordinates = canvas.coords(line)
        overlaps = canvas.find_overlapping(*line_coordinates)

        for overlap_needle in overlaps:
            if overlap_needle in needles_ids:
                canvas.itemconfig(overlap_needle, fill='lime')
                overlapped_needles.add(overlap_needle)


def draw_chart(coordinates):
    """
    Отрисовывает точечную диаграмму.
    По вертикальной оси располагается отношение кол-ва иголок,
    попавших на нити, к общему кол-ву брошенных иголок.
    По горизонтальной число иголок
    Args:
        coordinates: координаты точки
    """
    global chart
    global chart_factor

    def scale_coordinates(coords):
        """Скалирует координаты по оси x"""
        for no, coord in enumerate(coords):
            yield coord * chart_factor if no % 2 == 0 else coord

    if chart is None:
        chart = canvas_chart.create_line(coordinates,
                                         coordinates[0] + 4, coordinates[1] + 4,
                                         **CHART_OPTIONS)
    else:
        old_coords = canvas_chart.coords(chart)
        scaled_coordinates = scale_coordinates(coordinates)
        if canvas_chart.coords(chart)[-2] >= canvas_chart.winfo_width() - 100:
            chart_factor /= 2
            old_coords = list(scale_coordinates(old_coords))
        canvas_chart.coords(chart, *(old_coords + list(scaled_coordinates)))


def create_text(data_one, data_two):
    """
    Отрисовка данных на полотне
    Args:
        data_one: данные, которые необходимо отобразить на полотне
        data_two: данные, которые необходимо отобразить на полотне
    """
    global data_ids
    global list_values_pi
    data_ids = [canvas_chart.create_text(CANVAS_OPTIONS['width'] // 2 - 10, 20,
                                         text=f'Общее кол-во иголок: {data_one}', fill='lime',
                                         font=('Comic Sans MS', 20)),

                canvas_chart.create_text(CANVAS_OPTIONS['width'] // 2 - 10, 50,
                                         text=f'Кол-во иголок, которые пересекли нить: {data_two}', fill='lime',
                                         font=('Comic Sans MS', 20)),

                canvas_chart.create_text(CANVAS_OPTIONS['width'] // 2 - 10, 80,
                                         text=f'2 / (вероятность пересечения): {round(2 / (data_two / data_one), 10)}',
                                         fill='lime', font=('Comic Sans MS', 20)),

                canvas_chart.create_text(
                    CANVAS_OPTIONS['width'] // 2 - 10, 110,
                    text=f'Среднее арифметическое всех значений: {sum(list_values_pi) / len(list_values_pi)}',
                    fill='lime', font=('Comic Sans MS', 20)),

                canvas_chart.create_text(
                    CANVAS_OPTIONS['width'] // 2 - 10, 140,
                    text=f'Погрешность: {(pi / (2 / (data_two / data_one))) - 1}',
                    fill='lime', font=('Comic Sans MS', 20))]


def draw_middle_line():
    """
    Отрисовка средней линии
    """
    global middle_line_ids
    global list_values_pi
    middle_line_ids = [canvas_chart.create_line(0, sum(list_values_pi) / len(list_values_pi) * 80,
                                                CANVAS_OPTIONS['width'], sum(list_values_pi) / len(list_values_pi) * 80,
                                                fill='blue', width=1, tags=('for clean',))]


def process():
    """
    Анимационный процесс
    """
    global amount_needles
    global list_overlapping
    global needles_ids
    global chart
    global stop_process
    global data_ids
    global list_values_pi
    global middle_line_ids

    # обновление текстовых данных:
    for canvas_id in data_ids:
        canvas_chart.delete(canvas_id)
    data_ids = []

    # обновление средней линии:
    for canvas_id in middle_line_ids:
        canvas_chart.delete(canvas_id)
    middle_line_ids = []

    stop_process = root.after(100, process)

    draw_needles()
    paint_needles()
    create_text(drawed_needles, len(overlapped_needles))
    # для того, чтобы уменьшить шаг по горизонтали на диаграмме, нужно разделить
    # len(needles_ids) на какое-либо число (в строке ниже):
    draw_chart((drawed_needles // 1, (2 / (len(overlapped_needles) / drawed_needles)) * 80))

    list_values_pi.append(2 / (len(overlapped_needles) / drawed_needles))

    draw_middle_line()

    # обновление списка пересечений:
    list_overlapping = []


def stop(event):
    """
    Остановить процесс
    """
    root.after_cancel(stop_process)


def continues(event):
    """
    Продолжить процесс
    """
    process()


def clean_canvas(event):
    """
    Очистка полотна от иголок
    """
    global needles_ids
    global chart
    global drawed_needles

    canvas.delete('for clean')
    canvas_chart.delete('for clean')
    for canvas_id in needles_ids:
        canvas.delete(canvas_id)
    needles_ids = []
    chart = None
    drawed_needles = 0
    overlapped_needles.clear()


root = Tk()

root.bind('<a>', stop)
root.bind('<d>', continues)
root.bind('<w>', clean_canvas)

canvas = Canvas(root, **CANVAS_OPTIONS)
canvas.pack()

canvas_chart = Canvas(root, **CANVAS_OPTIONS)
canvas_chart.pack()

canvas_chart.create_line(0, pi * 80, CANVAS_OPTIONS['width'], pi * 80, fill='yellow', width=1)  # значение 3.14
draw_lines()

process()

root.mainloop()
