<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                Advanced AI Training System
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Authentication Notice -->
                <div v-if="!isAuthenticated" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-yellow-800">
                                Authentication Required
                            </h3>
                            <div class="mt-2 text-sm text-yellow-700">
                                <p>Please log in to access the Advanced AI Training features. The dropdown and search functionality require authentication.</p>
                            </div>
                            <div class="mt-4">
                                <a href="/login" class="bg-yellow-50 text-yellow-800 hover:bg-yellow-100 px-3 py-2 rounded-md text-sm font-medium">
                                    Go to Login
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Stock Selection Section -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6 text-gray-900">
                        <h3 class="text-lg font-semibold mb-4">🔍 Stock Selection</h3>
                        
                        <!-- Quick Selection Dropdown -->
                        <div class="mb-6">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Quick Select Popular Stocks</label>
                            <div class="flex gap-4">
                                <select 
                                    v-model="selectedStockSymbol" 
                                    @change="selectStockFromDropdown"
                                    class="flex-1 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                                >
                                    <option value="">Select a stock...</option>
                                    <option value="AAPL">AAPL - Apple Inc.</option>
                                    <option value="TSLA">TSLA - Tesla, Inc.</option>
                                    <option value="GOOGL">GOOGL - Alphabet Inc.</option>
                                    <option value="MSFT">MSFT - Microsoft Corporation</option>
                                    <option value="NVDA">NVDA - NVIDIA Corporation</option>
                                    <option value="AMZN">AMZN - Amazon.com, Inc.</option>
                                    <option value="META">META - Meta Platforms, Inc.</option>
                                    <option value="NFLX">NFLX - Netflix, Inc.</option>
                                    <option value="AMD">AMD - Advanced Micro Devices, Inc.</option>
                                    <option value="INTC">INTC - Intel Corporation</option>
                                </select>
                                <PrimaryButton @click="loadStockInfo" :disabled="loadingStock">
                                    {{ loadingStock ? 'Loading...' : 'Load Stock Info' }}
                                </PrimaryButton>
                            </div>
                        </div>

                        <!-- Search Stocks -->
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Or Search for Other Stocks</label>
                            <div class="flex gap-4">
                                <input 
                                    v-model="searchQuery" 
                                    @keyup.enter="searchStocks"
                                    placeholder="Search stocks (e.g., AAPL, Tesla, Apple)"
                                    class="flex-1 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                                />
                                <PrimaryButton @click="searchStocks" :disabled="searching">
                                    {{ searching ? 'Searching...' : 'Search' }}
                                </PrimaryButton>
                            </div>
                        </div>
                        
                        <!-- Search Results -->
                        <div v-if="searchResults.length > 0" class="mt-4">
                            <h4 class="font-medium mb-2">Search Results:</h4>
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div 
                                    v-for="stock in searchResults" 
                                    :key="stock.symbol"
                                    @click="selectStock(stock)"
                                    class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                                >
                                    <div class="font-semibold text-lg">{{ stock.symbol }}</div>
                                    <div class="text-gray-600">{{ stock.name }}</div>
                                    <div class="text-sm text-gray-500">{{ stock.exchange }}</div>
                                    <div class="text-sm" :class="stock.tradable ? 'text-green-600' : 'text-red-600'">
                                        {{ stock.tradable ? 'Tradable' : 'Not Tradable' }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Selected Stock Info -->
                <div v-if="selectedStock" class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6 text-gray-900">
                        <h3 class="text-lg font-semibold mb-4">📊 Selected Stock: {{ selectedStock.symbol }}</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <h4 class="font-medium mb-2">Stock Information</h4>
                                <div class="space-y-2">
                                    <div><strong>Name:</strong> {{ selectedStock.name }}</div>
                                    <div><strong>Exchange:</strong> {{ selectedStock.exchange }}</div>
                                    <div><strong>Status:</strong> {{ selectedStock.status }}</div>
                                    <div><strong>Current Price:</strong> ${{ selectedStock.current_price || 'N/A' }}</div>
                                </div>
                            </div>
                            <div v-if="selectedStock.performance">
                                <h4 class="font-medium mb-2">Recent Performance (30 days)</h4>
                                <div class="space-y-2">
                                    <div><strong>Price Change:</strong> 
                                        <span :class="selectedStock.performance.price_change_pct >= 0 ? 'text-green-600' : 'text-red-600'">
                                            {{ selectedStock.performance.price_change_pct?.toFixed(2) }}%
                                        </span>
                                    </div>
                                    <div><strong>Volatility:</strong> {{ selectedStock.performance.volatility?.toFixed(4) }}</div>
                                    <div><strong>Avg Volume:</strong> {{ selectedStock.performance.volume_avg?.toLocaleString() }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Data Import Section -->
                <div v-if="selectedStock" class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6 text-gray-900">
                        <h3 class="text-lg font-semibold mb-4">📊 Import Historical Data</h3>
                        <div class="flex gap-4 mb-4">
                            <select v-model="importMonths" class="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm">
                                <option value="1">1 Month</option>
                                <option value="2">2 Months</option>
                                <option value="3">3 Months</option>
                                <option value="4">4 Months</option>
                                <option value="5">5 Months</option>
                                <option value="6">6 Months</option>
                            </select>
                            <PrimaryButton @click="importData" :disabled="importing">
                                {{ importing ? 'Importing...' : 'Import Data' }}
                            </PrimaryButton>
                        </div>
                        
                        <!-- Import Results -->
                        <div v-if="importResult" class="mt-4 p-4 bg-gray-50 rounded-lg">
                            <h4 class="font-medium mb-2">Import Results:</h4>
                            <div class="space-y-2">
                                <div><strong>Data Points:</strong> {{ importResult.data_points }}</div>
                                <div><strong>Date Range:</strong> {{ importResult.date_range?.start }} to {{ importResult.date_range?.end }}</div>
                                <div><strong>Price Range:</strong> ${{ importResult.statistics?.price_stats?.min?.toFixed(2) }} - ${{ importResult.statistics?.price_stats?.max?.toFixed(2) }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Model Training Section -->
                <div v-if="importResult" class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6 text-gray-900">
                        <h3 class="text-lg font-semibold mb-4">🤖 Train Advanced AI Model</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Model Type</label>
                                <select v-model="modelType" class="w-full border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm">
                                    <option value="PPO">PPO (Proximal Policy Optimization)</option>
                                    <option value="A2C">A2C (Advantage Actor-Critic)</option>
                                    <option value="SAC">SAC (Soft Actor-Critic)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Training Steps</label>
                                <input 
                                    v-model="trainingSteps" 
                                    type="number" 
                                    min="10000" 
                                    max="200000"
                                    class="w-full border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                                />
                            </div>
                            <div class="flex items-end">
                                <PrimaryButton @click="trainModel" :disabled="training">
                                    {{ training ? 'Training...' : 'Start Training' }}
                                </PrimaryButton>
                            </div>
                        </div>
                        
                        <!-- Training Status -->
                        <div v-if="trainingStatus" class="mt-4 p-4 bg-blue-50 rounded-lg">
                            <h4 class="font-medium mb-2">Training Status:</h4>
                            <div class="space-y-2">
                                <div><strong>Status:</strong> {{ trainingStatus.status }}</div>
                                <div v-if="trainingStatus.progress"><strong>Progress:</strong> {{ trainingStatus.progress }}%</div>
                                <div v-if="trainingStatus.start_time"><strong>Started:</strong> {{ new Date(trainingStatus.start_time).toLocaleString() }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Simulation Section -->
                <div v-if="availableModels.length > 0" class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6 text-gray-900">
                        <h3 class="text-lg font-semibold mb-4">🎯 Run Simulation</h3>
                        <div class="flex gap-4 mb-4">
                            <select v-model="selectedModel" class="flex-1 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm">
                                <option value="">Select a trained model</option>
                                <option v-for="model in availableModels" :key="model.filename" :value="model.path">
                                    {{ model.symbol }} - {{ model.model_type }} ({{ (model.size / 1024 / 1024).toFixed(1) }}MB)
                                </option>
                            </select>
                            <input 
                                v-model="simulationDays" 
                                type="number" 
                                min="1" 
                                max="90"
                                placeholder="Days"
                                class="w-24 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                            />
                            <PrimaryButton @click="runSimulation" :disabled="simulating">
                                {{ simulating ? 'Running...' : 'Run Simulation' }}
                            </PrimaryButton>
                        </div>
                        
                        <!-- Simulation Results -->
                        <div v-if="simulationResult" class="mt-4 p-4 bg-green-50 rounded-lg">
                            <h4 class="font-medium mb-2">Simulation Results:</h4>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <div><strong>Total Return:</strong> 
                                        <span :class="simulationResult.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'">
                                            {{ simulationResult.total_return_pct?.toFixed(2) }}%
                                        </span>
                                    </div>
                                    <div><strong>Total Trades:</strong> {{ simulationResult.total_trades }}</div>
                                    <div><strong>Initial Value:</strong> ${{ simulationResult.initial_value?.toFixed(2) }}</div>
                                    <div><strong>Final Value:</strong> ${{ simulationResult.final_value?.toFixed(2) }}</div>
                                </div>
                                <div>
                                    <div><strong>Total Reward:</strong> {{ simulationResult.total_reward?.toFixed(4) }}</div>
                                    <div><strong>Simulation Days:</strong> {{ simulationDays }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Available Models -->
                <div v-if="availableModels.length > 0" class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6 text-gray-900">
                        <h3 class="text-lg font-semibold mb-4">📁 Available Trained Models</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div 
                                v-for="model in availableModels" 
                                :key="model.filename"
                                class="border rounded-lg p-4"
                            >
                                <div class="font-semibold">{{ model.symbol }}</div>
                                <div class="text-gray-600">{{ model.model_type }}</div>
                                <div class="text-sm text-gray-500">{{ (model.size / 1024 / 1024).toFixed(1) }}MB</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue'
import PrimaryButton from '@/Components/PrimaryButton.vue'

// Reactive data
const searchQuery = ref('')
const searchResults = ref([])
const selectedStock = ref(null)
const selectedStockSymbol = ref('')
const searching = ref(false)
const loadingStock = ref(false)
const importing = ref(false)
const training = ref(false)
const simulating = ref(false)
const isAuthenticated = ref(false)

// Import settings
const importMonths = ref(3)
const importResult = ref(null)

// Training settings
const modelType = ref('PPO')
const trainingSteps = ref(50000)
const trainingStatus = ref(null)

// Simulation settings
const selectedModel = ref('')
const simulationDays = ref(30)
const simulationResult = ref(null)
const availableModels = ref([])

// Methods
const selectStockFromDropdown = () => {
    if (selectedStockSymbol.value) {
        loadStockInfo()
    }
}

const loadStockInfo = async () => {
    if (!selectedStockSymbol.value) return
    
    loadingStock.value = true
    try {
        // First get stock info
        const response = await fetch(`/api/training/stock-info/${selectedStockSymbol.value}`)
        
        if (response.status === 401) {
            console.error('Authentication required. Please log in.')
            alert('Please log in to access the Advanced Training features.')
            return
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.stock) {
            selectedStock.value = data.stock
        } else {
            // Fallback: create basic stock object
            selectedStock.value = {
                symbol: selectedStockSymbol.value,
                name: `${selectedStockSymbol.value} Stock`,
                exchange: 'NASDAQ',
                status: 'active',
                tradable: true
            }
        }
    } catch (error) {
        console.error('Error loading stock info:', error)
        if (error.message.includes('Unexpected token')) {
            alert('Please log in to access the Advanced Training features.')
            return
        }
        // Fallback: create basic stock object
        selectedStock.value = {
            symbol: selectedStockSymbol.value,
            name: `${selectedStockSymbol.value} Stock`,
            exchange: 'NASDAQ',
            status: 'active',
            tradable: true
        }
    } finally {
        loadingStock.value = false
    }
}

const searchStocks = async () => {
    if (!searchQuery.value.trim()) return
    
    searching.value = true
    try {
        const response = await fetch(`/api/training/search-stocks?query=${encodeURIComponent(searchQuery.value)}`)
        
        if (response.status === 401) {
            console.error('Authentication required. Please log in.')
            alert('Please log in to access the Advanced Training features.')
            return
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        searchResults.value = data.stocks || []
    } catch (error) {
        console.error('Error searching stocks:', error)
        if (error.message.includes('Unexpected token')) {
            alert('Please log in to access the Advanced Training features.')
            return
        }
    } finally {
        searching.value = false
    }
}

const selectStock = async (stock) => {
    selectedStock.value = stock
    try {
        const response = await fetch(`/api/training/stock-info/${stock.symbol}`)
        const data = await response.json()
        selectedStock.value = { ...stock, ...data }
    } catch (error) {
        console.error('Error getting stock info:', error)
    }
}

const importData = async () => {
    if (!selectedStock.value) return
    
    importing.value = true
    try {
        const response = await fetch('/api/training/import-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                symbol: selectedStock.value.symbol,
                months: parseInt(importMonths.value)
            })
        })
        const data = await response.json()
        importResult.value = data
        if (data.success) {
            loadAvailableModels()
        }
    } catch (error) {
        console.error('Error importing data:', error)
    } finally {
        importing.value = false
    }
}

const trainModel = async () => {
    if (!selectedStock.value || !importResult.value) return
    
    training.value = true
    try {
        const response = await fetch('/api/training/train-model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                symbol: selectedStock.value.symbol,
                model_type: modelType.value,
                training_steps: parseInt(trainingSteps.value)
            })
        })
        const data = await response.json()
        if (data.success) {
            trainingStatus.value = data
            // Poll for training status
            pollTrainingStatus(data.training_id)
        }
    } catch (error) {
        console.error('Error training model:', error)
    } finally {
        training.value = false
    }
}

