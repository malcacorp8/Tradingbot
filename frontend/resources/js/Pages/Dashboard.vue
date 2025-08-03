<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                Trading Bot Dashboard
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Connection Status -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center">
                                <div class="mr-3">
                                    <div 
                                        :class="connectionStatusClass"
                                        class="w-3 h-3 rounded-full"
                                    ></div>
                                </div>
                                <div>
                                    <h3 class="text-lg font-medium">Backend Connection</h3>
                                    <p class="text-sm text-gray-600">{{ connectionStatusText }}</p>
                                </div>
                            </div>
                            <button 
                                @click="refreshStatus"
                                :disabled="loading"
                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Refreshing...' : 'Refresh' }}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Trading Controls -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">Trading Controls</h3>
                        <div class="flex space-x-4">
                            <button 
                                @click="startTrading"
                                :disabled="loading || tradingActive || !backendConnected"
                                class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Starting...' : 'Start Trading' }}
                            </button>
                            <button 
                                @click="stopTrading"
                                :disabled="loading || !tradingActive || !backendConnected"
                                class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Stopping...' : 'Stop Trading' }}
                            </button>
                            <select 
                                v-model="selectedMode"
                                @change="switchMode"
                                :disabled="loading || tradingActive || !backendConnected"
                                class="border border-gray-300 rounded px-3 py-2 disabled:opacity-50"
                            >
                                <option value="paper">Paper Trading</option>
                                <option value="live">Live Trading</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Trading Status -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6" v-if="tradingStatus">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">Trading Status</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-gray-50 p-4 rounded">
                                <div class="text-sm text-gray-600">Status</div>
                                <div class="text-lg font-medium">
                                    {{ tradingActive ? 'Active' : 'Inactive' }}
                                </div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded">
                                <div class="text-sm text-gray-600">Mode</div>
                                <div class="text-lg font-medium capitalize">
                                    {{ tradingStatus.mode || 'Unknown' }}
                                </div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded">
                                <div class="text-sm text-gray-600">Stocks</div>
                                <div class="text-lg font-medium">
                                    {{ tradingStatus.stocks ? tradingStatus.stocks.length : 0 }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Portfolio Overview -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6" v-if="tradingStatus && tradingStatus.portfolio">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">Portfolio Overview</h3>
                        <div class="overflow-x-auto">
                            <table class="min-w-full table-auto">
                                <thead>
                                    <tr class="bg-gray-50">
                                        <th class="px-4 py-2 text-left">Symbol</th>
                                        <th class="px-4 py-2 text-left">Balance</th>
                                        <th class="px-4 py-2 text-left">Position</th>
                                        <th class="px-4 py-2 text-left">Total Trades</th>
                                        <th class="px-4 py-2 text-left">Win Rate</th>
                                        <th class="px-4 py-2 text-left">Return</th>
                                        <th class="px-4 py-2 text-left">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr 
                                        v-for="(data, symbol) in tradingStatus.portfolio" 
                                        :key="symbol"
                                        class="border-t"
                                    >
                                        <td class="px-4 py-2 font-medium">{{ symbol }}</td>
                                        <td class="px-4 py-2">
                                            ${{ formatNumber(data.performance?.balance || 0) }}
                                        </td>
                                        <td class="px-4 py-2">
                                            {{ data.performance?.position || 0 }}
                                        </td>
                                        <td class="px-4 py-2">
                                            {{ data.performance?.total_trades || 0 }}
                                        </td>
                                        <td class="px-4 py-2">
                                            {{ formatPercentage(data.performance?.win_rate || 0) }}%
                                        </td>
                                        <td class="px-4 py-2" :class="getReturnClass(data.performance?.total_return || 0)">
                                            {{ formatPercentage(data.performance?.total_return || 0) }}%
                                        </td>
                                        <td class="px-4 py-2">
                                            <button 
                                                @click="evaluateAgent(symbol)"
                                                :disabled="loading"
                                                class="bg-blue-500 hover:bg-blue-700 text-white text-xs px-2 py-1 rounded mr-1 disabled:opacity-50"
                                            >
                                                Evaluate
                                            </button>
                                            <button 
                                                @click="retrainAgent(symbol)"
                                                :disabled="loading || tradingActive"
                                                class="bg-orange-500 hover:bg-orange-700 text-white text-xs px-2 py-1 rounded disabled:opacity-50"
                                            >
                                                Retrain
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Learning Progress -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg" v-if="tradingStatus && tradingStatus.learning_progress">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">Learning Progress</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div 
                                v-for="(progress, symbol) in tradingStatus.learning_progress" 
                                :key="symbol"
                                class="bg-gray-50 p-4 rounded"
                            >
                                <h4 class="font-medium mb-2">{{ symbol }}</h4>
                                <div class="space-y-1 text-sm">
                                    <div>Episodes: {{ progress.total_episodes || 0 }}</div>
                                    <div>Learning Cycles: {{ progress.learning_cycles || 0 }}</div>
                                    <div>Avg Reward: {{ formatNumber(progress.recent_avg_reward || 0, 4) }}</div>
                                    <div :class="getReturnClass(progress.improvement || 0)">
                                        Improvement: {{ formatNumber(progress.improvement || 0, 4) }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Error Messages -->
                <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                    <strong>Error:</strong> {{ error }}
                </div>

                <!-- Success Messages -->
                <div v-if="success" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
                    <strong>Success:</strong> {{ success }}
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Head } from '@inertiajs/vue3'
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue'
import axios from 'axios'

// Props
const props = defineProps({
    initialData: {
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
const error = ref('')
const success = ref('')
const tradingStatus = ref(props.initialData.trading_status || null)
const backendConnected = ref(props.backendConnected)
const selectedMode = ref('paper')
const refreshInterval = ref(null)

// Computed properties
const tradingActive = computed(() => {
    return tradingStatus.value?.trading_active || false
})

const connectionStatusClass = computed(() => {
    return backendConnected.value ? 'bg-green-500' : 'bg-red-500'
})

const connectionStatusText = computed(() => {
    return backendConnected.value ? 'Connected to backend' : 'Backend disconnected'
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
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.get('/api/bot/status')
        if (response.data.success) {
            tradingStatus.value = response.data.data
            backendConnected.value = true
            selectedMode.value = tradingStatus.value.mode || 'paper'
        } else {
            showError('Failed to get status: ' + (response.data.message || 'Unknown error'))
            backendConnected.value = false
        }
    } catch (err) {
        showError('Error connecting to backend: ' + (err.response?.data?.message || err.message))
        backendConnected.value = false
    } finally {
        loading.value = false
    }
}

const startTrading = async () => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post('/api/bot/start')
        if (response.data.success) {
            showSuccess('Trading bot started successfully')
            await refreshStatus()
        } else {
            showError('Failed to start trading: ' + (response.data.message || 'Unknown error'))
        }
    } catch (err) {
        showError('Error starting trading: ' + (err.response?.data?.message || err.message))
    } finally {
        loading.value = false
    }
}

const stopTrading = async () => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post('/api/bot/stop')
        if (response.data.success) {
            showSuccess('Trading bot stopped successfully')
            await refreshStatus()
        } else {
            showError('Failed to stop trading: ' + (response.data.message || 'Unknown error'))
        }
    } catch (err) {
        showError('Error stopping trading: ' + (err.response?.data?.message || err.message))
    } finally {
        loading.value = false
    }
}

