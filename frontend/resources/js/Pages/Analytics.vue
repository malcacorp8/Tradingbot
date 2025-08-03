<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                📊 Trading Analytics Dashboard
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
                <!-- Performance Overview -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">📈 Performance Overview</h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-600">Total Balance</div>
                                <div class="text-2xl font-bold text-blue-600">
                                    ${{ formatNumber(performanceMetrics?.total_balance || 0) }}
                                </div>
                            </div>
                            
                            <div class="bg-green-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-600">Total Trades</div>
                                <div class="text-2xl font-bold text-green-600">
                                    {{ performanceMetrics?.total_trades || 0 }}
                                </div>
                            </div>
                            
                            <div class="bg-purple-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-600">Average Return</div>
                                <div class="text-2xl font-bold" :class="getReturnClass(performanceMetrics?.average_return || 0)">
                                    {{ formatPercentage(performanceMetrics?.average_return || 0) }}%
                                </div>
                            </div>
                            
                            <div class="bg-orange-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-600">Active Symbols</div>
                                <div class="text-2xl font-bold text-orange-600">
                                    {{ performanceMetrics?.active_symbols || 0 }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Portfolio Performance -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">💼 Portfolio Performance</h3>
                        
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Balance</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Position</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trades</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Win Rate</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Return</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    <tr v-for="(data, symbol) in portfolio" :key="symbol">
                                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {{ symbol }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            ${{ formatNumber(data.performance?.balance || 0) }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ data.performance?.position || 0 }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ data.performance?.total_trades || 0 }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ formatPercentage(data.performance?.win_rate || 0) }}%
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm" :class="getReturnClass(data.performance?.total_return || 0)">
                                            {{ formatPercentage(data.performance?.total_return || 0) }}%
                                        </td>
                                    </tr>
                                    <tr v-if="Object.keys(portfolio).length === 0">
                                        <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                                            No portfolio data available
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Trading Statistics -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Daily Performance Chart -->
                    <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium mb-4">📈 Daily Performance</h3>
                            
                            <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                                <div class="text-center text-gray-500">
                                    <div class="text-4xl mb-2">📊</div>
                                    <div>Performance Chart</div>
                                    <div class="text-sm mt-1">(Chart visualization would go here)</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Risk Metrics -->
                    <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium mb-4">⚠️ Risk Metrics</h3>
                            
                            <div class="space-y-4">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Sharpe Ratio</span>
                                    <span class="font-medium">1.42</span>
                                </div>
                                
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Max Drawdown</span>
                                    <span class="font-medium text-red-600">-8.5%</span>
                                </div>
                                
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Volatility</span>
                                    <span class="font-medium">15.2%</span>
                                </div>
                                
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Beta</span>
                                    <span class="font-medium">0.98</span>
                                </div>
                                
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Alpha</span>
                                    <span class="font-medium text-green-600">2.1%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Learning Progress -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">🤖 AI Learning Progress</h3>
                        
                        <div v-if="Object.keys(learningProgress).length > 0" class="space-y-4">
                            <div v-for="(progress, symbol) in learningProgress" :key="symbol" class="border rounded-lg p-4">
                                <div class="flex justify-between items-center mb-2">
                                    <span class="font-medium">{{ symbol }}</span>
                                    <span class="text-sm text-gray-500">{{ progress.episodes || 0 }} episodes</span>
                                </div>
                                
                                <div class="w-full bg-gray-200 rounded-full h-2">
                                    <div 
                                        class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                        :style="{ width: (progress.completion || 0) + '%' }"
                                    ></div>
                                </div>
                                
                                <div class="mt-2 text-sm text-gray-600">
                                    Reward: {{ formatNumber(progress.reward || 0, 2) }} | 
                                    Accuracy: {{ formatPercentage(progress.accuracy || 0) }}%
                                </div>
                            </div>
                        </div>
                        
                        <div v-else class="text-center py-8 text-gray-500">
                            <div class="text-4xl mb-2">🧠</div>
                            <div>No learning data available</div>
                            <div class="text-sm mt-1">AI training data will appear here</div>
                        </div>
                    </div>
                </div>

                <!-- Recent Trades -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">🕒 Recent Trades</h3>
                        
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    <tr v-for="trade in mockTrades" :key="trade.id">
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ formatTime(trade.time) }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {{ trade.symbol }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="px-2 py-1 text-xs rounded-full" :class="trade.action === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                                                {{ trade.action }}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ trade.quantity }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            ${{ formatNumber(trade.price, 2) }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm" :class="getReturnClass(trade.pnl)">
                                            ${{ formatNumber(trade.pnl, 2) }}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Controls -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-medium">Analytics Controls</h3>
                                <p class="text-sm text-gray-600">Last updated: {{ formatTime(new Date()) }}</p>
                            </div>
                            
                            <button 
                                @click="refreshData"
                                :disabled="loading"
                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Refreshing...' : 'Refresh Data' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Head } from '@inertiajs/vue3'
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue'
import axios from 'axios'

// Props
const props = defineProps({
    analyticsData: {
        type: Object,
        default: () => ({})
    },
    backendConnected: {
        type: Boolean,
        default: false
    }
})

// Reactive data
const loading = ref(false)
const portfolio = ref(props.analyticsData?.portfolio || {})
const learningProgress = ref(props.analyticsData?.learning_progress || {})
const performanceMetrics = ref(props.analyticsData?.performance_metrics || {})

// Mock data for demonstration
const mockTrades = ref([
    { id: 1, time: new Date(), symbol: 'AAPL', action: 'BUY', quantity: 10, price: 180.50, pnl: 125.30 },
    { id: 2, time: new Date(Date.now() - 300000), symbol: 'TSLA', action: 'SELL', quantity: 5, price: 245.80, pnl: -45.20 },
    { id: 3, time: new Date(Date.now() - 600000), symbol: 'GOOGL', action: 'BUY', quantity: 3, price: 2750.00, pnl: 89.15 },
    { id: 4, time: new Date(Date.now() - 900000), symbol: 'MSFT', action: 'SELL', quantity: 8, price: 380.25, pnl: 67.80 },
    { id: 5, time: new Date(Date.now() - 1200000), symbol: 'NVDA', action: 'BUY', quantity: 12, price: 450.75, pnl: -23.45 }
])

// Methods
const formatNumber = (value, decimals = 0) => {
    return Number(value).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    })
}

