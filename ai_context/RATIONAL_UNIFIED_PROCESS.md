## Rational Unified Process Phases

1. **Inception**
   - Define project scope, vision, and business case
   - Identify key requirements and risks
   - Estimate costs and schedule
2. **Elaboration**
   - Refine requirements and project architecture
   - Address high-risk elements
   - Create and validate the project plan
3. **Construction**
   - Design, implement, and test software components
   - Build the product incrementally
   - Ensure software meets quality standards
4. **Transition**
   - Deploy to users
   - Perform beta testing and feedback
   - Finalize documentation, training, and support

## Core Activities (Disciplines, Continuous throughout phases)

- **Business Modeling:** Analyze business context and processes
- **Requirements:** Gather, document, and manage requirements
- **Analysis & Design:** Create the system architecture and detailed designs
- **Implementation:** Write code and integrate components
- **Testing:** Verify and validate developed software
- **Deployment:** Package and distribute the product
- **Configuration & Change Management:** Track changes and manage versions
- **Project Management:** Plan, monitor, and control the project
- **Environment:** Set up tools and processes

## Key Technical Steps of the Elaboration Phase

### 1. Analyze and Refine Requirements

- **Requirement Workshops:**
  - Conduct structured workshops/interviews with stakeholders to clarify and refine all requirements from Inception.
- **Review & Update Use Cases:**
  - Detail primary and secondary use cases.
  - Write flows: basic (happy path), alternative, exception.
  - Attach non-functional requirements (performance, security, scalability) to relevant use cases.
- **Prioritize Requirements:**
  - Use tools like MoSCoW (Must, Should, Could, Won't).
  - Map requirements against risk and architectural significance.

**Artifacts:**
Updated Use-Case Model, Glossary, Supplementary Requirements Document.

### 2. Create or Refine the Software Architecture

- **Architectural Analysis:**
  - Identify key architectural drivers (performance, security, etc.).
- **Select Architecture Patterns:**
  - Choose suitable patterns (MVC, layered, microservices, event-driven, etc.).
- **Define Logical/Physical Views:**
  - Logical view: key classes, components, interactions (UML class diagrams, sequence diagrams).
  - Physical view: deployment diagrams, network architecture, 3rd-party integrations.
- **Executable Architecture Prototype:**
  - Implement “walking skeleton” or prototype of high-risk/critical parts (e.g., core transaction path, data access, authentication module).
  - Ensure end-to-end data and control flows work in principle, even if “stubbed out.”
- **Architectural Decisions Log:**
  - Document all key decisions and their rationale.

**Artifacts:**
Software Architecture Document (SAD), UML diagrams, architectural prototypes.

### 3. Identify and Resolve Technical Risks

- **Technical Risk Assessment:**
  - Explicitly identify the major project risks (new technology, performance limits, legacy integration, etc.).
- **Risk Resolution Prototypes (“Spikes”):**
  - Build minimal, targeted prototypes to validate technological approaches (e.g., database throughput, message queue scalability).
  - Document findings and next steps.

**Artifacts:**
Risk List, Spike Code (throw-away or basis for production).

### 4. Develop Refined Project Plans

- **Iteration Planning:**
  - Break down remaining work into iterations (typically 2-6 weeks).
  - Assign use cases and features to iterations based on architectural priority and risk.
- **Resource Assignment:**
  - Allocate developers, QA, analysts, etc., to features and iterations.
- **Milestone Criteria:**
  - Define measurable exit criteria for the phase (e.g., “90% of priority use cases architected and prototyped”).

**Artifacts:** Updated Project Plan, Iteration Plans, Work Assignments.

### 5. Update Environment and Tools

- **Tool Selection & Setup:**
  - Ensure CI/CD system, requirement tracking tool (e.g., Jira, DOORS), and modeling software (e.g., Rational Rose, Enterprise Architect) are ready.
- **Establish Development Standards:**
  - Set code style, branching and merging policies, and documentation templates.
- **Build and Test Infrastructure:**
  - Install code analysis tools, test automation frameworks, etc.

**Artifacts:**
Updated ENV Checklist, Standards Document, configured tools.

## How This Differs from “Vibe-Coding”

Rational Unified Process’s elaboration phase leaves little to chance:

- All architectural choices are justified and documented.
- Coding—even for prototypes—is deliberate and addresses known risks, not just building features for their own sake.
- Uncertainties are identified and aggressively reduced through analysis or prototype “spikes.”
- Everything results in an artifact: a spec, a diagram, a stub, or a working prototype.

**Summary Table:**

| Activity                  | Main Outputs                                  |
| ------------------------- | --------------------------------------------- |
| Requirement Analysis      | Refined use-cases, NFRs, Priority matrix      |
| Architecture Definition   | SAD, UML diagrams, Prototype/WaIking Skeleton |
| Technical Risk Mitigation | Risk list, Spike code, Reports                |
| Planning                  | Iteration plan, Resource plan, Exit criteria  |
| Environment/Tools         | Standards doc, CI setup, Tool checklist       |

## Key Technical Steps of the Construction Phase

### 1. Detailed Design & Implementation

- **Refine Detailed Design**

  - For each use case/component scheduled for this iteration, expand class diagrams, sequence diagrams, and state charts as needed.
  - Specify interfaces, algorithms, data models, and component interactions to an implementable level.
  - Review designs—peer reviews or architecture board approval.

- **Code Development**
  - Implement software incrementally, focusing on one use case or feature at a time.
  - Strictly follow coding standards, architectural constraints, and defined interfaces.
  - Write accompanying unit tests for each component/class using established frameworks.
  - Regularly commit code to version control, following branch/merge policies.

**Artifacts:** Updated UML diagrams, source code, unit tests, code review reports.

---

❯ Help me understand the specific technical steps for "1. Detailed Design and Implementation"

✨ Absolutely—let’s get as concrete as possible about **“Detailed Design and Implementation”** in the Rational Unified Process Construction phase. Here are the **specific, technical steps** teams follow, with focus on what actually happens at the keyboard and in documents:

## 1. Detailed Design & Implementation — Technical Steps

### **A. Review and Refine Detailed Design**

1. **Update UML Diagrams**
   - Refine/expand relevant **class diagrams** for objects implementing the use cases.
   - Create or update **sequence diagrams** for key workflows—showing object interactions, method calls, and control flow for each scenario.
   - Specify **state diagrams** for complex objects with different modes or states.
   - Add attributes, methods, relationships, visibility, and design patterns to diagrams.
2. **Specify Interfaces and Algorithms**
   - Write **detailed interface definitions** (e.g., Java interfaces, Python abstract base classes) for major modules/components.
   - Define method signatures, parameters, expected returns, and error handling.
   - Outline critical algorithms in **pseudo-code** or detailed flowcharts where necessary.
3. **Document Design Decisions**
   - For each component or subsystem, document why approaches or patterns (e.g., Singleton, Factory, Observer) were chosen.
   - Update the **Software Architecture Document** or maintain a “Design Decision Log.”
4. **Design Reviews**
   - Hold peer or architecture board reviews for these diagrams and specifications to ensure design intent and alignment with architecture.
   - Capture action items and update docs as needed.
