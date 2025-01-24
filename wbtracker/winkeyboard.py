import pyglet

_symbols: dict[int, str] = {
    pyglet.window.key._0: "0",
    pyglet.window.key._1: "1",
    pyglet.window.key._2: "2",
    pyglet.window.key._3: "3",
    pyglet.window.key._4: "4",
    pyglet.window.key._5: "5",
    pyglet.window.key._6: "6",
    pyglet.window.key._7: "7",
    pyglet.window.key._8: "8",
    pyglet.window.key._9: "9",
    pyglet.window.key.MINUS: "-",
    pyglet.window.key.PLUS: "+",
    pyglet.window.key.SLASH: "/",
    pyglet.window.key.BACKSLASH: "\\",
    pyglet.window.key.Q: "q",
    pyglet.window.key.W: "w",
    pyglet.window.key.E: "e",
    pyglet.window.key.R: "r",
    pyglet.window.key.T: "t",
    pyglet.window.key.Y: "y",
    pyglet.window.key.U: "u",
    pyglet.window.key.I: "i",
    pyglet.window.key.O: "o",
    pyglet.window.key.P: "p",
    pyglet.window.key.A: "a",
    pyglet.window.key.S: "s",
    pyglet.window.key.D: "d",
    pyglet.window.key.F: "f",
    pyglet.window.key.G: "g",
    pyglet.window.key.H: "h",
    pyglet.window.key.J: "j",
    pyglet.window.key.K: "k",
    pyglet.window.key.L: "l",
    pyglet.window.key.Z: "z",
    pyglet.window.key.X: "x",
    pyglet.window.key.C: "c",
    pyglet.window.key.V: "v",
    pyglet.window.key.B: "b",
    pyglet.window.key.N: "n",
    pyglet.window.key.M: "m",
    pyglet.window.key.SPACE: " ",
}


def get_symbol(symbol: int, modifiers: int) -> str:
    if symbol not in _symbols:
        return ""
    if modifiers == pyglet.window.key.MOD_SHIFT:
        return _symbols[symbol].upper()
    elif not modifiers:
        return _symbols[symbol]
    else:
        return ""


def to_delete_symbol(symbol: int, modifiers: int) -> bool:
    return symbol == pyglet.window.key.BACKSPACE and modifiers == 0


def to_delete_all(symbol: int, modifiers: int) -> bool:
    return (
        symbol == pyglet.window.key.BACKSPACE
        and modifiers == pyglet.window.key.MOD_CTRL
    )
