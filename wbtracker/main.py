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
                win.Shape.RoundedRectangle(100, 600, 250, 50, 10, color=(148, 0, 216)),
                win.Text.Label(
                    "Добавить виды товаров", color=(255, 255, 255), font_size=14
                ),
                utils.add_products,
            )
        )

    def _info(self, text: str):
        self._output.text.text = text
        self.on_draw()


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
