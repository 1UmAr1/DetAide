# Intelligent Document Drafting System with LangChain

## Overview

This repository contains the codebase and documentation for an intelligent document drafting system powered by LangChain and LangGraphs. The system leverages the capabilities of Large Language Models (LLMs) to create a flexible, modular, and reusable architecture for automating complex document drafting tasks.

## Key Features

- **Dynamic Configuration:** Real-time adjustments to settings and prompts, allowing seamless customization for various applications.
- **Modular Design:** Reusable and interchangeable components, promoting code reuse and maintainability.
- **Efficient Workflow Management:** Robust state graph management ensures efficient and dynamic task routing.
- **Comprehensive Tool Integration:** Integration of tools like web search, knowledge base search, and quality assurance to ensure accurate outputs.

## Folder Structure

- **Application:** FastAPI endpoints and related functionalities.
- **Configuration:** Configuration files and prompt templates for central management of settings.
- **Ingestion:** Scripts for ingesting documents into Elasticsearch to populate the knowledge base.
- **Source:** Main Python code files driving the core functionality of the system.
- **Template:** UI components for the service.


## Usage

1. **Ingestion:** Use the scripts in the `ingestion` folder to populate the knowledge base with relevant documents.
2. **Configuration:** Adjust settings and prompts in the `configuration` folder to customize the system for your specific use case.
3. **Endpoints:** Interact with the system via the FastAPI endpoints defined in the `application` folder.

## Contributing

We welcome contributions to enhance the functionality and features of this system. Please fork the repository, create a new branch, and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or inquiries, please contact [Umar Hajam](umerayoub54@gmail.com).

---

Feel free to customize the README further to suit your needs. Let me know if there are any specific details or sections you'd like to add.
