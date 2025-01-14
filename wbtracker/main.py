import win


class MainWindow(win.Window):
    def __init__(self):
        super().__init__(1080, 720, "WB Tracker")
        self.reg_obj(win.Background(self, (200, 200, 200)))


def main():
    MainWindow().run()


if __name__ == "__main__":
    main()
