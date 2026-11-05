# Controls / map / targeting status (phone+pad worker)
- 23:10 CDT: Settings list updated (A jump/wallride/grind pop). Legacy #skmini minimap now skips drawing when MINIMAP_V2 (other worker) is active; tests/phone.py minimap checks adapt to MM2. Rebuilt OK.
- 23:22: phone.py crashed at legacy #skmini check (absent under MINIMAP_V2); test fixed, rerunning.
