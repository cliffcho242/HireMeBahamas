# Notification Sounds

This directory contains notification sounds for the HireMeBahamas messaging system.

## notification.mp3

A short "ding" notification sound that plays when a new message is received.

If this file is missing, the app will fall back to using the Web Audio API to generate a beep sound.

## Adding a Custom Sound

To add a custom notification sound:
1. Place an MP3 file named `notification.mp3` in this directory
2. Keep the file size small (< 50KB recommended)
3. Duration should be 0.1-0.5 seconds for best user experience
