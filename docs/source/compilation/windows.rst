Windows
=======

Install Python
--------------

I highly recommend using the latest version of Python, which at the time of writing is 3.11.
Anything 3.10 or higher should suffice, but the latest version is recommended.

If you've already got Python 3.10 or higher, then you just need to find out whether you use
``python``, ``python3``, or ``python3.X`` (where ``X`` is a number) in PowerShell (use ``python
-V`` to check). We'll need that for later.

.. code-block:: pwsh-session

   PS C:\Users\johndoe> python -V
   3.11.0

If you don't already have Python 3.10 or newer, download the latest release from `python.org
<https://www.python.org/downloads/>`_.

Make sure to download the installer. You'll probably want the 64-bit one (if you've got ``Program
Files`` and ``Program Files (x86)`` folders), but if you're using a 32-bit machine, then download
the 32-bit installer.

In the installer, check the box that says "Add Python 3.X to PATH", and then click "Install now"
to install Python in ``C:\Users\<username>\...``

Now open PowerShell from the start menu and run ``python -V`` to check that it says whichever
version you installed.

Get the lintrans source code
----------------------------

Go to the `release page <https://github.com/DoctorDalek1963/lintrans/releases/tag/vVERSION_NUMBER>`_
on GitHub and download the source code zip file. Unzip the file by just right-clicking it in your
Downloads folder and clicking "Extract All...", and keep the default name. Then run the following
commands.

.. code-block:: pwsh-session

   PS C:\Users\johndoe> cd ~\Downloads
   PS C:\Users\johndoe\Downloads> cd .\lintrans-VERSION_NUMBER\lintrans-VERSION_NUMBER
   PS C:\Users\johndoe\Downloads\lintrans-VERSION_NUMBER\lintrans-VERSION_NUMBER>

Compile the program
-------------------

Using whichever version of Python is the latest version for you, run the following commands to
install all the dependencies and compile lintrans.

.. code-block:: pwsh-session

   PS C:\Users\johndoe\...\lintrans-VERSION_NUMBER> python -m venv venv
   PS C:\Users\johndoe\...\lintrans-VERSION_NUMBER> .\venv\Scripts\pip.exe install -e .[compile]
   Obtaining file:///C:/Users/johndoe/Downloads/lintrans-VERSION_NUMBER/lintrans-VERSION_NUMBER
     Installing build dependencies ...
     etc...
   PS C:\Users\johndoe\...\lintrans-VERSION_NUMBER> .\venv\Scripts\python.exe compile.py
   Created Compiler(filename=lintrans, version_name=VERSION_NUMBER, platform=win32)
   Compiling for platform=win32
   etc...

You should now have an exe file called ``lintrans`` in the current folder and you can either keep
it somewhere, or use it to create the installer to install lintrans properly. If you choose to keep
the standalone exe, then you can delete the ``lintrans-VERSION_NUMBER`` folder from your Downloads
folder.


Install lintrans (optional)
---------------------------

The lintrans installer for Windows is automatically generated using a program called NSIS. You
first need to install version 3 or above from `here <https://nsis.sourceforge.io/Download>`_.

Then you need to move the ``lintrans.exe`` file into the ``installers`` folder. Right click on
the ``Windows.nsi`` file and select "Compile NSIS Script".

Wait for the compilation to complete and then run ``install-lintrans-Windows.exe``. Once lintrans
is installed, you can delete the ``lintrans-VERSION_NUMBER`` folder from your Downloads folder.

-----

Thank you for installing lintrans! If you had any issues with the installation or have any
questions about the app, don't hesitate to `report a bug <https://forms.gle/Q82cLTtgPLcV4xQD6>`_ or
email me directly at :email:`dyson.dyson@icloud.com`.
