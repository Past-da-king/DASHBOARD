# Power BI Visualization Report
## Liberty Towers Fibre Relocation - Project Status Dashboard

---

## 📊 Executive Summary

This report outlines the recommended Power BI visualizations for the **Liberty Towers Fibre Relocation** project status dashboard. The data has been cleaned and exported from the original Excel workbook into structured CSV files optimized for Power BI consumption.

### Data Sources Created

| File Name | Purpose | Key Fields |
|-----------|---------|------------|
| `cost_breakdown.csv` | Cost distribution by category | Cost_Category, Amount, Percentage |
| `project_kpis.csv` | Key performance indicators | KPI, Value, Unit |
| `project_status.csv` | Project overview metrics | Contract_Value, Total_Costs, Profit_Loss |
| `monthly_cost_trend.csv` | Month-over-month spending | Month, Labour_Cost, Vehicle_Cost, Material_Cost |
| `labour_all_months.csv` | Detailed labour records | DATE, LABOUR, QUANTITY, RATE, TIME, TOTAL |
| `materials_inventory.csv` | Materials and inventory | Model, Responsible_employee, Unit_Cost, Total |
| `vehicle_costs_detail.csv` | Vehicle expense breakdown | Vehicle_Reg, Supervisor, Cost_Per_KM, Total_Costs |
| `tools_equipment.csv` | Tools and equipment costs | Item, Description, Quantity, Amount |

---

## 🎯 Recommended Dashboard Layout

### Page 1: Executive Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LIBERTY TOWERS FIBRE RELOCATION                          │
│                         PROJECT STATUS DASHBOARD                            │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   KPI CARD 1    │   KPI CARD 2    │   KPI CARD 3    │      KPI CARD 4       │
│ Contract Value  │  Total Costs    │  Profit/Loss    │  Budget Utilization   │
│  R 240,100.82   │  R 89,033.86    │  R 151,137.96   │       37.1%           │
├─────────────────┴─────────────────┴─────────────────┴─────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────┐    ┌──────────────────────────────────┐   │
│  │      COST BREAKDOWN          │    │      MONTHLY COST TREND          │   │
│  │      (Pie/Donut Chart)       │    │      (Line Chart)                │   │
│  │                              │    │                                  │   │
│  │   Labour: 33.9%              │    │     ────────────────────         │   │
│  │   Material: 33.6%            │    │    /                             │   │
│  │   OHC: 27.0%                 │    │   /                              │   │
│  │   Vehicle: 5.5%              │    │  /   Jan      Feb                │   │
│  │                              │    │                                  │   │
│  └──────────────────────────────┘    └──────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │              BUDGET VS ACTUAL (Gauge Chart)                           │  │
│  │                                                                       │  │
│  │                    ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░                   │  │
│  │                          37.1% Utilized                               │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📈 Detailed Visualization Specifications

### 1. KPI Cards (Top Row)

**Purpose**: Display key project metrics at a glance

| Card | Data Source | Field | Format | Conditional Formatting |
|------|-------------|-------|--------|----------------------|
| Contract Value | `project_kpis.csv` | Value (where KPI = 'Contract Value') | Currency (ZAR) | Blue background |
| Total Costs | `project_kpis.csv` | Value (where KPI = 'Total Costs to Date') | Currency (ZAR) | Orange if > 50% of contract |
| Profit/Loss | `project_kpis.csv` | Value (where KPI = 'Indicative Profit/Loss') | Currency (ZAR) | Green if positive, Red if negative |
| Budget Utilization | `project_status.csv` | Completion_Percentage | Percentage | Traffic light (Green < 75%, Yellow 75-90%, Red > 90%) |

**Power BI Steps**:
1. Insert → Card visual
2. Drag appropriate field to "Fields" well
3. Format → Data label → Display units: None, Decimal places: 2
4. Add conditional formatting via Format → Conditional formatting

---