const pollTrainingStatus = async (trainingId) => {
    const poll = async () => {
        try {
            const response = await fetch(`/api/training/status?training_id=${trainingId}`)
            const data = await response.json()
            trainingStatus.value = data
            
            if (data.status === 'training') {
                setTimeout(poll, 5000) // Poll every 5 seconds
            } else if (data.status === 'completed') {
                loadAvailableModels()
            }
        } catch (error) {
            console.error('Error polling training status:', error)
        }
    }
    poll()
}

const runSimulation = async () => {
    if (!selectedModel.value) return
    
    simulating.value = true
    try {
        const response = await fetch('/api/training/simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                symbol: selectedStock.value.symbol,
                days: parseInt(simulationDays.value),
                model_path: selectedModel.value
            })
        })
        const data = await response.json()
        if (data.success) {
            simulationResult.value = data.results
        }
    } catch (error) {
        console.error('Error running simulation:', error)
    } finally {
        simulating.value = false
    }
}

const loadAvailableModels = async () => {
    try {
        const response = await fetch('/api/training/models')
        
        if (response.status === 401) {
            console.error('Authentication required. Please log in.')
            return
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        availableModels.value = data.models || []
    } catch (error) {
        console.error('Error loading models:', error)
        if (error.message.includes('Unexpected token')) {
            console.error('Authentication required. Please log in.')
            return
        }
    }
}

// Check authentication status
const checkAuthentication = async () => {
    try {
        const response = await fetch('/api/bot/status')
        if (response.ok) {
            isAuthenticated.value = true
            loadAvailableModels()
        } else {
            isAuthenticated.value = false
        }
    } catch (error) {
        console.error('Error checking authentication:', error)
        isAuthenticated.value = false
    }
}

// Load available models on mount
onMounted(() => {
    checkAuthentication()
})
</script> 