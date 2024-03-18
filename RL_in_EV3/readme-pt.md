
Este documento explica o que você precisa fazer para executar este projeto no seu **Lego EV3**.

Testado com:
- **ev3dev-browser 0.8.1 + ev3dev-jessie** (mais antigo)
- **ev3dev-browser 1.1.0 e 1.2.1 + ev3dev-stretch**

Para saber a versão do ev3dev que você tem, execute isso no console SSH conectado
ao bloco inteligente (*intelligent brick*): `more /etc/ev3dev-release`.


## CONFIGURAÇÃO DO ROBÔ

1. Baixe a versão EV3dev stretch e grave-a em um cartão SD
   - Obtenha o ev3dev aqui: https://www.ev3dev.org/docs/getting-started/ 
   - Uma ferramenta de gravação: https://rufus.ie/pt_BR/

1. Inicie o EV3 com o cartão SD e use um cabo USB para conectar o EV3 ao PC

1. Conecte seu EV3 ao seu PC com uma destas opções:

   1. **Bluetooth** (você precisa seguir estes passos apenas na primeira vez, provavelmente):
      - Siga isto: https://www.ev3dev.org/docs/tutorials/connecting-to-the-internet-via-bluetooth/
      - No passo 7, marque a opção "Conectar automaticamente"

   2. **Cabo USB**:
      - Conecte o cabo USB do seu PC ao EV3
      - No Windows, verifique no "Gerenciador de Dispositivos" (Windows 10) se seu EV3 foi reconhecido como "Dispositivo Compatível com NDIS Remoto"
         - Obs.: Não uso mais esta opção. Talvez eu tenha esquecido alguns passos iniciais a serem feitos no Windows/Linux.
         - Veja http://www.ev3dev.org para mais informações.
      - Use o menu ev3dev mostrado através do display do tijolo
      - Usando os botões do tijolo, navegue até "Wireless and Networks" e clique em "ok" (botão central)
      - Então escolha "All Networks"
      - Agora escolha "Wired"
      - Clique em "Connect"
      - Aguarde o endereço IP aparecer
      - Se algo der errado: tente novamente; se nada funcionar, reinicie tudo e tente novamente.

1. No VS Code, faça estas configurações:

   - Instale a extensão "ev3dev-browser" mais nova. 
   - (Opcional) Para facilitar o desenvolvimento, instale no PC os módulos de Python com estes comandos:

      ```
      > pip install python-ev3dev
      > pip install python-ev3dev2
      ```

1. Conectando pelo VS Code 
   - Clicar no "Explorer" (botão no canto esquerdo, que abre uma visão dos arquivos do projeto)
   - Desça até o o painel com o nome da extensão "EV3DEV DEVICE BROWSER"
   - Escolha "Click here to connect to a device"
   - Escolha seu dispositivo EV3 na lista. Geralmente o nome é "ev3dev". Se a conexão for por Bluetooth, você verá um comentário ao lado indicando.
   - Uma bolinha verde vai aparecer ao lado do nome "ev3dev", no "EV3DEV DEVICE BROWSER"

   - **Se der certo**:
      - Você pode expandir o nome "eve3dev" e ver arquivos e informações
      - Clique com o botão direito e escolha "Open SSH Terminal"
      - Você pode usar comandos do linux

   - **Se *não* der certo**:
      - Tente reiniciar o windows
      - Confira se não desconectou, por alguma falha no cabo (sumiu o IP no topo da tela do EV3)

1. (**Apenas na primeira vez**) Para configurar a referência entre as pastas, faça isso apenas da 1a vez:
   - Em "EV3DEV DEVICE BROWSER" clique no pequeno botão com a descrição (pop-up) "Send workspace to device" (canto superior direito do painel)
     - isso pode ser bastante lento com conexão Bluetooth
   - Clique com o botão direito em "ev3dev" e escolha "Abrir Terminal SSH"
   - Digite
      ```
      > cd ~
      > chmod +x RL_in_EV3/setup_paths 
      > ./RL_in_EV3/setup_paths 
      ```

1. (**Quando necessário**) A qualquer momento, saiba que você está logado no ev3dev como o usuário indicado abaixo. Você provavelmente precisará
   disso para executar alguns comandos que requerem "sudo" (super usuário).
   - login: "robot"
   - senha: "maker"


## PARA BAIXAR TODO O PROJETO PARA O EV3

1. No painel EV3DEV DEVICE BROWSER do lado esquerdo, ao lado do nome "ev3dev", clique no botão "Send workspace to device"
   - O botão à esquerda do nome "ev3dev" tem que estar verde -- ou seja, o dispositivo precisa estar conectado!
1. Lembre-se de fazer isso sempre que alterar alguma coisa, se você estiver executando os arquivos usando as opções descritas nos passos 3 e 4 da próxima seção.


## PARA EXECUTAR UM SCRIPT PYTHON

Use isso, se você não tiver alterado desde o último download para o EV3 ou
após alterações feitas apenas na pasta "RL_in_EV3".

1. Antes de tudo, lembre-se de salvar os arquivos abertos.

1. Pressione Ctrl+F5 (no arquivo aberto desejado no VS Code)
   - Isso fará o download automático de todo o projeto para o EV3 e, em seguida, executará o arquivo
   - O arquivo Python deve começar com "#!/usr/bin/env python3"

1. Se um problema (erro de execução) ocorrer ou se você estiver usando ev3dev-jessie:
   - Primeiro, faça o download da versão mais recente do projeto
   - No ev3dev-browser escolha "Abrir Terminal SSH"
   - No terminal, execute isto:
      ```
      python3 <seu-arquivo.py>
      ```
1. Você também pode escolher o arquivo desejado pelo menu ev3dev através da interface mostrada no display do tijolo
   - Do menu inicial, escolha "Navegador de Arquivos"
   - Navegue até o arquivo desejado
   - Pressione o botão "ok" (central) no tijolo


## SOLUÇÃO DE PROBLEMAS

### Problema no Ubuntu 18.04: Conexão caindo

O PC mostraria "Conectando Ethernet" e nunca mostraria "Ethernet conectada". Eu poderia usar a conexão, mas ela caía após alguns minutos. Eu tinha que pedir manualmente ao PC para conectar novamente.

Eu resolvi isso mudando algumas coisas - não sei qual delas funcionou:
   - EV3: Wireless and Networks / All Network Connections / Wired / 
        Conectar automaticamente - desabilitar / IPV4 / Mudar / Carregar padrões do linux (provavelmente poderia configurar qualquer configuração aqui)
   - PC: Configurações / Rede / você deveria ver a opção "Ethernet USB"
        IPV4 manual - em "Endereço" copie as configurações do EV3, deixe o outro em Automático /
        IPV6 desabilitado
   - Toda vez que você reiniciar (PC ou EV3): no EV3: vá até o menu "Wired", clique em "Conectar"


### Menu ev3dev congelado (no display do bloco inteligente)

Abra o terminal SSH e envie este comando:
   ```
   sudo poweroff
   ```
ou
   ```
   sudo shutdown -h now
   ```
(Lembre-se do usuário e senha: 'robot/maker')
