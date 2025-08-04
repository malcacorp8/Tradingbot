<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                📋 System Logs & Monitoring
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
                <!-- Log Controls -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium">📊 Log Controls</h3>
                            
                            <div class="flex items-center space-x-4">
                                <!-- Log Level Filter -->
                                <div class="flex items-center space-x-2">
                                    <label class="text-sm text-gray-600">Filter:</label>
                                    <select v-model="logLevelFilter" class="form-select text-sm">
                                        <option value="">All Levels</option>
                                        <option value="ERROR">Errors</option>
                                        <option value="WARNING">Warnings</option>
                                        <option value="INFO">Info</option>
                                        <option value="DEBUG">Debug</option>
                                    </select>
                                </div>
                                
                                <!-- Symbol Filter -->
                                <div class="flex items-center space-x-2">
                                    <label class="text-sm text-gray-600">Symbol:</label>
                                    <select v-model="symbolFilter" class="form-select text-sm">
                                        <option value="">All Symbols</option>
                                        <option value="SYSTEM">System</option>
                                        <option value="ALPACA">Alpaca API</option>
                                        <option value="PORTFOLIO">Portfolio</option>
                                        <option value="PRICE_FEED">Price Feed</option>
                                        <option value="RISK_MGR">Risk Manager</option>
                                        <option value="TRADING">Trading Engine</option>
                                        <option value="AI_MODELS">AI Models</option>
                                        <option value="DATABASE">Database</option>
                                        <option value="AAPL">AAPL</option>
                                        <option value="TSLA">TSLA</option>
                                        <option value="GOOGL">GOOGL</option>
                                        <option value="MSFT">MSFT</option>
                                        <option value="NVDA">NVDA</option>
                                    </select>
                                </div>
                                
                                <!-- Auto-refresh toggle -->
                                <label class="flex items-center space-x-2">
                                    <input 
                                        type="checkbox" 
                                        v-model="autoRefresh" 
                                        class="form-checkbox text-blue-600"
                                    >
                                    <span class="text-sm text-gray-600">Auto-refresh</span>
                                </label>
                                
                                <!-- Refresh button -->
                                <button 
                                    @click="fetchLogs"
                                    :disabled="loading"
                                    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                                >
                                    {{ loading ? 'Loading...' : 'Refresh' }}
                                </button>
                                
                                <!-- Clear logs button -->
                                <button 
                                    @click="clearDisplayedLogs"
                                    class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Integration Status -->
                <div class="bg-gradient-to-br from-white to-gray-50 overflow-hidden shadow-xl sm:rounded-xl">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-xl font-bold text-gray-800 flex items-center">
                                <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                🔗 Integration Status
                            </h3>
                            <div class="flex items-center space-x-3">
                                <div class="flex items-center space-x-2">
                                    <div 
                                        :class="getOverallHealthClass(integrationSummary?.overall_health)"
                                        class="w-3 h-3 rounded-full animate-pulse"
                                    ></div>
                                    <span class="text-sm font-medium text-gray-700">
                                        {{ getOverallHealthText(integrationSummary?.overall_health) }}
                                    </span>
                                </div>
                                <button 
                                    @click="fetchIntegrationStatus"
                                    :disabled="loading"
                                    class="text-sm bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded disabled:opacity-50"
                                >
                                    {{ loading ? 'Checking...' : 'Refresh' }}
                                </button>
                            </div>
                        </div>
                        
                        <!-- Integration Grid -->
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div 
                                v-for="(integration, key) in integrations" 
                                :key="key"
                                class="bg-white p-4 rounded-lg shadow-sm border-l-4 hover:shadow-md transition-shadow"
                                :class="getIntegrationBorderClass(integration.status)"
                            >
                                <div class="flex items-center justify-between mb-2">
                                    <div class="flex items-center space-x-2">
                                        <div 
                                            :class="getStatusIndicatorClass(integration.status)"
                                            class="w-2 h-2 rounded-full"
                                        ></div>
                                        <span class="text-sm font-semibold text-gray-700">{{ integration.name }}</span>
                                    </div>
                                    <span 
                                        class="px-2 py-1 text-xs font-bold rounded-full"
                                        :class="getStatusBadgeClass(integration.status)"
                                    >
                                        {{ integration.status.toUpperCase() }}
                                    </span>
                                </div>
                                <p class="text-xs text-gray-600 mb-2">{{ integration.message }}</p>
                                <p class="text-xs text-gray-400">
                                    Last check: {{ formatTime(integration.last_check) }}
                                </p>
                            </div>
                        </div>
                        
                        <!-- Integration Summary -->
                        <div class="mt-6 bg-gray-50 rounded-lg p-4">
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                                <div>
                                    <div class="text-2xl font-bold text-green-600">{{ integrationSummary?.connected || 0 }}</div>
                                    <div class="text-sm text-gray-600">Connected</div>
                                </div>
                                <div>
                                    <div class="text-2xl font-bold text-yellow-600">{{ integrationSummary?.warnings || 0 }}</div>
                                    <div class="text-sm text-gray-600">Warnings</div>
                                </div>
                                <div>
                                    <div class="text-2xl font-bold text-red-600">{{ integrationSummary?.errors || 0 }}</div>
                                    <div class="text-sm text-gray-600">Errors</div>
                                </div>
                                <div>
                                    <div class="text-2xl font-bold text-blue-600">{{ integrationSummary?.total || 0 }}</div>
                                    <div class="text-sm text-gray-600">Total</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- System Status -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">🔧 System Status</h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div class="flex items-center space-x-3">
                                <div 
                                    :class="backendConnected ? 'bg-green-500' : 'bg-red-500'"
                                    class="w-3 h-3 rounded-full"
                                ></div>
                                <div>
                                    <div class="text-sm text-gray-600">Backend</div>
                                    <div class="font-medium">{{ backendConnected ? 'Connected' : 'Disconnected' }}</div>
                                </div>
                            </div>
                            
                            <div class="flex items-center space-x-3">
                                <div class="bg-blue-500 w-3 h-3 rounded-full"></div>
                                <div>
                                    <div class="text-sm text-gray-600">Logs Loaded</div>
                                    <div class="font-medium">{{ logs.length }}</div>
                                </div>
                            </div>
                            
                            <div class="flex items-center space-x-3">
                                <div class="bg-yellow-500 w-3 h-3 rounded-full"></div>
                                <div>
                                    <div class="text-sm text-gray-600">Warnings</div>
                                    <div class="font-medium">{{ getLogCount('WARNING') }}</div>
                                </div>
                            </div>
                            
                            <div class="flex items-center space-x-3">
                                <div class="bg-red-500 w-3 h-3 rounded-full"></div>
                                <div>
                                    <div class="text-sm text-gray-600">Errors</div>
                                    <div class="font-medium">{{ getLogCount('ERROR') }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Log Display -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-medium">📜 System Logs</h3>
                            <div class="text-sm text-gray-500">
                                Last updated: {{ lastUpdated ? formatTime(lastUpdated) : 'Never' }}
                            </div>
                        </div>
                        
                        <!-- Log entries -->
                        <div class="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
                            <div 
                                v-for="log in filteredLogs" 
                                :key="log.id || log.timestamp"
                                class="mb-2 flex items-start space-x-3"
                            >
                                <!-- Timestamp -->
                                <span class="text-gray-400 whitespace-nowrap">
                                    {{ formatLogTime(log.timestamp) }}
                                </span>
                                
                                <!-- Level -->
                                <span 
                                    class="px-2 py-1 rounded text-xs font-bold whitespace-nowrap"
                                    :class="getLogLevelClass(log.level)"
                                >
                                    {{ log.level }}
                                </span>
                                
                                <!-- Symbol -->
                                <span class="text-blue-300 whitespace-nowrap">
                                    [{{ log.symbol }}]
                                </span>
                                
                                <!-- Message -->
                                <span class="text-white flex-1">
                                    {{ log.message }}
                                </span>
                            </div>
                            
                            <!-- Empty state -->
                            <div v-if="filteredLogs.length === 0" class="text-center text-gray-500 py-8">
                                <div class="text-2xl mb-2">📝</div>
                                <div>No logs to display</div>
                                <div class="text-sm mt-1">
                                    {{ logs.length > 0 ? 'Try adjusting your filters' : 'Logs will appear here when available' }}
                                </div>
                            </div>
                        </div>
                        
                        <!-- Log statistics -->
                        <div class="mt-4 flex items-center justify-between text-sm text-gray-600">
                            <div>
                                Showing {{ filteredLogs.length }} of {{ logs.length }} log entries
                            </div>
                            <div class="flex items-center space-x-4">
                                <span>
                                    <span class="text-green-600">●</span> Info: {{ getLogCount('INFO') }}
                                </span>
                                <span>
                                    <span class="text-yellow-600">●</span> Warnings: {{ getLogCount('WARNING') }}
                                </span>
                                <span>
                                    <span class="text-red-600">●</span> Errors: {{ getLogCount('ERROR') }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Export Controls -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">💾 Export & Download</h3>
                        
                        <div class="flex items-center space-x-4">
                            <button 
                                @click="exportLogs('txt')"
                                class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                            >
                                📄 Export as TXT
                            </button>
                            
                            <button 
                                @click="exportLogs('json')"
                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                            >
                                📊 Export as JSON
                            </button>
                            
                            <div class="text-sm text-gray-600">
                                Export current filtered logs ({{ filteredLogs.length }} entries)
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Head } from '@inertiajs/vue3'
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue'
import axios from 'axios'

// Props
const props = defineProps({
    backendUrl: {
        type: String,
        default: 'http://localhost:8080'
    }
})

// Reactive data
const loading = ref(false)
const logs = ref([])
const logLevelFilter = ref('')
const symbolFilter = ref('')
const autoRefresh = ref(true)
const lastUpdated = ref(null)
const refreshInterval = ref(null)
const backendConnected = ref(true)
const integrations = ref({})
const integrationSummary = ref(null)

// Computed
const filteredLogs = computed(() => {
    return logs.value.filter(log => {
        const levelMatch = !logLevelFilter.value || log.level === logLevelFilter.value
        const symbolMatch = !symbolFilter.value || log.symbol === symbolFilter.value
        return levelMatch && symbolMatch
    }).slice(-100) // Show last 100 logs
})

// Methods
const formatTime = (date) => {
    return new Date(date).toLocaleTimeString()
}

const formatLogTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString() + '.' + 
           new Date(timestamp).getMilliseconds().toString().padStart(3, '0')
}

