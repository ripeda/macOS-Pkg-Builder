#!/bin/zsh --no-rcs

if [ ! -d "/Library/Desktop Pictures/" ]; then
    /bin/mkdir "/Library/Desktop Pictures/"
fi

if [ -f "/Library/Desktop Pictures/Snow Leopard Server.jpg" ]; then
    /bin/rm "/Library/Desktop Pictures/Snow Leopard Server.jpg"
fi