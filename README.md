# Discord Server Cloner

An application that allows you to easily clone a Discord server, including roles, categories, text channels, voice channels, and messages.

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

## Screenshot

![Application screenshot](screenshot.png)

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
![Main interface](https://github.com/user-attachments/assets/f69bc820-c85b-49c4-a52c-e97e3a9f265d)
![Settings panel](https://github.com/user-attachments/assets/41e00e89-24ab-4ea5-aae5-36d166d4f450)
![Cloning process](https://github.com/user-attachments/assets/ba883570-e996-466f-8511-02c1c88f5e9e)
