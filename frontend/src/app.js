// Quant Trading Platform JavaScript Application

const API_BASE = '';  // Same origin
let globalData = {
    screenerTypes: {},
    popularSymbols: {},
    currentScreen: 'dashboard'
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Quant Trading Platform initializing...');
    loadInitialData();
    checkAPIHealth();
});

// API Helper Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}/api${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showAlert(`API Error: ${error.message}`, 'danger');
        throw error;
    }
}

async function checkAPIHealth() {
    try {
        const health = await apiCall('/health');
        document.getElementById('apiStatus').textContent = 'Online';
        document.getElementById('apiStatus').className = 'text-success';
        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
    } catch (error) {
        document.getElementById('apiStatus').textContent = 'Offline';
        document.getElementById('apiStatus').className = 'text-danger';
    }
}

async function loadInitialData() {
    try {
        // Load screener types
        globalData.screenerTypes = await apiCall('/screener-types');
        populateScreenerTypes();
        
        // Load popular symbols
        globalData.popularSymbols = await apiCall('/popular-symbols');
        updateDashboardStats();
        
    } catch (error) {
        console.error('Failed to load initial data:', error);
    }
}

function populateScreenerTypes() {
    const select = document.getElementById('screenerType');
    select.innerHTML = '<option value="">Select strategy...</option>';
    
    Object.entries(globalData.screenerTypes).forEach(([type, info]) => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = info.name;
        select.appendChild(option);
    });
}

function updateDashboardStats() {
    const totalStrategies = Object.values(globalData.screenerTypes)
        .reduce((sum, type) => sum + type.strategies.length, 0);
    
    document.getElementById('totalStrategies').textContent = totalStrategies;
    document.getElementById('totalStocks').textContent = globalData.popularSymbols.stocks?.length || 0;
    document.getElementById('totalETFs').textContent = globalData.popularSymbols.etfs?.length || 0;
}

// Navigation Functions
function showScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.style.display = 'none';
    });
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected screen
    document.getElementById(`${screenId}-screen`).style.display = 'block';
    event.target.classList.add('active');
    
    globalData.currentScreen = screenId;
}

// Dashboard Functions
function refreshDashboard() {
    loadInitialData();
    checkAPIHealth();
    showAlert('Dashboard refreshed!', 'success');
}

async function quickScreen() {
    try {
        const symbols = globalData.popularSymbols.stocks?.slice(0, 5) || ['AAPL', 'MSFT', 'GOOGL'];
        
        showAlert('Running quick momentum screen...', 'info');
        
        const results = await apiCall('/screen-stocks', {
            method: 'POST',
            body: JSON.stringify({
                symbols: symbols,
                screener_type: 'momentum'
            })
        });
        
        displayQuickResults('Quick Momentum Screen Results', results.results);
        
    } catch (error) {
        showAlert('Quick screen failed. Try the full screener.', 'warning');
    }
}

async function sampleBacktest() {
    try {
        const symbols = ['AAPL', 'MSFT', 'GOOGL'];
        
        showAlert('Running sample backtest...', 'info');
        
        const results = await apiCall('/backtest', {
            method: 'POST',
            body: JSON.stringify({
                symbols: symbols,
                strategy_type: 'equal_weight',
                initial_capital: 100000,
                rebalance_frequency: 'monthly'
            })
        });
        
        displayQuickBacktestResults(results);
        
    } catch (error) {
        showAlert('Sample backtest failed. Try the full backtester.', 'warning');
    }
}

// Screening Functions
function loadPopularStocks() {
    if (globalData.popularSymbols.stocks) {
        document.getElementById('stockSymbols').value = globalData.popularSymbols.stocks.join(',');
    }
}

function loadPopularETFs() {
    if (globalData.popularSymbols.etfs) {
        document.getElementById('stockSymbols').value = globalData.popularSymbols.etfs.join(',');
    }
}