const switchMode = async () => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post('/api/bot/switch-mode', {
            mode: selectedMode.value
        })
        if (response.data.success) {
            showSuccess(`Switched to ${selectedMode.value} mode`)
            await refreshStatus()
        } else {
            showError('Failed to switch mode: ' + (response.data.message || 'Unknown error'))
        }
    } catch (err) {
        showError('Error switching mode: ' + (err.response?.data?.message || err.message))
    } finally {
        loading.value = false
    }
}

const evaluateAgent = async (symbol) => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.get(`/api/bot/evaluate/${symbol}`)
        if (response.data.success) {
            showSuccess(`Evaluation completed for ${symbol}`)
            console.log('Evaluation result:', response.data.data)
        } else {
            showError('Failed to evaluate agent: ' + (response.data.message || 'Unknown error'))
        }
    } catch (err) {
        showError('Error evaluating agent: ' + (err.response?.data?.message || err.message))
    } finally {
        loading.value = false
    }
}

const retrainAgent = async (symbol) => {
    if (!confirm(`Are you sure you want to retrain the agent for ${symbol}? This may take some time.`)) {
        return
    }
    
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post(`/api/bot/retrain/${symbol}`, {
            timesteps: 50000
        })
        if (response.data.success) {
            showSuccess(`Retraining started for ${symbol}`)
        } else {
            showError('Failed to start retraining: ' + (response.data.message || 'Unknown error'))
        }
    } catch (err) {
        showError('Error starting retraining: ' + (err.response?.data?.message || err.message))
    } finally {
        loading.value = false
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
    // Set initial mode
    if (tradingStatus.value?.mode) {
        selectedMode.value = tradingStatus.value.mode
    }
    
    // Set up auto-refresh
    refreshInterval.value = setInterval(() => {
        if (backendConnected.value && !loading.value) {
            refreshStatus()
        }
    }, 10000) // Refresh every 10 seconds
    
    // Initial status check
    refreshStatus()
})

onUnmounted(() => {
    if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
    }
})
</script>