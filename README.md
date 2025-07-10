# 🔍 Port Scanner X

> 🎯 A powerful desktop application with a graphical interface for scanning ports on a target host.

![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## ✨ Features

- 🖱️ **Graphical Interface**: Intuitive UI for scanning and viewing port status
- 🚀 **Asynchronous Scanning**: Fast port scanning with adjustable concurrency
- 📊 **Detailed Results**: Displays port status, response time, and service descriptions
- 📋 **Export Options**: Save scan results in TXT and JSON formats
- ⚙️ **Customizable**: Configure ports, timeout, and simultaneous connections

---

## 🚀 Installation

### 📋 Requirements

- 🐍 Python 3.8+
- 🎨 Flet (GUI library)
- 🌐 asyncio (included in Python standard library)

### 📦 Install Dependencies

```bash
pip install flet
```

### ▶️ Run the Application

```bash
python main_gui.py
```

---

## 📖 Usage

1. **🚀 Launch the Application**
   ```bash
   python main_gui.py
   ```

2. **🔍 Enter Target Host**  
   Input an IP address (e.g., `192.168.1.1`) or domain (e.g., `google.com`) in the "IP-адрес или домен" field.

3. **📋 Specify Ports**  
   Enter ports to scan (e.g., `20-80,443,8080`) or use buttons for "Популярные порты" or "Все порты (1-65535)".

4. **⚙️ Adjust Settings**  
   - Set concurrency using the slider (50-1000 simultaneous connections).  
   - Set timeout in seconds (e.g., `1.0`).

5. **▶️ Start Scanning**  
   Click the "Сканировать" button to begin.

6. **📊 View Results**  
   Results appear in the table with port number, status (open/closed/timeout/error), response time, and service description.

7. **📦 Export Results**  
   Use "Сохранить TXT" or "Сохранить JSON" buttons to save the scan results.

---

## 📂 Project Structure

```
port-scanner-x/
├── 🔍 main_gui.py       # Graphical interface and main application logic
├── 🚀 scanner.py        # Asynchronous port scanning functionality
├── 🛠️ utils.py          # Utility functions for parsing and formatting
└── 📖 README.md         # This file
```

---

## 📦 Create an Executable File

To create a standalone `.exe` file, use PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main_gui.py
```

> 📁 The executable file will be created in the `dist/` folder.

---

## 🎯 Special Features

- 🚀 **Multithreaded Scanning**: Runs scans in a separate thread for a responsive UI
- 🛡️ **Host Validation**: Verifies IP addresses and domains before scanning
- 📊 **Interactive Table**: Color-coded results for easy analysis
- 🌙 **Theme Switching**: Toggle between light and dark modes
- 📦 **PyInstaller Support**: Compile into a single executable file

---

## 📄 License

This project is licensed under the **GPLv2**. See the `LICENSE` file for details.

---

## 🤝 Contributing

Pull requests are welcome! 🎉 For major changes, please open an issue first to discuss.

### 📝 How to Contribute:

1. 🍴 Fork the project
2. 🌿 Create a Feature Branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the Branch (`git push origin feature/amazing-feature`)
5. 🔁 Open a Pull Request

---

## 👨‍💻 Author

Created with ❤️ using Python and Flet.

---

<div align="center">

### 🌟 Star this project if you found it useful! 🌟

</div>