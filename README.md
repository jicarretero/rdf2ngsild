# RDF to NGSI-LD



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.aeros-project.eu/wp4/t4.2/rdf-to-ngsi-ld.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.aeros-project.eu/wp4/t4.2/rdf-to-ngsi-ld/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing(SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thank you to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README
Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
### Prerequisites
Python 3.10+ is required. Some programming constructs from Python 3.10 has been used in the project. At least Python 3.11 is recommended.

### Installation in our system, with virtual environment
Creating a Python Virtual Environment is quite recommendable `virtualenv ~/.venv/rdf2ngsild` and activating the virtual environment before doing anything with `source ~/.ven/rdf2ngsild/bin/activate`. Then we can proceed with installation:

```
git clone https://gitlab.aeros-project.eu/wp4/t4.2/rdf-to-ngsi-ld.git
cd rdf-to-ngsi-ld
pip install -r requirements.txt
```

### Docker installation
Docker installation will come in a few days.

## Usage
The main idea of the program  is reading data from a kafka topic and writing to on OrionLD, converting the Kafka input in RDF to NGSI-LD understood by OrionLD

```
python main.py --from-kafka --to-orionld
```

## Configuration file
This is an example of a configuration file
```
# Transformations to URN
[urn-transform]
## urn = std_urn_name - If this is the value, the id of the enties will be calculated from
##                      the URI value of RDF's file, something similar to this: 
##                      id = urn:xxx:typeentity:identity
urn = std_urn_name_no

[type-transform]
## urn = std_type_name - If this is the value, the type will be calculated removing anything
##                       before the last ":" character. It can be other things and the name
##                       will be left as URI.
urn = std_type_name


[kafka-client]
## Cofiguration for de Kafka reader. It will connect to a topic in a server
servers = localhost:19092
topic = rdf-topic

# Timeout of reader. -1 means infinte. 
reader_timeout = -1

[orionld]
### OrionLD basic URL to connect to when data is sent to OrionLD.
url = http://localhost:1026

[kafka-demo]
## This is for testing purposes. It is used with the --to-kafka parameter and it will
## say how many messages are going to be sent, and the waiting time between them.

## Max number of messages to be sent (<0 means infinity)
max_messages_sent = 100000

## thread.sleep between messages. It will send a message every... seconds
wait_between_messages = 10

```


### Testing purposes
For testing purposes, you could write some data to the Kafka topic where the application reads from, example:
```
python main.py --to-kafka-demo tests/examples/simple-sample-relationship.ttl tests/examples/containerlab-graph.nt
```


## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
