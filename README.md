![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![run-tests](https://github.com/swe-students-spring2026/4-containers-dream_team/actions/workflows/pytest.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-dream_team/actions/workflows/pytest.yml)

# FunnAI
A web-app that lets you record a joke, and then it will give you a score back on how funny it is. FunnAI stores all recorded jokes and will rank your joke based on how funny it is compared to other people.

## Contributors
- [Luca Andreani](https://github.com/Landreani04)
- [Aleks Nuzhnyi](https://github.com/nuzhny25)
- [Mikhail Bond](https://github.com/mikhailbond1)
- [Rohit Dayanand](https://github.com/RohitDayanand)
- [Lucas Bazoberry](https://github.com/lucasbazoberry)


## Setup & Configuration

To run this system, you need to configure your environment and initialize the database. Follow these steps:

1. Environment Variables

The application requires several environment variables to handle API integrations and server settings.

    1. Create a .env file in the root directory following the .env.example instructions.

    2. Copy the variables from .env.example

## Docker initialization

1. ```docker compose up —build```

2. Go to ```http://localhost:5000/```

3. Try recording and sending the audio!