import sublime, sublime_plugin, re, sys
if sys.version >= '3':
    long  = int

def get_wrap_width(view):
    wrap_width = view.settings().get('auto_wrap_width')
    if not wrap_width or wrap_width == 0:
        wrap_width = view.settings().get('wrap_width')
        if not wrap_width or wrap_width == 0:
            rulers = view.settings().get('rulers')
            if rulers:
                wrap_width = rulers[0]
            else:
                wrap_width = 80
    return wrap_width


class AutoWrapListener(sublime_plugin.EventListener):
    saved_sel = 0

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        if not view.settings().get('auto_wrap', False): return
        sel = view.sel()
        if not sel or len(sel)>1 or sel[0].begin()!=sel[0].end(): return
        wrap_width = get_wrap_width(view)
        pt = sel[0].end()
        if pt<=self.saved_sel or pt-self.saved_sel>1 or view.rowcol(pt)[1]<wrap_width:
            self.saved_sel = sel[0].end()
            return
        else:
            self.saved_sel = sel[0].end()

        # to obtain the insert point
        line = view.substr(view.line(pt))
        m = re.match('.*\s(\S*\s?)$',line)
        if not m: return
        insertpt = view.line(pt).end()-len(m.group(1))
        if pt<insertpt: return
        if not view.settings().get('auto_wrap_break_long_word',True) and view.rowcol(insertpt)[1]<=wrap_width:
            return

        view.run_command('auto_wrap_insert', {'insertpt': insertpt})

class AutoWrapInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, insertpt):
        view = self.view
        view.replace(edit, sublime.Region(long(insertpt-1),long(insertpt)), "\n")
        if view.settings().get('auto_indent'):
            view.run_command('reindent', {'force_indent': False})
        if view.scope_name(view.sel()[0].begin()-1).find("comment")>=0:
            view.run_command('toggle_comment', { "block": False })


class ToggleAutoWrap(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.settings().set("auto_wrap", not view.settings().get("auto_wrap", False))
        onoff = "on" if view.settings().get("auto_wrap") else "off"
        sublime.status_message("Auto (Hard) Wrap %s" % onoff)