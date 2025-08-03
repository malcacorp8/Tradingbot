<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                🤖 Advanced AI Trading Dashboard
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- System Status -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-medium">🧠 AI Trading System Status</h3>
                            <div class="flex items-center space-x-2">
                                <div 
                                    :class="systemStatus?.running ? 'bg-green-500' : 'bg-red-500'"
                                    class="w-3 h-3 rounded-full"
                                ></div>
                                <span class="text-sm">
                                    {{ systemStatus?.running ? 'AI Active' : 'AI Inactive' }}
                                </span>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div class="bg-gray-50 p-4 rounded">
                                <div class="text-sm text-gray-600">Total Balance</div>
                                <div class="text-xl font-bold text-green-600">
                                    ${{ formatNumber(totalPerformance?.total_balance || 0) }}
                                </div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded">
                                <div class="text-sm text-gray-600">Total Trades</div>
                                <div class="text-xl font-bold">
                                    {{ totalPerformance?.total_trades || 0 }}
                                </div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded">
                                <div class="text-sm text-gray-600">Avg Return</div>
                                <div class="text-xl font-bold" :class="getReturnClass(totalPerformance?.avg_return || 0)">
                                    {{ formatPercentage(totalPerformance?.avg_return || 0) }}%
                                </div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded">
                                <div class="text-sm text-gray-600">Active Agents</div>
                                <div class="text-xl font-bold text-blue-600">
                                    {{ totalPerformance?.agent_count || 0 }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Controls -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">🎮 AI Trading Controls</h3>
                        <div class="flex space-x-4">
                            <button 
                                @click="startAdvancedTrading"
                                :disabled="loading || (systemStatus?.running)"
                                class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Starting...' : '🚀 Start AI Trading' }}
                            </button>
                            <button 
                                @click="stopAdvancedTrading"
                                :disabled="loading || !(systemStatus?.running)"
                                class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Stopping...' : '🛑 Stop AI Trading' }}
                            </button>
                            <button 
                                @click="refreshStatus"
                                :disabled="loading"
                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Refreshing...' : '🔄 Refresh' }}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- AI Agents Performance -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6" v-if="systemStatus?.agents">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">🤖 AI Agent Performance</h3>
                        <div class="overflow-x-auto">
                            <table class="min-w-full table-auto">
                                <thead>
                                    <tr class="bg-gray-50">
                                        <th class="px-4 py-2 text-left">Agent</th>
                                        <th class="px-4 py-2 text-left">Balance</th>
                                        <th class="px-4 py-2 text-left">Position</th>
                                        <th class="px-4 py-2 text-left">Total Return</th>
                                        <th class="px-4 py-2 text-left">Trades</th>
                                        <th class="px-4 py-2 text-left">Win Rate</th>
                                        <th class="px-4 py-2 text-left">Exploration</th>
                                        <th class="px-4 py-2 text-left">Learning</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr 
                                        v-for="(agent, symbol) in systemStatus.agents" 
                                        :key="symbol"
                                        class="border-t"
                                    >
                                        <td class="px-4 py-2 font-medium">
                                            {{ symbol }}
                                        </td>
                                        <td class="px-4 py-2">
                                            ${{ formatNumber(agent.balance) }}
                                        </td>
                                        <td class="px-4 py-2">
                                            {{ agent.position }}
                                        </td>
                                        <td class="px-4 py-2" :class="getReturnClass(agent.total_return)">
                                            {{ formatPercentage(agent.total_return) }}%
                                        </td>
                                        <td class="px-4 py-2">
                                            {{ agent.successful_trades }}/{{ agent.total_trades }}
                                        </td>
                                        <td class="px-4 py-2" :class="getReturnClass(agent.win_rate - 0.5)">
                                            {{ formatPercentage(agent.win_rate) }}%
                                        </td>
                                        <td class="px-4 py-2">
                                            <div class="w-full bg-gray-200 rounded-full h-2">
                                                <div 
                                                    class="bg-blue-600 h-2 rounded-full" 
                                                    :style="`width: ${(agent.exploration_rate * 100)}%`"
                                                ></div>
                                            </div>
                                            <span class="text-xs text-gray-500">
                                                {{ formatNumber(agent.exploration_rate * 100, 1) }}%
                                            </span>
                                        </td>
                                        <td class="px-4 py-2">
                                            <span class="text-sm">
                                                Q-States: {{ agent.q_table_size }}
                                            </span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Real-time Rewards Chart -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6" v-if="systemStatus?.agents">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">📈 Real-time Learning Progress</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div 
                                v-for="(agent, symbol) in systemStatus.agents" 
                                :key="symbol"
                                class="bg-gray-50 p-4 rounded"
                            >
                                <h4 class="font-medium mb-2">{{ symbol }} Rewards</h4>
                                <div class="h-32 flex items-end space-x-1">
                                    <div 
                                        v-for="(reward, index) in agent.recent_rewards" 
                                        :key="index"
                                        :class="reward > 0 ? 'bg-green-400' : 'bg-red-400'"
                                        class="w-2 min-h-1"
                                        :style="`height: ${Math.max(5, Math.abs(reward * 1000))}px`"
                                        :title="`Reward: ${reward.toFixed(4)}`"
                                    ></div>
                                </div>
                                <div class="text-xs text-gray-500 mt-1">
                                    Avg: {{ formatNumber(agent.avg_reward, 4) }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Live Trading Log -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">📊 Live Trading Activity</h3>
                        <div class="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm max-h-64 overflow-y-auto">
                            <div v-for="(log, index) in tradingLogs" :key="index" class="mb-1">
                                [{{ log.timestamp }}] {{ log.message }}
                            </div>
                            <div v-if="tradingLogs.length === 0" class="text-gray-500">
                                Waiting for trading activity...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Error Messages -->
                <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 mt-6">
                    <strong>Error:</strong> {{ error }}
                </div>

                <!-- Success Messages -->
                <div v-if="success" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 mt-6">
                    <strong>Success:</strong> {{ success }}
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue'
import axios from 'axios'

// Reactive data
const loading = ref(false)
const error = ref('')
const success = ref('')
const systemStatus = ref(null)
const tradingLogs = ref([])
const refreshInterval = ref(null)

// Computed properties
const totalPerformance = computed(() => {
    return systemStatus.value?.total_performance || {}
})

// Methods
const clearMessages = () => {
    error.value = ''
    success.value = ''
}

const showError = (message) => {
    error.value = message
    success.value = ''
    setTimeout(() => {
        error.value = ''
    }, 5000)
}

const showSuccess = (message) => {
    success.value = message
    error.value = ''
    setTimeout(() => {
        success.value = ''
    }, 5000)
}

const refreshStatus = async () => {
    try {
        const response = await axios.get('http://localhost:8081/status-advanced')
        if (response.data) {
            systemStatus.value = response.data
        }
    } catch (err) {
        // Silently handle connection errors during refresh
        console.warn('Advanced system not available:', err.message)
    }
}

const startAdvancedTrading = async () => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post('http://localhost:8081/start-advanced')
        if (response.data) {
            showSuccess('🤖 Advanced AI trading started! Watch the agents learn...')
            addLog('🚀 AI Trading System activated - Agents are now learning autonomously')
            await refreshStatus()
        }
    } catch (err) {
        showError('Error starting advanced trading: ' + (err.response?.data?.error || err.message))
    } finally {
        loading.value = false
    }
}

