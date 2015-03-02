import sublime
import sublime_plugin


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
    _continue = 0
    last_view = None

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return
        if not view.settings().get('auto_wrap', False):
            return
        if self.last_view != view:
            self.last_view = view
            return
        sel = view.sel()
        if len(sel) == 0 or len(sel) > 1 or sel[0].begin() != sel[0].end():
            return
        pt = sel[0].end()
        if pt <= self.saved_sel or pt-self.saved_sel > 1:
            if pt < self.saved_sel or pt-self.saved_sel > 1:
                AutoWrapListener._continue = 0
            self.saved_sel = sel[0].end()
            return
        else:
            self.saved_sel = sel[0].end()

        wrap_width = get_wrap_width(view)

        if view.settings().get('auto_wrap_beyond_only', False):
            if view.rowcol(pt)[1] < wrap_width:
                return

        line_begin = view.line(pt).begin()
        line_end = view.line(pt).end()
        insertpt = nextbrk_end = line_begin

        if view.score_selector(pt, "text.tex.latex"):
            default = r"\\left\\.|\\left.|\\\{|[ (\[\n]"
        else:
            default = r"[ ({\[\n]"

        break_chars = view.settings().get('auto_wrap_break_chars', default)
        blongw = view.settings().get("auto_wrap_break_long_word", True)
        n = 0
        while True:
            # prevent dead loop
            if n == 100:
                # print("max")
                return
            nextbrk = view.find(break_chars, nextbrk_end)

            if view.rowcol(insertpt)[0] > view.rowcol(line_begin)[0]:
                # print("insertpt in next line")
                return

            nextbrk_begin = nextbrk.begin()
            nextbrk_end = nextbrk.end()

            if nextbrk_begin == -1:
                nextbrk_begin = line_end
                nextbrk_end = line_end
                if view.rowcol(nextbrk_begin)[1] <= wrap_width:
                    # print("eof")
                    return

            # print(view.rowcol(insertpt)[1],view.substr(insertpt), view.rowcol(nextbrk_begin)[1])

            if view.rowcol(nextbrk_begin)[0] > view.rowcol(line_begin)[0]:
                # print("nextbrk_begin in next line")
                return

            if blongw and view.rowcol(insertpt)[1] <= wrap_width and \
                    view.rowcol(nextbrk_begin)[1] > wrap_width:
                break
            elif not blongw and view.rowcol(insertpt)[1] >= wrap_width:
                break
            else:
                insertpt = nextbrk_begin
                # and search continue
            n = n + 1

        # protect from the listener
        view.settings().set('auto_wrap', False)
        view.run_command('auto_wrap_insert', {'insertpt': insertpt})
        # release from the listener
        view.settings().set('auto_wrap', True)


class AutoWrapInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, insertpt):
        view = self.view

        insertpt = int(insertpt)
        insertpt_row = view.rowcol(insertpt)[0]
        iscomment = view.score_selector(insertpt-1, "comment") > 0 and \
            view.score_selector(insertpt-1, "comment.block") == 0

        if view.substr(sublime.Region(insertpt, insertpt+1)) is " ":
            view.replace(edit, sublime.Region(insertpt, insertpt+1), "\n")
        elif view.substr(sublime.Region(insertpt-1, insertpt)) is " ":
            view.replace(edit, sublime.Region(insertpt-1, insertpt), "\n")
        else:
            view.insert(edit, insertpt, "\n")
        view.add_regions("auto_wrap_oldsel", view.sel())

        AutoWrapListener._continue = AutoWrapListener._continue + 1
        if AutoWrapListener._continue >= 2:
            if iscomment:
                view.sel().clear()
                view.sel().add(view.text_point(insertpt_row+2, 0))
                view.run_command('toggle_comment', {"block": False})

        view.sel().clear()
        view.sel().add(sublime.Region(insertpt+1, insertpt+1))

        if AutoWrapListener._continue >= 2:
            view.run_command('join_lines')

        if view.settings().get('auto_indent'):
            view.run_command('reindent', {'force_indent': False})

        if iscomment:
            view.run_command('toggle_comment', {"block": False})

        view.sel().clear()
        view.sel().add_all(view.get_regions("auto_wrap_oldsel"))
        view.erase_regions("auto_wrap_oldsel")


class ToggleAutoWrap(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.settings().set("auto_wrap", not view.settings().get("auto_wrap", False))
        onoff = "on" if view.settings().get("auto_wrap") else "off"
        sublime.status_message("Auto (Hard) Wrap %s" % onoff)
