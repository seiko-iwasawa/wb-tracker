from abc import ABC, abstractmethod
from collections.abc import Generator

import pyglet


class WinObj:
    def __init__(self, name: str, window: "Window") -> None:
        self._name = name
        self._window = window

    @property
    def name(self) -> str:
        return self._name


class WinBlock(WinObj):
    def __init__(self, name: str, window: "Window") -> None:
        super().__init__(name, window)
        self._block: dict[str, WinObj] = {}

    def __getitem__(self, name: str) -> WinObj:
        return self._block[name]

    def reg_obj(self, obj: WinObj) -> None:
        if obj.name in self._block:
            raise ValueError(f"name {obj.name} is already registered")
        self._block[obj.name] = obj

    def remove_obj(self, name: str) -> None:
        self._block.pop(name)

    def all(self) -> Generator[WinObj]:
        for obj in self._block.values():
            if isinstance(obj, WinBlock):
                yield from obj.all()
            else:
                yield obj


class ActiveObj(WinObj, ABC):
    @abstractmethod
    def __contains__(self, coords: tuple[int, int]) -> bool: ...

    @abstractmethod
    def act(self) -> None: ...


class InactiveObj(WinObj): ...


class Background(InactiveObj):
    def __init__(self, window: "Window", color: tuple[int, int, int]) -> None:
        super().__init__("background", window)
        self.background = pyglet.shapes.Rectangle(
            0, 0, window.width, window.height, color, batch=window.batch
        )


class Window(pyglet.window.Window):
    def __init__(self, width: int, height: int, name: str) -> None:
        super().__init__(
            width,
            height,
            name,
            config=pyglet.gl.Config(sample_buffers=1, samples=4),  # anti-aliasing
        )
        self._batch = pyglet.graphics.Batch()
        self._objects = WinBlock("main", self)

    def __getitem__(self, name: str) -> WinObj:
        return self._objects[name]

    @property
    def batch(self) -> pyglet.graphics.Batch:
        return self._batch

    def reg_obj(self, obj: WinObj) -> None:
        self._objects.reg_obj(obj)

    def remove_obj(self, name: str) -> None:
        self._objects.remove_obj(name)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        for obj in self._objects.all():
            if isinstance(obj, ActiveObj) and (x, y) in obj:
                obj.act()

    def on_draw(self) -> None:
        self.clear()
        self._batch.draw()
        pyglet.gl.glFlush()

    def run(self) -> None:
        pyglet.app.run(1 / 30)

    def exit(self) -> None:
        pyglet.app.exit()
