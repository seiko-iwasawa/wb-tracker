import datetime
import weakref

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
                table.reg_obj(
                    win.TextButton(
                        f"apply-{i}",
                        self.window,
                        win.Shape.RoundedRectangle(
                            570, 500 - i * 40, 100, 30, 5, color=(148, 0, 216)
                        ),
                        win.Text.Label("ПРИНЯТЬ", color=(255, 255, 255), font_size=14),
                        utils.apply_price,
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
                win.Shape.RoundedRectangle(100, 600, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Добавить артикулы", font_size=14),
                self._add_products,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "add-sales",
                self,
                win.Shape.RoundedRectangle(350, 600, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Добавить продажи", font_size=14),
                self._add_wb_sales,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "update-price",
                self,
                win.Shape.RoundedRectangle(600, 600, 200, 50, 10, color=(148, 0, 216)),
                win.Text.Label("Обновить цены", font_size=14),
                self._update_price,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "clear-body",
                self,
                win.Shape.RoundedRectangle(850, 600, 50, 50, 10, color=(148, 0, 216)),
                win.Text.Label("X", font_size=14),
                self._clear_body,
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


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
