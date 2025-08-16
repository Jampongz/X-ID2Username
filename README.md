# X-ID2Username 🚀

![X-ID2Username](https://img.shields.io/badge/version-1.0.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Python](https://img.shields.io/badge/python-3.8%2B-yellow.svg)

## Overview

Welcome to the **X-ID2Username** repository! This project aims to simplify the process of converting user IDs from follower.js, a component of the X (formerly Twitter) data archive, into a list of usernames. With this tool, you can easily retrieve usernames for any user ID you have collected from your follower data.

### Why X-ID2Username?

When working with social media data, especially from X, you often end up with user IDs instead of usernames. This can make it challenging to analyze your follower base or understand your audience. X-ID2Username bridges that gap, allowing you to convert those IDs into meaningful usernames.

### Key Features

- **User-Friendly**: Designed for simplicity and ease of use.
- **Efficient**: Quickly converts a large number of IDs.
- **Headless Operation**: Uses Selenium for seamless operation without a visible browser.
- **Cross-Platform**: Works on any system that supports Python.

### Topics

This repository covers various topics, including:

- converter
- follower
- followers
- headless
- headless-browser
- id-to-username
- python
- selenium
- selenium-webdriver
- twitter
- twitter-data
- twitter-follower
- twitter-id
- x
- x-data
- x-follower
- x-follower-id
- x-twitter

## Getting Started

To get started with **X-ID2Username**, follow these simple steps:

### Prerequisites

Ensure you have the following installed on your machine:

- Python 3.8 or higher
- pip (Python package installer)
- Selenium library
- A compatible web driver (e.g., ChromeDriver for Google Chrome)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Jampongz/X-ID2Username.git
   ```

2. Navigate to the project directory:

   ```bash
   cd X-ID2Username
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Download the latest release from the [Releases section](https://github.com/Jampongz/X-ID2Username/releases). Make sure to execute the downloaded file.

2. Prepare a text file with user IDs, one ID per line.

3. Run the script:

   ```bash
   python main.py your_user_ids.txt
   ```

4. The output will be saved in a file named `usernames_output.txt`.

## Example

Here’s an example of how to use the tool:

1. Create a text file named `user_ids.txt`:

   ```
   123456789
   987654321
   555555555
   ```

2. Run the command:

   ```bash
   python main.py user_ids.txt
   ```

3. Check the `usernames_output.txt` for the results.

## Contributing

We welcome contributions to improve the **X-ID2Username** project. If you want to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature/YourFeature`).
6. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please check the [Releases section](https://github.com/Jampongz/X-ID2Username/releases) for updates and solutions. You can also open an issue in the repository.

## Acknowledgments

- Thanks to the Selenium team for their excellent web automation tools.
- Special thanks to the open-source community for their contributions and support.

## Contact

For any inquiries or feedback, feel free to reach out:

- Email: your_email@example.com
- Twitter: [@your_twitter_handle](https://twitter.com/your_twitter_handle)

---

Thank you for using **X-ID2Username**! We hope this tool makes your data analysis easier and more effective. Enjoy converting those IDs into usernames!