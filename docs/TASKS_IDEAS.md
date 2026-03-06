# Tasks and Ideas for HideDiff
## Quick Items

* Add comment change hiding.

## General

- Create the equivalent of a sales brochure or a web home page, in markdown format,
  that pitches why someone would want to use this tool. Provide an overview of the major features and how this is better than existing tools.

- Define consistent terminology for the two or three files being compared. I'm struggling with what to call the file on the left and the file on the right. Are these the source and the destination?. The original and the new?.

- Define the coding style, conventions, code comments, guidelines, documentation, architecture, workflow, tools, version control, static analysis, unit tests, system tests, performance tests, review stages, code simplifier, CI, etc. Define completion checklists for each phase and issue. Consider different checklists for different types of issues.

- Review the licensing options. Try to preserve the option to make a commercial version of this for special applications like comparing legal documents or regulatory documents.


## Claude Code Tasks

* Plan to use the /simplify action after any significant code changes.
* Research and ask Claude for guidance on whether we should create any custom new agents for this project.
* Research available skills. Add any applicable skills.
* Try the Claude Code /insights command.
* Review and refine the Claude Code permissions. Disallow certain unsafe things.

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

## Requirement Management

* Define a requirement review process.
* Migrate the detailed requirements into their own file or into GitHub issues. Ask CC for recommendations.
* For non-trivial requirements, document the risk and the research required. Plan to start by focusing on the items requiring more research and that are higher risk.

## Algorithms

* Document in more detail how we will detect renaming so that we can hide renames. This may require some understanding of programming language scope.
* Document in more detail how we will detect moves and copy pastes so that we can hide them and/or tag them clearly.
* Study the recommended algorithms. Look for other algorithms that may be useful.
  * Check the PMD CPD Copy-Paste Detector. They list three algorithms that they have used and I believe the source code is available.
* It occurred to me that we may want to develop a new algorithm or modify existing algorithms, so that we can categorize every difference as a particular type of change, i.e. a formatting change, a move, a copy-paste, or a rename.