const getLogLevelClass = (level) => {
    switch (level) {
        case 'ERROR':
            return 'bg-red-600 text-white'
        case 'WARNING':
            return 'bg-yellow-500 text-black'
        case 'INFO':
            return 'bg-blue-500 text-white'
        case 'DEBUG':
            return 'bg-gray-500 text-white'
        default:
            return 'bg-gray-400 text-white'
    }
}

const getLogCount = (level) => {
    return logs.value.filter(log => log.level === level).length
}

const fetchLogs = async () => {
    loading.value = true
    
    try {
        const response = await axios.get('/api/bot/logs')
        
        if (response.data.success) {
            logs.value = response.data.data.logs || []
            lastUpdated.value = new Date()
            backendConnected.value = true
        } else {
            console.error('Failed to fetch logs:', response.data.message)
            backendConnected.value = false
        }
    } catch (err) {
        console.error('Error fetching logs:', err)
        backendConnected.value = false
        
        // Add mock logs for demonstration if backend fails
        addMockLogs()
    } finally {
        loading.value = false
    }
}

const fetchIntegrationStatus = async () => {
    try {
        const response = await axios.get('/api/bot/integration-status')
        
        if (response.data.success) {
            integrations.value = response.data.data.integrations
            integrationSummary.value = response.data.data.summary
            backendConnected.value = true
        } else {
            console.error('Failed to fetch integration status:', response.data.message)
            backendConnected.value = false
            addMockIntegrations()
        }
    } catch (err) {
        console.error('Error fetching integration status:', err)
        backendConnected.value = false
        addMockIntegrations()
    }
}

