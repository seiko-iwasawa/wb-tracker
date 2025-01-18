import calendar
import datetime
import weakref
from collections.abc import Callable

import utils
import win


class PeriodChooser(win.WinBlock):

    def __init__(self, window: win.Window, action: Callable) -> None:
        super().__init__("body", window)
        weak_self = weakref.proxy(self)
        self._year = 2025
        self._month = 1
        self._months = [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ]
        self._year_label = win.Text(
            "year",
            window,
            win.Text.Label(
                str(self._year),
                340,
                310,
                0,
                160,
                100,
                align="center",
                color=(0, 0, 0),
                font_size=14,
            ),
        )
        self._month_label = win.Text(
            "month",
            window,
            win.Text.Label(
                self._months[self._month - 1],
                340,
                210,
                0,
                160,
                100,
                align="center",
                color=(0, 0, 0),
                font_size=14,
            ),
        )
        self.reg_obj(self._year_label)
        self.reg_obj(self._month_label)
        self.reg_obj(
            win.TextButton(
                "OK",
                window,
                win.Shape.RoundedRectangle(400, 400, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label("OK", font_size=14),
                action,
            )
        )
        self.reg_obj(
            win.TextButton(
                "year-down",
                window,
                win.Shape.RoundedRectangle(300, 300, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label("<", font_size=14),
                lambda: weak_self._year_shift(-1),
            )
        )
        self.reg_obj(
            win.TextButton(
                "year-up",
                window,
                win.Shape.RoundedRectangle(500, 300, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label(">", font_size=14),
                lambda: weak_self._year_shift(+1),
            )
        )
        self.reg_obj(
            win.TextButton(
                "month-down",
                window,
                win.Shape.RoundedRectangle(300, 200, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label("<", font_size=14),
                lambda: weak_self._month_shift(-1),
            )
        )
        self.reg_obj(
            win.TextButton(
                "month-up",
                window,
                win.Shape.RoundedRectangle(500, 200, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label(">", font_size=14),
                lambda: weak_self._month_shift(+1),
            )
        )

    def _year_shift(self, delta: int):
        self._year += delta
        self._year_label.text.text = str(self._year)

    def _month_shift(self, delta: int):
        self._month = (self._month + delta - 1) % 12 + 1
        self._month_label.text.text = self._months[self._month - 1]


class MainWindow(win.Window):
    def __init__(self) -> None:
        super().__init__(1080, 720, "WB Tracker")
        self.reg_obj(win.Background(self, (255, 255, 255)))
        self._reg_menu()
        self._output = win.Text(
            "output", self, win.Text.Label("", 30, 30, color=(0, 0, 0))
        )
        self.reg_obj(self._output)

    def _reg_menu(self) -> None:
        menu = win.WinBlock("menu", self)
        self.reg_obj(menu)
        menu.reg_obj(
            win.TextButton(
                "add-products",
                self,
                win.Shape.RoundedRectangle(100, 650, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Добавить артикулы", font_size=14),
                self._add_products,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "add-sales",
                self,
                win.Shape.RoundedRectangle(350, 650, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Добавить продажи", font_size=14),
                self._add_sales,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "download-products",
                self,
                win.Shape.RoundedRectangle(100, 570, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Выгрузить товары", font_size=14),
                self._download_products,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "download-sales",
                self,
                win.Shape.RoundedRectangle(350, 570, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Выгрузить продажи", font_size=14),
                self._download_sales,
            )
        )

    def _info(self, text: str):
        self._output.text.text = text
        self.on_draw()

    def _clear_body(self):
        if "body" in self:
            self.remove_obj("body")

    def _add_products(self):
        self._info("загрузка...")
        for info in utils.add_products():
            self._info(info)
        self._info("загрузка артикулов завершена")

    def _add_sales(self):
        self._clear_body()
        body = win.WinBlock("body", self)
        self.reg_obj(body)
        body.reg_obj(
            win.TextButton(
                "wb",
                self,
                win.Shape.RoundedRectangle(200, 200, 100, 100, 10, color=(148, 0, 216)),
                win.Text.Label("WB", font_size=14),
                self._add_wb_sales,
            )
        )
        body.reg_obj(
            win.TextButton(
                "ozon",
                self,
                win.Shape.RoundedRectangle(400, 200, 100, 100, 10, color=(71, 0, 254)),
                win.Text.Label("OZON", font_size=14),
                self._add_ozon_sales,
            )
        )

    def _add_wb_sales(self):
        self._info("загрузка...")
        for id in utils.add_wb_sales():
            self._info(id)
        self._info("загрузка продаж завершена")

    def _add_ozon_sales(self):
        self._info("загрузка...")
        for id in utils.add_ozon_sales():
            self._info(id)
        self._info("загрузка продаж завершена")

    def _download_products(self):
        self._clear_body()
        self._info("выгрузка...")
        file = utils.download_products()
        self._info(f"выгрузка товаров завершена ({file})")
        utils.appopen(file)

    def _download_sales(self):
        self._clear_body()
        self.reg_obj(PeriodChooser(self, self._download_sales_for_period))

    def _download_sales_for_period(self):
        assert isinstance(period := self["body"], PeriodChooser)
        year, month = period._year, period._month
        self._clear_body()
        self._info("выгрузка...")
        start = datetime.datetime(year, month, 1)
        end = start + datetime.timedelta(
            days=calendar.monthrange(year, month)[1], seconds=-1
        )
        file = utils.download_sales(start, end)
        self._info(f"выгрузка товаров завершена ({file})")
        utils.appopen(file)


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
