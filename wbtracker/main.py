import datetime
import weakref

import utils
import win


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

    def _info(self, text: str):
        self._output.text.text = text
        self.on_draw()

    def _add_products(self):
        self._info("загрузка...")
        for id in utils.add_products():
            self._info(id)
        self._info("")

    def _add_wb_sales(self):
        self._info("загрузка...")
        for id in utils.add_wb_sales():
            self._info(id)
        self._info("")


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
