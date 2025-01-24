import calendar
import datetime
import weakref
from collections.abc import Callable
from typing import Generator

import utils
import win


class ListSwitcher(win.WinBlock):

    def __init__(self, options: list[str], x: int, y: int, length: int) -> None:
        super().__init__()
        self._options = options
        self._ind = 0
        weak_self = weakref.proxy(self)
        self["left"] = win.TextButton(
            win.Shape.RoundedRectangle(x, y, 40, 40, 5, color=(148, 0, 216)),
            win.Text.Label("<", font_size=14),
            lambda: weak_self._left(),
        )
        self["right"] = win.TextButton(
            win.Shape.RoundedRectangle(
                x + 40 + length, y, 40, 40, 5, color=(148, 0, 216)
            ),
            win.Text.Label(">", font_size=14),
            lambda: weak_self._right(),
        )
        self["option"] = win.Text(
            win.Text.Label(
                "",
                x + 40,
                y + 13,
                0,
                length,
                40,
                align="center",
                color=(0, 0, 0),
                font_size=14,
            )
        )
        self._update_option()

    @property
    def option(self) -> win.Text:
        assert isinstance(res := self["option"], win.Text)
        return res

    def _update_option(self) -> None:
        self.option.label.text = self._options[self._ind]

    def _left(self) -> None:
        self._ind = (self._ind - 1) % len(self._options)
        self._update_option()

    def _right(self) -> None:
        self._ind = (self._ind + 1) % len(self._options)
        self._update_option()


class Menu(win.WinBlock):

    def __init__(
        self, window: "win.Window", buttons: list[tuple[str, Callable]]
    ) -> None:
        super().__init__()
        window["menu"] = self
        for n, button in enumerate(buttons):
            i, j = n // 2, n % 2
            self[f"{i}-{j}"] = win.TextButton(
                win.Shape.RoundedRectangle(
                    100 + j * 250,
                    650 - 80 * i,
                    200,
                    50,
                    10,
                    color=(148, 0, 216),
                ),
                win.Text.Label(button[0], font_size=14),
                button[1],
            )


class Info(win.Text):

    def __init__(self, window: "win.Window") -> None:
        super().__init__(win.Text.Label("", 30, 30, color=(0, 0, 0)))
        window["output"] = self
        self._window = window

    @property
    def info(self) -> str:
        return self.label.text

    @info.setter
    def info(self, text: str) -> None:
        self.label.text = text
        # self._window.on_draw()


