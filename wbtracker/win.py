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
                group=pyglet.graphics.Group(-9999),
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

    class ShapedLabel:

        def __init__(self, shape: Shape.Base, text: "Text.Label") -> None:
            if isinstance(shape, Shape.Rectangle | Shape.RoundedRectangle):
                text.x = shape.x
                text.y = shape.y + shape.height / 2 - text.font_size / 2
                text.width = int(shape.width)
                text.height = int(shape.height)
                text.set_style("align", "center")
            else:
                raise NotImplemented("unknown area type")
            self._shape = shape
            self._text = text

        @property
        def shape(self) -> Shape.Base:
            return self._shape

        @property
        def text(self) -> "Text.Label":
            return self._text

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
        shaped_text: Text.ShapedLabel,
        action: Callable,
        *action_args,
        **action_kwargs,
    ) -> None:
        super().__init__(
            name, window, shaped_text.shape, action, *action_args, **action_kwargs
        )
        shaped_text.text.batch = window.batch
        self._text = shaped_text.text


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


class Input(ActiveObj):

    def __init__(
        self,
        name: str,
        window: "Window",
        field: Text.ShapedLabel,
        default_text: str = "input...",
    ) -> None:
        super().__init__(name, window)
        self._shape = field.shape
        self._text = field.text
        self._text.text = default_text
        self._shape.batch = window.batch
        self._text.batch = window.batch
        self._shape.opacity = 127
        self._flag = False
        self._default_text = default_text

    def __contains__(self, coords: tuple[int, int]) -> bool:
        return coords in self._shape

    def act(self) -> None:
        self.window.input = self
        if not self._flag:
            self._text.text = ""
        self._flag = True
        self._shape.opacity = 255

    def deact(self) -> None:
        self.window.input = None
        if not self._text.text:
            self._text.text = self._default_text
            self._flag = False
        self._shape.opacity = 127

    def write(self, symbol: int, modifiers: int) -> None:
        if symbol == pyglet.window.key._0:
            self._text.text += "0"
        elif symbol == pyglet.window.key._1:
            self._text.text += "1"
        elif symbol == pyglet.window.key._2:
            self._text.text += "2"
        elif symbol == pyglet.window.key._3:
            self._text.text += "3"
        elif symbol == pyglet.window.key._4:
            self._text.text += "4"
        elif symbol == pyglet.window.key._5:
            self._text.text += "5"
        elif symbol == pyglet.window.key._6:
            self._text.text += "6"
        elif symbol == pyglet.window.key._7:
            self._text.text += "7"
        elif symbol == pyglet.window.key._8:
            self._text.text += "8"
        elif symbol == pyglet.window.key._9:
            self._text.text += "9"
        elif symbol == pyglet.window.key.MINUS:
            self._text.text += "-"
        elif symbol == pyglet.window.key.BACKSPACE:
            self._text.text = self._text.text[:-1]
        else:
            print(symbol)


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
        self._input: Input | None = None

    def __getitem__(self, name: str) -> WinObj:
        return self._objects[name]

    def __contains__(self, name: str) -> bool:
        return name in self._objects

    @property
    def batch(self) -> pyglet.graphics.Batch:
        return self._batch

    @property
    def input(self) -> Input | None:
        return self._input

    @input.setter
    def input(self, input: Input | None) -> None:
        self._input = input

    def reg_obj(self, obj: WinObj) -> None:
        self._objects.reg_obj(obj)

    def remove_obj(self, name: str) -> None:
        self._objects.remove_obj(name)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self._input:
            self._input.deact()
        for obj in self._objects.all():
            if isinstance(obj, ActiveObj) and (x, y) in obj:
                return obj.act()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == pyglet.window.key.ESCAPE:
            self.exit()
        elif self._input:
            self._input.write(symbol, modifiers)

    def on_draw(self) -> None:
        self.clear()
        self._batch.draw()
        pyglet.gl.glFlush()

    def run(self) -> None:
        pyglet.app.run(1 / 30)

    def exit(self) -> None:
        self.close()
