# Discord Server Cloner
![Github All Releases](https://img.shields.io/github/downloads/seregonwar/DiscordServerCloner/total.svg)


An application that allows you to easily clone a Discord server, including roles, categories, text channels, voice channels, and messages.


<img  src="https://github.com/seregonwar/DiscordServerCloner/blob/main/src/interface/assets/discord_logo.png" alt="R.E.P.O Save Editor logo" width="512">

## Features

- **Intuitive graphical interface**: Easy to use thanks to the modern user interface
- **Selective cloning**: Select exactly what you want to clone
  - Roles
  - Categories
  - Text channels
  - Voice channels
  - Messages (with customizable limit)
- **Multilingual**: Support for Italian and English
- **Customizable**: Light and dark themes


## Prerequisites

- Python 3.8 or higher
- Internet connection to download dependencies
- Valid Discord token with appropriate permissions

## Installation

### Option 1: Pre-compiled executable

1. Download the latest version from the [Releases](https://github.com/yourusername/DiscordServerCloner/releases) section
2. Extract the ZIP file
3. Run `Discord Server Cloner.exe`

### Option 2: From source code

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/DiscordServerCloner.git
   cd DiscordServerCloner
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## How to use

1. Start the application
2. Enter the source server ID you want to clone
3. Enter the destination server ID (must be an empty server)
4. Enter your Discord token
5. Select the elements you want to clone (roles, channels, etc.)
6. Click on "Start Cloning"
7. Wait for the process to complete

## Building the executable

To create a standalone executable:

1. Make sure you have PyInstaller installed:
   ```
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   python build.py
   ```

3. The executable file will be created in the `dist` folder and a ZIP archive containing the distribution will be created in the main directory.

## Troubleshooting

- **Authentication error**: Verify that the Discord token is valid and has the necessary permissions
- **Cloning error**: Make sure the source and destination servers exist and that you have the necessary permissions for both
- **"Same server" error**: The source and destination server IDs cannot be the same

## Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer


## GUI
![Main interface](https://github.com/user-attachments/assets/9a417fd9-cb31-4a1f-8ff1-be0a5dd6b352)
![Settings panel](https://github.com/user-attachments/assets/b6dd3177-e82f-4279-8d7a-7ba1d8e18cea)

