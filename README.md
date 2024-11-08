# 🌐 ESP32 Telegram Monitoring Bot
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fmehrdadmb2%2FV2ray_Sub&count_bg=%2379C83D&title_bg=%23555555&icon=github.svg&icon_color=%23E7E7E7&title=Visitors&edge_flat=false)](https://github.com/mehrdadmb2/V2ray_Sub)
[![GitHub Stars](https://img.shields.io/github/stars/mehrdadmb2/V2ray_Sub?style=plastic&color=brightgreen&label=Stars)](https://github.com/mehrdadmb2/V2ray_Sub/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/mehrdadmb2/V2ray_Sub?style=plastic&color=blue&label=Forks)](https://github.com/mehrdadmb2/V2ray_Sub/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/mehrdadmb2/V2ray_Sub?style=plastic&color=orange&label=Issues)](https://github.com/mehrdadmb2/V2ray_Sub/issues)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/mehrdadmb2/V2ray_Sub?style=plastic&color=red&label=Last%20Commit)](https://github.com/mehrdadmb2/V2ray_Sub/commits/main)

[![Mehrdad's Database](https://img.shields.io/badge/Database-Custom%20IoT%20Data-%23121011?style=plastic&logo=database&logoColor=white)]()
![Database](https://img.shields.io/badge/Database-Custom%20owned%20data%20-%23121011?style=plastic&logo=database&logoColor=white) 
![Sensor](https://img.shields.io/badge/Sensor-DHT22-%23FFCC00?style=plastic&logo=sensor&logoColor=black) 
![Board](https://img.shields.io/badge/Board-ESP32-%2344CC11?style=plastic&logo=esp32&logoColor=white)

This Telegram bot is designed for monitoring and logging data from an ESP32 device. It allows you to retrieve real-time data like temperature and humidity, log it to Excel files, and analyze or view it through Telegram conveniently.

## ✨ Features

- 🔄 **Real-time Data Fetching**: Get live data from ESP32 instantly.
- 📊 **Excel Logging**: Automatically save data every minute in an Excel file for long-term analysis.
- 📈 **Dynamic Chart Generation**: Generate 24-hour temperature and humidity charts with the `/chart` command.
- 🔒 **Admin-only Features**: Options to download Excel files, view logs, and access specific user data.
- 🔄 **Robust Error Handling**: Ensures continuous data logging and reconnection in case of connection loss.
- ⚙️ **Automatic Library Installation**: Installs all required libraries on the first run.

---

## 🚀 Getting Started

### 🛠 Prerequisites

1. **ESP32**: Configured to send data like temperature and humidity.
2. **Python**: Python 3.7 or later installed.
3. **Telegram Bot API**: Set up a Telegram bot and get its token from the BotFather.
4. **Excel Logging**: `openpyxl` library for handling Excel files (automatically installed).

### ⚙️ Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/yourrepositoryname.git
    cd yourrepositoryname
    ```

2. Run the script to install required libraries:
    ```bash
    python main.py
    ```
   This step installs libraries such as `openpyxl`, `colorama`, and `telebot`.

3. Update the `config.json` file with your details:
   - **bot_token**: Telegram bot token.
   - **ESP32 URL**: URL to access ESP32 data (e.g., `http://mehrdadmb.duckdns.org`).

---

## 📲 How to Use

1. **Start the Bot**:
   ```bash
   python main.py
   ```

2. **Telegram Commands**:
   - **/start**: Initialize and start the bot.
   - **/data**: Display the current temperature and humidity.
   - **/chart**: Generate and send a 24-hour temperature and humidity chart.
   - **/logs** (admin only): Show recent logs.
   - **/download_logs** (admin only): Download Excel log files.
   - **/user_logs** (admin only): View logs for a specific user.

3. Only specified admins can access **Admin-only Features**.

---

### 🔧 Configuration

Update options in `config.json` as needed:
- **bot_token**: Telegram bot token.
- **ESP32 URL**: ESP32 data access URL.
- **Logging Settings**: Customize time intervals or data formats.

---

## 📝 Example Workflow

1. Add the bot to your Telegram chat.
2. Start the bot using `/start`.
3. Use `/data` to view real-time temperature and humidity.
4. Receive charts by sending `/chart`.
5. Admins can view recent logs with `/logs` or download Excel files with `/download_logs`.

---

## 🔧 Troubleshooting

- **Connection Issues**: Ensure the ESP32 device is online and accessible.
- **Error Handling**: The bot includes automatic checks to ensure continuous data logging and reconnection.
- **Access Control**: Only admins have access to specific commands like `/download_logs`.

---

## 📈 Future Enhancements

Proposed improvements:
- **Advanced Charts**: Add options for daily or weekly averages.
- **Additional Sensors**: Integrate more sensors with the ESP32.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 📄 requirements.txt

Create a file named `requirements.txt` and include the following dependencies:

```plaintext
openpyxl
telebot
colorama
requests
matplotlib
pandas
```

This setup prepares the project for GitHub. Let me know if you need additional help with the configuration!
