import sublime, sublime_plugin

class AutoWrapListener(sublime_plugin.EventListener):
    prev_sel = 0

    def on_load(self, view):
        pass

    def on_selection_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        if not view.settings().get('auto_wrap', False): return
        self.prev_sel = view.sel()[0].end()

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        if not view.settings().get('auto_wrap', False): return
        rulers = view.settings().get('rulers')
        if not rulers: rulers = [80]
        sel = view.sel()
        if len(sel)>1 or sel[0].begin()!=sel[0].end(): return
        pt = sel[0].end()
        if pt<=self.prev_sel or pt-self.prev_sel>1 or view.rowcol(pt)[1]<=rulers[0] \
            or view.substr(pt-1)==" " or view.line(pt).end() != pt:
            return

        # to obtain the insert point
        saved_sel = sel[0].end()
        view.run_command("move", {"by": "stops", "word_begin": True, "empty_line": True, "separators": "", "forward": False})
        insertpt = view.sel()[0].end()
        view.sel().clear()
        view.show(saved_sel)
        view.sel().add(saved_sel)

        # insert enter
        edit_insert = view.begin_edit()
        view.insert(edit_insert, insertpt, "\n")
        if view.settings().get('auto_indent'):
            view.run_command('reindent', {'force_indent': False})
        view.end_edit(edit_insert)

class ToggleAutoWrap(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.settings().set("auto_wrap", not view.settings().get("auto_wrap", False))
        if view.settings().get("auto_wrap"):
            onoff = "on"
        else:
            onoff = "off"
        sublime.status_message("Auto (Hard) Wrap %s" % onoff)