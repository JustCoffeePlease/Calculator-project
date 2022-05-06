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
    '-': sub,
    '×': mul,
    '/': truediv
}


class Calupator(QMainWindow):
    def __init__(self):
        super(Calupator, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.entry = self.ui.le_entry

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

        #math
        self.ui.btn_calc.clicked.connect(self.calculation)
        self.ui.btn_add.clicked.connect(self.math_operation)
        self.ui.btn_sub.clicked.connect(self.math_operation)
        self.ui.btn_mul.clicked.connect(self.math_operation)
        self.ui.btn_div.clicked.connect(self.math_operation)

    def add_digit(self) -> None:
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
        # Очистка Line Edit
        self.ui.le_entry.setText('0')
        self.ui.lbl_temp.clear()

    def clear_entry(self) -> None:
        # Очистка label
        self.ui.le_entry.setText('0')

    def add_point(self) -> None:
        # Добаление точки
        if '.' not in self.ui.le_entry.text():
            self.ui.le_entry.setText(self.ui.le_entry.text() + '.')

    def add_temp(self) -> None:
        # Добавление временных выражений: Число и математический знак, равенство
        btn = self.sender()
        entry = self.remove_trailing_zeros(self.ui.le_entry.text())

        if not self.ui.lbl_temp.text() or self.get_math_sign() == '=':
            self.ui.lbl_temp.setText(self.ui.le_entry.text() + f' {btn.text()} ')
            self.ui.le_entry.setText('0')

    @staticmethod
    def remove_trailing_zeros(num: str) -> str:
        # Удаление лишних нулей. Используется статический декоратор. В функцию передается и возвращается string число
        n = str(float(num))
        if n[-2:] == 0:
            return n[:-2]
        else:
            return n

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
            result = self.remove_trailing_zeros(
                str(operations[self.get_math_sign()](self.get_temp_num(), self.get_entry_num())))
            self.ui.lbl_temp.setText(temp + self.remove_trailing_zeros(entry) + ' =')
            self.ui.le_entry.setText(result)
            return result

    def math_operation(self):
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
                self.ui.lbl_temp.setText(self.calculate() + f' {btn.text()}')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calupator()
    window.show()

    sys.exit(app.exec())