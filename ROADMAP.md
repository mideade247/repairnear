# RepairNear Roadmap

## Goal

Launch a useful, accessible directory of repair, reuse and tool-lending services
for one town or borough. Visitors should be able to find a suitable organisation,
understand its service and follow its official booking or contact link.

Status: planning. All milestones below are outstanding. Estimates are working
estimates, not completed hours or commitments. Update this document as decisions
are made and functionality is delivered.

## Delivery milestones

| Milestone | Outcome | Estimated effort |
| --- | --- | --- |
| 1. Project foundation | Reproducible local application and automated checks | 4-6 hours |
| 2. Directory backend | Validated listings and protected editorial tools | 8-12 hours |
| 3. Public directory | Search, filters and readable service pages | 8-12 hours |
| 4. Information maintenance | Reviewed corrections and verification tracking | 8-12 hours |
| 5. Quality and accessibility | Tested visitor journeys and robust error handling | 6-10 hours |
| 6. Pilot preparation | Checked listings and a documented maintenance process | 5-8 hours |
| 7. Deployment and release | Operable hosted application and recovery instructions | 6-10 hours |
| **Total** | **Initial public release** | **45-70 hours** |

Complete milestones in order. Establish automated tests in milestone 1 and extend
them with each feature. Milestone 5 brings the whole application together rather
than postponing testing until the end.

## 1. Project foundation

- [ ] Confirm the pilot area and initial service categories.
- [ ] Initialise the dedicated repository and preserve genuine development history.
- [ ] Add an MIT license after confirming ownership of the original code.
- [ ] Set up Django, server-rendered templates and SQLite for local development.
- [ ] Separate development and deployment configuration through environment variables.
- [ ] Add a README, dependency configuration, example configuration and ignore rules.
- [ ] Configure automated tests, Ruff lint and formatting checks in CI.
- [ ] Establish SAST and secret scanning for application changes.

Acceptance: a clean checkout can install dependencies, run migrations, start the
local application and run its checks using documented commands. No credentials
or real personal records are committed.

## 2. Directory backend

- [ ] Model organisations, service locations, areas and item categories.
- [ ] Distinguish repair, reuse and tool-lending services.
- [ ] Store descriptions, official links, booking requirements and published costs.
- [ ] Support opening-hours text and optional event dates without inventing missing details.
- [ ] Record source links, reuse permission notes and last-checked dates.
- [ ] Add draft, published and archived listing states.
- [ ] Define validation rules and a duplicate-review process.
- [ ] Configure a protected administration interface with appropriate editor permissions.
- [ ] Add an explicit development command to load fictional listings.

Acceptance: editors can create and update valid listings. Invalid records are
rejected with useful errors. Draft and archived records never appear in public
queries. Unknown values remain distinguishable from confirmed answers.

### First bounded implementation task

After the project foundation, implement storage and filtering for fictional
listings. Include an area, category, service type and publication state.

Acceptance criteria:

1. Migrations create the schema in an empty local database.
2. A valid listing survives saving and reloading.
3. Invalid required fields are rejected through the application validation path.
4. Area and category filters work separately and together.
5. Results have deterministic ordering and empty searches return an empty result.
6. Public queries exclude drafts and archived listings.
7. Isolated tests use synthetic records and require no external services.

Estimated effort: 4-6 hours within this milestone. Public pages, imports and
correction submissions are outside this first task.

## 3. Public directory

- [ ] Build a responsive home page explaining the directory's purpose.
- [ ] Add organisation-name and description search.
- [ ] Add area, category and service-type filters with shareable query URLs.
- [ ] Implement stable pagination and clear empty-result messages.
- [ ] Build service pages with location, booking, cost and opening information.
- [ ] Display source links, verification dates and unknown information clearly.
- [ ] Provide useful missing-page and error pages.
- [ ] Keep external booking and contact actions on providers' official websites.

Acceptance: a visitor can find a fictional bicycle repair service in a chosen
area, inspect its details and follow its official link on mobile and desktop.
Filter selections persist through pagination. Unpublished detail URLs return no
public listing information.

