---
name: Bug Report
about: Create a report to help us improve the email assistant system
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

# Bug Report

## Bug Description

**Summary:** A clear and concise description of what the bug is.

**Component(s) Affected:**
- [ ] `mail_client_api` - Mail client abstraction
- [ ] `gmail_client_impl` - Gmail client implementation
- [ ] Testing infrastructure
- [ ] CI/CD pipeline
- [ ] Documentation
- [ ] Authentication system

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Steps to Reproduce

1. 
2. 
3. 
4. 

**Minimal Reproducible Example:**
```python
# Provide the minimal code that reproduces the issue
from mail_client_api import get_client

client = get_client()
# ... rest of the code that causes the bug
```

## Environment Information

### System Environment
- **Operating System:** [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]
- **Python Version:** [e.g., 3.11.5]
- **UV Version:** [run `uv --version`]

### Project Environment
- **Branch:** [e.g., main, develop, feature-branch]
- **Last Working Commit:** [if known]
- **Dependencies:** [any recent dependency changes]

### Authentication Setup
- [ ] Using local credential files (`credentials.json`, `token.json`)
- [ ] Using environment variables
- [ ] Interactive authentication
- [ ] Non-interactive authentication
- [ ] No authentication required for this bug

## Error Details

### Error Messages
```
Paste the complete error message and stack trace here
```

### Log Output
```
Paste relevant log output here (remove sensitive information)
```

### CircleCI Build (if applicable)
- **Build Link:** [paste CircleCI build URL if relevant]
- **Failed Job:** [e.g., lint, test, integration]

## Impact Assessment

### Severity
- [ ] **Critical** - System is unusable, data loss, security vulnerability
- [ ] **High** - Major functionality broken, significant impact on users
- [ ] **Medium** - Feature partially broken, workaround available
- [ ] **Low** - Minor issue, cosmetic problem, edge case

### Frequency
- [ ] **Always** - Happens every time
- [ ] **Often** - Happens frequently (> 50% of the time)
- [ ] **Sometimes** - Happens occasionally (< 50% of the time)  
- [ ] **Rare** - Happens very rarely

### User Impact
- [ ] **Blocks development** - Cannot continue development work
- [ ] **Reduces productivity** - Slows down development significantly
- [ ] **Minor inconvenience** - Slightly annoying but manageable
- [ ] **No user impact** - Internal issue only

## Additional Context

### Workaround
If you found a way to work around this issue, please describe it:

### Related Issues
- Related to #(issue_number)
- Possibly caused by #(issue_number)

### Recent Changes
Did this issue start happening after any recent changes?
- [ ] After updating dependencies
- [ ] After code changes  
- [ ] After authentication changes
- [ ] After environment changes
- [ ] Issue was always present

## Testing Information

### Test Reproducibility
- [ ] Bug reproduces in unit tests
- [ ] Bug reproduces in integration tests
- [ ] Bug reproduces in end-to-end tests
- [ ] Bug only reproduces in manual testing
- [ ] Bug reproduces in CI/CD environment
- [ ] Bug only reproduces locally

### Test Commands That Fail
```bash
# List the specific test commands that demonstrate this bug
uv run pytest src/component/tests/test_specific.py::test_method -v
```

## Screenshots/Attachments

If applicable, add screenshots, configuration files, or other attachments to help explain the problem.

## Debugging Information

### What You've Tried
- [ ] Checked documentation
- [ ] Searched existing issues
- [ ] Tried different authentication methods
- [ ] Verified dependencies are up to date
- [ ] Checked CI/CD logs
- [ ] Reviewed recent commits

### Investigation Results
Describe any debugging steps you've taken and their results:

## Proposed Solution (Optional)

If you have ideas about what might be causing this issue or how to fix it:

### Root Cause Hypothesis


### Potential Fix


### Alternative Approaches


## Component Architecture Impact

### Interface Contracts
- [ ] This bug violates an abstract contract
- [ ] This bug affects dependency injection
- [ ] This bug breaks component boundaries
- [ ] This bug affects multiple components

### Backward Compatibility
- [ ] This is a regression from previous version
- [ ] This affects existing API contracts
- [ ] This requires breaking changes to fix

---

**Additional Notes:**
Add any other context about the problem here.

**Reporter Information:**
- **Experience Level:** [e.g., new to project, familiar with codebase, maintainer]
- **Availability for Follow-up:** [e.g., available for questions, limited availability]
