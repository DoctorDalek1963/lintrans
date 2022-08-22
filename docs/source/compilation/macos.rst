macOS
=====

Install Python
--------------

I highly recommend using the latest version of Python, which at the time of writing is 3.10.
Anything 3.8 or higher should suffice, but the latest version is recommended.

If you've already got Python 3.8 or higher, then you just need to find out whether you use
``python``, ``python3``, or ``python3.X`` (where ``X`` is a number) in `Terminal` (use ``python
-V`` to check). We'll need that for later.

.. code-block:: shell-session

   johndoe@mac-name ~ % python3 -V
   3.10.6

If you don't already have Python 3.8 or newer, download the latest release from `here
<https://www.python.org/downloads/>`_. Make sure to download the macOS installer, and then just run
it.

Follow all of the instructions and at the end, run ``Install Certificates.command`` and ``Update
Shell Profile.command`` (available in ``/Applications/Python 3.10`` if it doesn't show up
automatically).

Then open `Terminal` from Spotlight Search and check that ``python3 -V`` says the version that you
just installed.

Get the lintrans source code
----------------------------

Go to the `release page <https://github.com/DoctorDalek1963/lintrans/releases/tag/vVERSION_NUMBER>`_
on GitHub. Download the source code zip file. macOS should unzip the file for you, so open
`Terminal` from Spotlight Search and ``cd`` in the new folder:

.. code-block:: shell-session

   johndoe@mac-name ~ % cd ~/Downloads/lintrans-VERSION_NUMBER

Compile the program
-------------------

Using whichever version of Python is the latest version for you, run the following commands to
install all the dependencies and compile lintrans.

.. code-block:: shell-session

   johndoe@mac-name lintrans-VERSION_NUMBER % python3 -m venv venv
   johndoe@mac-name lintrans-VERSION_NUMBER % ./venv/bin/pip install -e .[compile]
   Obtaining file:///Users/johndoe/Downloads/lintrans-VERSION_NUMBER
     Installing build dependencies ...
     etc...
   johndoe@mac-name lintrans-VERSION_NUMBER % ./venv/bin/python compile.py
   Created Compiler(filename=lintrans, version_name=VERSION_NUMBER, platform=darwin)
   Compiling for platform=darwin
   etc...

If this is your first time doing something like this, then you might need to install the macOS
developer tools. Just agree to the legal stuff and wait for it to install. It might take a while.
Then run the compile command again.

You should now have an app file called ``lintrans`` in the current folder. I would recommend
moving this file, either to your desktop or some other folder where you keep small programs, and
then you can delete the ``lintrans-VERSION_NUMBER`` folder from your Downloads folder.

-----

Thank you for installing lintrans! If you had any issues with the installation or have any
questions about the app, don't hesitate to `report a bug <https://forms.gle/Q82cLTtgPLcV4xQD6>`_ or
email me directly at :email:`dyson.dyson@icloud.com`.
