import sublime
import sublime_plugin
import re


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
    cursor = (0, 0)
    status = 0
    left_delete = False

    def reset_status(self):
        self.status = 0

    def set_status(self):
        self.status = self.status + 1

    def check_selection(self, view):
        sel = view.sel()
        if len(sel) == 0 or len(sel) > 1 or not sel[0].empty():
            self.reset_status()
            return False

        pt = sel[0].end()
        rc = view.rowcol(pt)
        if rc[0] != self.cursor[0]:
            self.reset_status()

        if rc[0] != self.cursor[0] or rc[1] <= self.cursor[1] or rc[1] > self.cursor[1]+1:
            self.cursor = view.rowcol(sel[0].end())
            return False
        else:
            self.cursor = view.rowcol(sel[0].end())
            return True

    def get_insert_pt(self, view):
        sel = view.sel()
        pt = sel[0].end()
        content = view.substr(view.line(pt))
        wrap_width = get_wrap_width(view)

        if len(content) <= wrap_width:
            return None

        if view.settings().get('auto_wrap_beyond_only', False):
            if view.rowcol(pt)[1] < wrap_width:
                return None

        default = [r"\[", r"\(", r"\{", " ", r"\n"]
        if view.score_selector(pt, "text.tex.latex"):
            default = [r"\\left\\.", r"\\left.", r"\\\{"] + default

        break_chars = "|".join(view.settings().get('auto_wrap_break_patterns', default))
        results = re.finditer(break_chars, content, re.VERBOSE)
        indices = [m.start(0) for m in results] + [len(content)]
        index = next(x[0] for x in enumerate(indices) if x[1] > wrap_width)

        if view.settings().get("auto_wrap_break_long_word", True) and index > 0:
            return view.line(pt).begin() + indices[index-1]
        else:
            if index == len(indices)-1:
                return None
            return view.line(pt).begin() + indices[index]

    def on_modified(self, view):
        if view.settings().get('is_widget'):
            return
        if not view.settings().get('auto_wrap', False):
            return

        if not self.check_selection(view):
            return

        insertpt = self.get_insert_pt(view)
        if not insertpt:
            return

        self.set_status()

        join = self.status >= 2
        left_delete = " " not in view.substr(sublime.Region(insertpt-1, insertpt+1))

        # protect from the listener
        view.settings().set('auto_wrap', False)
        view.run_command('auto_wrap_insert', {
            'insertpt': insertpt, 'join': join, "left_delete": self.left_delete
        })
        self.left_delete = left_delete
        # release from the listener
        view.settings().set('auto_wrap', True)

    def on_post_text_command(self, view, command_name, args):
        if view.settings().get('is_widget'):
            return
        if not view.settings().get('auto_wrap', False):
            return

        if command_name in ['undo', 'soft_undo']:
            self.reset_status()

    def on_deactivated(self, view):
        if view.settings().get('is_widget'):
            return
        if not view.settings().get('auto_wrap', False):
            return
        self.reset_status()


class AutoWrapInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, insertpt, join=False, left_delete=False):
        view = self.view

        insertpt = int(insertpt)
        insertpt_row = view.rowcol(insertpt)[0]
        iscomment = view.score_selector(insertpt-1, "comment") > 0 and \
            view.score_selector(insertpt-1, "comment.block") == 0

        view.insert(edit, insertpt, "\n")

        view.add_regions("auto_wrap_oldsel", [s for s in view.sel()], "")

        if join and iscomment:
            view.sel().clear()
            view.sel().add(view.text_point(insertpt_row+2, 0))
            view.run_command('toggle_comment', {"block": False})

        view.sel().clear()
        view.sel().add(sublime.Region(insertpt+1, insertpt+1))

        if join:
            view.run_command('join_lines')
            pt = view.sel()[0].end()
            if left_delete and view.substr(sublime.Region(pt-1, pt)) == " ":
                view.run_command("left_delete")

        if view.settings().get('auto_indent'):
            view.run_command('reindent', {'force_indent': False})

        if iscomment:
            view.run_command('toggle_comment', {"block": False})

        view.sel().clear()
        for s in view.get_regions("auto_wrap_oldsel"):
            view.sel().add(s)
        view.erase_regions("auto_wrap_oldsel")


class ToggleAutoWrap(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.settings().set("auto_wrap", not view.settings().get("auto_wrap", False))
        onoff = "on" if view.settings().get("auto_wrap") else "off"
        sublime.status_message("Auto (Hard) Wrap %s" % onoff)
