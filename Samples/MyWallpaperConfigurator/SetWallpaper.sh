#!/bin/zsh

_runAsUser() {
    local currentUser
    local uid

    currentUser=$( echo "show State:/Users/ConsoleUser" | scutil | awk '/Name :/ { print $3 }' )
    uid=$(id -u "${currentUser}")

	if [[ "${currentUser}" != "loginwindow" ]]; then
		launchctl asuser "$uid" sudo -u "${currentUser}" "$@"
	else
		echo "No user logged in, exiting..."
		exit 1
	fi
}

_runAsUser ./desktoppr "/Library/Desktop Pictures/Snow Leopard Server.jpg"