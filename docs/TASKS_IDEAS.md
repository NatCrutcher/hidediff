# Tasks and Ideas for hidediff
## General

- Brainstorm for a good name that is not already in use. I haven't checked, but it would not surprise me if hidediff is already being used.

- Create the equivalent of a sales brochure or a web home page, in markdown format,
  that pitches why someone would want to use this tool. Provide an overview of the major features and how this is better than existing tools.

- Create a CLAUDE.md file for this project. Keep it concise and refer to other files when appropriate.

  - Review and add CLAUDE_MD_TESTING_SECTION.md to CLAUDE.md.

- Set up a public GitHub repository for this project and link it to this development folder.

- Define the coding style, conventions, code comments, guidelines, documentation, architecture, workflow, tools, version control, static analysis, unit tests, system tests, performance tests, review stages, code simplifier, CI, etc. Define completion checklists for each phase and issue. Consider different checklists for different types of issues.

- Determine and document the open source licensing, probably some MIT open-source license.

## DESIGN.md and Feature Review

- In DESIGN.md, convert architecture diagram to Mermaid format.

- Review DESIGN.md and the development sequence to focus first on the more unique features and the ones posing the highest risk.

- Define a rubric for evaluating the Detailed Requirements in DESIGN.md. For non-trivial requirements, include a short analysis of the feasibility and risks.

- Human review of DESIGN.md.

- Review the features and requirements to see if we have overlooked any common, useful, or popular features from existing differencing tools. Consider which of these we might want to add to our own requirements.

- Consider how this architecture might enable other related enhancements, especially in domains outside of coding, and decide if we want to add any more features based on that analysis.

- Consider use cases for AI coding agents that might guide us to new features.

- Get AI reviews from Gemini and ChatGPT of the feature set and design.

- Create a comparison matrix with the most comparable existing diff tools, perhaps including paid tools. This could be a new Markdown document.

- Get human reviews from 2-4 people of the high-level features and architecture.

- Review my enhanced document notes to see if I come up with any other ideas that
  might be useful.

- Consider if the existing algorithms will meet all of our requirements. If not, try to develop new algorithms.

- Highly advanced feature: consider using AI to review the differences in conjunction with commit messages, the rest of the code base, and if needed, the prior history, to create a description that explains the change. Since this would be very computationally expensive and possibly slow, we would probably make it an on-demand feature for individual changes or defined sections.
