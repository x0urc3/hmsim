# Plan: Enhance HMSim GUI with Memory Region Setup

This plan outlines the steps to enhance the HM Simulator GUI by allowing users to define specific memory regions for "Text" (executable code) and "Data" sections.

## 1. Engine & State Persistence

### HMEngine Modifications
- Add `text_region` and `data_region` attributes to the `HMEngine` class (in `src/hmsim/engine/cpu.py` or where `HMEngine` is defined).
- **Default values**: `text_region = (0x0000, 0x0100)` and `data_region = (0x0101, 0xFFFF)`.
- **Constraint**: These regions must be strictly non-overlapping as they share the same memory.

### State File Format (.hm)
- Update `src/hmsim/engine/state.py` to include a `setup` field in the JSON structure.
- Example structure:
  ```json
  {
    "version": "HMv1",
    "setup": {
      "text": [0, 256],
      "data": [257, 65535]
    },
    ...
  }
  ```
- Modify `save_state_to_dict` to only include addresses within the defined `text_region` in the `text` section and addresses within `data_region` in the `data` section.
- Modify `load_state_from_dict` to restore these region definitions.

## 2. GUI Enhancement: Memory View

### Visual Indication
- Update `src/hmsim/gui/widgets/memory_view.py` to add a narrow indicator column in the `Gtk.TreeView`.
- **Placement**: This column should be positioned between the PC register arrow (icon column) and the Memory Address column.
- Use a `Gtk.CellRenderer` (e.g., `Gtk.CellRendererText` with background color or a custom renderer) to provide a color-coded vertical strip:
    - **Text Region**: Green indicator (`#2ECC71` or similar).
    - **Data Region**: Blue indicator (`#3498DB` or similar).
    - **Unassigned**: No color/transparent.
- The `Gtk.ListStore` model will need an additional column to store the color or region type for each address.
- Add a method `set_regions(text_range, data_range)` to `MemoryView` to refresh the visual indicators.

## 3. GUI Enhancement: Setup Submenu

### Setup Menu
- In `src/hmsim/gui/main_window.py`, add a new "Setup" menu to the menubar.
- Add a "Simulator Setup..." submenu item.

### Setup Dialog
- Create a new dialog class (e.g., `SetupDialog`) that allows users to input start and end addresses for:
    - **Text Section** (Start/End)
    - **Data Section** (Start/End)
- **Strict Validation**: The dialog MUST NOT allow overlapping regions. It must ensure:
    - `text_start <= text_end`
    - `data_start <= data_end`
    - `text_region` and `data_region` are disjoint (no shared addresses).
    - All addresses are within 0x0000–0xFFFF.

## 4. Editor Integration

### Dynamic Assembly/Disassembly
- **Disassembly**: Modify `_refresh_editor_from_memory` in `MainWindow` to only disassemble instructions within the `text_region`.
    - The editor should start from `text_region[0]`.
    - **0x0 Handling**: If a memory location in the text region contains `0x0`, it should be treated as an invalid opcode and ignored (e.g., shown as an empty line in the editor and not counted as a valid instruction).
- **Assembly**: Modify `EditorView.assemble_to_engine` and related methods to map editor lines to addresses starting from `text_region[0]`.
    - Ensure it doesn't write machine code outside the `text_region`.
    - Blank lines in the editor should not result in `0x0` being written if it's meant to be "ignored", or we should maintain the convention that `0x0` in text is a "no-op/ignore" state.
- Update the `EditorView` to show the base address of the text section if possible, or ensure the user knows line 1 is `text_start`.

## 5. Implementation Steps

1.  **Modify `HMEngine`**: Add region state.
2.  **Update Persistence**: Save/load regions in `.hm` files.
3.  **Update `MemoryView`**: Add the color-coded region indicator column between the icon and address columns.
4.  **Implement `SetupDialog`**: Create the UI for defining regions.
5.  **Update `MainWindow`**:
    - Add the "Setup" menu.
    - Connect the `SetupDialog` to the engine and `MemoryView`.
    - Update assembly/disassembly logic to respect `text_region`.
## 6. Testing & Edge Cases

### Edge Case Scenarios
- **Minimum Region Size**: Test with 1-byte regions (e.g., `text: 0x0000-0x0000`).
- **Adjacent Regions**: Test with `text: 0x0000-0x07FF` and `data: 0x0800-0xFFFF`.
- **Validation Failure**: Attempt to set overlapping regions (e.g., `text: 0-100`, `data: 100-200`) and verify the `SetupDialog` blocks the change.
- **PC Out-of-Bounds**: Move the PC to an address outside the `text_region` and verify the editor/disassembler handles it gracefully (e.g., doesn't crash, perhaps shows a "PC outside text area" status).
- **Assembly Overflow**: Write more lines in the editor than the `text_region` can hold. Verify that assembly is truncated or an error is shown.
- **Legacy File Loading**: Load a `.hm` file that lacks the `setup` section. Verify it defaults to `text: 0x0000-0x0100` and `data: 0x0101-0xFFFF`.
* **0x0 in Text**: Verify that `0x0` values in the text region are ignored during disassembly and result in empty lines in the editor.
- **Data Persistence**: Verify that non-zero values placed in the `data_region` (via `MemoryView` or code) are correctly saved and reloaded.

### Automated Tests
- **Unit Tests**:
    - `test_engine_regions`: Verify `HMEngine` stores and validates regions correctly.
    - `test_state_persistence_with_setup`: Verify `save_state` and `load_state` correctly handle the `setup` field.
- **Integration Tests**:
    - `test_editor_assembly_mapping`: Verify editor line $N$ maps to `text_start + N`.
    - `test_memory_view_indicators`: (If testable via CLI/Mock) Verify the model contains correct color/region metadata.