async function runScreening() {
    const screenerType = document.getElementById('screenerType').value;
    const symbolsText = document.getElementById('stockSymbols').value;
    
    if (!screenerType) {
        showAlert('Please select a screening strategy', 'warning');
        return;
    }
    
    if (!symbolsText.trim()) {
        showAlert('Please enter stock symbols', 'warning');
        return;
    }
    
    const symbols = symbolsText.split(',').map(s => s.trim().toUpperCase()).filter(s => s);
    
    // Show loading
    document.getElementById('screeningLoading').style.display = 'block';
    document.getElementById('runScreenBtn').disabled = true;
    
    try {
        const results = await apiCall('/screen-stocks', {
            method: 'POST',
            body: JSON.stringify({
                symbols: symbols,
                screener_type: screenerType
            })
        });
        
        displayScreeningResults(results);
        
    } catch (error) {
        showAlert('Screening failed. Please try again.', 'danger');
    } finally {
        document.getElementById('screeningLoading').style.display = 'none';
        document.getElementById('runScreenBtn').disabled = false;
    }
}

function displayScreeningResults(data) {
    const container = document.getElementById('screeningResults');
    
    if (!data.results || data.results.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-search fa-2x mb-3"></i>
                <p>No stocks passed the screening criteria</p>
                <small>Try adjusting your parameters or selecting different stocks</small>
            </div>
        `;
        return;
    }
    
    // Store results globally for backtesting
    window.currentScreeningResults = data;
    
    let html = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6>Found ${data.results.length} qualifying stocks (from ${data.total_screened} screened)</h6>
            <div class="btn-group">
                <button class="btn btn-sm btn-success" onclick="startIntegratedBacktest()">
                    <i class="fas fa-chart-line me-1"></i>Backtest These
                </button>
                <button class="btn btn-sm btn-outline-primary" onclick="exportResults('screening')">
                    <i class="fas fa-download me-1"></i>Export
                </button>
            </div>
        </div>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Strategy</th>
                        <th>Score</th>
                        <th>P/E Ratio</th>
                        <th>Market Cap</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.results.forEach(result => {
        const scoreClass = result.score > 0.7 ? 'score-high' : 
                          result.score > 0.4 ? 'score-medium' : 'score-low';
        
        const peRatio = result.metrics.pe_ratio ? result.metrics.pe_ratio.toFixed(2) : 'N/A';
        const marketCap = result.metrics.market_cap ? 
                         (result.metrics.market_cap / 1e9).toFixed(1) + 'B' : 'N/A';
        
        html += `
            <tr>
                <td><strong>${result.symbol}</strong></td>
                <td><span class="badge bg-secondary">${result.strategy}</span></td>
                <td><span class="badge strategy-badge ${scoreClass}">${result.score.toFixed(3)}</span></td>
                <td>${peRatio}</td>
                <td>$${marketCap}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="viewStockDetails('${result.symbol}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Backtesting Functions
async function runBacktest() {
    const strategy = document.getElementById('backtestStrategy').value;
    const symbolsText = document.getElementById('backtestSymbols').value;
    const initialCapital = parseFloat(document.getElementById('initialCapital').value);
    const rebalanceFreq = document.getElementById('rebalanceFreq').value;
    
    if (!symbolsText.trim()) {
        showAlert('Please enter stock symbols', 'warning');
        return;
    }
    
    const symbols = symbolsText.split(',').map(s => s.trim().toUpperCase()).filter(s => s);
    
    // Show loading
    document.getElementById('backtestLoading').style.display = 'block';
    document.getElementById('runBacktestBtn').disabled = true;
    
    try {
        const results = await apiCall('/backtest', {
            method: 'POST',
            body: JSON.stringify({
                symbols: symbols,
                strategy_type: strategy,
                initial_capital: initialCapital,
                rebalance_frequency: rebalanceFreq
            })
        });
        
        displayBacktestResults(results);
        
    } catch (error) {
        showAlert('Backtest failed. Please try again.', 'danger');
    } finally {
        document.getElementById('backtestLoading').style.display = 'none';
        document.getElementById('runBacktestBtn').disabled = false;
    }
}

function displayBacktestResults(data) {
    const container = document.getElementById('backtestResults');
    const perf = data.performance;
    
    const totalReturnClass = perf.total_return >= 0 ? 'positive' : 'negative';
    const sharpeClass = perf.sharpe_ratio >= 1 ? 'positive' : perf.sharpe_ratio >= 0 ? 'text-warning' : 'negative';
    
    let html = `
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card p-3">
                    <h5>Performance Summary</h5>
                    <div class="row text-center">
                        <div class="col-6">
                            <h4 class="${totalReturnClass}">${(perf.total_return * 100).toFixed(2)}%</h4>
                            <small>Total Return</small>
                        </div>
                        <div class="col-6">
                            <h4 class="${totalReturnClass}">${(perf.annual_return * 100).toFixed(2)}%</h4>
                            <small>Annual Return</small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card p-3">
                    <h5>Risk Metrics</h5>
                    <div class="row text-center">
                        <div class="col-6">
                            <h4 class="${sharpeClass}">${perf.sharpe_ratio.toFixed(2)}</h4>
                            <small>Sharpe Ratio</small>
                        </div>
                        <div class="col-6">
                            <h4 class="negative">${(perf.max_drawdown * 100).toFixed(2)}%</h4>
                            <small>Max Drawdown</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card p-3">
                    <h5>Detailed Metrics</h5>
                    <div class="row">
                        <div class="col-md-3 text-center">
                            <strong>$${perf.final_capital.toLocaleString()}</strong>
                            <br><small>Final Capital</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <strong>${(perf.win_rate * 100).toFixed(1)}%</strong>
                            <br><small>Win Rate</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <strong>${perf.number_of_trades}</strong>
                            <br><small>Total Trades</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <strong>${perf.sortino_ratio.toFixed(2)}</strong>
                            <br><small>Sortino Ratio</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add equity curve chart
    if (data.equity_curve && data.equity_curve.length > 0) {
        html += `
            <div class="card p-3 mb-4">
                <h5>Equity Curve</h5>
                <canvas id="equityChart" width="400" height="200"></canvas>
            </div>
        `;
    }
    
    // Add trades table if available
    if (data.trades && data.trades.length > 0) {
        html += `
            <div class="card p-3">
                <h5>Recent Trades</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Entry Date</th>
                                <th>Exit Date</th>
                                <th>P&L</th>
                                <th>P&L %</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        data.trades.slice(-10).forEach(trade => {
            const pnlClass = trade.pnl >= 0 ? 'positive' : 'negative';
            html += `
                <tr>
                    <td>${trade.symbol}</td>
                    <td>${new Date(trade.entry_date).toLocaleDateString()}</td>
                    <td>${new Date(trade.exit_date).toLocaleDateString()}</td>
                    <td class="${pnlClass}">$${trade.pnl.toFixed(2)}</td>
                    <td class="${pnlClass}">${(trade.pnl_pct * 100).toFixed(2)}%</td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div></div>';
    }
    
    container.innerHTML = html;
    
    // Draw equity curve chart if data exists
    if (data.equity_curve && data.equity_curve.length > 0) {
        setTimeout(() => drawEquityChart(data.equity_curve), 100);
    }
}

function drawEquityChart(equityData) {
    const ctx = document.getElementById('equityChart');
    if (!ctx) return;
    
    const labels = equityData.map(point => new Date(point.date).toLocaleDateString());
    const values = equityData.map(point => point.value);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Portfolio Value',
                data: values,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Utility Functions
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function displayQuickResults(title, results) {
    if (!results || results.length === 0) {
        showAlert('No results found', 'warning');
        return;
    }
    
    const topResult = results[0];
    showAlert(`${title}: Top pick is ${topResult.symbol} (score: ${topResult.score.toFixed(3)})`, 'success');
}

function displayQuickBacktestResults(results) {
    const perf = results.performance;
    const message = `Sample Backtest Complete! Total Return: ${(perf.total_return * 100).toFixed(2)}%, Sharpe: ${perf.sharpe_ratio.toFixed(2)}`;
    showAlert(message, 'success');
}

async function viewStockDetails(symbol) {
    try {
        const data = await apiCall(`/stock-info/${symbol}`);
        
        // Create modal or detailed view
        showAlert(`${symbol}: $${data.current_price.toFixed(2)}, 1M: ${(data.performance.return_1m * 100).toFixed(2)}%`, 'info');
        
    } catch (error) {
        showAlert(`Failed to load details for ${symbol}`, 'danger');
    }
}

// Integrated Backtesting Functions
async function startIntegratedBacktest() {
    if (!window.currentScreeningResults) {
        showAlert('No screening results available for backtesting', 'warning');
        return;
    }
    
    try {
        // Get backtest suggestions based on screening results
        showAlert('Getting backtest suggestions...', 'info');
        
        const suggestions = await apiCall('/get-backtest-suggestions', {
            method: 'POST',
            body: JSON.stringify(window.currentScreeningResults)
        });
        
        // Show backtest configuration modal
        showBacktestConfigModal(suggestions.suggestions);
        
    } catch (error) {
        showAlert('Failed to get backtest suggestions', 'danger');
    }
}

function showBacktestConfigModal(suggestions) {
    const modalHtml = `
        <div class="modal fade" id="backtestConfigModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Configure Backtest</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Engine Selection -->
                        <div class="mb-4">
                            <h6>Backtesting Engine</h6>
                            <div class="btn-group w-100" role="group" id="engineSelection">
                                <input type="radio" class="btn-check" name="engine" id="engine_custom" value="custom" checked onchange="toggleEngineSettings()">
                                <label class="btn btn-outline-primary" for="engine_custom">
                                    <i class="fas fa-rocket me-1"></i>Custom (Fast)
                                </label>
                                <input type="radio" class="btn-check" name="engine" id="engine_backtrader" value="backtrader" onchange="toggleEngineSettings()">
                                <label class="btn btn-outline-success" for="engine_backtrader">
                                    <i class="fas fa-cog me-1"></i>Backtrader (Advanced)
                                </label>
                            </div>
                            <small class="text-muted d-block mt-1" id="engineDescription">
                                Custom engine: Simple, fast backtesting with pandas/numpy
                            </small>
                        </div>

                        <div class="row">
                            <div class="col-md-6">
                                <h6>Basic Settings</h6>
                                <div class="mb-3">
                                    <label class="form-label">Initial Capital ($)</label>
                                    <input type="number" class="form-control" id="btInitialCapital" value="${suggestions.initial_capital}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Max Positions</label>
                                    <input type="number" class="form-control" id="btMaxPositions" value="${suggestions.max_positions}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Rebalance Frequency</label>
                                    <select class="form-select" id="btRebalanceFreq">
                                        <option value="weekly" ${suggestions.rebalance_frequency === 'weekly' ? 'selected' : ''}>Weekly</option>
                                        <option value="monthly" ${suggestions.rebalance_frequency === 'monthly' ? 'selected' : ''}>Monthly</option>
                                        <option value="quarterly">Quarterly</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6 id="advancedSettingsTitle">Advanced Settings</h6>
                                <div class="mb-3">
                                    <label class="form-label">Commission (%)</label>
                                    <input type="number" step="0.001" class="form-control" id="btCommission" value="${suggestions.commission * 100}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Slippage (%)</label>
                                    <input type="number" step="0.001" class="form-control" id="btSlippage" value="${suggestions.slippage * 100}">
                                </div>
                                <div class="mb-3" id="lookbackSection">
                                    <label class="form-label">Lookback Period</label>
                                    <select class="form-select" id="btLookback">
                                        <option value="6mo">6 Months</option>
                                        <option value="1y" ${suggestions.lookback_period === '1y' ? 'selected' : ''}>1 Year</option>
                                        <option value="2y" ${suggestions.lookback_period === '2y' ? 'selected' : ''}>2 Years</option>
                                        <option value="3y">3 Years</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Backtrader-specific settings (hidden by default) -->
                        <div id="backtraderSettings" style="display: none;">
                            <div class="border-top pt-3 mt-3">
                                <h6 class="text-success">
                                    <i class="fas fa-cog me-1"></i>Backtrader Advanced Settings
                                </h6>
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">RSI Period</label>
                                            <input type="number" class="form-control form-control-sm" id="btRsiPeriod" value="14" min="5" max="50">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">RSI Lower</label>
                                            <input type="number" class="form-control form-control-sm" id="btRsiLower" value="30" min="10" max="40">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">RSI Upper</label>
                                            <input type="number" class="form-control form-control-sm" id="btRsiUpper" value="70" min="60" max="90">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Momentum Period</label>
                                            <input type="number" class="form-control form-control-sm" id="btMomentumPeriod" value="10" min="5" max="30">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Momentum Threshold (%)</label>
                                            <input type="number" step="0.01" class="form-control form-control-sm" id="btMomentumThreshold" value="5.0" min="1" max="20">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">SMA Period</label>
                                            <input type="number" class="form-control form-control-sm" id="btSmaPeriod" value="20" min="10" max="50">
                                        </div>
                                    </div>
                                </div>
                                <div class="alert alert-info alert-sm">
                                    <small>
                                        <i class="fas fa-info-circle me-1"></i>
                                        <strong>Note:</strong> Backtrader uses more sophisticated technical indicators and order management. 
                                        These settings will be applied only if Backtrader is installed.
                                    </small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <h6>Select Symbols for Backtesting</h6>
                            <div class="border p-3 rounded" style="max-height: 200px; overflow-y: auto;">
                                <div class="mb-2">
                                    <button type="button" class="btn btn-sm btn-outline-primary me-2" onclick="selectAllStocks()">Select All</button>
                                    <button type="button" class="btn btn-sm btn-outline-secondary me-2" onclick="deselectAllStocks()">Deselect All</button>
                                    <small class="text-muted">(<span id="selectedCount">${window.currentScreeningResults.results.length}</span> selected)</small>
                                </div>
                                <div class="row" id="stockSelection">
                                    ${window.currentScreeningResults.results.map((r, index) => `
                                        <div class="col-md-6 mb-2">
                                            <div class="form-check">
                                                <input class="form-check-input stock-checkbox" type="checkbox" 
                                                       value="${r.symbol}" id="stock_${index}" checked 
                                                       onchange="updateSelectedCount()">
                                                <label class="form-check-label d-flex justify-content-between align-items-center" for="stock_${index}">
                                                    <span><strong>${r.symbol}</strong></span>
                                                    <span class="badge bg-secondary ms-2">${r.score.toFixed(3)}</span>
                                                </label>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3 p-3 bg-light rounded">
                            <small>
                                <strong>Strategy:</strong> ${window.currentScreeningResults.results[0]?.strategy || 'Screening-based'}<br>
                                <strong>Risk Level:</strong> ${suggestions.risk_level || 'Moderate'}<br>
                                <strong>Expected Duration:</strong> 2-5 minutes
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="runIntegratedBacktest()">
                            <i class="fas fa-play me-1"></i>Run Backtest
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('backtestConfigModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('backtestConfigModal'));
    modal.show();
}

// Engine switching functionality
function toggleEngineSettings() {
    const selectedEngine = document.querySelector('input[name="engine"]:checked').value;
    const backtraderSettings = document.getElementById('backtraderSettings');
    const engineDescription = document.getElementById('engineDescription');
    
    if (selectedEngine === 'backtrader') {
        backtraderSettings.style.display = 'block';
        engineDescription.textContent = 'Backtrader: Advanced backtesting with sophisticated technical indicators';
    } else {
        backtraderSettings.style.display = 'none';
        engineDescription.textContent = 'Custom engine: Simple, fast backtesting with pandas/numpy';
    }
}

async function runIntegratedBacktest() {
    // Get selected engine
    const selectedEngine = document.querySelector('input[name="engine"]:checked').value;
    
    // Get configuration values
    const config = {
        engine: selectedEngine,
        initial_capital: parseFloat(document.getElementById('btInitialCapital').value),
        max_positions: parseInt(document.getElementById('btMaxPositions').value),
        rebalance_frequency: document.getElementById('btRebalanceFreq').value,
        commission: parseFloat(document.getElementById('btCommission').value) / 100,
        slippage: parseFloat(document.getElementById('btSlippage').value) / 100,
        lookback_period: document.getElementById('btLookback').value
    };
    
    // Add Backtrader-specific settings if selected
    if (selectedEngine === 'backtrader') {
        config.backtrader_settings = {
            rsi_period: parseInt(document.getElementById('btRsiPeriod').value),
            rsi_lower: parseFloat(document.getElementById('btRsiLower').value),
            rsi_upper: parseFloat(document.getElementById('btRsiUpper').value),
            momentum_period: parseInt(document.getElementById('btMomentumPeriod').value),
            momentum_threshold: parseFloat(document.getElementById('btMomentumThreshold').value) / 100,
            sma_period: parseInt(document.getElementById('btSmaPeriod').value)
        };
    }
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('backtestConfigModal'));
    modal.hide();
    
    // Get selected symbols from checkboxes
    const selectedCheckboxes = document.querySelectorAll('.stock-checkbox:checked');
    const symbols = Array.from(selectedCheckboxes).map(cb => cb.value);
    const screenerType = document.getElementById('screenerType').value;
    
    if (symbols.length === 0) {
        showAlert('Please select at least one stock for backtesting', 'warning');
        return;
    }
    
    try {
        showAlert('Running integrated backtest... This may take a few minutes.', 'info');
        
        // Show loading in backtest screen
        showScreen('backtest');
        document.getElementById('backtestResults').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
                <h5>Running Backtest</h5>
                <p>Testing ${symbols.length} stocks using ${screenerType} screening strategy...</p>
            </div>
        `;
        
        // Run backtest with proper error handling and extended timeout
        const response = await fetch(`${API_BASE}/api/run-integrated-backtest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbols: symbols,
                screener_type: screenerType,
                backtest_settings: config
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const results = await response.json();
        
        // Check if installation is required
        if (results.installation_required) {
            showAlert('Backtrader not installed. Please install from your internal artifactory.', 'warning');
            document.getElementById('backtestResults').innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-download fa-3x mb-3 text-warning"></i>
                    <h5>Backtrader Installation Required</h5>
                    <p class="mb-3">Backtrader is not installed. Please install from your internal artifactory.</p>
                    <div class="alert alert-warning">
                        <strong>Installation Command:</strong><br>
                        <code>pip install backtrader --index-url YOUR_INTERNAL_ARTIFACTORY_URL</code>
                    </div>
                    <button class="btn btn-primary" onclick="document.getElementById('engine_custom').checked = true; toggleEngineSettings();">
                        Switch to Custom Engine
                    </button>
                </div>
            `;
            return;
        }
        
        // Display results
        displayBacktestResults(results);
        const engineUsed = results.strategy_info?.engine || selectedEngine;
        showAlert(`Integrated backtest completed successfully using ${engineUsed}!`, 'success');
        
    } catch (error) {
        console.error('Integrated backtest error:', error);
        const errorMessage = error.message.includes('timeout') ? 
            'Backtest timed out. Try with fewer stocks or shorter time period.' :
            `Backtest failed: ${error.message}`;
        
        showAlert(errorMessage, 'danger');
        document.getElementById('backtestResults').innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                <p>Backtest failed: ${error.message}</p>
                <small class="text-muted">Try reducing the number of stocks or adjusting parameters.</small>
            </div>
        `;
    }
}

// Stock selection helper functions
function selectAllStocks() {
    const checkboxes = document.querySelectorAll('.stock-checkbox');
    checkboxes.forEach(cb => cb.checked = true);
    updateSelectedCount();
}

function deselectAllStocks() {
    const checkboxes = document.querySelectorAll('.stock-checkbox');
    checkboxes.forEach(cb => cb.checked = false);
    updateSelectedCount();
}

function updateSelectedCount() {
    const selectedCheckboxes = document.querySelectorAll('.stock-checkbox:checked');
    const count = selectedCheckboxes.length;
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = count;
    }
}

function exportResults(type) {
    showAlert(`Export functionality for ${type} results coming soon!`, 'info');
}