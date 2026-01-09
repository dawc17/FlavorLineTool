# FlavorLineTool

FlavorLineTool is a command-line interface application designed for interacting with the Flavortown API and tracking coding statistics via Hackatime. It allows users to manage their cookies, projects, view shop items, check coding time, and search the ecosystem.

## Features

- **Project Management**: Create and edit projects with a guided interactive TUI form.
- **Enhanced Search**: Server-side searching for users and projects.
- **Cookie Management**: View your current cookie balance and stats.
- **Shop Interaction**: List all available items in the Flavortown shop.
- **Time Tracking**: Integrate with Hackatime to track daily coding time and project statistics.

## Installation

FlavorLineTool can be installed using pip from your local directory or via PyPI.

```bash
pip install flavorlinetool
```

## Usage

FlavorLineTool is built with a nested command structure. Running any command without arguments will show its available sub-commands.

### Authentication

Configure your credentials. If you omit the key/ID, the tool will prompt you interactively.

- **Login to Flavortown API**:
  ```bash
  flavor login api
  ```
- **Set Flavortown User ID**:
  ```bash
  flavor login id
  ```
- **Login to Hackatime**:
  ```bash
  flavor login hackatime
  ```
- **Set Hackatime Username**:
  ```bash
  flavor login hackatimeuser
  ```

### Projects (Interactive TUI)

Manage your Flavortown projects using a user-friendly interactive form.

- **Create a Project**:
  ```bash
  flavor projects create
  ```
- **Edit a Project**:
  ```bash
  flavor projects edit <project_id>
  ```
- **View Project Details**:
  ```bash
  flavor projects view <project_id>
  ```

### Search

Search the Flavortown ecosystem using server-side filtering.

- **Search Users**:
  ```bash
  flavor search users "query"
  ```
- **Search Projects**:
  ```bash
  flavor search projects "query"
  ```

### Listing Resources

Explore Flavortown resources.

- **Shop**: ``flavor list shop``
- **Users**: ``flavor list users --page 1``
- **My Projects**: ``flavor list my-projects``

### Stats & Time

- **Global Stats**: ``flavor stats`` (Combines Flavortown and Hackatime data)
- **Today coding time**: ``flavor time today``
- **Check Status**: ``flavor status``

## License

This project is licensed under the MIT License.
