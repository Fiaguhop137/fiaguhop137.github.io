#!/bin/bash
set -e
sudo dnf update -y; sudo dnf install dnf5 -y; sudo dnf5 upgrade -y
sudo dnf5 install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm git gcc gcc-c++ make cmake python3 python3-pip curl wget htop fastfetch pv firefox tar 7z yt-dlp nodejs npm gnome-menus jq mpv ccache clang++ alacritty flite sl
mkdir -p /home/firebot/.config/alacritty
cp /home/firebot/Downloads/alacritty.toml /home/firebot/.config/alacritty/alacritty.toml
echo please log in and set up firefox
firefox
read -p "press enter to continue"
curl -fL -o /tmp/proton-drive https://proton.me/download/drive/cli/0.5.0/linux-x64/proton-drive
chmod 755 /tmp/proton-drive
sudo install -m 755 /tmp/proton-drive /usr/local/bin/proton-drive
rm -f /tmp/proton-drive
echo please log in
proton-drive auth login
read -p "press enter to continue"
proton-drive filesystem download -f replace -d replace /my-files/Backups /home/firebot/Downloads/
tar -xJf /home/firebot/Downloads/Backups/Downloads.tar.xz -C /home/firebot/
curl -fsSL https://ollama.com/install.sh | sh
flatpak install flathub org.prismlauncher.PrismLauncher -y
flatpak run org.prismlauncher.PrismLauncher
tar -xJf /home/firebot/Downloads/Backups/Minecraft.tar.xz -C /tmp
rm -rf /home/firebot/.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances
mv /tmp/Minecraft/instances /home/firebot/.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances
rm -rf /home/firebot/Downloads/Backups
git config --global alias.sync '!/home/firebot/Downloads/shell/git-sync.sh'
python3 -m pip install --break-system-packages discord.py cairosvg python-dotenv cryptography
git config --global user.name "Fiaguhop137"
git config --global user.email "eastonzou@gmail.com"
UUID_ARC="arcmenu@arcmenu.com"
VERSION_ARC=$(curl -s "https://extensions.gnome.org/extension-info/?pk=3628" | jq -r '.shell_version_map | to_entries | max_by(.value.version) | .value.version')
curl -fL "https://extensions.gnome.org/extension-data/${UUID_ARC}.v${VERSION_ARC}.shell-extension.zip" -o /tmp/arcmenu.zip
UUID_DASH="dash-to-panel@jderose9.github.com"
VERSION_DASH=$(curl -s "https://extensions.gnome.org/extension-info/?pk=1160" | jq -r '.shell_version_map | to_entries | max_by(.value.version) | .value.version')
curl -fL "https://extensions.gnome.org/extension-data/${UUID_DASH}.v${VERSION_DASH}.shell-extension.zip" -o /tmp/dash-to-panel.zip
gnome-extensions install --force /tmp/arcmenu.zip
gnome-extensions install --force /tmp/dash-to-panel.zip
test -f /home/firebot/.local/share/gnome-shell/extensions/arcmenu@arcmenu.com/metadata.json
test -f /home/firebot/.local/share/gnome-shell/extensions/dash-to-panel@jderose9.github.com/metadata.json
dconf load /org/gnome/shell/extensions/arcmenu/ < /home/firebot/Downloads/arc_menu_settings.conf
dconf load /org/gnome/shell/extensions/dash-to-panel/ < /home/firebot/Downloads/dash_to_panel_settings.conf
gnome-extensions enable arcmenu@arcmenu.com
gnome-extensions enable dash-to-panel@jderose9.github.com
gsettings set org.gnome.desktop.interface clock-format '24h'
gsettings set org.gnome.desktop.calendar week-start-day 1
gsettings set org.gnome.desktop.interface enterpriseswitch-applications-prevented 'true' 2>/dev/null || gsettings set org.gnome.desktop.wm.keybindings switch-applications "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-windows "['<Alt>Tab']"
read -p "press enter to reboot"
sync
sudo systemctl reboot
