
## 🤖 ElectBot

---

### 📖 Table of Contents

1. [Introduction](#-introduction)
2. [Prerequisites](#-prerequisites)
3. [Setup Instructions](#-setup-instructions)
   - [Using Docker](#-using-docker)
   - [Without Docker](#-without-docker)
4. [Configuration](#-configuration)
5. [Contributing](#-contributing)
6. [License](#-license)
7. [Support](#-support)

### 🚀 Introduction

ElectBot is a Discord bot designed to facilitate elections within your Discord server. With a seamless integration with MariaDB, it offers a robust way to manage candidates and votes.

P.S : *As you can see, the bot has been customized for a particular use. But it will be fully customizable in future versions.*

### 🛠 Prerequisites

- **For Docker Use**:
  - Docker
  - Docker Compose
- **For Non-Docker Use**:
  - Python 3.x
  - MariaDB (or another compatible database)

### 🛎 Setup Instructions

#### 🐳 Using Docker:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Rename `config.yml.sample` to `config.yml` and update the placeholders (`<discord_token>`, `<guild_id>`, etc.) with your details.
4. Run the bot using:
   ```bash
   docker-compose up --build
   ```

#### 💻 Without Docker:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Rename `config.yml.sample` to `config.yml` and update the placeholders with your details.
4. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Install the required mariadb packages:
- `libmariadb3`
- `libmariadb-dev`

See the [official docs](https://mariadb.com/docs/skysql-previous-release/connect/programming-languages/c/install/) if you struggle.

6. Run the bot using:
   ```bash
   python3 electbot.py
   ```

### 🔧 Configuration

The bot's configuration is stored in `config.yml`. This file contains the following sections:

- **Discord**: Contains the bot token and guild ID.
- **Database**: Contains database connection details such as host, port, username, password, and database name.
- **Candidates**: A list of candidates for the election with their respective names and descriptions.

### 🌐 Contributing

If you wish to contribute to the bot's development, feel free to fork the repository, make your changes, and submit a pull request.

### 📜 License

[MIT License](LICENSE)

### 🤝 Support

For support, questions, or feedback, feel free to [contact me](mailto:0xsysr3ll@pm.me)

---
