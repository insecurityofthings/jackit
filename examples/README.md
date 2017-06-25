# Example Scripts

These example ducky scripts can be used for testing, auditing, and general mayhem. Examples include:
- `nyan_troll_macos.txt` uses Command+Space to open Spotlight, opens a Terminal window, then types `open http://nyan.cat` to open up the Nyancat video and audio in a browser.
- `nyan_troll_windows.txt` is similar to the macOS version, but uses GUI+r to open the run dialog, then uses explorer to open up the nyan.cat site.
- `barbiegirl_troll_windows.txt` uses GUI+r again, but then loads a Powershell download cradle for `http://bit.ly/2t6LWej`, which points to the `barbiegirl.ps1` file in the repo. This is a troll from [Powershell Empire](https://www.powershellempire.com) that loads a browser payload in a background IE instance, and jacks the volume.
- `barbiegirl_troll_macos.txt` is similar to the example above, but executes `curl... | bash` on a macOS system instead. The bitly link points to the `barbiegirl.sh` file. We are so, so, so sorry.
