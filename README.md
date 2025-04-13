# X Follower ID to Username Converter (X-ID2Username)

**Disclaimer Warning**: This script may breach X's Terms of Service contract that you agreed to when creating an account. It was made for educational & informational purposes.

A Python utility for automating the extraction of usernames from X (formerly Twitter) follower links containing user IDs. This tool instructs you how to convert the follower.js file provided from [X's Data Archive download](https://x.com/settings/download_your_data) into JSON, which contains all the user links but only consists of user IDs, and creates a clean list of all the usernames that the user IDs belong to.

**This script does NOT use the X API, as their free tier only allows fetching 1 user ID every 24 hours. It uses a (headless) web browser to get usernames from links that only contain

## Overview

The X ID2Username Converter is designed to process a JSON file containing links consisting of user IDs to X user profiles and extract the actual usernames from those links. It uses Selenium to visit each link, handle any redirects, and extract the username from the resulting page.

## Features

- **Automated Username Extraction**: Visits X user ID links and extracts usernames automatically
- **Real-time Saving**: Writes usernames to output file as they're discovered to preserve progress
- **Comprehensive Logging**: Detailed logs with timestamps for troubleshooting
- **Error Handling**: Tracks and saves failed URLs for manual review
- **Configurable**: Settings managed via YAML configuration file

## How It Works

The script operates through the following process:

1. **Configuration Loading**: Reads login credentials from a YAML file
2. **JSON Processing**: Extracts user links from follower.json (converted from follower.js, exported from [X Data Archive](https://x.com/settings/download_your_data))
3. **Browser Automation**: Uses Selenium to:
   - Log in to your X account
   - Visit each user link
   - Handle redirects
   - Extract the username from the final page
4. **Username Extraction**: Employs multiple methods to find usernames:
   - URL parameters (screen_name)
   - URL path analysis
   - Page content scanning (title, meta tags, DOM elements)
5. **Output Generation**: 
   - Saves extracted usernames to followers.txt in real-time
   - Records failed URLs in failed_urls.txt for manual review

## Requirements

- Python 3.6 or higher
- Chrome browser
- ChromeDriver (compatible with your Chrome version)
- Selenium
- PyYAML

## Installation

1. Clone this repository or download the script files
2. Install required Python packages:

```bash
pip install selenium pyyaml
```

3. Ensure ChromeDriver is installed and available in your PATH or in the same directory as the script

## Getting Your X Data Archive

Before running the tool, you need to download your X data archive:

1. Log in to your X account
2. Click on 'More' from the navigation bar
3. Go to 'Settings and Privacy' 
4. Select '[Your Account](https://x.com/settings/account)'
5. Click on '[Download an archive of your data](https://x.com/settings/download_your_data)'
6. Click 'Request archive'
7. Wait for X to process your request (this can take 24 hours or more)
8. Once ready, X will send an email with a download link

## Preparing Your Data

After downloading your X data archive:

1. Extract the .zip file contents
2. Navigate to the `data` folder in the extracted archive
3. Locate the `follower.js` file and copy it to inside this tool's directory (where `config.yml` and `main.py` is)
4. Convert `follower.js` to JSON format:
   - Open `follower.js` in a text editor
   - Remove the prefix `window.YTD.follower.part0 = ` from the first line (keeping the `[` bracket & everything after/below it)
   - Save the file as `follower.json` in the tool's directory

## Configuration

Copy or rename `config.yml.example` to `config.yml` in the same directory as the script with the following structure:

```yaml
x_credentials:
  username: "name_here"  # Your X login username
  password: "pass_here"  # Your X login password
  account_name: "name_here"  # Optional, only used for log identification
```

*Using a burner or alt account is recommended. Visiting thousands of profile links in a headless browser may trigger rate limits, verification prompts, or temporary freezes. If any, negative effects from this are unknown.*

## Required Files

- `main.py`: The main script
- `config.yml`: Configuration file with X credentials
- `follower.json`: JSON file containing follower information with userLinks

## Running the Script

1. Ensure you have the required files in place (main.py, config.yml, follower.json)
2. Run the script:

```bash
python main.py
```

## Output Files

- `followers.txt`: List of extracted usernames (one per line)
- `failed_urls.txt`: List of URLs where username extraction failed
- `follower_extractor_[timestamp].log`: Detailed log file

## Troubleshooting

If you encounter issues:

1. Check the log file for specific error messages
2. Verify your Chrome and ChromeDriver versions match
3. For login issues, try running in non-headless mode by changing `headless = False` in the `main()` function
4. Review failed_urls.txt to manually process URLs that couldn't be automatically processed, or use the `retry_failed_urls.py` script to try them again. [More info below](#retry-failed-urls)

## Common Issues

- **Login Failures:** X/Twitter frequently changes its login page structure. If login fails, the tool will save a screenshot named `login_error_[timestamp].png` which can help diagnose the issue.
- **Rate Limiting**: If X detects too many requests, try increasing the wait time between requests.
- **ChromeDriver Compatibility**: Ensure your ChromeDriver version matches your Chrome browser version.

## Technical Details

The script employs several techniques to efficiently extract usernames:

1. **Redirect Tracking**: Monitors URL changes to ensure it's working with the final destination (I.e. `twitter.com` to `x.com`)
2. **Multiple Extraction Methods**: Uses various techniques to extract usernames:
   - URL parameter parsing
   - URL path analysis
   - DOM content scanning
3. **Error Recovery**: Implements fallback mechanisms if primary extraction methods fail

## Retry Failed URLs

After running through a large number of profile links, the account may hit a temporary rate limit, causing it to fail at retrieving some usernames. This often requires logging into the account to trigger a prompt for email or phone verification due to unusual activity.

When this happens, the failed links are saved to a file called `failed_urls.txt`.

You can retry these links later using the `retry_failed_urls.py` script. This script processes the links in `failed_urls.txt`, adds any successfully resolved usernames to followers.txt (or creates it if not present), and moves any still-failing links to a new file, `failed_urls2.txt`. These secondary failures are likely due to another temporary rate limit.

If you notice that links are consistently failing while the script is running, stop it and log into the account to trigger the verification prompt. Then, in the console logs, look for the last successfully processed link. Open `failed_urls.txt`, find that link, and delete it along with any links above it. Save the file, delete `failed_urls2.txt`, and then run `retry_failed_urls.py` again.

## Contributing

Feel free to fork this project and submit pull requests.

## To Do
- After X failed URLs, stop the script and log a message indicating the account may be rate-limited or flagged for unusual activity. Inform the user that they may need to log into the account (sometimes in a new private/incognito browser window) to trigger email or phone verification. Add a config setting to define the number of allowed failed URLs, with `0` disabling this feature.
- For accounts with many thousands of followers, add logic to remove all the successful URLs in follower.json so it doesn't run through these again.

## License

This project is licensed under the [MIT License](LICENSE).

### Author
slapped together by [rich](https://richw.xyz)
