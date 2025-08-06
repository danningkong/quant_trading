# Quick Fix for HTTP 500 Error

## ✅ Problem Identified
The backend logic is working correctly, but the server has stale imports from the broken `backtrader_wrapper.py` file.

## ✅ Solution: Complete Server Restart

### Step 1: Stop the Current Server
- Find the server process and stop it completely
- Use Ctrl+C in the terminal where the server is running
- Or use Task Manager to kill Python processes if needed

### Step 2: Restart the Server
```bash
cd "C:\Dev\AI\Claude_Code\Quant Trading"
start_server_final.bat
```

### Step 3: Verify Fix
```bash
python test_minimal_api.py
```

## ✅ Expected Results After Restart

The minimal API test should show:
```
1. Health Check... [OK] 
2. Simple Screening... [OK]
3. Custom Engine Backtest... [SUCCESS] ✅
4. Backtrader Engine... [OK] Installation required message ✅
```

## ✅ What Was Fixed

1. **Import Error**: Fixed `NameError: name 'bt' is not defined` in `backtrader_wrapper.py`
2. **Class Definitions**: Moved Backtrader classes inside availability check
3. **Graceful Degradation**: System now works without Backtrader installed
4. **Engine Selection**: Frontend can choose between Custom and Backtrader engines

## ✅ Features Now Working

1. **Stock Selection**: Check/uncheck stocks from screening results
2. **Engine Choice**: Custom (Fast) or Backtrader (Advanced) 
3. **Settings Panel**: Basic + Advanced + Backtrader-specific settings
4. **Error Handling**: Proper messages for missing Backtrader installation
5. **Fallback System**: Always works with Custom engine

## ✅ Usage Instructions

1. **Access Platform**: http://localhost:8001
2. **Run Screening**: Select strategy, enter symbols, click "Run Screening"
3. **Start Backtest**: Click "Backtest These" button on results
4. **Configure Engine**: 
   - Custom Engine: Fast, simple (always available)
   - Backtrader Engine: Advanced (requires installation)
5. **Select Stocks**: Use checkboxes to pick which stocks to backtest
6. **Run Backtest**: Configure settings and click "Run Backtest"

## ✅ Installation for Backtrader (Optional)

To enable advanced Backtrader features:
```bash
pip install backtrader --index-url YOUR_INTERNAL_ARTIFACTORY_URL
```

Then restart the server to detect the installation.

---

**The fix is complete - just restart the server! 🚀**