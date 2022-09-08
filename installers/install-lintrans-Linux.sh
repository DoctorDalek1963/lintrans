#!/usr/bin/env sh

create_desktop_file() {
	rm -f doctordalek1963-lintrans.desktop
	touch doctordalek1963-lintrans.desktop
	echo "[Desktop Entry]"                          >> doctordalek1963-lintrans.desktop
	echo "Type=Application"                         >> doctordalek1963-lintrans.desktop
	echo "Version=1.5"                              >> doctordalek1963-lintrans.desktop
	echo "Name=lintrans"                            >> doctordalek1963-lintrans.desktop
	echo "Comment=Linear transformation visualizer" >> doctordalek1963-lintrans.desktop
	echo "Icon=$HOME/.lintrans/icons/128.xpm"       >> doctordalek1963-lintrans.desktop
	echo "Exec='$1' %f"                             >> doctordalek1963-lintrans.desktop
	echo "Terminal=false"                           >> doctordalek1963-lintrans.desktop
	echo "Categories=Education"                     >> doctordalek1963-lintrans.desktop
}

download_icons() {
	dest="$HOME/.lintrans/icons"
	if [ ! -d "$dest" ]; then
		mkdir -p "$dest"
	fi

	wget -q --show-progress "https://github.com/DoctorDalek1963/lintrans/raw/v$1/src/lintrans/gui/assets/16.jpg" -O "$dest/16.jpg"
	wget -q --show-progress "https://github.com/DoctorDalek1963/lintrans/raw/v$1/src/lintrans/gui/assets/32.jpg" -O "$dest/32.jpg"
	wget -q --show-progress "https://github.com/DoctorDalek1963/lintrans/raw/v$1/src/lintrans/gui/assets/64.jpg" -O "$dest/64.jpg"
	wget -q --show-progress "https://github.com/DoctorDalek1963/lintrans/raw/v$1/src/lintrans/gui/assets/128.jpg" -O "$dest/128.jpg"
}

echo "Welcome to the lintrans installer!"

latest_version="$(curl -sL https://github.com/DoctorDalek1963/lintrans/releases/latest | \grep -Po '(?<=/DoctorDalek1963/lintrans/releases/download/v)\d+\.\d+\.\d+(?=/lintrans-Linux)')"
binary_url="https://github.com/DoctorDalek1963/lintrans/releases/download/v${latest_version}/lintrans-Linux-${latest_version}"

echo "The latest release is lintrans v${latest_version}"
echo

prefix="$HOME/.local/bin"
echo -n "Please enter an installation prefix (leave empty for ${prefix}): "
read prefix_input

if [ -n "$prefix_input" ]; then
	prefix="$prefix_input"
fi

filename="${prefix}/lintrans"

if [ -x "$filename" ]; then
	current_version="$($filename --version | \grep -Po '(?<=lintrans \(version )\d+\.\d+\.\d+(?=\))')"

	if [ "$current_version" = "$latest_version" ]; then
		echo
		echo "You've got the latest version of lintrans installed there already!"
		exit 0
	fi
fi

echo
echo "Now downloading the lintrans binary..."
wget -q --show-progress "$binary_url" -O lintrans-binary

mv lintrans-binary "$filename"
chmod +x "$filename"

echo
echo "Now downloading the icons..."
download_icons "$latest_version"

echo
echo "Now installing the XDG .desktop file..."
create_desktop_file "$filename"
xdg-desktop-menu install --mode user doctordalek1963-lintrans.desktop
rm -f doctordalek1963-lintrans.desktop

echo
echo "Thanks for installing lintrans!"
