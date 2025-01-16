import datetime
import weakref

import utils
import win


class WBTop(win.WinBlock):
    def __init__(self, name: str, window: win.Window, top: list[list]) -> None:
        super().__init__(name, window)
        self._top = top
        self._start = 0
        self._build_table()
        weak_self: WBTop = weakref.proxy(self)
        self.reg_obj(
            win.TextButton(
                "scroll-up",
                window,
                win.Shape.RoundedRectangle(800, 350, 40, 40, 5, color=(127, 127, 127)),
                win.Text.Label(
                    "↑", font_name="Times New Roman", color=(0, 0, 0), font_size=14
                ),
                lambda: weak_self._up(),
            )
        )
        self.reg_obj(
            win.TextButton(
                "scroll-down",
                window,
                win.Shape.RoundedRectangle(800, 300, 40, 40, 5, color=(127, 127, 127)),
                win.Text.Label(
                    "↓", font_name="Times New Roman", color=(0, 0, 0), font_size=14
                ),
                lambda: weak_self._down(),
            )
        )

    def _build_table(self) -> None:
        if "table" in self:
            self.remove_obj("table")
        table = win.WinBlock("table", self.window)
        self.reg_obj(table)
        for i, row in enumerate(self._top[self._start : self._start + 10]):
            for j, val in enumerate([self._start + i + 1] + row):
                table.reg_obj(
                    win.Shape(
                        f"box-{i}-{j}",
                        self.window,
                        win.Shape.Box(
                            100 + j * 100 - 5,
                            500 - 5 - i * 40,
                            100,
                            40,
                            2,
                            color=(127, 127, 127),
                        ),
                    )
                )
                table.reg_obj(
                    win.Text(
                        f"{i}-{j}",
                        self.window,
                        win.Text.Label(
                            str(val), 100 + j * 100, 500 - i * 40, color=(0, 0, 0)
                        ),
                    )
                )
            table.reg_obj(
                win.TextButton(
                    f"url-{i}",
                    self.window,
                    win.Shape.RoundedRectangle(
                        700, 500 - i * 40, 60, 30, 5, color=(127, 127, 127)
                    ),
                    win.Text.Label("open", color=(0, 0, 0), font_size=14),
                    utils.webopen,
                    row[0],
                )
            )

    def _up(self) -> None:
        if self._start > 0:
            self._start -= 1
            self._build_table()

    def _down(self) -> None:
        if self._start + 1 < len(self._top):
            self._start += 1
            self._build_table()


class MainWindow(win.Window):
    def __init__(self) -> None:
        super().__init__(1080, 720, "WB Tracker")
        self.reg_obj(win.Background(self, (200, 200, 200)))
        self._reg_menu()

    def _reg_menu(self) -> None:
        menu = win.WinBlock("menu", self)
        self.reg_obj(menu)
        menu.reg_obj(
            win.TextButton(
                "add-products",
                self,
                win.Shape.RoundedRectangle(
                    100, 600, 250, 50, 10, color=(127, 127, 127)
                ),
                win.Text.Label("Добавить виды товаров", color=(0, 0, 0), font_size=14),
                utils.add_products,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "record",
                self,
                win.Shape.RoundedRectangle(
                    400, 600, 250, 50, 10, color=(127, 127, 127)
                ),
                win.Text.Label("Сделать запись", color=(0, 0, 0), font_size=14),
                self._record,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "show-deltas",
                self,
                win.Shape.RoundedRectangle(
                    700, 600, 250, 50, 10, color=(127, 127, 127)
                ),
                win.Text.Label("Проверить цены", color=(0, 0, 0), font_size=14),
                self._show_deltas,
            )
        )

    def _record(self) -> None:
        if "body" in self:
            self.remove_obj("body")
            self.on_draw()
        cnt = 0
        loading = win.Text(
            "loading",
            self,
            win.Text.Label("0/?", 100, 100, color=(0, 0, 0), font_size=14),
        )
        self.reg_obj(loading)
        self.on_draw()
        product_list = utils.read_product_list()
        loading.text.text = f"0/{len(product_list)}"
        self.on_draw()
        for wb_article, data in product_list.items():
            try:
                print(wb_article)
                data["history"][str(datetime.date.today())] = utils.get_wb_price(
                    wb_article
                )
            except Exception:
                ...
            cnt += 1
            loading.text.text = f"{cnt}/{len(product_list)}"
            self.on_draw()
        utils.write_product_list(product_list)
        self.remove_obj("loading")

    def _show_deltas(self):
        if "body" in self:
            self.remove_obj("body")
        body = win.WinBlock("body", self)
        self.reg_obj(body)
        product_list = utils.read_product_list()
        top = []
        for wb_article, data in product_list.items():
            history = list(data["history"].items())
            history.sort(
                key=lambda x: datetime.datetime.strptime(x[0], "%Y-%m-%d"), reverse=True
            )
            if len(history) >= 2:
                top.append(
                    [
                        wb_article,
                        history[0][0],
                        history[0][1],
                        history[1][0],
                        history[1][1],
                    ]
                )
        top.sort(key=lambda x: abs(x[2] - x[4]))
        print(len(top))
        body.reg_obj(WBTop("top", self, top))


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
