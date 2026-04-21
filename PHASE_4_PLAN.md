# Phase 4: Analytics Dashboard - Implementation Plan

## 📊 Phase Overview

**Goal**: Create a professional analytics dashboard with statistics, charts, and reporting.

**Components**:
1. **Analytics Panel** - Main dashboard with statistics and visualizations
2. **Report Dialog** - Detailed scan report viewer with export options

**Status**: Ready to implement  
**Estimated Tasks**: 3  
**Estimated LOC**: 800-1000 lines

---

## 🎯 Detailed Requirements

### Analytics Panel Features

**Statistics Section**:
- Total scans performed
- Total files scanned (cumulative)
- Total threats detected
- Current threat level (Low/Medium/High)
- Last scan date/time
- Average scan duration

**Charts Section**:
- Threat distribution pie chart (by severity: Critical/High/Medium/Low)
- Scan timeline line graph (scans over time)
- File status distribution (Clean/Malicious/Suspicious)
- Threat family breakdown (top 10)

**Actions**:
- Generate detailed report
- Export report as PDF/CSV
- View scan history
- Clear statistics (with confirmation)

### Report Dialog Features

**Report Content**:
- Header: Report title, date generated, scanner version
- Summary: Total scans, files, threats, statistics
- Detailed scan history (table with columns):
  - Scan date
  - Target directory
  - Files scanned
  - Threats found
  - Duration
  - Status

**Export Options**:
- PDF export
- CSV export
- Print dialog
- Copy to clipboard

**UI Elements**:
- Report header with metadata
- Scrollable content area
- Export buttons
- Close button

---

## 📋 Task Breakdown

### Task 1: Analytics Panel (gui-analytics-panel)
**Files to Create**:
- `gui/widgets/analytics_panel.py` (400-500 lines)

**Features**:
- Statistics calculation (from scan results)
- Chart generation (pie chart, line graph)
- Report dialog integration
- Export functionality

**Dependencies**:
- PyQt6 (QTableWidget, QDialog, etc.)
- Matplotlib (for charts)
- Data source (scan results, quarantine manifest)

### Task 2: Report Dialog (gui-report-dialog)
**Files to Create**:
- `gui/dialogs/report_dialog.py` (250-350 lines)

**Features**:
- Report generation
- Export to PDF/CSV
- Print support
- Clipboard copy

**Dependencies**:
- PyQt6 (QDialog, QTextEdit, etc.)
- reportlab or weasyprint (PDF generation)
- csv module (CSV export)

### Task 3: Integration (gui-analytics-integration)
**Files to Modify**:
- `gui/main_window.py` - Replace Analytics placeholder
- `gui_main.py` - Initialize analytics panel
- `gui/widgets/__init__.py` - Export AnalyticsPanel

**Actions**:
- Connect scan results to analytics
- Initialize analytics with historical data
- Link report button to report dialog

---

## 🔧 Technical Stack

### Libraries Needed
- **PyQt6**: GUI framework (already installed)
- **Matplotlib**: Chart generation
- **Reportlab or WeasyPrint**: PDF export
- **CSV module**: Built-in Python

### Data Sources
- Scan results from `scan_results.log`
- Quarantine manifest: `data/quarantine/manifest.json`
- Application logs: `~/.antivirus/logs/gui.log`

### Architecture

```
AnalyticsPanel
├── Statistics Section (QGroupBox)
│   ├── Labels for metrics
│   └── Real-time data display
├── Charts Section (QGroupBox)
│   ├── Pie chart (threats by severity)
│   ├── Line graph (scan timeline)
│   └── Bar chart (threat families)
└── Actions Section (QHBoxLayout)
    ├── Generate Report button
    ├── Export buttons
    └── Clear Stats button

ReportDialog
├── Report Header
├── Summary Statistics
├── Scan History Table
└── Export Buttons
    ├── PDF Export
    ├── CSV Export
    ├── Print
    └── Copy
```

---

## 📊 Analytics Data Model

```python
class ScanStatistics:
    total_scans: int
    total_files_scanned: int
    total_threats: int
    threat_breakdown: {severity: count}
    file_status: {status: count}
    threat_families: {family: count}
    last_scan_date: datetime
    avg_scan_duration: float
```

---

## 🎨 UI/UX Design

**Layout**:
```
┌─────────────────────────────────────────────┐
│  Analytics Dashboard                        │
├─────────────────────────────────────────────┤
│  ┌─ Statistics ──────────────────────────┐  │
│  │ Total Scans: 5      Total Files: 250  │  │
│  │ Threats Found: 3    Current Level: High│  │
│  │ Last Scan: 2026-04-21 13:45:20       │  │
│  │ Avg Duration: 2.5s                    │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─ Charts ──────────────────────────────┐  │
│  │ [Pie: By Severity] [Line: Timeline]   │  │
│  │ [Bar: Top Threats]                    │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─ Actions ─────────────────────────────┐  │
│  │ [Generate Report] [Export PDF] [Clear]│  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Color Scheme**:
- Professional dark theme with accent colors
- Threat severity colors:
  - 🔴 Critical/High: Red (#d32f2f)
  - 🟠 Medium: Orange (#f57c00)
  - 🟡 Low: Yellow (#fbc02d)
  - 🟢 Clean: Green (#388e3c)

---

## 📈 Implementation Order

1. **Analytics Panel** (Core statistics & charts)
   - Statistics calculation
   - Matplotlib chart integration
   - Report dialog launching

2. **Report Dialog** (Export & detailed view)
   - Report generation
   - PDF/CSV export
   - Print support

3. **Integration** (Connect all pieces)
   - Replace Analytics placeholder
   - Wire up data sources
   - Test end-to-end

---

## ✅ Success Criteria

Phase 4 is complete when:

- ✅ Analytics panel displays all statistics
- ✅ Charts render correctly (pie, line, bar)
- ✅ Report dialog shows detailed scan history
- ✅ PDF export works
- ✅ CSV export works
- ✅ Print dialog functional
- ✅ Copy to clipboard works
- ✅ Smooth integration with scan panel
- ✅ No crashes or errors
- ✅ Professional appearance with theming
- ✅ All unit tests pass
- ✅ Comprehensive documentation

---

## 📚 Dependencies to Install

```bash
pip install matplotlib
pip install reportlab  # For PDF export
# OR
pip install weasyprint  # Alternative PDF library
```

---

## 🚀 Next Steps

1. Review this plan
2. Approve scope and approach
3. Begin Phase 4 implementation
4. Build Analytics Panel
5. Build Report Dialog
6. Integrate and test
7. Document and commit

---

**Estimated Time**: 4-6 hours for full Phase 4 implementation

**Start?** Yes → Let's begin! 🚀