### 2. Cost Breakdown - Donut Chart

**Purpose**: Show proportional cost distribution across categories

**Data Source**: `cost_breakdown.csv`

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | Donut Chart |
| **Legend** | Cost_Category |
| **Values** | Amount (Sum) |
| **Detail Labels** | Show percentage |

**Recommended Colors**:
- Labour: #1E88E5 (Blue)
- Material: #43A047 (Green)
- Overhead (OHC): #FB8C00 (Orange)
- Vehicle: #E53935 (Red)

**Power BI Steps**:
1. Insert → Donut Chart
2. Drag `Cost_Category` to Legend
3. Drag `Amount` to Values
4. Format → Detail labels → Label style: All detail labels

---

### 3. Monthly Cost Trend - Line Chart

**Purpose**: Track spending over time, identify trends

**Data Source**: `monthly_cost_trend.csv`

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | Line Chart (Multi-line) |
| **X-Axis** | Month |
| **Y-Axis (Lines)** | Labour_Cost, Vehicle_Cost, Material_Cost |
| **Tooltips** | Total_Cost |

**Power BI Steps**:
1. Insert → Line Chart
2. Drag `Month` to X-Axis
3. Drag `Labour_Cost`, `Vehicle_Cost`, `Material_Cost` to Y-Axis
4. Format → X-Axis → Sort by Month_Num ascending

**Alternative**: Stacked Area Chart to show cumulative effect

---

### 4. Budget Gauge Chart

**Purpose**: Visual representation of budget consumption

**Data Source**: `project_status.csv`

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | Gauge |
| **Value** | Total_Costs |
| **Minimum** | 0 |
| **Maximum** | Contract_Value |
| **Target** | Contract_Value * 0.9 (Warning threshold) |

**Color Bands**:
- 0-75%: Green
- 75-90%: Yellow
- 90-100%: Red

---

### Page 2: Labour Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LABOUR COST ANALYSIS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────┐    ┌────────────────────────────────┐   │
│  │   LABOUR BY ROLE               │    │   DAILY LABOUR TREND           │   │
│  │   (Horizontal Bar Chart)       │    │   (Line Chart with Markers)    │   │
│  │                                │    │                                │   │
│  │   General Labour ████████████  │    │   ───●───●───●───●───          │   │
│  │   Team Leader    ███████       │    │                                │   │
│  │   Supervisor     █████         │    │   Jan           Feb            │   │
│  │                                │    │                                │   │
│  └────────────────────────────────┘    └────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    LABOUR DETAILS TABLE                               │  │
│  ├───────────┬──────────────────┬──────────┬───────┬───────┬────────────┤  │
│  │   Date    │   Labour Type    │ Quantity │ Rate  │ Hours │   Total    │  │
│  ├───────────┼──────────────────┼──────────┼───────┼───────┼────────────┤  │
│  │ 17/01/25  │ General Labour   │    4     │ 28.68 │  8.75 │  R1,003.80 │  │
│  │ 20/01/25  │ General Labour   │    4     │ 28.68 │  8.75 │  R1,003.80 │  │
│  │    ...    │       ...        │   ...    │  ...  │  ...  │     ...    │  │
│  └───────────┴──────────────────┴──────────┴───────┴───────┴────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 5. Labour by Role - Bar Chart

**Data Source**: `labour_all_months.csv` (aggregated)

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | Clustered Bar Chart |
| **Y-Axis** | LABOUR (role type) |
| **X-Axis** | Sum of TOTAL |
| **Legend** | Month |

---

### 6. Daily Labour Trend - Line Chart with Markers

**Data Source**: `labour_all_months.csv`

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | Line Chart |
| **X-Axis** | Date_Formatted |
| **Y-Axis** | Sum of TOTAL |
| **Legend** | LABOUR |

---

### 7. Labour Details Table

