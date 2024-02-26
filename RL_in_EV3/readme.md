
This document explains what you need to do to run this project in your **Lego EV3**.

Tested with:
- **ev3dev-browser 0.8.1 + ev3dev-jessie** (older)
- **ev3dev-browser 1.1.0 and 1.2.1 + ev3dev-stretch**

To know which version of ev3dev you have, run this in the SSH console connected 
to the intelligent brick: `more /etc/ev3dev-release`.


## ROBOT SETUP

1. Download EV3dev stretch version and flash it to a SD card
   - Get ev3dev here: https://www.ev3dev.org/docs/getting-started/ 
   - A flash utility: https://rufus.ie/pt_BR/

1. Boot EV3 with the SD card and use a USB cable to connect EV3 to PC

1. Connect your EV3 to your PC with one of these options:

   1. **Bluetooth** (you need to follow these steps only in the first-time, probably):
      - Follow this: https://www.ev3dev.org/docs/tutorials/connecting-to-the-internet-via-bluetooth/
      - In step 7, check option "Connect automatically"

   2. **USB cable**:
      - Connect the USB cable from your PC to the EV3
      - On Windows, verifiy in the "Device Manager" (Windows 10) if your EV3 was recognized as "Remote NDIS Compatible Device"
         - Obs.: I don't use this option anymore. Maybe I forgot some initial steps to be done in the Windows/Linux. 
         - See http://www.ev3dev.org for more info.
      - Use the ev3dev menu shown through the brick display
      - Using the brick buttons, navigate to "Wireless and Networks" and click "ok" (center button)
      - Then choose "All Networks"
      - Noew choose "Wired"
      - Click in "Connect"
      - Await the IP address to appear
      - If anything goes wrong: try again; if nothing works, restart everything and try again.

1. No VS Code, faça estas configurações:

   - Instale a extensão "ev3dev-browser" mais nova. (Essencial).
   - (Opcional) Para melhor editar, instale o pacote no PC com estes comandos:

      ```
      > pip install python-ev3dev
      > pip install python-ev3dev2
      ```

1. Conectando no VS Code 
   - Clicar no "Explorer" (canto esquerdo, que oferece a visão dos arquivos do projeto)
   - Desça até o o painel com o nome da extensão "EV3DEV DEVICE BROWSER"
   - Escolha "Click here to connect to a device"
   - Escolher na lista, geralmente o nome é "ev3dev". Se a conexão for por bluetooth, você verá um comentário ao lado indicando.
   - Ao lado do nome "ev3dev" vai aparecer uma bolinha verde

   - **Se der certo**:
      - Você pode expandir o nome "eve3dev" e ver arquivos e informações
      - Clique com o botão direito e escolha "Open SSH Terminal"
      - Você pode usar comandos do linux

   - **Se *não* der certo**:
      - Tente reiniciar o windows
      - Confira se não desconectou, por alguma falha no cabo (sumiu o IP no topo da tela do EV3)

1. (**First-time only**) Para configurar a referência entre as pastas, faça isso apenas da 1a vez:
   - In "EV3DEV DEVICE BROWSER" click on the small button with (pop-up) caption "Send workspace to device" (top right of the panel)
     - this may be rather slow with Bluetooth connection
   - Right-click on "ev3dev" then choose "Open SSH Terminal"
   - Type
      ```
      > cd ~
      > chmod +x RL_in_EV3/setup_paths 
      > ./RL_in_EV3/setup_paths 
      ```

1. (**When needed**) At any moment, know that you are logged in ev3dev as the user indicated below. You will probably need
   this to run some commands that require "sudo" (super user).
   - login: "robot"
   - password: "maker"


## TO DOWNLOAD THE WHOLE PROJECT TO EV3

1. No painel EV3DEV DEVICE BROWSER do lado esquerdo, ao lado do nome "ev3dev", clique no botão "Send workspace to device"
   - The button to the left of the name "ev3dev" must be green -- the device must be connected!

2. Remember to do this whenever you change anything, if you run the files using options 2 and 3 (of the next section).

## TO RUN A PYTHON SCRIPT 
Use this, if you haven't changed since last donwload to EV3 or 
after changes made to "RL_in_EV3" folder only.

1. Before anything, remember to save the open files.

1. Hit Ctrl+F5 (on the desired open file in VS Code)
   - It will automatically download the whole project to the EV3, then run the file
   - The Python file must start with "#!/usr/bin/env python3"

1. If a problem (runtime error) occurs or if your are using ev3dev-jessie: 
   - First, download the latest version of the project
   - On the ev3dev-browser choose "Open SSH Terminal"
   - On the terminal, run this: 
      ```
      python3 <your-file.py>
      ```
1. You can also choose the desired file from ev3dev menu through the interface shown in the brick display
   - From the initial menu, choose "File Browser"
   - Navigate to the desired file
   - Press the "ok" (center) button in the brick


## TROUBLESHOOTING

### Problem in Ubuntu 18.04: Connection dropping

The PC would show "Ethernet connecting" and never show "Ethernet connected". I could use the connection, but it dropped after few minutes. I had to manually ask the PC to connect again.

I solved this by changing a few things - I don't know which one worked:
   - EV3: Wireless and Networks / All Network Connections / Wired / 
        Connect automatically - disable / IPV4 / Change / Load linux defauls (probably could set any config here)
   - PC: Settings / Network / you should see the option "USB Ethernet"
        IPV4 manual - in "Address" copy settings from EV3, let the other in Automatic /
        IPV6 disabled
   - Everytime you restart (PC or EV3): in EV3: go all the way to "Wired" menu, click "Connect"


### The ev3dev menu is frozen (in the intelligent brick display)

Abra o terminal SSH e envie este comando:
   ```
   sudo poweroff
   ```
ou
   ```
   sudo shutdown -h now
   ```
(Remember the user/password: 'robot/maker')
