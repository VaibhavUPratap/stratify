import { useState, useEffect } from 'react';
import { api } from './api';
import type { DashboardMetrics, BusinessHealth, AlertItem, TimelineEvent, ForecastResponse, DemandForecastResponse, RiskResponse, AgentReport, RecommendationItem, SimulationResult } from './api';

function App() {
  const [theme, setTheme] = useState('dark');
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'forecast' | 'risk' | 'agents' | 'simulate' | 'chat' | 'upload' | 'history'>('dashboard');
  
  // Dashboard & Metrics State
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [health, setHealth] = useState<BusinessHealth | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  
  // Forecast States
  const [revForecast, setRevForecast] = useState<ForecastResponse | null>(null);
  const [cashForecast, setCashForecast] = useState<ForecastResponse | null>(null);
  const [demandForecast, setDemandForecast] = useState<DemandForecastResponse[]>([]);
  const [inventoryForecast, setInventoryForecast] = useState<DemandForecastResponse[]>([]);
  
  // Risk & Pricing
  const [custRisks, setCustRisks] = useState<RiskResponse[]>([]);
  const [suppRisks, setSuppRisks] = useState<RiskResponse[]>([]);
  const [pricingRecs, setPricingRecs] = useState<any[]>([]);

  // Agent Engine
  const [agentReports, setAgentReports] = useState<AgentReport[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [explanation, setExplanation] = useState<any>(null);

  // Digital Twin Simulation State
  const [priceChange, setPriceChange] = useState(0.0);
  const [hiringCost, setHiringCost] = useState(0.0);
  const [supplierChange, setSupplierChange] = useState('standard');
  const [inventoryDecision, setInventoryDecision] = useState('standard');
  const [loanDecision, setLoanDecision] = useState('no_loan');
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const [simulating, setSimulating] = useState(false);

  // Chat State
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ sender: 'user' | 'gemma'; text: string }>>([]);
  const [chatLoading, setChatLoading] = useState(false);

  // Upload States
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadType, setUploadType] = useState<'invoice' | 'gst' | 'bank' | 'excel'>('invoice');
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [parsedMetadata, setParsedMetadata] = useState<any>(null);

  // History State
  const [decisionHistory, setDecisionHistory] = useState<any[]>([]);

  // Apply Theme class
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Load Dashboard baseline on mount
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const dash = await api.getDashboard();
      setMetrics(dash.metrics);
      
      const bh = await api.getBusinessHealth();
      setHealth(bh);
      
      const al = await api.getAlerts();
      setAlerts(al);
      
      const tl = await api.getTimeline();
      setTimeline(tl);
    } catch (e) {
      console.error('Failed to load dashboard:', e);
    }
  };

  // Load contextual tab data
  useEffect(() => {
    if (currentPage === 'forecast') {
      api.getRevenueForecast().then(setRevForecast);
      api.getCashflowForecast().then(setCashForecast);
      api.getDemandForecast().then(setDemandForecast);
      api.getInventoryForecast().then(setInventoryForecast);
    } else if (currentPage === 'risk') {
      api.getCustomerRisks().then(setCustRisks);
      api.getSupplierRisks().then(setSuppRisks);
      api.getPricingRecommendations().then(setPricingRecs);
    } else if (currentPage === 'agents') {
      api.getAgentReports().then(res => setAgentReports(res.reports));
      api.getRecommendations().then(setRecommendations);
    } else if (currentPage === 'history') {
      api.getDecisionHistory().then(setDecisionHistory);
    }
  }, [currentPage]);

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    const userQ = question;
    setChatHistory(prev => [...prev, { sender: 'user', text: userQ }]);
    setQuestion('');
    setChatLoading(true);
    
    try {
      const res = await api.sendChat(userQ);
      setChatHistory(prev => [...prev, { sender: 'gemma', text: res.response }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { sender: 'gemma', text: 'Error fetching AI response.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const res = await api.simulate({
        price_change_pct: priceChange,
        hiring_cost: hiringCost,
        supplier_change: supplierChange,
        inventory_decisions: inventoryDecision,
        loan_decisions: loanDecision
      });
      setSimResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setSimulating(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploadStatus('Processing document...');
    setParsedMetadata(null);
    try {
      const res = await api.uploadFile(uploadType, uploadFile);
      setUploadStatus('Document processed & saved to Business Memory.');
      setParsedMetadata(res.parsed_metadata);
      loadDashboardData(); // Refresh timeline event
    } catch (e) {
      setUploadStatus('Failed to upload document.');
    }
  };

  const handleDecision = async (id: number, action: 'Approve' | 'Decline') => {
    try {
      await api.logDecision(id, action);
      // Reload recommendations to update state
      api.getRecommendations().then(setRecommendations);
      alert(`Recommendation successfully logged as: ${action}`);
    } catch (e) {
      console.error(e);
    }
  };

  const handleExplain = async (id: number) => {
    try {
      const exp = await api.explainRecommendation(id);
      setExplanation(exp);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--color-paper)' }}>
      {/* Sidebar Navigation */}
      <aside style={{ width: '260px', borderRight: '1px solid var(--color-rule)', display: 'flex', flexDirection: 'column', padding: 'var(--space-md)', background: 'var(--color-paper-2)' }}>
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h1 style={{ fontSize: 'var(--text-lg)', margin: 0, fontWeight: '700' }}>Stratify</h1>
          <span style={{ color: 'var(--color-muted)', fontSize: 'var(--text-xs)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>SME Operating System</span>
        </div>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2xs)', flexGrow: 1 }}>
          {[
            { id: 'dashboard', label: 'Console' },
            { id: 'forecast', label: 'Forecasts' },
            { id: 'risk', label: 'Risk Models' },
            { id: 'agents', label: 'CEO Agents' },
            { id: 'simulate', label: 'Digital Twin' },
            { id: 'chat', label: 'Gemma Chat' },
            { id: 'upload', label: 'Document Ingestion' },
            { id: 'history', label: 'Decision Logs' }
          ].map(tab => (
            <button 
              key={tab.id}
              onClick={() => setCurrentPage(tab.id as any)}
              className={currentPage === tab.id ? 'btn-primary' : 'btn-secondary'}
              style={{
                textAlign: 'left',
                justifyContent: 'flex-start',
                borderLeft: currentPage === tab.id ? '4px solid var(--color-accent)' : '1px solid transparent',
                borderRadius: '0 var(--radius-button) var(--radius-button) 0'
              }}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div style={{ marginTop: 'auto', borderTop: '1px solid var(--color-rule)', paddingTop: 'var(--space-md)' }}>
          <button className="btn-secondary" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} style={{ width: '100%' }}>
            Toggle {theme === 'dark' ? 'Light' : 'Dark'} Mode
          </button>
        </div>
      </aside>

      {/* Main Workbench Viewport */}
      <main style={{ flexGrow: 1, padding: 'var(--space-xl)', overflowY: 'auto' }}>
        {/* Header telemetry status */}
        {health && (
          <div className="flex-between" style={{ borderBottom: '1px solid var(--color-rule)', paddingBottom: 'var(--space-md)', marginBottom: 'var(--space-xl)' }}>
            <div>
              <h2 style={{ margin: 0, fontSize: 'var(--text-xl)' }}>
                {currentPage.charAt(0).toUpperCase() + currentPage.slice(1)} Workbench
              </h2>
              <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-ink-2)' }}>Apex Industrial Solutions</span>
            </div>
            <div className="flex-center" style={{ gap: 'var(--space-md)' }}>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>Corporate Health Score</span>
                <div style={{ fontWeight: '600', color: health.health_score > 70 ? 'var(--color-success)' : 'var(--color-warning)' }}>
                  {health.health_score}/100
                </div>
              </div>
              <div style={{ textAlign: 'right', borderLeft: '1px solid var(--color-rule)', paddingLeft: 'var(--space-md)' }}>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>Total Cash Balance</span>
                <div style={{ fontWeight: '600', color: 'var(--color-ink)' }}>
                  $185,200.50
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 1. Dashboard View */}
        {currentPage === 'dashboard' && metrics && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            {/* Bento Grid KPIs */}
            <div className="bento-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
              <div className="card glass-panel">
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>Total Revenue</span>
                <h3 style={{ fontSize: 'var(--text-xl)', margin: 'var(--space-2xs) 0' }}>${metrics.total_revenue.toLocaleString()}</h3>
                <span style={{ color: 'var(--color-success)', fontSize: 'var(--text-xs)' }}>+5.2% from forecast</span>
              </div>
              <div className="card glass-panel">
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>Net Working Capital</span>
                <h3 style={{ fontSize: 'var(--text-xl)', margin: 'var(--space-2xs) 0' }}>${metrics.net_working_capital.toLocaleString()}</h3>
                <span style={{ color: 'var(--color-muted)', fontSize: 'var(--text-xs)' }}>AR vs AP balances</span>
              </div>
              <div className="card glass-panel">
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>Accounts Receivable</span>
                <h3 style={{ fontSize: 'var(--text-xl)', margin: 'var(--space-2xs) 0' }}>${metrics.accounts_receivable.toLocaleString()}</h3>
                <span style={{ color: 'var(--color-warning)', fontSize: 'var(--text-xs)' }}>1 Outstanding Invoice</span>
              </div>
              <div className="card glass-panel">
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>Accounts Payable</span>
                <h3 style={{ fontSize: 'var(--text-xl)', margin: 'var(--space-2xs) 0' }}>${metrics.accounts_payable.toLocaleString()}</h3>
                <span style={{ color: 'var(--color-muted)', fontSize: 'var(--text-xs)' }}>1 Upcoming Bill</span>
              </div>
            </div>

            {/* Split Panel: Alerts & Timeline */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
              <div className="card">
                <h3>Active Operational Alerts</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                  {alerts.map((alert, i) => (
                    <div key={i} style={{
                      padding: 'var(--space-xs)',
                      background: alert.severity === 'CRITICAL' ? 'var(--color-error-dim)' : 'var(--color-warning-dim)',
                      color: alert.severity === 'CRITICAL' ? 'var(--color-error)' : 'var(--color-warning)',
                      border: '1px solid currentColor',
                      borderRadius: '4px'
                    }}>
                      <div style={{ fontWeight: '600' }}>{alert.title}</div>
                      <div style={{ fontSize: 'var(--text-sm)', opacity: 0.9 }}>{alert.message}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card">
                <h3>Business Memory timeline</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                  {timeline.map((event) => (
                    <div key={event.id} style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 'var(--space-2xs)', borderBottom: '1px solid var(--color-rule-2)' }}>
                      <div>
                        <span style={{ fontWeight: '500', fontSize: 'var(--text-sm)' }}>{event.description}</span>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>Source: {event.event_type}</div>
                      </div>
                      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 2. Forecasts View */}
        {currentPage === 'forecast' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
              {revForecast && (
                <div className="card">
                  <h3>Revenue Projection (90-Day)</h3>
                  <p>{revForecast.prediction}</p>
                  <div style={{ background: 'var(--color-paper-2)', padding: 'var(--space-sm)', borderRadius: '6px' }}>
                    <div style={{ fontSize: 'var(--text-sm)' }}><strong>Confidence Score:</strong> {revForecast.confidence_score * 100}%</div>
                    <div style={{ fontSize: 'var(--text-sm)' }}><strong>Feature Weights:</strong> {revForecast.important_features.join(', ')}</div>
                    <div style={{ fontSize: 'var(--text-sm)' }}><strong>Suggested Action:</strong> {revForecast.suggested_action}</div>
                  </div>
                </div>
              )}

              {cashForecast && (
                <div className="card">
                  <h3>Cash Flow Forecast (30-Day)</h3>
                  <p>{cashForecast.prediction}</p>
                  <div style={{ background: 'var(--color-paper-2)', padding: 'var(--space-sm)', borderRadius: '6px' }}>
                    <div style={{ fontSize: 'var(--text-sm)' }}><strong>Confidence Score:</strong> {cashForecast.confidence_score * 100}%</div>
                    <div style={{ fontSize: 'var(--text-sm)' }}><strong>Business Impact:</strong> {cashForecast.business_impact}</div>
                    <div style={{ fontSize: 'var(--text-sm)' }}><strong>Suggested Action:</strong> {cashForecast.suggested_action}</div>
                  </div>
                </div>
              )}
            </div>

            <div className="card">
              <h3>Demand forecasting</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 'var(--space-sm)' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--color-rule)' }}>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Product</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>SKU</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Prediction</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Suggested Action</th>
                  </tr>
                </thead>
                <tbody>
                  {demandForecast.map((item, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--color-rule-2)' }}>
                      <td style={{ padding: '8px' }}>{item.name}</td>
                      <td style={{ padding: '8px' }}>{item.sku}</td>
                      <td style={{ padding: '8px' }}>{item.prediction}</td>
                      <td style={{ padding: '8px' }}>{item.suggested_action}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {inventoryForecast.length > 0 && (
              <div className="card">
                <h3>Inventory & Stockout Forecasting</h3>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 'var(--space-sm)' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid var(--color-rule)' }}>
                      <th style={{ textAlign: 'left', padding: '8px' }}>Product</th>
                      <th style={{ textAlign: 'left', padding: '8px' }}>SKU</th>
                      <th style={{ textAlign: 'left', padding: '8px' }}>Prediction Indicators</th>
                      <th style={{ textAlign: 'left', padding: '8px' }}>Suggested Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventoryForecast.map((item, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid var(--color-rule-2)' }}>
                        <td style={{ padding: '8px' }}>{item.name}</td>
                        <td style={{ padding: '8px' }}>{item.sku}</td>
                        <td style={{ padding: '8px' }}>{item.prediction}</td>
                        <td style={{ padding: '8px' }}>{item.suggested_action}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* 3. Risk Models View */}
        {currentPage === 'risk' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <div className="card">
              <h3>Customer Churn & Payment Volatility</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--color-rule)' }}>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Customer</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Late Payment Risk</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Action Plan</th>
                  </tr>
                </thead>
                <tbody>
                  {custRisks.map((c, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--color-rule-2)' }}>
                      <td style={{ padding: '8px' }}>{c.name}</td>
                      <td style={{ padding: '8px' }}>{c.prediction}</td>
                      <td style={{ padding: '8px' }}>{c.suggested_action}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="card">
              <h3>Supplier Delivery delays</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--color-rule)' }}>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Supplier</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Delay Risk</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Mitigation Action</th>
                  </tr>
                </thead>
                <tbody>
                  {suppRisks.map((s, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--color-rule-2)' }}>
                      <td style={{ padding: '8px' }}>{s.name}</td>
                      <td style={{ padding: '8px' }}>{s.prediction}</td>
                      <td style={{ padding: '8px' }}>{s.suggested_action}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {pricingRecs.length > 0 && (
              <div className="card">
                <h3>Optimal Margin Pricing Recommendations</h3>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid var(--color-rule)' }}>
                      <th style={{ textAlign: 'left', padding: '8px' }}>Product</th>
                      <th style={{ textAlign: 'left', padding: '8px' }}>SKU</th>
                      <th style={{ textAlign: 'left', padding: '8px' }}>Recommended Adjustments</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pricingRecs.map((p, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid var(--color-rule-2)' }}>
                        <td style={{ padding: '8px' }}>{p.name}</td>
                        <td style={{ padding: '8px' }}>{p.sku}</td>
                        <td style={{ padding: '8px' }}>{p.prediction}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* 4. Agents & Recommendations View */}
        {currentPage === 'agents' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <div className="card">
              <h3>CEO Strategic Recommendations Consensus</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', marginTop: 'var(--space-sm)' }}>
                {recommendations.map(rec => (
                  <div key={rec.id} style={{ border: '1px solid var(--color-rule)', borderRadius: 'var(--radius-card)', padding: 'var(--space-md)' }}>
                    <div className="flex-between">
                      <span style={{ fontWeight: '600', textTransform: 'uppercase', fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>
                        {rec.agent_name} Report
                      </span>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: 'var(--text-xs)',
                        background: rec.risk === 'CRITICAL' ? 'var(--color-error-dim)' : 'var(--color-warning-dim)',
                        color: rec.risk === 'CRITICAL' ? 'var(--color-error)' : 'var(--color-warning)'
                      }}>{rec.risk} RISK</span>
                    </div>
                    
                    <h4 style={{ margin: 'var(--space-2xs) 0' }}>{rec.action}</h4>
                    <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-ink-2)' }}>{rec.reasoning}</p>
                    
                    <div className="flex-between" style={{ marginTop: 'var(--space-sm)' }}>
                      <button className="btn-secondary" onClick={() => handleExplain(rec.id)}>Audit Evidence</button>
                      <div className="flex-center" style={{ gap: 'var(--space-xs)' }}>
                        <button className="btn-secondary" onClick={() => handleDecision(rec.id, 'Decline')} style={{ color: 'var(--color-error)' }}>Decline</button>
                        <button className="btn-primary" onClick={() => handleDecision(rec.id, 'Approve')}>Approve</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {agentReports.length > 0 && (
              <div className="card">
                <h3>Specialist Agent Real-Time Diagnostics</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-md)', marginTop: 'var(--space-sm)' }}>
                  {agentReports.map((rep, idx) => (
                    <div key={idx} className="card glass-panel" style={{ padding: 'var(--space-sm)' }}>
                      <strong>{rep.agent_name}</strong>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)', marginTop: '4px' }}>{rep.role}</div>
                      <div style={{ fontSize: 'var(--text-sm)', marginTop: '8px', color: 'var(--color-ink)' }}>{rep.analysis}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {explanation && (
              <div className="card glass-panel" style={{ border: '1px solid var(--color-success)' }}>
                <h3>Auditable Explainability Log</h3>
                <p><strong>Evidentiary Details:</strong> {explanation.evidence}</p>
                <p><strong>Business Impact:</strong> {explanation.business_impact}</p>
                <p><strong>Affected Departments:</strong> {explanation.affected_departments.join(', ')}</p>
                <button className="btn-secondary" onClick={() => setExplanation(null)}>Close Audit File</button>
              </div>
            )}
          </div>
        )}

        {/* 5. Digital Twin Simulation View */}
        {currentPage === 'simulate' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
            <div className="card">
              <h3>What-If Simulation Inputs</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', marginTop: 'var(--space-sm)' }}>
                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-sm)', marginBottom: '4px' }}>Price Adjustments: {priceChange}%</label>
                  <input type="range" min="-30" max="30" step="1" value={priceChange} onChange={e => setPriceChange(parseFloat(e.target.value))} style={{ width: '100%' }} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-sm)', marginBottom: '4px' }}>Hiring Budget: ${hiringCost.toLocaleString()}</label>
                  <input type="range" min="0" max="50000" step="1000" value={hiringCost} onChange={e => setHiringCost(parseFloat(e.target.value))} style={{ width: '100%' }} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-sm)', marginBottom: '4px' }}>Supplier Protocol</label>
                  <select value={supplierChange} onChange={e => setSupplierChange(e.target.value)} style={{ width: '100%' }}>
                    <option value="standard">Maintain standard supplier relations</option>
                    <option value="diversify">Diversify suppliers (reduces concentration risk)</option>
                    <option value="cheaper_alternative">Partner with cheaper alternative supplier</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-sm)', marginBottom: '4px' }}>Inventory Strategy</label>
                  <select value={inventoryDecision} onChange={e => setInventoryDecision(e.target.value)} style={{ width: '100%' }}>
                    <option value="standard">Standard inventory reorder levels</option>
                    <option value="bulk_buy">Bulk Buy (requires cash, lowers cost margin)</option>
                    <option value="just_in_time">Just-In-Time replenishment</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-sm)', marginBottom: '4px' }}>Corporate Loan</label>
                  <select value={loanDecision} onChange={e => setLoanDecision(e.target.value)} style={{ width: '100%' }}>
                    <option value="no_loan">No Loan</option>
                    <option value="take_loan">Take $50,000 corporate liquidity loan</option>
                  </select>
                </div>

                <button className="btn-primary" onClick={handleSimulate} disabled={simulating}>
                  {simulating ? 'Calculating Twin Forecasts...' : 'Run Simulation'}
                </button>
              </div>
            </div>

            <div className="card">
              <h3>Simulated Business Health Forecast</h3>
              {simResult ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', marginTop: 'var(--space-sm)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-rule-2)', paddingBottom: 'var(--space-2xs)' }}>
                    <span>Projected Revenue</span>
                    <strong style={{ fontSize: 'var(--text-md)' }}>${simResult.revenue.toLocaleString()}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-rule-2)', paddingBottom: 'var(--space-2xs)' }}>
                    <span>Projected Profit</span>
                    <strong style={{ fontSize: 'var(--text-md)' }}>${simResult.profit.toLocaleString()}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-rule-2)', paddingBottom: 'var(--space-2xs)' }}>
                    <span>Cash Flow State</span>
                    <strong style={{ color: simResult.cash_flow === 'Positive' ? 'var(--color-success)' : 'var(--color-error)' }}>{simResult.cash_flow}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-rule-2)', paddingBottom: 'var(--space-2xs)' }}>
                    <span>Calculated Enterprise Risk</span>
                    <strong style={{ color: simResult.risk === 'LOW' ? 'var(--color-success)' : 'var(--color-warning)' }}>{simResult.risk}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-rule-2)', paddingBottom: 'var(--space-2xs)' }}>
                    <span>Warehouse Stocks</span>
                    <strong>{simResult.inventory}</strong>
                  </div>
                  
                  <div style={{ textAlign: 'center', marginTop: 'var(--space-md)', padding: 'var(--space-md)', background: 'var(--color-paper-2)', borderRadius: '8px' }}>
                    <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-muted)' }}>Resulting Health Score</div>
                    <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '700', color: 'var(--color-accent)' }}>{simResult.business_health}/100</div>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: 'var(--color-muted)', marginTop: 'var(--space-xl)' }}>
                  Awaiting simulation execution... Adjust the sliders and run.
                </div>
              )}
            </div>
          </div>
        )}

        {/* 6. Gemma Chat View */}
        {currentPage === 'chat' && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '80vh' }}>
            <h3>Context-Aware Chat</h3>
            <div style={{ flexGrow: 1, overflowY: 'auto', border: '1px solid var(--color-rule)', borderRadius: 'var(--radius-card)', padding: 'var(--space-md)', background: 'var(--color-paper-2)', marginBottom: 'var(--space-md)' }}>
              {chatHistory.map((chat, i) => (
                <div key={i} style={{
                  marginBottom: 'var(--space-md)',
                  textAlign: chat.sender === 'user' ? 'right' : 'left'
                }}>
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-muted)' }}>{chat.sender === 'user' ? 'You' : 'Gemma'}</span>
                  <div style={{
                    display: 'inline-block',
                    maxWidth: '80%',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    background: chat.sender === 'user' ? 'var(--color-accent)' : 'var(--color-paper-3)',
                    color: chat.sender === 'user' ? 'var(--color-accent-ink)' : 'var(--color-ink)',
                    textAlign: 'left'
                  }}>
                    {chat.text}
                  </div>
                </div>
              ))}
              {chatLoading && <div style={{ color: 'var(--color-muted)', fontSize: 'var(--text-xs)' }}>Gemma is searching business memory...</div>}
            </div>

            <form onSubmit={handleChat} style={{ display: 'flex', gap: 'var(--space-xs)' }}>
              <input 
                type="text" 
                value={question} 
                onChange={e => setQuestion(e.target.value)} 
                placeholder="Ask about inventory, supplier delays, or GPM updates..." 
                style={{ flexGrow: 1 }}
              />
              <button type="submit" className="btn-primary">Query</button>
            </form>
          </div>
        )}

        {/* 7. Document Ingestion View */}
        {currentPage === 'upload' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
            <div className="card">
              <h3>Ingest Business Documents</h3>
              <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', marginTop: 'var(--space-sm)' }}>
                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-sm)', marginBottom: '4px' }}>Document Classification</label>
                  <select value={uploadType} onChange={e => setUploadType(e.target.value as any)} style={{ width: '100%' }}>
                    <option value="invoice">Invoice / Bill</option>
                    <option value="gst">GST tax report</option>
                    <option value="bank">Bank Statement</option>
                    <option value="excel">Excel sheet ledger</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-sm)', marginBottom: '4px' }}>Select File</label>
                  <input type="file" onChange={e => setUploadFile(e.target.files ? e.target.files[0] : null)} style={{ width: '100%' }} />
                </div>

                <button type="submit" className="btn-primary">Process Document</button>
              </form>
              {uploadStatus && (
                <div style={{ marginTop: 'var(--space-sm)', fontSize: 'var(--text-sm)', color: 'var(--color-success)' }}>
                  {uploadStatus}
                </div>
              )}
            </div>

            <div className="card">
              <h3>Extracted Entity Schema</h3>
              {parsedMetadata ? (
                <pre style={{
                  background: 'var(--color-paper-2)',
                  padding: 'var(--space-sm)',
                  borderRadius: '6px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  overflowX: 'auto'
                }}>
                  {JSON.stringify(parsedMetadata, null, 2)}
                </pre>
              ) : (
                <div style={{ textAlign: 'center', color: 'var(--color-muted)', marginTop: 'var(--space-xl)' }}>
                  Metadata schema will render here after upload processing.
                </div>
              )}
            </div>
          </div>
        )}

        {/* 8. Decision Logs View */}
        {currentPage === 'history' && (
          <div className="card">
            <h3>Decision Audit Trail</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 'var(--space-sm)' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-rule)' }}>
                  <th style={{ textAlign: 'left', padding: '8px' }}>Timestamp</th>
                  <th style={{ textAlign: 'left', padding: '8px' }}>Specialist Initiator</th>
                  <th style={{ textAlign: 'left', padding: '8px' }}>Action Target</th>
                  <th style={{ textAlign: 'left', padding: '8px' }}>User Response</th>
                </tr>
              </thead>
              <tbody>
                {decisionHistory.map((item, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--color-rule-2)' }}>
                    <td style={{ padding: '8px' }}>{new Date(item.timestamp).toLocaleString()}</td>
                    <td style={{ padding: '8px' }}>{item.agent_name}</td>
                    <td style={{ padding: '8px' }}>{item.recommendation_text}</td>
                    <td style={{ padding: '8px', color: item.action_taken === 'Approve' ? 'var(--color-success)' : 'var(--color-error)' }}>
                      {item.action_taken}
                    </td>
                  </tr>
                ))}
                {decisionHistory.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', padding: '24px', color: 'var(--color-muted)' }}>
                      No decisions have been logged yet. Approve a recommendation from the CEO Agent tab.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