**Data Source**: `labour_all_months.csv`

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | Table |
| **Columns** | DATE, LABOUR, QUANTITY, RATE, TIME, TOTAL |
| **Formatting** | Currency for TOTAL, Number for QUANTITY, RATE |

---

### Page 3: Materials & Resources

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MATERIALS & RESOURCES TRACKING                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────┐    ┌────────────────────────────────┐   │
│  │   TOP MATERIALS BY COST        │    │   MATERIALS BY EMPLOYEE        │   │
│  │   (TreeMap)                    │    │   (Stacked Bar Chart)          │   │
│  │                                │    │                                │   │
│  │   48 CORE FIBRE    │ LC PIGTAIL│    │   Mbongeni ██████████████      │   │
│  │                    │           │    │   Nkosinathi ████████          │   │
│  │   6 WAY DOME       │ CABLE     │    │                                │   │
│  │                    │ TIES      │    │                                │   │
│  └────────────────────────────────┘    └────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    MATERIALS INVENTORY TABLE                          │  │
│  ├───────────────────────────────────┬────────────┬───────────┬──────────┤  │
│  │   Material Description            │  Quantity  │ Unit Cost │  Total   │  │
│  ├───────────────────────────────────┼────────────┼───────────┼──────────┤  │
│  │ 48 CORE HDD SM (9/125) FIBRE 2025 │    900     │  R 20.00  │ R18,000  │  │
│  │ 12 CORE CST SM (9/125) FIBRE      │    300     │  R 11.44  │ R 3,432  │  │
│  │ 6 WAY DOME JOINT                  │      2     │ R1,595.00 │ R 3,190  │  │
│  │ LC/PC Pigtails 2025               │    168     │  R 10.00  │ R 1,680  │  │
│  └───────────────────────────────────┴────────────┴───────────┴──────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 8. Top Materials by Cost - TreeMap

**Data Source**: `materials_inventory.csv`

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | TreeMap |
| **Group** | Model (Material name) |
| **Values** | Total (Sum) |
| **Colors** | Gradient by value |

---

### 9. Materials by Employee - Stacked Bar

**Data Source**: `materials_inventory.csv`

| Configuration | Setting |
|--------------|---------|
| **Visual Type** | Stacked Bar Chart |
| **Y-Axis** | Responsible employee |
| **X-Axis** | Sum of Total |
| **Legend** | Model |

---

### Page 4: Vehicle & Diesel Costs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VEHICLE & FUEL EXPENSES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────┐    ┌────────────────────────────────┐   │
│  │   VEHICLE COSTS BY REG         │    │   COST PER KM COMPARISON       │   │
│  │   (Column Chart)               │    │   (Bar Chart)                  │   │
│  │                                │    │                                │   │
│  │         ███                    │    │   BG51VCZN ████████  R6.86     │   │
│  │   ███   ███   ███              │    │   NU107063 █████    R5.08     │   │
│  │   ███   ███   ███   ███        │    │   NPN85677 █████    R4.96     │   │
│  │   REG1  REG2  REG3  REG4       │    │                                │   │
│  └────────────────────────────────┘    └────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    VEHICLE DETAILS TABLE                              │  │
│  ├───────────────┬─────────────┬────────────┬────────────────────────────┤  │
│  │ Vehicle Reg   │ Supervisor  │ Cost/KM    │  Total Costs               │  │
│  ├───────────────┼─────────────┼────────────┼────────────────────────────┤  │
│  │ BG51VCZN      │ Machi       │ R 6.86     │  R 3,259.87                │  │
│  │ NU107063      │ Sipho       │ R 5.08     │  R 804.67                  │  │
│  │ NPN85677      │ Mbongeni    │ R 4.96     │  R 874.94                  │  │
│  │ NPN85677      │ Jojisa      │ R 4.96     │  R 1,571.33                │  │
│  └───────────────┴─────────────┴────────────┴────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Power BI Implementation Steps

### Step 1: Data Import

