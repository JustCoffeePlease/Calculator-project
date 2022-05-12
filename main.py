# перед началом работы необходимо конвертировать файлы files.qrc (файл ресурсов) и qt_calupator.ui в формат .py
# Для этого в терминале используем следующие команды:
# pyside6-rcc files.qrc > files_rc.py
# pyside6-uic design.ui > design.py

import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QFontDatabase

from typing import Union, Optional
from operator import add, sub, mul, truediv

from design import Ui_MainWindow

operations = {
    '+': add,
    '−': sub,
    '×': mul,
    '/': truediv
}

error_zero_div = 'Division by zero'
error_undefined = 'Result is undefined'


class Calupator(QMainWindow):
    def __init__(self):
        super(Calupator, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.entry = self.ui.le_entry
        self.entry_max_len = self.entry.maxLength()

        QFontDatabase.addApplicationFont("fonts/Rubik-Regular.ttf")

        # digits
        self.ui.btn_0.clicked.connect(self.add_digit)
        self.ui.btn_1.clicked.connect(self.add_digit)
        self.ui.btn_2.clicked.connect(self.add_digit)
        self.ui.btn_3.clicked.connect(self.add_digit)
        self.ui.btn_4.clicked.connect(self.add_digit)
        self.ui.btn_5.clicked.connect(self.add_digit)
        self.ui.btn_6.clicked.connect(self.add_digit)
        self.ui.btn_7.clicked.connect(self.add_digit)
        self.ui.btn_8.clicked.connect(self.add_digit)
        self.ui.btn_9.clicked.connect(self.add_digit)

        #action
        self.ui.btn_clear.clicked.connect(self.clear_all)
        self.ui.btn_ce.clicked.connect(self.clear_entry)
        self.ui.btn_point.clicked.connect(self.add_point)
        self.ui.btn_neg.clicked.connect(self.negate)
        self.ui.btn_backspace.clicked.connect(self.backspace)

        #math
        self.ui.btn_calc.clicked.connect(self.calculation)
        self.ui.btn_add.clicked.connect(self.math_operation)
        self.ui.btn_sub.clicked.connect(self.math_operation)
        self.ui.btn_mul.clicked.connect(self.math_operation)
        self.ui.btn_div.clicked.connect(self.math_operation)

    def add_digit(self) -> None:
        # Инициализация удаления ошибок
        self.remove_error()
        # Инициализация отчистки поля временного выражения
        self.clear_temp_if_equality()
        # Добавление цифр
        btn = self.sender()
        # Метод sender() возвращает Qt объект, который посылает сигнал
        digit_buttons = ('btn_0', 'btn_1', 'btn_2', 'btn_3', 'btn_4',
                         'btn_5', 'btn_6', 'btn_7', 'btn_8', 'btn_9')

        if btn.objectName() in digit_buttons:
            if self.entry.text() == '0':
                self.entry.setText(btn.text())
            else:
                self.entry.setText(self.entry.text() + btn.text())

    def clear_all(self) -> None:
        self.remove_error()
        # Очистка Line Edit
        self.ui.le_entry.setText('0')
        self.ui.lbl_temp.clear()

    def clear_entry(self) -> None:
        self.remove_error()
        self.clear_temp_if_equality()
        # Очистка label
        self.ui.le_entry.setText('0')

    def add_point(self) -> None:
        self.clear_temp_if_equality()
        # Добаление точки
        if '.' not in self.ui.le_entry.text():
            self.ui.le_entry.setText(self.ui.le_entry.text() + '.')

    @staticmethod
    def remove_trailing_zeros(num: str) -> str:
        # Удаление лишних нулей. Используется статический декоратор. В функцию передается и возвращается string число
        n = str(float(num))
        return n[:-2] if n[-2:] == '.0' else n

    def add_temp(self) -> None:
        # Метод добавления временных выражений
        # Удаление лишних нулей в поле добавления временного выражения
        btn = self.sender()
        entry = self.remove_trailing_zeros(self.ui.le_entry.text())

        if not self.ui.lbl_temp.text() or self.get_math_sign() == '=':
            self.ui.lbl_temp.setText(entry + f' {btn.text()} ')
            self.ui.le_entry.setText('0')

    def get_entry_num(self) -> Union[int, float]: # Метод может возвращать только целое или вещественное число
        # Получаем число из Line Edit
        entry = self.ui.le_entry.text().strip('.') # Метод strip() убирает потенцияльное значение (В этом случае точку)
        if '.' in entry:
            return float(entry)
        else:
            return int(entry)

    def get_temp_num(self) -> Union[int, float]:
        # Получение числа из Label. Если есть текст, то он делится по пробелам и берется первый элемент, то есть число.
        if self.ui.lbl_temp.text():
            temp = self.ui.lbl_temp.text().strip('.').split()[0]
            if '.' in temp:
                return float(temp)
            else:
                return int(temp)

    def get_math_sign(self) -> Optional[str]:
        # Получение знака из Label
        if self.ui.lbl_temp.text():
            return self.ui.lbl_temp.text().strip('.').split()[-1]

    def calculation(self):
        entry = self.ui.le_entry.text()
        temp = self.ui.lbl_temp.text()
        # Если в лейбле есть текст, вводится переменная результата.
        # Далее обрезаются конечные нули, выпоняется приведение к строке.
        # Далее из словаря по знаку берется операция.
        if temp:
            try:
                result = self.remove_trailing_zeros(
                    str(operations[self.get_math_sign()](self.get_temp_num(), self.get_entry_num())))
                self.ui.lbl_temp.setText(temp + self.remove_trailing_zeros(entry) + ' =')
                self.ui.le_entry.setText(result)
                return result

            except KeyError:
                pass

            except ZeroDivisionError:
                if self.get_temp_num() ==0:
                    self.show_error(error_undefined)
                else:
                    self.show_error(error_zero_div)

    def math_operation(self) -> None:
        # Метод математической операции
        temp = self.ui.lbl_temp.text()
        btn = self.sender()

        if not temp:
            self.add_temp() # Если в Label нет выражения, мы его добавляем
        else:
            # Если выражение есть, берется знак.
            # Если он не равен знаку нажатой кнопки, то есть два случая.
            # Первый - это равенство. В этом случае добавляется временное выражение.
            # Иначе меняется знак выражения на знак нажатой кнопки.
            # Если же знак равен знаку нажатой кнопки, то мы считаем выражение и добавляем в конец лейбла этот знак.
            if self.get_math_sign() != btn.text():
                if self.get_math_sign() == '=':
                    self.add_temp()
                else:
                    self.ui.lbl_temp.setText(temp[:-2] + f'{btn.text()} ')
            else:
                try:
                    self.ui.lbl_temp.setText(self.calculation() + f' {btn.text()}')
                except TypeError:
                    pass

    def negate(self) -> None:
        self.clear_temp_if_equality()
        # Добавление отрицания
        entry = self.ui.le_entry.text()
        # Логика условия:
        # Если отрицания нет в поле,
        # значит оно добавляется.
        # Иначе убирается левый символ с помощью среза [1:].
        # Учитывается дополнительное условие для нуля.
        if '-' not in entry:
            if entry != '0':
                entry = '-' + entry
        else:
            entry = entry[1:]

        if len(entry) == self.entry_max_len + 1 and '-' in entry:
            self.entry.setMaxLength(self.entry_max_len + 1)
        else:
            self.entry.setMaxLength(self.entry_max_len)

        self.entry.setText(entry)

    def backspace(self) -> None:
        self.remove_error()
        self.clear_temp_if_equality()
        # Добавляем функцию backspace
        entry = self.ui.le_entry.text()

        if len(entry) != 1:
            if len(entry) == 2 and '-' in entry:
                self.ui.le_entry.setText('0')
            else:
                self.ui.le_entry.setText(entry[:-1])
        else:
            self.ui.le_entry.setText('0')

    def clear_temp_if_equality(self) -> None:
        # Удаление равенства из временного выражения (Label)
        # при дальнейшем нажатии кнопок цифр, точки, отрицания, Backspace и очищении поля вывода
        if self.get_math_sign() == '=':
            self.ui.lbl_temp.clear()

    def show_error(self, text: str) -> None:
        self.ui.le_entry.setMaxLength(len(text))
        self.ui.le_entry.setText(text)
        self.disable_buttons(True) # Выключаем кнопки

    def remove_error(self) -> None:
        # Убирание ошибок
        if self.ui.le_entry.text() in (error_undefined, error_zero_div):
            self.ui.le_entry.setMaxLength(self.entry_max_len)
            self.ui.le_entry.setText('0')
            self.disable_buttons(False) # Включаем кнопки

    def disable_buttons(self, disable: bool) -> None:
        self.ui.btn_calc.setDisabled(disable)
        self.ui.btn_add.setDisabled(disable)
        self.ui.btn_sub.setDisabled(disable)
        self.ui.btn_mul.setDisabled(disable)
        self.ui.btn_div.setDisabled(disable)
        self.ui.btn_neg.setDisabled(disable)
        self.ui.btn_point.setDisabled(disable)

        color = 'color: #888;' if disable else 'color: white;'
        self.change_buttons_color(color)

    def change_buttons_color(self, css_color: str) -> None:
        self.ui.btn_calc.setStyleSheet(css_color)
        self.ui.btn_add.setStyleSheet(css_color)
        self.ui.btn_sub.setStyleSheet(css_color)
        self.ui.btn_mul.setStyleSheet(css_color)
        self.ui.btn_div.setStyleSheet(css_color)
        self.ui.btn_neg.setStyleSheet(css_color)
        self.ui.btn_point.setStyleSheet(css_color)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calupator()
    window.show()

    sys.exit(app.exec())


