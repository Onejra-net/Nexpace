## Important Notice - Open-Source Version

# Nexpace

Nexpace is an open-source desktop application built with **Python** and **PySide6**.

The goal of Nexpace is to provide a single desktop workspace for working with web-based AI services, notes, PDFs, custom links, and other useful tools without having to manage multiple separate applications.

## Features

- AI and web service tabs
- Integrated web browser
- PDF viewer
- Notes editor
- Custom links
- Dock and tab management
- Workspace persistence
- Multilingual interface
- Embedded web content powered by Qt WebEngine

## Technology

Nexpace is built using:

- **Python**
- **PySide6 / Qt**
- **Qt WebEngine**
- **PyPDF**

## Getting Started

### Requirements

- Python 3.x
- PySide6
- PyPDF
- Qt WebEngine

### Running the application

Clone the repository and install the required dependencies.

Then run:

```bash
debug.bat
```

The application will create the main Nexpace window and start the Qt event loop.

## Project Structure

The main application entry point is:

```text
main.py
```

The application is organized into separate modules responsible for:

- application and window management
- browser and AI services
- PDF viewing
- notes
- custom links
- localization
- Qt WebEngine functionality

More detailed architectural documentation is provided separately in the project.

# License

Nexpace is **open-source software**.

The source code may be:

- used,
- studied,
- modified,
- adapted,
- redistributed,
- and used to create derivative versions.

### Attribution Requirement

Any modified, adapted, or redistributed version of Nexpace must clearly state that the source code originates from the **Nexpace** project.

The original author must also be credited.

The attribution must remain clearly visible in the README, documentation, or another appropriate location.

For example:

> Based on the open-source Nexpace project.  
> Original author: Damian Kujawski 
> Company: Onejra

Modified versions may be distributed under a different name, provided that the origin of the original source code remains clearly identified.

### Full License

The complete license terms are available in the [`LICENSE`](LICENSE) file.

## Author

**Damian Kujawski**

Original project: **Nexpace**