1. Open Power BI Desktop
2. Click **Get Data** → **Text/CSV**
3. Navigate to `c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\cleaned_data`
4. Import each CSV file:
   - `cost_breakdown.csv`
   - `project_kpis.csv`
   - `project_status.csv`
   - `monthly_cost_trend.csv`
   - `labour_all_months.csv`
   - `materials_inventory.csv`
   - `vehicle_costs_detail.csv`
   - `tools_equipment.csv`

### Step 2: Data Modeling

1. Go to **Model View**
2. Create relationships:
   - `labour_all_months[Month]` → `monthly_cost_trend[Month]`
   - All tables share `Project` field for filtering
3. Add calculated measures:

```DAX
// Total Project Cost
Total Cost = SUM(cost_breakdown[Amount])

// Budget Remaining
Budget Remaining = [Contract Value] - [Total Cost]

// Budget Utilization %
Budget Utilization % = DIVIDE([Total Cost], [Contract Value], 0) * 100

// Profit Margin %
Profit Margin % = DIVIDE([Budget Remaining], [Contract Value], 0) * 100
```

### Step 3: Create Dashboard Pages

1. Create 4 pages as outlined above
2. Add visuals according to specifications
3. Apply consistent formatting and color scheme

### Step 4: Add Interactivity

1. Add **Slicers** for:
   - Month filter
   - Date range
   - Cost category
2. Enable **Cross-filtering** between visuals
3. Add **Drill-through** pages for detailed analysis

---

## 🎨 Recommended Theme & Styling

### Color Palette

| Element | Hex Code | Usage |
|---------|----------|-------|
| Primary Blue | #1E88E5 | Headers, Labour costs |
| Success Green | #43A047 | Profit, positive KPIs |
| Warning Orange | #FB8C00 | Overhead, caution |
| Danger Red | #E53935 | Vehicle, negative values |
| Neutral Gray | #757575 | Secondary text |
| Background | #FAFAFA | Page background |

### Typography

- **Titles**: Segoe UI Bold, 16pt
- **Subtitles**: Segoe UI, 12pt
- **Data Labels**: Segoe UI, 10pt

---

## 📋 Summary Checklist

### Required Visualizations

- [ ] KPI Cards (Contract Value, Total Costs, Profit/Loss, Budget %)
- [ ] Cost Breakdown Donut Chart
- [ ] Monthly Cost Trend Line Chart
- [ ] Budget Gauge Chart
- [ ] Labour by Role Bar Chart
- [ ] Daily Labour Trend Line Chart
- [ ] Labour Details Table
- [ ] Materials TreeMap
- [ ] Materials by Employee Stacked Bar
- [ ] Materials Inventory Table
- [ ] Vehicle Costs Column Chart
- [ ] Cost per KM Bar Chart
- [ ] Vehicle Details Table

### Optional Enhancements

- [ ] Project Timeline/Gantt Chart
- [ ] Forecast projections
- [ ] Year-over-year comparisons (when data available)
- [ ] Mobile-optimized layout
- [ ] Automated refresh schedule

---

## 📁 Files Created

All cleaned CSV files are located in:
```
c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\cleaned_data\
```

| File | Records | Purpose |
|------|---------|---------|
| cost_breakdown.csv | 4 | Pie/Donut chart data |
| project_kpis.csv | 5 | KPI card values |
| project_status.csv | 1 | Project overview |
| monthly_cost_trend.csv | 2 | Line chart trends |
| labour_all_months.csv | 10+ | Detailed labour data |
| materials_inventory.csv | 11 | Materials tracking |
| vehicle_costs_detail.csv | 4 | Vehicle expenses |
| tools_equipment.csv | 10+ | Tools and equipment |

---

**Report Generated**: 2026-01-21  
**Project**: Liberty Towers Fibre Relocation  
**Data Source**: Fibre Relocation - Liberty Towers.xlsx
