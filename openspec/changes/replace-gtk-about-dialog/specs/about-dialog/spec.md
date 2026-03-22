## ADDED Requirements

### Requirement: About dialog displays application info
The custom about dialog SHALL display the same information as the previous GTK AboutDialog: program name, version, comments, copyright, authors, website, and license.

#### Scenario: Dialog displays program information
- **WHEN** user selects Help > About
- **THEN** a modal dialog appears with program name "HM Simulator", version, and description

#### Scenario: Dialog shows copyright and authors
- **WHEN** about dialog is displayed
- **THEN** it displays copyright notice and author contact info

#### Scenario: Dialog shows website and license
- **WHEN** about dialog is displayed
- **THEN** it shows website URL and Apache 2.0 license

#### Scenario: Dialog closes on button click
- **WHEN** user clicks the Close button
- **THEN** dialog closes and returns control to main window

### Requirement: Dialog behaves as modal
The about dialog SHALL be modal (blocks interaction with parent window).

#### Scenario: Parent window is blocked while dialog open
- **WHEN** about dialog is displayed
- **THEN** user cannot interact with the main window until dialog is closed
