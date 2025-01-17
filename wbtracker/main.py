import calendar
import datetime
import weakref
from collections.abc import Callable

import database
import utils
import win


class PriceUpdater(win.WinBlock):

    def __init__(
        self, window: win.Window, prices: list[tuple[database.Database.Product, int]]
    ) -> None:
        super().__init__("body", window)
        self._prices = prices
        self._start = 0
        self._build_table()
        weak_self: PriceUpdater = weakref.proxy(self)
        self.reg_obj(
            win.TextButton(
                "scroll-up",
                window,
                win.Shape.RoundedRectangle(700, 350, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label(
                    "↑",
                    font_name="Times New Roman",
                    color=(255, 255, 255),
                    font_size=14,
                ),
                lambda: weak_self._up(),
            )
        )
        self.reg_obj(
            win.TextButton(
                "scroll-down",
                window,
                win.Shape.RoundedRectangle(700, 300, 40, 40, 5, color=(148, 0, 216)),
                win.Text.Label(
                    "↓",
                    font_name="Times New Roman",
                    color=(255, 255, 255),
                    font_size=14,
                ),
                lambda: weak_self._down(),
            )
        )
        self.reg_obj(
            win.TextButton(
                "apply-all",
                window,
                win.Shape.RoundedRectangle(700, 450, 200, 40, 5, color=(148, 0, 216)),
                win.Text.Label(
                    "ПРИНЯТЬ ВСЕ",
                    color=(255, 255, 255),
                    font_size=14,
                ),
                lambda: weak_self._apply_all(),
            )
        )

    def _build_table(self) -> None:
        if "table" in self:
            self.remove_obj("table")
        self._prices.sort(
            key=lambda elem: (
                abs(elem[0]._price - elem[1]) / max(elem[0]._price, elem[1]),
                max(elem[0]._price, elem[1]),
            ),
            reverse=True,
        )
        table = win.WinBlock("table", self.window)
        self.reg_obj(table)
        for i, elem in enumerate(self._prices[self._start : self._start + 10]):
            # 0
            table.reg_obj(
                win.Shape(
                    f"box-{i}-0",
                    self.window,
                    win.Shape.Box(
                        100 - 5,
                        500 - 5 - i * 40,
                        100,
                        40,
                        2,
                        color=(148, 0, 216),
                    ),
                )
            )
            table.reg_obj(
                win.Text(
                    f"{i}-0",
                    self.window,
                    win.Text.Label(
                        str(elem[0]._vendor_code), 100, 500 - i * 40, color=(0, 0, 0)
                    ),
                )
            )
            # 1
            table.reg_obj(
                win.Shape(
                    f"box-{i}-1",
                    self.window,
                    win.Shape.Box(
                        200 - 5,
                        500 - 5 - i * 40,
                        100,
                        40,
                        2,
                        color=(148, 0, 216),
                    ),
                )
            )
            table.reg_obj(
                win.Text(
                    f"{i}-1",
                    self.window,
                    win.Text.Label(
                        str(elem[0]._price) if elem[0]._price != -1 else "-",
                        200,
                        500 - i * 40,
                        color=(0, 0, 0),
                    ),
                )
            )
            # 2
            table.reg_obj(
                win.Shape(
                    f"box-{i}-2",
                    self.window,
                    win.Shape.Box(
                        300 - 5,
                        500 - 5 - i * 40,
                        100,
                        40,
                        2,
                        color=(148, 0, 216),
                    ),
                )
            )
            table.reg_obj(
                win.Text(
                    f"{i}-2",
                    self.window,
                    win.Text.Label(
                        str(elem[1]) if elem[1] != -1 else "-",
                        300,
                        500 - i * 40,
                        color=(0, 0, 0),
                    ),
                )
            )
            # 3
            table.reg_obj(
                win.Shape(
                    f"box-{i}-3",
                    self.window,
                    win.Shape.Box(
                        400 - 5,
                        500 - 5 - i * 40,
                        100,
                        40,
                        2,
                        color=(148, 0, 216),
                    ),
                )
            )
            if elem[0]._price < elem[1]:
                table.reg_obj(
                    win.Text(
                        f"{i}-3",
                        self.window,
                        win.Text.Label(
                            "+" + str(elem[1] - elem[0]._price),
                            400,
                            500 - i * 40,
                            color=(0, 255, 0),
                        ),
                    )
                )
            elif elem[0]._price == elem[1]:
                table.reg_obj(
                    win.Text(
                        f"{i}-3",
                        self.window,
                        win.Text.Label(
                            "0",
                            400,
                            500 - i * 40,
                            color=(0, 0, 0),
                        ),
                    )
                )
            else:
                table.reg_obj(
                    win.Text(
                        f"{i}-3",
                        self.window,
                        win.Text.Label(
                            "-" + str(elem[0]._price - elem[1]),
                            400,
                            500 - i * 40,
                            color=(255, 0, 0),
                        ),
                    )
                )
            # open
            table.reg_obj(
                win.TextButton(
                    f"url-{i}",
                    self.window,
                    win.Shape.RoundedRectangle(
                        500, 500 - i * 40, 60, 30, 5, color=(148, 0, 216)
                    ),
                    win.Text.Label("OPEN", color=(255, 255, 255), font_size=14),
                    utils.webopen,
                    elem[0]._id,
                )
            )
            # apply
            if elem[0]._price != elem[1] or True:
                weak_self = weakref.proxy(self)
                table.reg_obj(
                    win.TextButton(
                        f"apply-{i}",
                        self.window,
                        win.Shape.RoundedRectangle(
                            570, 500 - i * 40, 100, 30, 5, color=(148, 0, 216)
                        ),
                        win.Text.Label("ПРИНЯТЬ", color=(255, 255, 255), font_size=14),
                        lambda product, new_price: weak_self._apply_price(
                            product, new_price
                        ),
                        elem[0],
                        elem[1],
                    )
                )

    def _up(self) -> None:
        if self._start > 0:
            self._start -= 1
            self._build_table()

    def _down(self) -> None:
        if self._start + 1 < len(self._prices):
            self._start += 1
            self._build_table()

    def _apply_price(self, product: database.Database.Product, new_price: int) -> None:
        utils.apply_price(product, new_price)
        self._build_table()

    def _apply_all(self):
        for elem in self._prices:
            if elem[0]._price != elem[1]:
                utils.apply_price(elem[0], elem[1])
        self._build_table()


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
                self._add_wb_sales,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "update-price",
                self,
                win.Shape.RoundedRectangle(600, 650, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Обновить цены", font_size=14),
                self._update_price,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "clear-body",
                self,
                win.Shape.RoundedRectangle(850, 650, 50, 50, 10, color=(148, 0, 216)),
                win.Text.Label("X", font_size=14),
                self._clear_body,
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
        menu.reg_obj(
            win.TextButton(
                "analyze-sales",
                self,
                win.Shape.RoundedRectangle(600, 570, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Анализ продаж", font_size=14),
                self._analyze_sales,
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

    def _add_wb_sales(self):
        self._info("загрузка...")
        for id in utils.add_wb_sales():
            self._info(id)
        self._info("загрузка продаж завершена")

    def _update_price(self):
        self._clear_body()
        self._info("загрузка...")
        prices: list[tuple[database.Database.Product, int]] = []
        for product, new_price, info in utils.update_price():
            self._info(info)
            prices.append((product, new_price))
        self.reg_obj(PriceUpdater(self, prices))
        self._info("загрузка цен завершена")

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

    def _analyze_sales(self): ...


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