const formatPercentage = (value) => {
    return formatNumber(value * 100, 2)
}

const formatTime = (date) => {
    return new Date(date).toLocaleTimeString()
}

const getReturnClass = (value) => {
    if (value > 0) return 'text-green-600'
    if (value < 0) return 'text-red-600'
    return 'text-gray-600'
}

const refreshData = async () => {
    loading.value = true
    
    try {
        const response = await axios.get('/api/bot/status')
        
        if (response.data.success) {
            const data = response.data.data
            portfolio.value = data.portfolio || {}
            learningProgress.value = data.learning_progress || {}
            
            // Calculate performance metrics
            performanceMetrics.value = calculatePerformanceMetrics(data)
        }
    } catch (err) {
        console.error('Error refreshing analytics data:', err)
    } finally {
        loading.value = false
    }
}

const calculatePerformanceMetrics = (data) => {
    if (!data.portfolio) return {}
    
    let totalBalance = 0
    let totalTrades = 0
    let totalReturn = 0
    const portfolioCount = Object.keys(data.portfolio).length
    
    Object.values(data.portfolio).forEach(portfolioData => {
        if (portfolioData.performance) {
            totalBalance += portfolioData.performance.balance || 0
            totalTrades += portfolioData.performance.total_trades || 0
            totalReturn += portfolioData.performance.total_return || 0
        }
    })
    
    return {
        total_balance: totalBalance,
        total_trades: totalTrades,
        average_return: portfolioCount > 0 ? totalReturn / portfolioCount : 0,
        active_symbols: portfolioCount
    }
}

// Initialize
onMounted(() => {
    // Auto-refresh every 30 seconds
    setInterval(refreshData, 30000)
})
</script>