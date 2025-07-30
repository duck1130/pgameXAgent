@echo off
echo 🎮 啟動 Survival Realm - 生存領域
echo.
echo 檢查 Python 環境...
python --version
echo.
echo 檢查 Pygame...
python -c "import pygame; print(f'Pygame 版本: {pygame.version.ver}')"
echo.
echo 🚀 啟動遊戲...
python main.py
echo.
echo 遊戲已結束，按任意鍵退出...
pause > nul
