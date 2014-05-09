bridge-Bridgemate
=================
This project is developed based on Python and try to communicate with Bridgemate2.




Install on Windows
===================
- python27
- win32com python module
- wxpython python module
- pyinstaller python module
- Access 2010
- Bridgemate Controller Software (provide by bridgemate)
- BM2ServerDriver (provide by bridgemate)



How to use ?
============
python main.py [create/open] <PROJECT_NAME>


TODO
====
- bridgemate2manager.py, data process 
- scheduler.py, expand different kind of scheduler
  - RoundRobin alg.
  - Swiss alg, unknow
- WebUI ?
  - in one long page
  - Carousel at top
  - detail below
- QR code -> copy ?
- error handle of BCS, if can't open ?
- UI (http://zetcode.com/wxpython/)