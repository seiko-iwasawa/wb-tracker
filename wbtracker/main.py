import datetime

import utils
import win


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
                win.Button.RoundedArea(100, 600, 250, 50, 10, color=(127, 127, 127)),
                win.Text.Label("Добавить виды товаров", color=(0, 0, 0), font_size=14),
                utils.add_products,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "record",
                self,
                win.Button.RoundedArea(400, 600, 250, 50, 10, color=(127, 127, 127)),
                win.Text.Label("Сделать запись", color=(0, 0, 0), font_size=14),
                self._record,
            )
        )
        menu.reg_obj(
            win.TextButton(
                "show-deltas",
                self,
                win.Button.RoundedArea(700, 600, 250, 50, 10, color=(127, 127, 127)),
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

        def draw_top():
            if "top" in body:
                body.remove_obj("top")
            top_obj = win.WinBlock("top", self)
            body.reg_obj(top_obj)
            for i in range(10):
                if i + start[0] >= len(top):
                    break
                wb_article = top[i + start[0]][0]
                cur_price = top[i + start[0]][1][1]
                old_price = top[i + start[0]][2][1]
                top_obj.reg_obj(
                    win.Text(
                        f"top-wb-{i}",
                        self,
                        win.Text.Label(
                            f"{wb_article}",
                            100,
                            500 - 20 * i,
                            color=(0, 0, 0),
                            font_size=14,
                        ),
                    )
                )
                top_obj.reg_obj(
                    win.Text(
                        f"top-cur-{i}",
                        self,
                        win.Text.Label(
                            f"{cur_price}",
                            220,
                            500 - 20 * i,
                            color=(0, 0, 0),
                            font_size=14,
                        ),
                    )
                )
                top_obj.reg_obj(
                    win.Text(
                        f"top-old-{i}",
                        self,
                        win.Text.Label(
                            f"{old_price}",
                            300,
                            500 - 20 * i,
                            color=(0, 0, 0),
                            font_size=14,
                        ),
                    )
                )

        def up():
            if start[0] >= 0:
                start[0] -= 1
                draw_top()

        def down():
            if start[0] + 1 < len(top):
                start[0] += 1
                draw_top()

        if "body" in self:
            self.remove_obj("body")
        body = win.WinBlock("body", self)
        self.reg_obj(body)
        body.reg_obj(
            win.TextButton(
                "scroll-up",
                self,
                win.Button.RoundedArea(1000, 400, 50, 50, 5, color=(127, 127, 127)),
                win.Text.Label("up", color=(0, 0, 0), font_size=14),
                up,
            )
        )
        body.reg_obj(
            win.TextButton(
                "scroll-down",
                self,
                win.Button.RoundedArea(1000, 300, 50, 50, 5, color=(127, 127, 127)),
                win.Text.Label("down", color=(0, 0, 0), font_size=14),
                down,
            )
        )
        product_list = utils.read_product_list()
        top = []
        for wb_article, data in product_list.items():
            history = list(data["history"].items())
            history.sort(
                key=lambda x: datetime.datetime.strptime(x[0], "%Y-%m-%d"), reverse=True
            )
            if len(history) >= 2:
                top.append([wb_article, history[0], history[1]])
        top.sort(key=lambda x: abs(x[1][1] - x[2][1]))
        start = [0]
        print(len(top))
        draw_top()


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
