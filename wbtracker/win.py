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

    @property
    def window(self) -> "Window":
        return self._window


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


class Shape(InactiveObj):

    Base = pyglet.shapes.ShapeBase
    Line = pyglet.shapes.Line
    Rectangle = pyglet.shapes.Rectangle
    RoundedRectangle = pyglet.shapes.RoundedRectangle
    Box = pyglet.shapes.Box
    Circle = pyglet.shapes.Circle

    def __init__(self, name, window: "Window", shape: Base) -> None:
        super().__init__(name, window)
        shape.batch = window.batch
        self._shape = shape


class Background(Shape):
    def __init__(self, window: "Window", color: tuple[int, int, int]) -> None:
        super().__init__(
            "background",
            window,
            Shape.Rectangle(
                0,
                0,
                window.width,
                window.height,
                color,
                group=pyglet.graphics.Group(-1),
            ),
        )


class Button(ActiveObj):

    def __init__(
        self,
        name: str,
        window: "Window",
        shape: Shape.Base,
        action: Callable,
        *action_args,
        **action_kwargs,
    ) -> None:
        super().__init__(name, window)
        shape.batch = window.batch
        self._shape = shape
        self._action = lambda: action(*action_args, **action_kwargs)

    def __contains__(self, coords: tuple[int, int]) -> bool:
        return coords in self._shape

    def act(self) -> None:
        self._action()


class Text(InactiveObj):

    Label = pyglet.text.Label

    def __init__(self, name: str, window: "Window", text: Label) -> None:
        super().__init__(name, window)
        text.batch = window.batch
        self._text = text

    @property
    def text(self):
        return self._text


class TextButton(Button):
    def __init__(
        self,
        name: str,
        window: "Window",
        shape: Shape.Base,
        text: Text.Label,
        action: Callable,
        *action_args,
        **action_kwargs,
    ) -> None:
        super().__init__(name, window, shape, action, *action_args, **action_kwargs)
        if isinstance(shape, Shape.Rectangle | Shape.RoundedRectangle):
            text.x = shape.x
            text.y = shape.y + shape.height / 2 - text.font_size / 2
            text.width = int(shape.width)
            text.height = int(shape.height)
            text.set_style("align", "center")
        else:
            raise NotImplemented("unknown area type")
        text.batch = window.batch
        self._text = text


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
            config=pyglet.gl.Config(  # type: ignore
                sample_buffers=1, samples=4
            ),  # anti-aliasing
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
        self.close()
