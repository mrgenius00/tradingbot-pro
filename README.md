name: Build APK
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y build-essential git zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl libbz2-dev openjdk-17-jdk autoconf automake cmake unzip
          pip install --upgrade pip
          pip install buildozer cython==0.29.19
          sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
          pip install kivy kivymd pandas numpy ta requests
          pip install git+https://github.com/LBank-exchange/lbank-connector-python.git

      - name: Build APK
        run: |
          buildozer android debug

      - name: Upload APK
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: tradingbot-pro-apk
          path: bin/*.apk
