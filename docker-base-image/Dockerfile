FROM python:3.10-alpine
RUN apk update && apk add curl fontconfig gcc git libc-dev libgcc make ncurses perl wget

ENV PATH="/usr/local/texlive/2021/bin/x86_64-linuxmusl:/root/.cargo/bin:$PATH"

# Install TeXlive
RUN wget -r ftp://ftp.tu-chemnitz.de/pub/tug/historic/systems/texlive/2021/tlnet-final/install-tl-unx.tar.gz -O tl.tgz && \
	tar xzf tl.tgz && \
	rm tl.tgz && \
	mv install-tl-20220322 /tl
WORKDIR /tl
COPY texlive.profile texlive.profile
RUN ./install-tl -repository ftp://ftp.tu-chemnitz.de/pub/tug/historic/systems/texlive/2021/tlnet-final -profile texlive.profile
WORKDIR /
RUN rm -rf ftp.tu-chemnitz.de tl

RUN python -m pip install --upgrade pip && \
	python -m pip install pygments
RUN tlmgr update --all && \
	tlmgr install biber biblatex cancel catchfile csquotes footmisc framed fvextra minted subfiles tkz-euclide upquote was xstring

# Install Rust, just, and fd
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal

RUN cargo install --version 1.8.0 --force just && \
	cargo install --version 8.6.0 --force fd-find

# Install Hack font
RUN mkdir -p /root/.fonts
WORKDIR /root/.fonts
RUN wget https://github.com/source-foundry/Hack/releases/download/v3.003/Hack-v3.003-ttf.zip && \
	unzip Hack-v3.003-ttf.zip && \
	rm Hack-v3.003-ttf.zip && \
	fc-cache -fv
WORKDIR /

WORKDIR /write-up-lintrans
