import sublime

version = sublime.version()

if version >= "3000":
    from UnitTesting.unittesting import DeferrableTestCase
else:
    from unittesting import DeferrableTestCase

Lorem = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""


class TestCursor(DeferrableTestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.settings().set("auto_wrap", True)
        self.view.settings().set("auto_wrap_width", 80)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def test_cursor(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(64, 64))

        for c in " apple is apple apple":
            self.setText(c)
            yield 10

        self.assertEqual(self.getRow(1), "apple eiusmod")

    def test_cursor2(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(64, 64))

        for c in " apple is orange apple":
            self.setText(c)
            yield 10

        self.assertEqual(self.getRow(1), "appleeiusmod")

    def test_cursor3(self):
        self.setText(Lorem)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(72, 72))
        self.setText(" fooooo(")

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(80, 80))

        for c in "apple":
            self.setText(c)
            yield 10

        self.assertEqual(self.getRow(1), "(apple")

    def test_cursor4(self):
        self.setText(Lorem)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(72, 72))
        self.setText(" foooooo(")

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(81, 81))

        for c in "apple":
            self.setText(c)
            yield 10

        self.assertEqual(self.getRow(1), "(apple")
