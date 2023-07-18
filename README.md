# Systèmes parallèles et distribués

Ubuntu version: [Ubuntu](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support#1-overview) 

Working with Visual Studio Code on Ubuntu: [Vscode in Ubuntu](https://ubuntu.com/tutorials/working-with-visual-studio-code-on-ubuntu-on-wsl2#1-overview)

Configuration [Git in vscode](https://code.visualstudio.com/docs/sourcecontrol/github)

## Commands for upload the repository in GitHub from vscode

```
git add *
git commit -m "Upload README"
git push
```
### Instalar librerias

Instalar las librerias de OPEN MPI (mpirun se utiliza para ejecutar programa MPI y mpicc se usa para compilar programas MPI en C (Make executable) y mpicxx compilar programas en C++)

```
sudo apt install openmpi-bin
sudo apt install libopenmpi-dev
```
