Auto (Hard) Wrap for Sublime Text 2
====================
Automatic hard wrap when the cursor is beyond the ruler (default 80).
It is very useful for text documents.

Installation
------------
[Package Control](http://wbond.net/sublime_packages/package_control)



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

###Wraping style
Long word will stay at the ruler and only the next word breaks into a new line.<br>
To change this behavior, put this in your preference or syntax specific preference.

    {
        "wrap_style" : "classic"
    }
