## 1. Enhanced Horizontal Rule Rendering

- [x] 1.1 Modify `_render_tokens` to handle horizontal rule rendering
- [x] 1.2 Add decorative Unicode characters for section breaks
- [x] 1.3 Ensure theme-appropriate colors for light/dark mode
- [x] 1.4 Test horizontal rules in User Guide and Tutorial

## 2. Enhanced Code Block Rendering

- [x] 2.1 Add top/bottom border lines using Unicode box-drawing characters
- [x] 2.2 Apply theme-appropriate border colors
- [x] 2.3 Ensure code block retains existing background and monospace styling
- [x] 2.4 Test code blocks in Tutorial markdown

## 3. Enhanced Table Rendering

- [x] 3.1 Modify `render_table` function to use Unicode box-drawing characters
- [x] 3.2 Implement proper corner, edge, and intersection characters
- [x] 3.3 Add header row separator using different border character
- [x] 3.4 Ensure vertical borders on all cells
- [x] 3.5 Test tables in User Guide markdown

## 4. Testing & Verification

- [x] 4.1 Test Help Window with User Guide in light theme
- [x] 4.2 Test Help Window with User Guide in dark theme
- [x] 4.3 Test Help Window with Tutorial in light theme
- [x] 4.4 Test Help Window with Tutorial in dark theme
- [x] 4.5 Verify fallback behavior when markdown_it unavailable
