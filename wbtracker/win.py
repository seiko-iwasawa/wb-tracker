from abc import ABC, abstractmethod
from collections.abc import Callable, Generator

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

    def __contains__(self, name: str) -> bool:
        return name in self._block

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
        self._background = pyglet.shapes.Rectangle(
            0, 0, window.width, window.height, color, batch=window.batch
        )


class Button(ActiveObj):
    def __init__(
        self,
        name: str,
        window: "Window",
        x: int,
        y: int,
        width: int,
        height: int,
        radius: int,
        action: Callable,
        *action_args,
        **action_kwargs,
    ) -> None:
        super().__init__(name, window)
        self._button_area = pyglet.shapes.RoundedRectangle(
            x, y, width, height, radius, color=(127, 127, 127), batch=window.batch
        )
        self._action = lambda: action(*action_args, **action_kwargs)

    def __contains__(self, coords: tuple[int, int]) -> bool:
        return coords in self._button_area

    def act(self) -> None:
        self._action()


class Text(InactiveObj):
    def __init__(
        self, name: str, window: "Window", text: str, x: int, y: int, font: int
    ) -> None:
        super().__init__(name, window)
        self._text = pyglet.text.Label(
            text, x, y, font_size=font, color=(0, 0, 0), batch=window.batch
        )


class TextButton(ActiveObj):
    def __init__(
        self,
        name: str,
        window: "Window",
        x: int,
        y: int,
        width: int,
        height: int,
        radius: int,
        text: str,
        font: int,
        action: Callable,
        *action_args,
        **action_kwargs,
    ) -> None:
        super().__init__(name, window)
        self._button_area = pyglet.shapes.RoundedRectangle(
            x, y, width, height, radius, color=(127, 127, 127), batch=window.batch
        )
        self._action = lambda: action(*action_args, **action_kwargs)
        self._text = pyglet.text.Label(
            text,
            x,
            y + height / 2 - font / 2,
            0,
            width,
            height,
            font_size=font,
            color=(0, 0, 0),
            align="center",
            batch=window.batch,
        )

    def __contains__(self, coords: tuple[int, int]) -> bool:
        return coords in self._button_area

    def act(self) -> None:
        self._action()


class Image(InactiveObj):
    def __init__(
        self,
        name: str,
        window: "Window",
        x: int,
        y: int,
        filename: str,
        width: int | None,
        height: int | None,
    ) -> None:
        super().__init__(name, window)
        self._img = pyglet.sprite.Sprite(
            pyglet.image.load(filename), x, y, batch=window.batch
        )
        self._img.width = width or self._img.width
        self._img.height = height or self._img.height


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

    def __contains__(self, name: str) -> bool:
        return name in self._objects

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
                return obj.act()

    def on_draw(self) -> None:
        self.clear()
        self._batch.draw()
        pyglet.gl.glFlush()

    def run(self) -> None:
        pyglet.app.run(1 / 30)

    def exit(self) -> None:
        pyglet.app.exit()
