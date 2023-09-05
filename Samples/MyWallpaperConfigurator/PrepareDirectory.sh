#!/bin/zsh

if [ ! -d "/Library/Desktop Pictures/" ]; then
    mkdir "/Library/Desktop Pictures/"
fi

if [ -f "/Library/Desktop Pictures/Snow Leopard Server.jpg" ]; then
    rm "/Library/Desktop Pictures/Snow Leopard Server.jpg"
fi