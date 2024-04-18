#!/bin/zsh --no-rcs

_runAsUser() {
    local currentUser
    local uid

    currentUser=$( echo "show State:/Users/ConsoleUser" | /usr/sbin/scutil | /usr/bin/awk '/Name :/ { print $3 }' )
    uid=$(/usr/bin/id -u "${currentUser}")

	if [[ "${currentUser}" != "loginwindow" ]]; then
		/bin/launchctl asuser "$uid" sudo -u "${currentUser}" "$@"
	else
		echo "No user logged in, exiting..."
		exit 1
	fi
}

_runAsUser ./desktoppr "/Library/Desktop Pictures/Snow Leopard Server.jpg"