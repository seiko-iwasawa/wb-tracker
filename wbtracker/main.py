import datetime
import weakref

import utils
import win


class MainWindow(win.Window):
    def __init__(self) -> None:
        super().__init__(1080, 720, "WB Tracker")
        self.reg_obj(win.Background(self, (255, 255, 255)))
        self._reg_menu()

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


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
