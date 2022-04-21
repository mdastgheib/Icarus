<div id="top"></div>
<!-- PROJECT SHIELDS -->

[![Forks][forks-shield]][forks-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/mdastgheib/Icarus-Discord-Bot/">
    <img src="images/logo.png" alt="Logo" width="100" height="100">
  </a>

<h3 align="center">Icarus Bot</h3>

  <p align="center">
    Icarus is a python based Discord chat bot that has multiple capabilities. The main intention was to gather real-time stock and crypto data such as pricing, charts, and cashflows. This bot is a work in progress with further optimization and features planned.
    <br />
    <a href="https://github.com/mdastgheib/Icarus-Discord-Bot"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/mdastgheib/Icarus-Discord-Bot">View Demo</a>
    ·
    <a href="https://github.com/mdastgheib/Icarus-Discord-Bot/issues">Report Bug</a>
    ·
    <a href="https://github.com/mdastgheib/Icarus-Discord-Bot/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


[![!sPrice Command][stockPrice-screenshot]]
[![!cPrice Command][cryptoPrice-screenshot]]
[![!cashflow Command][cashflow-screenshot]]
Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `github_username`, `repo_name`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description`

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [Python](https://www.python.org/)
* [AlphaVantage](https://www.alphavantage.co/)
* [CoinMarketCap](https://coinmarketcap.com/api/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is a simple python program installation. See the requirements needed in requirements.txt.
Run the program with python3 bot.py. Ensure that all proper libraries are installed in the respective directory.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* pip3
  ```sh
  pip3 install matplotlib
  pip3 install <example here>
  ```

### Installation

1. Get your free API keys from the links above, and store them in a config.json file
2. Clone the repo
   ```sh
   git clone https://github.com/mdastgheib/Icarus-Discord-Bot.git
   ```
3. Install Python packages
   ```sh
   pip3 install matplotlib
   pip3 install numpy
   pip3 install youtubedl
   etc..
   ```
4. Create a file named config.json and enter the following information in `config.json`
   ```json
   "discord_token": "token here",
   "coinmarketcap_api_key": "api key here",
   "alpha_vantage_api_key": "api key here",
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Reminder System for user reminders
- [ ] Currency Conversion with defined values (USD -> CAD 100)
- [ ] (Possible) Video Streaming Feature
    - [ ] Requires a secondary discord account. May or may not complete.

See the [open issues](https://github.com/mdastgheib/Icarus-Discord-Bot/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. 
You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Moses Dast - www.mdast.me - moses@mdast.me

Project Link: [https://github.com/mdastgheib/Icarus-Discord-Bot/](https://github.com/mdastgheib/Icarus-Discord-Bot/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS 
## Acknowledgments

* []()
* []()
* []()
-->

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/mdastgheib/Icarus-Discord-Bot/
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/mdastgheib/Icarus-Discord-Bot/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/mdast
[help-screenshot]: images/help.png
[cashflow-screenshot]: images/cashflow.png
[stockPrice-screenshot]: images/stockPrice.png
[cryptoPrice-screenshot]: images/cryptoPrice.png
[gas-screenshot]: images/gas.png
[poll-screenshot]: images/poll.png

