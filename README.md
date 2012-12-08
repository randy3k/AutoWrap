Auto (Hard) Wrap for Sublime Text 2
====================
Automatic hard wrap when the cursor is beyond the ruler (default 80).

Installation
------------
 1) (not available now) Via [Package Control](http://wbond.net/sublime_packages/package_control)

 2) Put the package under `Packages` folder



Usage
------------
###To toggle Auto Wrap
Type `Auto Wrap` in command palette.


###To activate Auto Wrap for a specific syntax at start up

Put the following in your syntax specific preference.<br>
Menu -> Preference -> Settings - More -> Syntax Specific - User

    {
        "auto_wrap" : true
    }