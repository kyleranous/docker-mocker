# Docker Mocker

## Description
Docker Mocker is python package that spoofs the docker SDK for unit testing. *Note, this project is not associate with Docker, Inc.*


## Installation
Clone repository and copy into project
Install docker package (if not already installed), `MockDocker` will pass the expected docker errors to test exception handling.
Import MockDocker into unit tests `from mock_docker import MockDocker`


# Project Status
<!---
Emoji Codes for Project Status
:red_circle: Not Started
:large_orange_diamond: Development In-Progress
:large_blue_diamond: Testing
:heavy_check_mark: Complete
--->
| Module | Status |
| :--- | :--- |
| Client | :large_orange_diamond: Development In-Progress |
| Configs | :red_circle: Not Started |
| Containers | :red_circle: Not Started |
| Images | :red_circle: Not Started |
| Networks | :red_circle: Not Started |
| Nodes | :large_blue_diamond: Testing |
| Plugins | :red_circle: Not Started |
| Secrets | :red_circle: Not Started |
| Services | :red_circle: Not Started |
| Swarm | :large_blue_diamond: Testing |
| Volumes | :red_circle: Not Started |

## Usage



## How to Contribute

### Bug Reports / Feature Requests / General Issues
Anyone can submit a Bug Report or Feature Request. Please use the template when submitting
- When submitting a Bug Report please include code snippet of what is failing, What expected behavior is, and what is happening. You may be asked for a copy of your client definition json to assist in troubleshooting.

- When submitting a feature request provide details of the request, why the feature is being requested, and links to relelvent Docker (official) documentation. Please Note, database based branch is being left up for reference and is not being activly developed or maintained by me.

### Submitting Code Changes
If you want to submit a code change
1. Fork the project
1. Make your updates to the code
1. Add Comprehensive Unit Tests and ensure **ALL** tests pass
1. Add / Update all relevent documentation in the branch. PR will be denied if unit tests or documentation are missing. 
1. Submit a PR with your changes to the `development` branch
1. In the PR, provide a description of what was changed/added, why it was changed/added, and what tests were added. Link to relevent Issues. If any unit tests were edited or removed, provide an explenation.
1. If PR is excepted, your username will be added to the contributers list with a link to your profile, unless you request otherwise. 

## Contributers
Just me for now