const stopAdvancedTrading = async () => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post('http://localhost:8081/stop-advanced')
        if (response.data) {
            showSuccess('🛑 Advanced AI trading stopped')
            addLog('🛑 AI Trading System deactivated')
            await refreshStatus()
        }
    } catch (err) {
        showError('Error stopping advanced trading: ' + (err.response?.data?.error || err.message))
    } finally {
        loading.value = false
    }
}

const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString()
    tradingLogs.value.unshift({
        timestamp,
        message
    })
    
    // Keep only last 50 logs
    if (tradingLogs.value.length > 50) {
        tradingLogs.value = tradingLogs.value.slice(0, 50)
    }
}

// Utility functions
const formatNumber = (value, decimals = 2) => {
    return Number(value).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    })
}

const formatPercentage = (value) => {
    return formatNumber(value * 100, 2)
}

const getReturnClass = (value) => {
    if (value > 0) return 'text-green-600'
    if (value < 0) return 'text-red-600'
    return 'text-gray-600'
}

// Lifecycle
onMounted(() => {
    // Initial status check
    refreshStatus()
    
    // Set up auto-refresh
    refreshInterval.value = setInterval(() => {
        refreshStatus()
    }, 5000) // Refresh every 5 seconds
    
    addLog('🎯 Advanced AI Dashboard loaded - Ready for autonomous trading')
})

onUnmounted(() => {
    if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
    }
})
</script>