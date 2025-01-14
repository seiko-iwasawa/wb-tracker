import win


class MainWindow(win.Window):
    def __init__(self):
        super().__init__(1080, 720, "WB Tracker")
        self.reg_obj(win.Background(self, (200, 200, 200)))
        self.reg_obj(
            win.Button("btn", self, 100, 100, 100, 100, 10, print, 1, 2, 3, sep=",")
        )
        self.reg_obj(win.Text("txt1", self, "123g", 100, 100, 28))
        self.reg_obj(win.Text("txt2", self, "hello", 300, 300, 40))
        self.reg_obj(
            win.TextButton(
                "txtbtn",
                self,
                500,
                500,
                200,
                100,
                10,
                "test",
                40,
                lambda: print("test"),
            ),
        )


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
