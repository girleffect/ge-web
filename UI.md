# GE Brands UI (Components based) templates

We need to find an optimal templating solution for GE brands pages in the current folder setup.


### Learning to take into consideration

Static template solution
* (Torchbox pattern components)[https://github.com/torchbox/wagtail-torchbox/tree/master/tbx/project_styleguide/templates/patterns]
* (Adding a React component in Wagtail Admin)[https://dev.to/lb/adding-a-react-component-in-wagtail-admin-3e]
#### What is the flow of these component structure?

- geweb templates base.html is the main page - which dynamically consumes different brand views. Or interpolate the brand view - which should tie in with the settings switch of the different brands ie. via a global variable for internationalized domain routing etc.
- the templates can be dynamic templates (bundled in javascript & css)  that serve the CMS interpolated streamfields 
- or the templates can be static django template language as it currently and broken down into smaller re-usable streamfield blocks with folder structure 
    - patterns (smallest re-usable markup & cms tags) - no logic 
    - pages (fullpage layout for each brand e.g. there's different layout for Springster, Ninyampinga etc.)
    - css/sass folder for different brands


### Assumptions 
- No javascript restrictions for Freebasics platform.