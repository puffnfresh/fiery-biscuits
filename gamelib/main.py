#!/usr/bin/env python
import sys
import os

# Make sure we can include the extra modules
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)

import pyglet
import data

class Menu(object):
    def __init__(self):
        self.items = []
        self.selected_index = 0

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.DOWN:
            self.selected_index += 1
        elif symbol == pyglet.window.key.UP:
            self.selected_index -= 1
        elif symbol == pyglet.window.key.RETURN:
            command = self.items[self.selected_index].command
            if command:
                command()

        if len(self.items) == 0:
            self.selected_index = 0
        else:
            self.selected_index %= len(self.items)

    def add_item(self, item):
        self.items.append(item)

    def on_draw(self):
        for index, item in enumerate(self.items):
            item.draw(index == self.selected_index)

class MenuItem(object):
    def __init__(self, title, position, command=None):
        self.title = title
        self.command = command
        self.label = pyglet.text.Label(self.title, font_size=22, x=position[0], y=position[1], anchor_x="center", anchor_y="center")
        self.color = (255, 255, 255, 128)
        self.selected_color = (255, 255, 255, 255)

    def draw(self, selected):
        if selected:
            self.label.color = self.selected_color
        else:
            self.label.color = self.color

        self.label.draw()

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__()

        self.title = pyglet.text.Label("Twinerama", font_size=72,
                                       anchor_x="center", anchor_y="center",
                                       x=window.width / 2, y=400)

        self.title_shadow = pyglet.text.Label("Twinerama", font_size=72,
                                              anchor_x="center",
                                              anchor_y="center",
                                              x=window.width / 2 + 5, y=400 - 5,
                                              color=(0, 0, 0, 255))

        self.add_item(MenuItem("Play", (window.width / 2, 200),
                               run_game))

        self.add_item(MenuItem("Instructions", (window.width / 2, 150),
                               show_instructions))

        self.add_item(MenuItem("Exit", (window.width / 2, 100),
                               pyglet.app.exit))

        self.background = pyglet.image.load(data.filepath('main_menu.png'))

    def on_draw(self):
        window.clear()
        self.background.blit(0, 0)
        self.title_shadow.draw()
        self.title.draw()
        super(MainMenu, self).on_draw()

def run_game():
    window.close()
    import game
    game.main()

def show_instructions():
    class Instructions(object):
        def __init__(self):
            f = open(data.filepath('instructions.htm'), 'r')
            self.label = pyglet.text.HTMLLabel(f.read(), width=window.width, anchor_y="center", y=window.height / 2, multiline=True)
            f.close()

        def on_draw(self):
            window.clear()
            self.label.draw()

        def on_key_press(self, symbol, modifers):
            if symbol == pyglet.window.key.ESCAPE:
                pyglet.gl.glClearColor(0, 0, 0, 1)
                window.pop_handlers()
                window.push_handlers(main_menu)
                return True

    pyglet.gl.glClearColor(1, 1, 1, 1)
    instructions = Instructions()
    window.pop_handlers()
    window.push_handlers(instructions)

window = pyglet.window.Window(800, 600)
main_menu = MainMenu()
window.push_handlers(main_menu)

def main():
    pyglet.app.run()

if __name__ == "__main__":
    main()
