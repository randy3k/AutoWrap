import sublime

version = sublime.version()

if version >= "3000":
    from UnitTesting.unittesting import DeferrableTestCase
else:
    from unittesting import DeferrableTestCase

Pythoncode = """# this is a comment this is a comment this is a comment this is a comment
def f(x):
    return(x)
"""


class TestPython(DeferrableTestCase):

    def setUp(self):
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)
        self.view = sublime.active_window().new_file()
        self.view.settings().set("auto_wrap", True)
        self.view.settings().set("auto_wrap_width", 80)
        self.view.settings().set("syntax", "Packages/Python/Python.tmLanguage")

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def test_comment(self):
        self.setText(Pythoncode)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(73, 73))
        for c in " this is a comment":
            self.setText(c)
            yield 10
        second_row = self.getRow(1)
        self.assertEqual(second_row, "# is a comment")

    def test_comment_middle(self):
        self.setText(Pythoncode)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(19, 19))
        for c in " this is a comment":
            self.setText(c)
            yield 10
        second_row = self.getRow(1)
        self.assertEqual(second_row, "# is a comment")
