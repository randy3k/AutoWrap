import sublime

version = sublime.version()

if version >= "3000":
    from UnitTesting.unittesting import DeferrableTestCase
else:
    from unittesting import DeferrableTestCase

Lorem = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do \\alpha
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad \\left[\\right]
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""


class TestLatex(DeferrableTestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.settings().set("auto_wrap", True)
        self.view.settings().set("auto_wrap_width", 80)
        self.view.settings().set("syntax", "Packages/LaTeX/LaTeX.tmLanguage")

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def test_one_single_wrap(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, 0))
        for c in "apple is orange ":
            self.setText(c)
            yield 10
        second_row = self.getRow(1)
        self.assertEqual(second_row, "\\alpha")

    def test_two_continuous_wrap(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, 0))
        for c in "apple is orange one two three":
            self.setText(c)
            yield 10
        second_row = self.getRow(1)
        self.assertEqual(second_row, "elit, sed do \\alpha")

    def test_middle_wrap(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(100, 100))
        for c in "apple is orange one two three":
            self.setText(c)
            yield 10
        third_row = self.getRow(2)
        self.assertEqual(third_row, "Ut enim ad \\left[\\right]")

    def test_change_position(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(100, 100))
        for c in "apple is orange one two three":
            self.setText(c)
            yield 10
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(120, 120))
        for c in "apple is orange one two three":
            self.setText(c)
            yield 10
        third_row = self.getRow(2)
        self.assertEqual(third_row, "threeet dolore magna aliqua. Ut enim ad \\left[\\right]")

    def test_move_to_next_line(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(71, 71))
        for c in " apple is orange one two three":
            self.setText(c)
            yield 10
        second_row = self.getRow(1)
        self.assertEqual(second_row, "orange one two three")