const addMockIntegrations = () => {
    integrations.value = {
        alpaca_market_data: {
            name: 'Alpaca Market Data API',
            status: 'connected',
            message: 'Latest AAPL price available',
            last_check: new Date().toISOString()
        },
        alpaca_trading: {
            name: 'Alpaca Trading API',
            status: 'connected',
            message: 'Account active, Cash: $123,380.00',
            last_check: new Date().toISOString()
        },
        price_feed: {
            name: 'Real-time Price Feed',
            status: 'connected',
            message: 'AAPL: $202.30',
            last_check: new Date().toISOString()
        },
        portfolio_manager: {
            name: 'Portfolio Management',
            status: 'connected',
            message: 'Managing 5 stocks, Total P&L: $23,380',
            last_check: new Date().toISOString()
        },
        risk_management: {
            name: 'Risk Management',
            status: 'connected',
            message: 'Risk controls active, Position limits enforced',
            last_check: new Date().toISOString()
        },
        trading_engine: {
            name: 'Trading Engine',
            status: 'connected',
            message: 'Paper trading mode, Ready for orders',
            last_check: new Date().toISOString()
        },
        ai_models: {
            name: 'AI/ML Models',
            status: 'connected',
            message: 'PPO agents loaded for all symbols',
            last_check: new Date().toISOString()
        },
        database: {
            name: 'Database',
            status: 'connected',
            message: 'SQLite database accessible',
            last_check: new Date().toISOString()
        }
    }
    
    integrationSummary.value = {
        total: 8,
        connected: 8,
        warnings: 0,
        errors: 0,
        overall_health: 'healthy'
    }
}

