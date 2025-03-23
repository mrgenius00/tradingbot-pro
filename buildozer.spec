[app]
title = TradingBot Pro
package.name = tradingbotpro
package.domain = org.tradingbotpro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3, kivy, kivymd, pandas, numpy, ta, requests

# حذف لوگو
# android.icon = logo.png

android.permissions = INTERNET
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 0
# This is a test comment to trigger GitHub Actions
