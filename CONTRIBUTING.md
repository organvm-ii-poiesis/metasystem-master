# Contributing to metasystem-master

Thank you for your interest in contributing to this project.

## Overview

Metasystem Master is a digital temple and multimedia art platform combining interactive web experiences, generative visuals, and audio synthesis. It serves as the creative flagship of the organvm art organ.

**Stack:** Node.js / HTML / CSS / JavaScript (digital temple, multimedia art)

## Prerequisites

- Git
- Node.js 20+ and npm
- A GitHub account

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/metasystem-master.git
cd metasystem-master

# Install dependencies
npm install

# Start development server
npm run dev
```

## How to Contribute

### Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Use the provided issue templates when available
- Include clear reproduction steps for bugs
- For documentation issues, specify which file and section

### Making Changes

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create a branch** for your change:
   ```bash
   git checkout -b feat/your-feature-name
   ```
4. **Make your changes** following the code style guidelines below
5. **Test** your changes:
   ```bash
   npm test
   ```
6. **Commit** with a clear, imperative-mood message:
   ```bash
   git commit -m "add validation for edge case in parser"
   ```
7. **Push** your branch and open a Pull Request

### Code Style

Use `const` over `let`; avoid `var`. Keep JavaScript readable and well-commented. CSS follows BEM naming where applicable. HTML should be semantic and accessible.

### Commit Messages

- Use imperative mood: "add feature" not "added feature"
- Keep the title under 72 characters
- Reference issue numbers when applicable: "fix auth bug (#42)"
- Keep commits atomic and focused on a single change

## Pull Request Process

1. Fill out the PR template with a description of your changes
2. Reference any related issues
3. Ensure all CI checks pass
4. Request review from a maintainer
5. Address review feedback promptly

PRs should be focused — one feature or fix per PR. Large changes should be
discussed in an issue first.

## Code of Conduct

Be respectful, constructive, and honest. This project is part of the
[organvm system](https://github.com/organvm-ii-poiesis), which values transparency
and building in public. We follow the
[Contributor Covenant](https://www.contributor-covenant.org/).

## Questions?

Open an issue on this repository or start a discussion if discussions are
enabled. For system-wide questions, see
[orchestration-start-here](https://github.com/organvm-iv-taxis/orchestration-start-here).
