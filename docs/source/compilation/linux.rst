Linux
=====

Install Python
--------------

I highly recommend using the latest version of Python, which at the time of writing is 3.10.
Anything 3.8 or higher should suffice, but the latest version is recommended.

If you've already got Python 3.8 or higher, then you just need to find out whether you use
``python``, ``python3``, or ``python3.X`` (where ``X`` is a number) in the shell (use ``python -V``
to check). We'll need that for later.

.. code-block:: shell-session

   johndoe@pc-name:~$ python -V
   3.10.6

If you don't already have Python 3.8 or newer, download the latest release from `here
<https://www.python.org/downloads/>`_. For Linux, you'll need to download the source tarball.

I highly recommend installing Python to your home directory to avoid messing with any other
installations, so you'll need to add ``~/.local/bin`` to your ``$PATH`` if it's not already there.

Replace ``~/.bashrc`` with whatever shell config file you use.

.. code-block:: shell-session

   johndoe@pc-name:~$ echo "$PATH"
   /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
   johndoe@pc-name:~$ mkdir -p ~/.local/bin
   johndoe@pc-name:~$ echo 'PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   johndoe@pc-name:~$ . ~/.bashrc
   johndoe@pc-name:~$ echo "$PATH"
   /home/johndoe/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games

Before compiling Python from source, you may need to install some dependencies. Please read the
`Python devguide
<https://devguide.python.org/getting-started/setup-building/index.html#install-dependencies>`_ and
install all the dependencies listed for your distro.

Then you can compile Python with the following commands:

.. code-block:: shell-session

   johndoe@pc-name:~$ cd ~/Downloads
   johndoe@pc-name:~/Downloads$ tar xf Python-3.10.6.tgz
   johndoe@pc-name:~/Downloads$ cd Python-3.10.6
   johndoe@pc-name:.../Python-3.10.6$ ./configure --prefix=$HOME/.local --enable-optimizations
   checking build system type... x86_64-pc-linux-gnu
   checking host system type... x86_64-pc-linux-gnu
   etc...
   johndoe@pc-name:.../Python-3.10.6$ make && make altinstall
   Running code to generate profile data (this can take a while):
   etc...

Get the lintrans source code
----------------------------

Go to the `release page <https://github.com/DoctorDalek1963/lintrans/releases/tag/vVERSION_NUMBER>`_
on GitHub. Download the source code tarball and run the following commands:

.. code-block:: shell-session

   johndoe@pc-name:~$ cd ~/Downloads
   johndoe@pc-name:~/Downloads$ tar xf lintrans-VERSION_NUMBER.tar.gz
   johndoe@pc-name:~/Downloads$ cd lintrans-VERSION_NUMBER
   johndoe@pc-name:~/Downloads/lintrans-VERSION_NUMBER$

Compile the program
-------------------

Using whichever version of Python is the latest version for you, run the following commands to
install all the dependencies and compile lintrans.

.. code-block:: shell-session

   johndoe@pc-name:~/Downloads/lintrans-VERSION_NUMBER$ python -m venv venv
   johndoe@pc-name:~/Downloads/lintrans-VERSION_NUMBER$ ./venv/bin/pip install -e .[compile]
   Obtaining file:///home/johndoe/Downloads/lintrans-VERSION_NUMBER
     Installing build dependencies ...
     etc...
   johndoe@pc-name:~/Downloads/lintrans-VERSION_NUMBER$ ./venv/bin/python compile.py
   Created Compiler(filename=lintrans, version_name=VERSION_NUMBER, platform=linux)
   Compiling for platform=linux
   etc...

You should now have an executable file called ``lintrans`` in the current directory. I would
recommend moving this file, either to your desktop or some other folder where you keep small
programs, and then you can delete the ``lintrans-VERSION_NUMBER`` folder from your
Downloads folder.

-----

Thank you for installing lintrans! If you had any issues with the installation or have any
questions about the app, don't hesitate to `report a bug <https://forms.gle/Q82cLTtgPLcV4xQD6>`_ or
email me directly at :email:`dyson.dyson@icloud.com`.
