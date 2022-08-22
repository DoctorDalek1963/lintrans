Welcome to the lintrans documentation
=====================================

This is the documentation for lintrans version |release|. It is split into 2 main parts.

The first part is the :ref:`tutorial<tutorial>`, which explains how to use the software. If you
just want to use it for teaching or learning linear transformations, read this.

The second part is the :ref:`backend documentation<backend>`. This is only relevant if you are a
maintainer of the software (currently just me) or want to learn about its inner workings. The
backend documentation is very technical, and you don't need to read it to learn how to use the
software.

.. only:: include_compilation

   There is also a :ref:`tutorial on compiling<compilation>` the software from its source code.
   This is rarely necessary, but is available for anyone who wants or needs it (macOS users need to
   compile from source due to issues with Apple preventing unsigned code from running on their
   system).

.. toctree::
   :maxdepth: 10
   :caption: Contents:

   tutorial/index
   backend/index
   compilation/index
