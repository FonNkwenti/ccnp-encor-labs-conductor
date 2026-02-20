Create a new conductor track for: $ARGUMENTS

## Workflow

1. **Parse the track name** from the arguments. Format: `<descriptive-name>`
   Example: "Implement OSPF Lab 05" → track folder `ospf_std_05_<today's date YYYYMMDD>`

2. **Create the track folder:** `conductor/tracks/<track_name>_<YYYYMMDD>/`

3. **Create `index.md`:**
   ```markdown
   # Track: <Track Title>
   - **Created**: <date>
   - **Status**: Active
   - **Goal**: <1-2 sentence summary>
   ```

4. **Create `spec.md`:**
   - Technical specification for the work
   - List of deliverables
   - Dependencies and prerequisites
   - Acceptance criteria

5. **Create `plan.md`:**
   - Organize into phases (Phase 1, Phase 2, etc.)
   - Each phase has numbered tasks with `[ ]` status markers
   - Include checkpoint markers for phase completion
   - Example format:
     ```markdown
     ## Phase 1: <Phase Name>
     - [ ] Task 1 description
     - [ ] Task 2 description

     ## Phase 2: <Phase Name>
     - [ ] Task 3 description
     - [ ] Task 4 description
     ```

6. **Add entry to `conductor/tracks.md`:**
   ```markdown
   - [ ] **Track: <Track Title>**
     *Link: [./tracks/<folder_name>/](./tracks/<folder_name>/)*
   ```

7. **Commit** the new track: `conductor(track): Create track '<Track Title>'`
