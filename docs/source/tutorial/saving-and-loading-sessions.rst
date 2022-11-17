.. _saving-and-loading-sessions:

Saving and loading sessions
===========================

Usefulness in teaching
----------------------

As a teacher, it is often useful to plan a lesson in advance. Defining a whole set of matrices at
the start of a lesson is boring and time consuming, so lintrans allows you to define a set of
matrices beforehand, save the whole session to a file, and then open that saved session for the
lesson. This session file saves all the matrices you've defined, the display settings, position of
the input vector, as well as the polygon if you've defined one.

When you open a previously saved session, you can view all the matrices you had defined by clicking
the `Show defined matrices` button. However, I would recommend writing down some separate notes to
remind you what these matrices were supposed to be for.

Saving
------

To save a session file, first define whatever matrices you want to, and then go to ``File`` >
``Save`` or press ``Ctrl+S``. Saving works like any other software. Just give it a name, and it
will save the session to a custom ``.lt`` file. If you have already saved but now want to use a
different file name, you can go to ``File`` > ``Save as...`` or press ``Ctrl+Shift+S``.

You can save the file anywhere on your computer, but lintrans creates a special folder just for
your lintrans session save files, and it will always default to this folder when saving or opening
a file, so I highly recommend using it.

If you have saved a session to a file, and then changed something that could be saved (maybe you
defined a new matrix or changed the polygon) without having saved since that change, then you will
be prompted to save your session before exiting. You can exit and discard your changes if you want
to, but I would recommend saving.

You will also be prompted to save the session when exiting lintrans even if you hadn't already
saved it somewhere.

Loading
-------

To open a previously saved session, go to ``File`` > ``Open`` or press ``Ctrl+O``. You will be
shown all the lintrans session save files in the special folder, and you can just double click on
the one you want. If you saved your session elsewhere, then you can simply navigate to wherever you
saved it just like you would with any other file.
