<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                ⚙️ Trading Bot Configuration
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
                <!-- Connection Status -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-medium">🔗 Backend Connection</h3>
                            <div class="flex items-center space-x-2">
                                <div 
                                    :class="backendConnected ? 'bg-green-500' : 'bg-red-500'"
                                    class="w-3 h-3 rounded-full"
                                ></div>
                                <span class="text-sm">
                                    {{ backendConnected ? 'Connected' : 'Disconnected' }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Trading Mode Configuration -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">📊 Trading Mode</h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Current Mode</label>
                                <div class="flex items-center space-x-4">
                                    <label class="flex items-center">
                                        <input 
                                            type="radio" 
                                            v-model="selectedMode" 
                                            value="paper"
                                            @change="updateMode"
                                            class="form-radio text-blue-600"
                                        >
                                        <span class="ml-2">Paper Trading</span>
                                    </label>
                                    <label class="flex items-center">
                                        <input 
                                            type="radio" 
                                            v-model="selectedMode" 
                                            value="live"
                                            @change="updateMode"
                                            class="form-radio text-red-600"
                                        >
                                        <span class="ml-2">Live Trading</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Mode Status</label>
                                <div class="p-3 rounded-lg" :class="selectedMode === 'paper' ? 'bg-blue-50 text-blue-800' : 'bg-red-50 text-red-800'">
                                    {{ selectedMode === 'paper' ? '📝 Safe for testing' : '⚠️ Real money trading' }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Stock Configuration -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">📈 Stock Configuration</h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Available Stocks -->
                            <div>
                                <h4 class="text-md font-medium mb-3">Available Stocks</h4>
                                <div class="grid grid-cols-2 gap-2">
                                    <div 
                                        v-for="stock in availableStocks" 
                                        :key="stock"
                                        class="flex items-center space-x-2"
                                    >
                                        <input 
                                            type="checkbox" 
                                            :id="stock"
                                            v-model="selectedStocks"
                                            :value="stock"
                                            class="form-checkbox text-blue-600"
                                        >
                                        <label :for="stock" class="text-sm font-mono">{{ stock }}</label>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Current Selection -->
                            <div>
                                <h4 class="text-md font-medium mb-3">Current Selection ({{ selectedStocks.length }})</h4>
                                <div class="space-y-2">
                                    <div 
                                        v-for="stock in selectedStocks" 
                                        :key="stock"
                                        class="flex items-center justify-between p-2 bg-gray-50 rounded"
                                    >
                                        <span class="font-mono">{{ stock }}</span>
                                        <button 
                                            @click="removeStock(stock)"
                                            class="text-red-600 hover:text-red-800"
                                        >
                                            ✕
                                        </button>
                                    </div>
                                    <div v-if="selectedStocks.length === 0" class="text-gray-500 text-sm">
                                        No stocks selected
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-6 flex space-x-4">
                            <button 
                                @click="saveConfiguration"
                                :disabled="loading || selectedStocks.length === 0"
                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                {{ loading ? 'Saving...' : 'Save Configuration' }}
                            </button>
                            
                            <button 
                                @click="resetConfiguration"
                                class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                            >
                                Reset
                            </button>
                        </div>
                    </div>
                </div>

                <!-- System Settings -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">🔧 System Settings</h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Auto Refresh Interval</label>
                                <select v-model="refreshInterval" class="form-select w-full">
                                    <option value="5">5 seconds</option>
                                    <option value="10">10 seconds</option>
                                    <option value="30">30 seconds</option>
                                    <option value="60">1 minute</option>
                                </select>
                            </div>
                            
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Max Positions</label>
                                <input 
                                    type="number" 
                                    v-model="maxPositions" 
                                    min="1" 
                                    max="10"
                                    class="form-input w-full"
                                >
                            </div>
                            
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Risk Level</label>
                                <select v-model="riskLevel" class="form-select w-full">
                                    <option value="conservative">Conservative</option>
                                    <option value="moderate">Moderate</option>
                                    <option value="aggressive">Aggressive</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Status Messages -->
                <div v-if="success || error" class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <div v-if="success" class="p-4 bg-green-50 text-green-700 rounded-lg">
                            ✅ {{ success }}
                        </div>
                        <div v-if="error" class="p-4 bg-red-50 text-red-700 rounded-lg">
                            ❌ {{ error }}
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
    configData: {
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
const selectedMode = ref(props.configData?.current_mode || 'paper')
const selectedStocks = ref([...props.configData?.current_stocks || []])
const availableStocks = ref(props.configData?.available_stocks || [
    'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'AMZN', 'META', 'NFLX', 'AMD', 'INTC'
])
const refreshInterval = ref(10)
const maxPositions = ref(5)
const riskLevel = ref('moderate')

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

const updateMode = async () => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post('/api/bot/switch-mode', {
            mode: selectedMode.value
        })
        
        if (response.data.success) {
            showSuccess(`Switched to ${selectedMode.value} mode`)
        } else {
            showError('Failed to switch mode: ' + (response.data.message || 'Unknown error'))
        }
    } catch (err) {
        showError('Error switching mode: ' + (err.response?.data?.message || err.message))
    } finally {
        loading.value = false
    }
}

const removeStock = (stock) => {
    selectedStocks.value = selectedStocks.value.filter(s => s !== stock)
}

const saveConfiguration = async () => {
    loading.value = true
    clearMessages()
    
    try {
        const response = await axios.post('/api/bot/configure', {
            stocks: selectedStocks.value
        })
        
        if (response.data.success) {
            showSuccess(`Configuration saved: ${selectedStocks.value.length} stocks selected`)
        } else {
            showError('Failed to save configuration: ' + (response.data.message || 'Unknown error'))
        }
    } catch (err) {
        showError('Error saving configuration: ' + (err.response?.data?.message || err.message))
    } finally {
        loading.value = false
    }
}

const resetConfiguration = () => {
    selectedStocks.value = [...props.configData?.current_stocks || []]
    selectedMode.value = props.configData?.current_mode || 'paper'
    refreshInterval.value = 10
    maxPositions.value = 5
    riskLevel.value = 'moderate'
    clearMessages()
    showSuccess('Configuration reset to defaults')
}

// Initialize
onMounted(() => {
    clearMessages()
})
</script>