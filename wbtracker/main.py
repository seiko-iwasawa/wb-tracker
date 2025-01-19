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
        self._year_label = win.Text(
            "year",
            window,
            win.Text.Label(
                str(self._year),
                630,
                670,
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
                utils.month_names[self._month - 1],
                630,
                590,
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
                win.Shape.RoundedRectangle(850, 585, 100, 100, 10, color=(148, 0, 216)),
                win.Text.Label("OK", font_size=14),
                action,
            )
        )
        self.reg_obj(
            win.TextButton(
                "year-down",
                window,
                win.Shape.RoundedRectangle(600, 655, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label("<", font_size=14),
                lambda: weak_self._year_shift(-1),
            )
        )
        self.reg_obj(
            win.TextButton(
                "year-up",
                window,
                win.Shape.RoundedRectangle(780, 655, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label(">", font_size=14),
                lambda: weak_self._year_shift(+1),
            )
        )
        self.reg_obj(
            win.TextButton(
                "month-down",
                window,
                win.Shape.RoundedRectangle(600, 575, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label("<", font_size=14),
                lambda: weak_self._month_shift(-1),
            )
        )
        self.reg_obj(
            win.TextButton(
                "month-up",
                window,
                win.Shape.RoundedRectangle(780, 575, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label(">", font_size=14),
                lambda: weak_self._month_shift(+1),
            )
        )

    def _year_shift(self, delta: int) -> None:
        self._year += delta
        self._year_label.text.text = str(self._year)

    def _month_shift(self, delta: int) -> None:
        self._month = (self._month + delta - 1) % 12 + 1
        self._month_label.text.text = utils.month_names[self._month - 1]


class Menu(win.WinBlock):

    def __init__(
        self, window: "MainWindow", buttons: list[tuple[str, Callable]]
    ) -> None:
        super().__init__("menu", window)
        window.reg_obj(self)
        for n, button in enumerate(buttons):
            i, j = n // 2, n % 2
            self.reg_obj(
                win.TextButton(
                    f"{i}-{j}",
                    window,
                    win.Shape.RoundedRectangle(
                        100 + j * 250, 650 - 80 * i, 200, 50, 10, color=(148, 0, 216)
                    ),
                    win.Text.Label(button[0], font_size=14),
                    button[1],
                )
            )


class Info(win.Text):

    def __init__(self, window: "MainWindow") -> None:
        super().__init__("output", window, win.Text.Label("", 30, 30, color=(0, 0, 0)))
        window.reg_obj(self)

    @property
    def info(self) -> str:
        return self.text.text

    @info.setter
    def info(self, text: str) -> None:
        self.text.text = text
        self.window.on_draw()


class MainWindow(win.Window):

    def __init__(self) -> None:
        super().__init__(1080, 720, "WB Tracker")
        self.reg_obj(win.Background(self, (255, 255, 255)))
        self._menu = Menu(
            self,
            [
                ("Добавить артикулы", self._add_products),
                ("Добавить продажи", self._add_sales),
                ("Выгрузить товары", self._download_products),
                ("Выгрузить продажи", self._download_sales),
            ],
        )
        self._output = Info(self)

    def _clear_body(self) -> None:
        if "body" in self:
            self.remove_obj("body")
            self.on_draw()

    def _add_products(self) -> None:
        self._output.info = "загрузка..."
        for info in utils.add_products():
            self._output.info = info
        self._output.info = "загрузка артикулов завершена"

    def _add_sales(self) -> None:
        self._clear_body()
        body = win.WinBlock("body", self)
        self.reg_obj(body)
        body.reg_obj(
            win.TextButton(
                "wb",
                self,
                win.Shape.RoundedRectangle(600, 585, 100, 100, 10, color=(148, 0, 216)),
                win.Text.Label("WB", font_size=14),
                self._add_sales_from,
                "wb",
            )
        )
        body.reg_obj(
            win.TextButton(
                "ozon",
                self,
                win.Shape.RoundedRectangle(750, 585, 100, 100, 10, color=(71, 0, 254)),
                win.Text.Label("OZON", font_size=14),
                self._add_sales_from,
                "ozon",
            )
        )

    def _add_sales_from(self, store: str) -> None:
        self._output.info = "загрузка..."
        for info in utils.add_sales(store):
            self._output.info = info
        self._output.info = "загрузка продаж завершена"

    def _download_products(self) -> None:
        self._clear_body()
        self._output.info = "выгрузка..."
        file = utils.download_products()
        self._output.info = f"выгрузка товаров завершена ({file})"
        utils.appopen(file)

    def _download_sales(self) -> None:
        self._clear_body()
        self.reg_obj(PeriodChooser(self, self._download_sales_for_period))

    def _download_sales_for_period(self) -> None:
        assert isinstance(period := self["body"], PeriodChooser)
        year, month = period._year, period._month
        self._clear_body()
        self._output.info = "выгрузка..."
        start = datetime.datetime(year, month, 1)
        end = start + datetime.timedelta(
            days=calendar.monthrange(year, month)[1], seconds=-1
        )
        file = utils.download_sales(start, end)
        self._output.info = f"выгрузка товаров завершена ({file})"
        utils.appopen(file)


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