## 4. Information maintenance

- [ ] Add a correction form tied to an existing listing.
- [ ] Request only the proposed change and supporting source; no identity fields.
- [ ] Apply input limits, CSRF protection and submission throttling.
- [ ] Keep submissions private until an editor reviews them.
- [ ] Add pending, accepted and rejected review states.
- [ ] Record editorial decisions and published changes without exposing private notes.
- [ ] Provide a configurable stale-listing report based on last-checked dates.
- [ ] Keep verification dates unchanged unless an editor explicitly confirms a check.
- [ ] Define retention and deletion rules for submissions and operational logs.

Acceptance: a correction cannot change a public listing automatically. Only an
authorised editor can resolve it, and the resulting change is traceable. Tests
cover unauthorised requests, repeated submissions and invalid input. Throttling
and logging choices document any temporary technical identifiers retained.

## 5. Quality and accessibility

- [ ] Test the full search-to-service journey and correction review workflow.
- [ ] Verify labels, headings, focus order, contrast and keyboard operation.
- [ ] Check primary pages with a screen reader and automated accessibility checks.
- [ ] Ensure important information is available without JavaScript.
- [ ] Test escaped user input, permission boundaries and safe external URL handling.
- [ ] Test invalid filter parameters, pagination boundaries and database failures.
- [ ] Review database queries and add indexes supported by the filtering workload.
- [ ] Review dependencies and resolve security findings or document their disposition.

Acceptance: all automated checks pass, key journeys work with a keyboard, and
manual accessibility findings are addressed or recorded with a release decision.
No claim of full accessibility conformance is made solely from automated checks.

## 6. Pilot preparation

- [ ] Identify 15-30 candidate organisation listings in the selected area.
- [ ] Check permission to reuse each source before publishing its information.
- [ ] Verify accepted items, location, booking information and available hours.
- [ ] Publish only verified organisation-level details; exclude private contact data.
- [ ] Document who maintains the directory and how corrections are handled.
- [ ] Conduct a small voluntary usability review without collecting visitor profiles.
- [ ] Record whether participants can locate suitable services and understand next steps.
- [ ] Keep fictional development fixtures separate from public production records.

Acceptance: every published pilot listing has an attributable source and a real
verification date. Missing details are explicit. Reuse permission is recorded,
and an editor can explain how each listing will be kept current.

## 7. Deployment and release

- [ ] Select hosting and confirm the operating budget.
- [ ] Configure PostgreSQL if selected, and run integration tests against it.
- [ ] Configure HTTPS, allowed hosts, secure cookies and production settings.
- [ ] Provide static files, a health check and privacy-conscious error logging.
- [ ] Set up database backups and test restoration in an isolated environment.
- [ ] Document deployment, migrations, rollback and incident response.
- [ ] Run Django deployment checks and the complete CI suite.
- [ ] Publish an initial version with release notes and known limitations.

Acceptance: deployment is reproducible, secrets remain outside source control,
restoration has been demonstrated, and the public visitor journeys pass a smoke
test. Rollback instructions account for database migration compatibility.

## Release boundaries

The initial release does not include payments, visitor accounts, public reviews,
direct messaging, provider self-service accounts or a booking marketplace. Maps,
automated imports and expansion beyond the pilot area remain later decisions.
No repair quality, cost savings or waste reduction outcomes are claimed without
evidence.

## After the pilot

Prioritise improvements using observed needs:

- Better category coverage and clearer service descriptions.
- More efficient editorial checks and duplicate detection.
- Carefully licensed CSV imports with previews and row-level errors.
- Additional areas when an ongoing maintenance process is available.
- Maps if location browsing adds value beyond the accessible results list.

## Tracking progress

Create an issue for each bounded task with its scope and acceptance criteria.
Mark roadmap items complete only when the implementation and relevant checks
are finished. Update remaining effort estimates as work progresses. Keep the
README accurate about what works today and what is still planned.
