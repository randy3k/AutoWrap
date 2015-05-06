import sublime

version = sublime.version()

if version >= "3000":
    from UnitTesting.unittesting import DeferrableTestCase
else:
    from unittesting import DeferrableTestCase

Lorem = ("""Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod"""
         """tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,"""
         """quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo"""
         """consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse"""
         """cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non"""
         """proident, sunt in culpa qui officia deserunt mollit anim id est \nlaborum.""")


class TestLongline(DeferrableTestCase):

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

    def test_long_line_end(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(433, 433))

        for c in "apple is orange":
            self.setText(c)
            yield 10

        self.assertEqual(self.getRow(5),
                         "culpa qui officia deserunt mollit anim id est apple is orange")

        self.assertEqual(self.getRow(6), "laborum.")

    def test_long_line_middle(self):
        self.setText(Lorem)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(200, 200))

        for c in "apple is orange":
            self.setText(c)
            yield 10

        self.assertEqual(
            self.getRow(1),
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,quis"
        )
