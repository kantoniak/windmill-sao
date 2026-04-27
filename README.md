# Windmill SAO

Dutch [tower mill](https://en.wikipedia.org/wiki/Tower_mill) in a [SAO (Simple Add-on/Shitty Add-on)](https://hackaday.io/project/52950-shitty-add-ons/log/159806-introducing-the-shitty-add-on-v169bis-standard) form factor.

## Development

### Windows

1. Add FreeCAD's `bin/` directory to `PATH`. Usually `C:\Program Files\FreeCAD 1.0\bin\`
2. Generate the model:

    ```powershell
    cd enclosure/
    freecadcmd model.py
    ```

### Linux
```bash
# Install FreeCAD
sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
sudo apt update
sudo apt install freecad
```

## LICENSE

This project is licensed under the `CERN-OHL-S-2.0` license - see the [LICENSE](LICENSE) file for details.
