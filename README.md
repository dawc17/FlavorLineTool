# FlavorLineTool

FlavorLineTool is a command-line interface application designed for interacting with the Flavortown API and tracking coding statistics via Hackatime. It allows users to manage their cookies, view shop items, check coding time, and search for users.

## Features

- **Cookie Management**: View your current cookie balance and stats.
- **Shop Interaction**: List all available items in the Flavortown shop.
- **Time Tracking**: Integrate with Hackatime to track daily coding time and project statistics.
- **User Search**: Search for other users on the platform.
- **Authentication**: Secure login management for both Flavortown and Hackatime services.

## Installation

FlavorLineTool can be installed using pip.

```bash
pip install flavorlinetool
```

## Usage

The application provides several command groups for different functionalities.

### Authentication

Before using most features, you must configure your credentials.

- **Login to Flavortown API**:

  ```bash
  flavor login api <your_api_key>
  ```

  Note: The API key must start with `ft_sk_`.

- **Set Flavortown User ID**:

  ```bash
  flavor login id <your_user_id>
  ```

- **Login to Hackatime**:

  ```bash
  flavor login hackatime <your_hackatime_key>
  ```

- **Set Hackatime Username**:
  ```bash
  flavor login hackatimeuser <username>
  ```

### Cookies

View your current cookie stash and user statistics.

```bash
flavor cookies show
```

### Listing Resources

List available resources from Flavortown.

- **List Shop Items**:
  ```bash
  flavor list shop
  ```

### Time Tracking

Access your Hackatime statistics.

```bash
flavor time
```

### Other Commands

- **Check Status**: Verify the tool is operational.

  ```bash
  flavor status
  ```

- **Search**: Search for specific resources.
  ```bash
  flavor search
  ```

## License

This project is licensed under the MIT License.
