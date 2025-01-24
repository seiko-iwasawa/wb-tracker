import weakref
from abc import ABC, abstractmethod
from collections.abc import Callable, Generator, Iterator
from itertools import chain

import winkeyboard
import pyglet

Canvas = pyglet.graphics.Batch


class WinObj(ABC):

    def __init__(self) -> None:
        self._name: str | None = None
        self._parent: WinObj | None = None
        self._canvas: Canvas | None = None

    @property
    def name(self) -> str:
        return self._name

    def _set_name(self, name: str) -> None:
        self._name = name

    @property
    def parent(self) -> "WinObj | None":
        return self._parent

    def _set_parent(self, parent: "WinObj") -> None:
        self._parent = weakref.proxy(parent)
        self._set_canvas(parent.canvas)

    @property
    def canvas(self) -> Canvas | None:
        return self._canvas

    @abstractmethod
    def _set_canvas(self, canvas: Canvas | None) -> None: ...


class WinBlock(WinObj):

    def __init__(self) -> None:
        super().__init__()
        self._block: dict[str, WinObj] = {}

    def __getitem__(self, name: str) -> WinObj:
        return self._block[name]

    def __setitem__(self, name: str, obj: WinObj | None) -> None:
        if obj is None:
            self._block.pop(name, None)
        else:
            obj._set_name(name)
            obj._set_parent(self)
            self._block[name] = obj

    def __contains__(self, name: str) -> bool:
        return name in self._block

    def _set_canvas(self, canvas: Canvas | None) -> None:
        self._canvas = canvas
        for obj in self._block.values():
            obj._set_canvas(canvas)

    def all(self) -> Generator[WinObj]:
        for obj in self._block.values():
            if isinstance(obj, WinBlock):
                yield from obj.all()
            else:
                yield obj


class ActiveObj(WinObj):

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

    def __init__(self, shape: Base) -> None:
        super().__init__()
        self._shape = shape

    @property
    def shape(self):
        return self._shape

    def _set_canvas(self, canvas: Canvas | None) -> None:
        self._shape.batch = canvas


class Background(Shape):

    def __init__(
        self,
        window: "Window",
        color: tuple[int, int, int, int] | tuple[int, int, int],
    ) -> None:
        super().__init__(
            Shape.Rectangle(
                0,
                0,
                window.width,
                window.height,
                color,
                group=pyglet.graphics.Group(-9999),
            )
        )
        window["background"] = self


class Button(ActiveObj):

    def __init__(
        self,
        shape: Shape.Base,
        action: Callable,
        *action_args,
        **action_kwargs,
    ) -> None:
        super().__init__()
        self._shape = shape
        self._action = action
        self._args = action_args
        self._kwargs = action_kwargs

    def __contains__(self, coords: tuple[int, int]) -> bool:
        return coords in self._shape

    def _set_canvas(self, canvas: Canvas | None) -> None:
        self._shape.batch = canvas

    @property
    def shape(self) -> Shape.Base:
        return self._shape

    def act(self) -> None:
        self._action(*self._args, **self._kwargs)


class Text(InactiveObj):

    Label = pyglet.text.Label

    def __init__(self, label: Label) -> None:
        super().__init__()
        self._label = label

    @property
    def label(self) -> Label:
        return self._label

    def _set_canvas(self, canvas: Canvas | None) -> None:
        self.label.batch = canvas


def shape_label(shape: Shape.Base, label: Text.Label) -> None:
    if isinstance(shape, Shape.Rectangle | Shape.RoundedRectangle):
        label.x = shape.x
        label.y = shape.y + shape.height / 2 - label.font_size / 2
        label.width = int(shape.width)
        label.height = int(shape.height)
        label.set_style("align", "center")
    else:
        raise NotImplemented("unknown area type")


class ShapedText(InactiveObj):

    def __init__(self, shape: Shape.Base, label: Text.Label) -> None:
        super().__init__()
        shape_label(shape, label)
        self._shape = shape
        self._label = label

    @property
    def shape(self) -> Shape.Base:
        return self._shape

    @property
    def label(self) -> Text.Label:
        return self._label

    def _set_canvas(self, canvas: Canvas | None) -> None:
        self._shape.batch = canvas
        self._label.batch = canvas


