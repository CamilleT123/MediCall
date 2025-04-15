# Hackathon Doctolib 

Welcome to the **Hackathon Doctolib** project! This project was developed as part of a hackathon and is based on the use of **Large Language Models (LLMs)** to enhance the user experience in the healthcare sector.

## Prerequisites

Before getting started, make sure you have the following tools installed on your machine:

- [Make](https://www.gnu.org/software/make/)
- Python 3.8+

## Installation and Execution

To build and run the project, use the following commands:

```sh
make
make backend-local
```

### LLM Configuration

The project uses an AI model based on a **LLM (Large Language Model)**. To properly run the backend, you need to provide an **OpenAI API key** in a `.env` file located at the root of the `backend` folder.

#### Example of `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
```


## Project Structure

- `backend/` : Contains the backend code of the project.
- `frontend/` : Contains the frontend code (if applicable).
- `Makefile` : Contains commands to build and run the project.



