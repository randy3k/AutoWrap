import sublime
from unittesting import DeferrableTestCase

Ccode = """/*
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
*/
"""

Ccode_indented = """/*
    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
*/
"""


class TestC(DeferrableTestCase):

    def setUp(self):
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)
        self.view = sublime.active_window().new_file()
        self.view.settings().set("auto_wrap", True)
        self.view.settings().set("auto_wrap_width", 80)
        self.view.settings().set("syntax", "Packages/C++/C.tmLanguage")

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def test_comment_block(self):
        self.view.settings().set('auto_indent', False)
        self.setText(Ccode)
        self.view.settings().set('auto_indent', True)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(67, 67))
        for c in " foo foo foo foo foo ":
            self.setText(c)
            yield 10
        second_row = self.getRow(2)
        self.assertEqual(second_row, "foo eiusmod")
        self.assertTrue(
            self.view.score_selector(self.view.text_point(2, 0), "comment.block") > 0
            )

    def test_comment_block_indented(self):
        self.view.settings().set('auto_indent', False)
        self.setText(Ccode_indented)
        self.view.settings().set('auto_indent', True)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(71, 71))
        for c in " foo foo foo foo foo ":
            self.setText(c)
            yield 10
        second_row = self.getRow(2)
        self.assertEqual(second_row, "    foo foo eiusmod")
        self.assertTrue(
            self.view.score_selector(self.view.text_point(2, 0), "comment.block") > 0
            )
