import sublime, sublime_plugin

class AutoWrapListener(sublime_plugin.EventListener):
    saved_sel = 0

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        if not view.settings().get('auto_wrap', False): return
        sel = view.sel()
        if not sel or len(sel)>1 or sel[0].begin()!=sel[0].end(): return
        rulers = view.settings().get('rulers')
        if not rulers: rulers = [80]
        pt = sel[0].end()
        if pt<=self.saved_sel or pt-self.saved_sel>1 or view.rowcol(pt)[1]<=rulers[0] \
            or view.substr(pt-1)==" " or view.line(pt).end() != pt:
            activate = False
        else: activate = True
        self.saved_sel = sel[0].end()
        if not activate: return

        # to obtain the insert point
        view.run_command("move", {"by": "stops", "word_begin": True, "empty_line": True, "separators": "", "forward": False})
        insertpt = view.sel()[0].end()
        view.sel().clear()
        view.show(self.saved_sel)
        view.sel().add(self.saved_sel)

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
        onoff = "on" if view.settings().get("auto_wrap") else "off"
        sublime.status_message("Auto (Hard) Wrap %s" % onoff)