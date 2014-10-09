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
        if pt<=self.saved_sel or pt-self.saved_sel>1 or view.rowcol(pt)[1]<=wrap_width:
            self.saved_sel = sel[0].end()
            return
        else:
            self.saved_sel = sel[0].end()

        if view.substr(sublime.Region(pt-1,pt)) in \
                 view.settings().get('auto_wrap_end_chars', ",.?;:'\""):
            pt = pt -1
        # to obtain the insert point
        insertpt = view.word(pt).begin()

        # move cursor back one char for latex command
        if view.score_selector(insertpt-1, "text.tex.latex")>0 and \
                re.match(r"[^\\]\\", view.substr(sublime.Region(insertpt-2,insertpt))):
            insertpt = insertpt-1

        if not view.settings().get('auto_wrap_break_long_word',True) and \
                    view.rowcol(insertpt)[1]<=wrap_width:
            return

        view.run_command('auto_wrap_insert', {'insertpt': insertpt})

class AutoWrapInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, insertpt):
        view = self.view
        insertpt = long(insertpt)
        iscomment = view.score_selector(insertpt-1, "comment")>0 and \
                    view.score_selector(insertpt-1, "comment.block")==0

        if view.substr(sublime.Region(insertpt,insertpt+1)) is " ":
            view.replace(edit, sublime.Region(insertpt,insertpt+1), "\n")
        elif view.substr(sublime.Region(insertpt-1,insertpt)) is " ":
            view.replace(edit, sublime.Region(insertpt-1,insertpt), "\n")
        else:
            view.insert(edit, insertpt, "\n")

        if view.settings().get('auto_indent'):
            view.run_command('reindent', {'force_indent': False})

        if iscomment:
            view.run_command('toggle_comment', { "block": False })

class ToggleAutoWrap(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.settings().set("auto_wrap", not view.settings().get("auto_wrap", False))
        onoff = "on" if view.settings().get("auto_wrap") else "off"
        sublime.status_message("Auto (Hard) Wrap %s" % onoff)
