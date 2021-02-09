# AD9174 demo project

# Install
  First install litex according to:
  https://github.com/enjoy-digital/litex#quick-start-guide

  Then replace the jesd204b/ library with my forked version

  ```bash
  cd litejesd204b/
  git remote add fork https://github.com/yetifrisstlama/litejesd204b.git
  git checkout fork/master
  ```

# Clocking setup
![clocking](docs/dac_clocking.png)

# See also
  * [Spreadsheet](https://docs.google.com/spreadsheets/d/1F6s6cVM1Lo6IOUgZoq9xm0ueGYkePZFeD96N0-kPR9o/edit#gid=0) with supported JESD modes and clock rates for AD9174
