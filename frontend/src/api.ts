const API_BASE_URL = '/api/v1';

export interface DashboardMetrics {
  total_revenue: number;
  monthly_revenue: number;
  accounts_receivable: number;
  accounts_payable: number;
  net_working_capital: number;
  low_stock_alerts: number;
  active_customers: number;
  monthly_orders: number;
}

export interface BusinessHealth {
  status: string;
  health_score: number;
  gross_profit_margin_pct: number;
  operating_ratio: number;
  overdue_invoices: number;
  low_stock_products: number;
  gross_profit: number;
  generated_at: string;
}

export interface AlertItem {
  severity: string;
  category: string;
  title: string;
  message: string;
  count?: number;
  product_id?: number;
}

export interface TimelineEvent {
  id: number;
  event_type: string;
  description: string;
  severity: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  model_used: string;
  context_summary: {
    events_loaded: number;
    customers_loaded: number;
    suppliers_loaded: number;
    products_loaded: number;
  };
}

export interface ForecastResponse {
  prediction: string;
  confidence_score: number;
  important_features: string[];
  business_impact: string;
  suggested_action: string;
}

export interface DemandForecastResponse extends ForecastResponse {
  product_id: number;
  sku: string;
  name: string;
}

export interface RiskResponse {
  customer_id?: number;
  supplier_id?: number;
  name: string;
  prediction: string;
  confidence_score: number;
  important_features: string[];
  business_impact: string;
  suggested_action: string;
}

export interface AgentReport {
  agent_name: string;
  role: string;
  analysis: string;
  alerts: string[];
  recommendations: Array<{
    action: string;
    roi: string;
    risk: string;
    confidence: number;
    reasoning: string;
  }>;
  confidence: number;
  supporting_evidence: string;
}

export interface RecommendationItem {
  id: number;
  agent_name: string;
  roi: string;
  risk: string;
  confidence: number;
  supporting_data: string;
  action: string;
  reasoning: string;
}

export interface SimulationResult {
  revenue: number;
  profit: number;
  cash_flow: string;
  risk: string;
  inventory: string;
  business_health: number;
}

export const api = {
  // Dashboard
  async getDashboard(): Promise<{ metrics: DashboardMetrics; generated_at: string }> {
    const res = await fetch(`${API_BASE_URL}/dashboard`);
    return res.json();
  },

  async getBusinessHealth(): Promise<BusinessHealth> {
    const res = await fetch(`${API_BASE_URL}/business-health`);
    return res.json();
  },

  async getAlerts(): Promise<AlertItem[]> {
    const res = await fetch(`${API_BASE_URL}/alerts`);
    return res.json();
  },

  async getTimeline(): Promise<TimelineEvent[]> {
    const res = await fetch(`${API_BASE_URL}/timeline`);
    return res.json();
  },

  // AI & Chat
  async sendChat(question: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    return res.json();
  },

  async getOllamaStatus(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/ai/ollama-status`);
    return res.json();
  },

  async getExecutiveBrief(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/ai/executive-brief`);
    return res.json();
  },

  // Forecasts
  async getRevenueForecast(): Promise<ForecastResponse> {
    const res = await fetch(`${API_BASE_URL}/forecast/revenue`);
    return res.json();
  },

  async getCashflowForecast(): Promise<ForecastResponse> {
    const res = await fetch(`${API_BASE_URL}/forecast/cashflow`);
    return res.json();
  },

  async getDemandForecast(): Promise<DemandForecastResponse[]> {
    const res = await fetch(`${API_BASE_URL}/forecast/demand`);
    return res.json();
  },

  async getInventoryForecast(): Promise<DemandForecastResponse[]> {
    const res = await fetch(`${API_BASE_URL}/forecast/inventory`);
    return res.json();
  },

  // Risk & Pricing
  async getCustomerRisks(): Promise<RiskResponse[]> {
    const res = await fetch(`${API_BASE_URL}/risk/customers`);
    return res.json();
  },

  async getSupplierRisks(): Promise<RiskResponse[]> {
    const res = await fetch(`${API_BASE_URL}/risk/suppliers`);
    return res.json();
  },

  async getPricingRecommendations(): Promise<any[]> {
    const res = await fetch(`${API_BASE_URL}/pricing`);
    return res.json();
  },

  // Multi-Agent & Decision Engine
  async getAgentReports(): Promise<{ status: string; reports: AgentReport[] }> {
    const res = await fetch(`${API_BASE_URL}/agents`);
    return res.json();
  },

  async getRecommendations(): Promise<RecommendationItem[]> {
    const res = await fetch(`${API_BASE_URL}/recommendations`);
    return res.json();
  },

  async simulate(payload: {
    price_change_pct: number;
    hiring_cost: number;
    supplier_change: string;
    inventory_decisions: string;
    loan_decisions: string;
  }): Promise<SimulationResult> {
    const res = await fetch(`${API_BASE_URL}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json();
  },

  async getDecisionHistory(): Promise<any[]> {
    const res = await fetch(`${API_BASE_URL}/decision-history`);
    return res.json();
  },

  async logDecision(recommendationId: number, actionTaken: 'Approve' | 'Decline'): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/decision-history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recommendation_id: recommendationId, action_taken: actionTaken })
    });
    return res.json();
  },

  async explainRecommendation(id: number): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/explain/${id}`);
    return res.json();
  },

  // File Upload
  async uploadFile(type: 'invoice' | 'gst' | 'bank' | 'excel', file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/upload/${type}`, {
      method: 'POST',
      body: formData
    });
    return res.json();
  }
};
