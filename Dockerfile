FROM doctordalek1963/write-up-lintrans-base-image:latest

RUN mkdir -p tikz-imgs
RUN git clone https://github.com/DoctorDalek1963/lintrans

COPY main.tex main.tex
COPY sections/ sections/
COPY bibs/*.bib bibs/
COPY images/ images/
COPY videos/ videos/
COPY generate_appendices.py generate_appendices.py
COPY lexers.py lexers.py
COPY process-code-snippets/Cargo.* process-code-snippets/
COPY process-code-snippets/src/ process-code-snippets/src/
COPY justfile justfile

RUN python -m pip install gitpython
RUN python generate_appendices.py

CMD [ "just", "build-zip" ]