class MainWindow(win.Window):

    def __init__(self) -> None:
        super().__init__(1080, 720, "WB Tracker")
        self.set_icon(win.Image.load("icon.png"))
        self._background = win.Background(self, (255, 255, 255))
        self["top-line"] = win.Shape(
            win.Shape.Line(0, 720, 1080, 720, 3, (148, 0, 216))
        )
        self._menu = Menu(
            self,
            [
                ("Добавить артикулы", lambda: self.loading(self._add_products)),
                ("Добавить продажи", self._add_sales),
                ("Выгрузить товары", lambda: self.loading(self._download_products)),
                ("Выгрузить продажи", self._download_sales),
                ("Построить график", lambda: self.loading(self._build_plot)),
            ],
        )
        self._output = Info(self)
        self._input_field = win.Input(
            self,
            win.Shape.RoundedRectangle(
                350,
                490,
                200,
                50,
                10,
                color=(148, 0, 216),
            ),
            win.Text.Label(font_size=14),
            "введите артикул...",
        )
        self["input"] = self._input_field

    def _clear_body(self) -> None:
        self["body"] = None
        self.on_draw()

    def _add_products(self) -> Generator:
        self._output.info = "загрузка..."
        self.need_redraw()
        yield
        for info in utils.add_products():
            self._output.info = info
            yield
        self._output.info = "загрузка артикулов завершена"
        yield

    def _add_sales(self) -> None:
        self._clear_body()
        body = win.WinBlock()
        self["body"] = body
        body["wb"] = win.TextButton(
            win.Shape.RoundedRectangle(600, 585, 100, 100, 10, color=(148, 0, 216)),
            win.Text.Label("WB", font_size=14),
            lambda: self.loading(lambda: self._add_sales_from("wb")),
        )
        body["ozon"] = win.TextButton(
            win.Shape.RoundedRectangle(750, 585, 100, 100, 10, color=(71, 0, 254)),
            win.Text.Label("OZON", font_size=14),
            lambda: self.loading(lambda: self._add_sales_from("ozon")),
        )

    def _add_sales_from(self, store: str) -> Generator:
        self._output.info = "загрузка..."
        self.need_redraw()
        yield
        warnings: list[str] = []
        for info in utils.add_sales(store):
            self._output.info = info
            if info.startswith("warning"):
                warnings.append(info)
            yield
        self._output.info = "загрузка продаж завершена"
        if warnings:
            self._clear_body()
            self["body"] = win.Text(
                win.Text.Label(
                    "\n".join(
                        [f"{len(warnings)} предупреждений. Первые из них:\n"]
                        + warnings[:10]
                    ),
                    100,
                    400,
                    width=800,
                    font_size=14,
                    color=(0, 0, 0),
                    multiline=True,
                ),
            )
        yield

    def _download_products(self) -> Generator:
        self._clear_body()
        self._output.info = "выгрузка..."
        self.need_redraw()
        yield
        file = utils.download_products()
        self._output.info = f"выгрузка товаров завершена ({file})"
        yield
        utils.appopen(file)

    def _download_sales(self) -> None:
        self._clear_body()
        self["body"] = (body := win.WinBlock())
        body["year"] = ListSwitcher(
            list(map(str, list(range(2025, 3000)) + list(range(2000, 2025)))),
            630,
            640,
            160,
        )
        body["month"] = ListSwitcher(utils.month_names, 630, 570, 160)
        body["for_year"] = win.TextButton(
            win.Shape.RoundedRectangle(
                100 + 500, 100 + 400, 100, 40, 10, color=(148, 0, 216)
            ),
            win.Text.Label("За год", font_size=14),
            lambda: self.loading(self._download_sales_for_year),
        )
        body["or"] = win.Text(
            win.Text.Label("или", 230 + 500, 115 + 400, color=(0, 0, 0), font_size=14)
        )
        body["for_month"] = win.TextButton(
            win.Shape.RoundedRectangle(
                300 + 500, 100 + 400, 100, 40, 10, color=(148, 0, 216)
            ),
            win.Text.Label("За месяц", font_size=14),
            lambda: self.loading(self._download_sales_for_month),
        )

    def _download_sales_for_year(self) -> Generator:
        assert isinstance(body := self["body"], win.WinBlock)
        assert isinstance(year_option := body["year"], ListSwitcher)
        year = int(year_option.option.label.text)
        start = datetime.datetime(year, 1, 1)
        end = datetime.datetime(year + 1, 1, 1) + datetime.timedelta(seconds=-1)
        return self._download_sales_for_period(start, end)

    def _download_sales_for_month(self) -> Generator:
        assert isinstance(body := self["body"], win.WinBlock)
        assert isinstance(year_option := body["year"], ListSwitcher)
        assert isinstance(month_option := body["month"], ListSwitcher)
        year, month = int(year_option.option.label.text), month_option._ind + 1
        start = datetime.datetime(year, month, 1)
        end = start + datetime.timedelta(
            days=calendar.monthrange(year, month)[1], seconds=-1
        )
        return self._download_sales_for_period(start, end)

    def _download_sales_for_period(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> Generator:
        self._clear_body()
        self._output.info = "выгрузка..."
        self.need_redraw()
        yield
        file = utils.download_sales(start, end)
        self._output.info = f"выгрузка товаров завершена ({file})"
        utils.appopen(file)
        yield

    def _build_plot(self) -> Generator:
        yield
        utils.build_plot(self._input_field.text)
        yield


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
