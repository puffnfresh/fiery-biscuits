#!/usr/bin/evn python

import pyglet
import sys
from pyglet.window import key

INPUT_INDICATOR = ">>> "

class Console(object):
    def __init__(self, window, globals):
        self.active = False
        self.globals = globals
        self.history = []
        self.history_steps = 0

        self.document = pyglet.text.document.UnformattedDocument(INPUT_INDICATOR)
        self.document.set_style(0, 0, {'color' : (255, 255, 255, 255)})
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, window.width, window.height, True)
        self.caret = pyglet.text.caret.Caret(self.layout)
        self.caret.color = (255, 255, 255)
        self.caret.position = len(self.document.text)

    def is_active(self):
        return self.active

    def toggle(self):
        self.active = not self.active

    def run_input(self):
        command = self.get_command()
        self.history.append(command)
        try:
            output = repr(eval(command, self.globals, {}))
        except Exception, inst:
            output = repr(inst)
        self.document.text += "\n" + output + "\n" + INPUT_INDICATOR
        self.caret.position = len(self.document.text)
        self.history_steps = 0

    def get_command(self):
        return self.document.text.splitlines()[-1][len(INPUT_INDICATOR):]

    def clear_command(self):
        command = self.get_command()
        if len(command) > 0:
            self.document.text = self.document.text[:-len(command)]
        self.reset_caret()

    def reset_caret(self):
        self.caret.position = len(self.document.text)

    def at_start(self):
        indicator_pos = self.document.text.rfind("\n" + INPUT_INDICATOR)
        if self.caret.position <= indicator_pos + len(INPUT_INDICATOR) + 1 or len(self.document.text) == len(INPUT_INDICATOR):
            return True
        return False
        
    def on_text(self, text):
        if text == "\r":
            self.run_input()
        elif text != "`":
            self.caret.on_text(text)

    def on_text_motion(self, motion):
        if motion == key.MOTION_BACKSPACE or motion == key.MOTION_LEFT:
            if self.at_start():
                return
            self.caret.on_text_motion(motion)    
        elif motion == key.MOTION_RIGHT:
            if self.caret.position >= len(self.document.text):
                return
            self.caret.on_text_motion(motion)
        elif motion == key.MOTION_DELETE:
            self.caret.on_text_motion(motion)
        elif motion in [key.MOTION_UP, key.MOTION_PREVIOUS_PAGE, key.MOTION_DOWN, key.MOTION_NEXT_PAGE]:
            if len(self.history) <= 0:
                return
            self.clear_command()

            if motion == key.MOTION_UP or motion == key.MOTION_PREVIOUS_PAGE:
                self.history_steps += 1
            else:
                self.history_steps -= 1

            command = self.history[-self.history_steps % len(self.history)]
            self.document.insert_text(self.caret.position, command)
            self.reset_caret()
        elif motion == key.MOTION_END_OF_LINE:
            self.reset_caret()
        #elif motion == key.MOTION_BEGINNING_OF_LINE:
        #    self.reset_caret()
