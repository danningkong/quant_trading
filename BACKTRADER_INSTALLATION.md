# Backtrader Installation Guide

## Overview
Your quant trading platform now supports **dual engines**:
- **Custom Engine** (Always available): Fast pandas/numpy backtesting
- **Backtrader Engine** (Optional): Advanced backtesting with sophisticated indicators

## Installation from Internal Artifactory

### Step 1: Install Backtrader
```bash
pip install backtrader --index-url YOUR_INTERNAL_ARTIFACTORY_URL
```

### Step 2: Verify Installation
```bash
python -c "import backtrader; print('Backtrader installed successfully!')"
```

### Step 3: Restart the Server
After installation, restart your quant trading server:
```bash
cd "C:\Dev\AI\Claude_Code\Quant Trading"
start_server_final.bat
```

## Using the Dual Engine Interface

### 1. Access the Platform
- Open: http://localhost:8001
- Navigate to the **Stock Screener** tab

### 2. Run Stock Screening
- Select a screening strategy (momentum, value, growth, etc.)
- Enter stock symbols or use popular stocks
- Click **"Run Screening"**

### 3. Enhanced Backtesting Workflow
1. After screening, click **"Backtest These"** button
2. **Select/Deselect Stocks**: Use checkboxes to choose which stocks to backtest
3. **Choose Engine**:
   - **Custom (Fast)**: Simple, quick backtesting
   - **Backtrader (Advanced)**: Sophisticated technical analysis
4. **Configure Settings**:
   - Basic: Capital, positions, frequency
   - Advanced: Commission, slippage, lookback period
   - **Backtrader-Specific**: RSI periods, momentum thresholds, SMA periods
5. Click **"Run Backtest"**

## Features Comparison

| Feature | Custom Engine | Backtrader Engine |
|---------|--------------|-------------------|
| **Speed** | ⚡ Very Fast | 🐢 Moderate |
| **Technical Indicators** | Basic (SMA, RSI) | 🎯 Advanced (50+ indicators) |
| **Order Types** | Market orders | 📊 Market, Limit, Stop orders |
| **Strategy Complexity** | Simple momentum | 🔬 Complex multi-factor |
| **Risk Management** | Basic | 🛡️ Advanced position sizing |
| **Installation** | ✅ Built-in | 📦 Requires installation |

## Backtrader-Specific Settings

When you select **Backtrader Engine**, additional settings become available:

### Technical Indicators
- **RSI Period**: Default 14 days (range: 5-50)
- **RSI Lower**: Oversold threshold, default 30
- **RSI Upper**: Overbought threshold, default 70
- **SMA Period**: Simple moving average, default 20 days

### Strategy Parameters
- **Momentum Period**: Lookback for momentum calculation, default 10 days
- **Momentum Threshold**: Minimum momentum for entry, default 5%

### Advanced Features
- **Event-driven backtesting**: More accurate order execution
- **Built-in performance analytics**: Comprehensive statistics
- **Portfolio optimization**: Better position sizing algorithms

## Troubleshooting

### If Backtrader Installation Fails
```bash
# Try with trusted hosts
pip install backtrader --trusted-host YOUR_ARTIFACTORY_HOST --index-url YOUR_INTERNAL_ARTIFACTORY_URL

# Or check your pip configuration
pip config list
```

### If the Server Doesn't Recognize Backtrader
1. Restart the Python backend
2. Check import in Python console:
   ```python
   from strategies.backtrader_wrapper import is_backtrader_available
   print(is_backtrader_available())
   ```

### If You See "Installation Required" Message
- This is normal before installation
- The platform will automatically fallback to Custom Engine
- Click **"Switch to Custom Engine"** to continue

## Testing the Installation

Run the comprehensive test:
```bash
cd "C:\Dev\AI\Claude_Code\Quant Trading"
python test_dual_engine.py
```

## Benefits of Dual Engine Approach

1. **Flexibility**: Choose the right tool for your needs
2. **Performance**: Fast custom engine for quick analysis
3. **Sophistication**: Advanced Backtrader for detailed strategies  
4. **Fallback**: Always works even without Backtrader
5. **Learning**: Compare results between engines

## Example Workflow

1. **Quick Analysis**: Use Custom Engine for rapid screening validation
2. **Detailed Research**: Use Backtrader for sophisticated technical analysis
3. **Production**: Choose based on your specific requirements

## Contact IT Department

If you need help with the internal artifactory URL or installation permissions, contact your IT department with this request:

**Subject**: Backtrader Installation for Quant Trading Platform  
**Request**: Please provide the correct artifactory URL and permissions to install the `backtrader` Python package for financial backtesting.

---

Your platform now gives you the best of both worlds: **speed** when you need it, and **sophistication** when you want it! 🚀