class TextButton(Button):
    def __init__(
        self,
        shape: Shape.Base,
        label: Text.Label,
        action: Callable,
        *action_args,
        **action_kwargs,
    ) -> None:
        super().__init__(shape, action, *action_args, **action_kwargs)
        shape_label(shape, label)
        self._label = label

    @property
    def label(self) -> Text.Label:
        return self._label

    def _set_canvas(self, canvas: Canvas | None) -> None:
        super()._set_canvas(canvas)
        self._label.batch = canvas


def image_load(filename: str) -> pyglet.image.AbstractImage:
    return pyglet.image.load(filename)


class Image(InactiveObj):

    Sprite = pyglet.sprite.Sprite

    @classmethod
    def load(cls, filename: str) -> pyglet.image.AbstractImage:
        return pyglet.image.load(filename)

    def __init__(
        self,
        sprite: Sprite,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        super().__init__()
        self._sprite = sprite
        self._sprite.width = width or self._sprite.width
        self._sprite.height = height or self._sprite.height

    def _set_canvas(self, canvas: Canvas | None) -> None:
        self._sprite.batch = canvas


class Input(ActiveObj):

    def __init__(
        self,
        window: "Window",
        shape: Shape.Base,
        label: Text.Label,
        default_text: str = "input...",
    ) -> None:
        super().__init__()
        self._window = window
        self._field = ShapedText(shape, label)
        self._default_text = default_text
        self._empty: bool = True
        self.disable()

    def __contains__(self, coords: tuple[int, int]) -> bool:
        return coords in self._field.shape

    def _set_canvas(self, canvas: Canvas | None) -> None:
        self._field._set_canvas(canvas)

    def act(self) -> None:
        self._window.input = self
        self.enable()

    def disable(self) -> None:
        self.shape.opacity = 127
        if self._empty:
            self.label.text = self._default_text

    def enable(self) -> None:
        self.shape.opacity = 255
        if self._empty:
            self.label.text = ""

    @property
    def shape(self) -> Shape.Base:
        return self._field.shape

    @property
    def label(self) -> Text.Label:
        return self._field.label

    @property
    def text(self) -> str:
        return self.label.text if not self._empty else ""

    def write(self, symbol: int, modifiers: int) -> None:
        if winkeyboard.to_delete_all(symbol, modifiers):
            self.label.text = ""
        elif winkeyboard.to_delete_symbol(symbol, modifiers):
            self.label.text = self.label.text[:-1]
        else:
            self.label.text += winkeyboard.get_symbol(symbol, modifiers)
        self._empty = not self.label.text


class Window(pyglet.window.Window):
    def __init__(self, width: int, height: int, name: str) -> None:
        super().__init__(
            width,
            height,
            name,
            config=pyglet.gl.Config(sample_buffers=1, samples=4),  # anti-aliasing
        )
        self._canvas = Canvas()
        self._objects = WinBlock()
        self._objects._set_canvas(self._canvas)
        self._input: Input | None = None
        self._queue: Iterator = iter(())
        self._redraw_flag: bool = True

    def __getitem__(self, name: str) -> WinObj:
        return self._objects[name]

    def __setitem__(self, name: str, obj: WinObj | None) -> None:
        self._objects[name] = obj

    def __contains__(self, name: str) -> bool:
        return name in self._objects

    def all(self) -> Generator[WinObj]:
        return self._objects.all()

    @property
    def input(self) -> Input | None:
        return self._input

    @input.setter
    def input(self, input: Input | None) -> None:
        self._input = input

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self._input:
            self._input.disable()
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
        self._canvas.draw()
        pyglet.gl.glFlush()
        self._redraw_flag = True

    def loading(self, process: Callable[..., Iterator]) -> None:
        self._queue = chain(self._queue, process())

    def need_redraw(self) -> None:
        self._redraw_flag = False

    def _queue_update(self, dt: float) -> None:
        try:
            if self._redraw_flag:
                next(self._queue)
        except StopIteration:
            pass

    def run(self) -> None:
        pyglet.clock.schedule(self._queue_update)
        pyglet.app.run(1 / 30)

    def exit(self) -> None:
        self.close()