const getStatusIndicatorClass = (status) => {
    switch (status) {
        case 'connected':
            return 'bg-green-500'
        case 'warning':
            return 'bg-yellow-500'
        case 'error':
            return 'bg-red-500'
        default:
            return 'bg-gray-400'
    }
}

const getStatusBadgeClass = (status) => {
    switch (status) {
        case 'connected':
            return 'bg-green-100 text-green-800'
        case 'warning':
            return 'bg-yellow-100 text-yellow-800'
        case 'error':
            return 'bg-red-100 text-red-800'
        default:
            return 'bg-gray-100 text-gray-800'
    }
}

const getIntegrationBorderClass = (status) => {
    switch (status) {
        case 'connected':
            return 'border-green-500'
        case 'warning':
            return 'border-yellow-500'
        case 'error':
            return 'border-red-500'
        default:
            return 'border-gray-400'
    }
}

const getOverallHealthClass = (health) => {
    switch (health) {
        case 'healthy':
            return 'bg-green-500'
        case 'warning':
            return 'bg-yellow-500'
        case 'critical':
            return 'bg-red-500'
        default:
            return 'bg-gray-400'
    }
}

const getOverallHealthText = (health) => {
    switch (health) {
        case 'healthy':
            return 'All Systems Operational'
        case 'warning':
            return 'Minor Issues Detected'
        case 'critical':
            return 'Critical Issues'
        default:
            return 'Unknown Status'
    }
}

const addMockLogs = () => {
    const mockLogs = [
        {
            timestamp: new Date().toISOString(),
            level: 'INFO',
            symbol: 'SYSTEM',
            message: 'Trading bot system initialized successfully'
        },
        {
            timestamp: new Date(Date.now() - 1000).toISOString(),
            level: 'INFO',
            symbol: 'SYSTEM',
            message: 'Connected to Alpaca API (Paper Trading)'
        },
        {
            timestamp: new Date(Date.now() - 2000).toISOString(),
            level: 'INFO',
            symbol: 'PORTFOLIO',
            message: 'Portfolio balance: $100,000.00'
        },
        {
            timestamp: new Date(Date.now() - 3000).toISOString(),
            level: 'INFO',
            symbol: 'AAPL',
            message: 'Agent loaded and ready for trading'
        },
        {
            timestamp: new Date(Date.now() - 4000).toISOString(),
            level: 'WARNING',
            symbol: 'TSLA',
            message: 'High volatility detected, adjusting position size'
        },
        {
            timestamp: new Date(Date.now() - 5000).toISOString(),
            level: 'INFO',
            symbol: 'GOOGL',
            message: 'Buy signal generated at $2,750.00'
        }
    ]
    
    logs.value = [...logs.value, ...mockLogs]
    lastUpdated.value = new Date()
}

const clearDisplayedLogs = () => {
    logs.value = []
    lastUpdated.value = null
}

const exportLogs = (format) => {
    const dataToExport = filteredLogs.value
    const timestamp = new Date().toISOString().split('T')[0]
    
    if (format === 'txt') {
        const txtContent = dataToExport.map(log => 
            `${formatLogTime(log.timestamp)} [${log.level}] [${log.symbol}] ${log.message}`
        ).join('\n')
        
        downloadFile(txtContent, `trading-bot-logs-${timestamp}.txt`, 'text/plain')
    } else if (format === 'json') {
        const jsonContent = JSON.stringify(dataToExport, null, 2)
        downloadFile(jsonContent, `trading-bot-logs-${timestamp}.json`, 'application/json')
    }
}

const downloadFile = (content, filename, contentType) => {
    const blob = new Blob([content], { type: contentType })
    const url = window.URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    window.URL.revokeObjectURL(url)
}

const startAutoRefresh = () => {
    if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
    }
    
    if (autoRefresh.value) {
        refreshInterval.value = setInterval(() => {
            fetchLogs()
            fetchIntegrationStatus()
        }, 5000) // Refresh every 5 seconds
    }
}

// Watchers
watch(autoRefresh, startAutoRefresh)

// Lifecycle
onMounted(() => {
    fetchLogs()
    fetchIntegrationStatus()
    startAutoRefresh()
})

onUnmounted(() => {
    if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
    }
})
</script>