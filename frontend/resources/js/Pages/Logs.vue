<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                📋 Advanced Trading Logs & Analytics
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
                
                <!-- Log Summary Dashboard -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-lg font-medium">📊 Log Summary Dashboard</h3>
                            <button 
                                @click="refreshSummary"
                                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                                :disabled="loadingSummary"
                            >
                                {{ loadingSummary ? 'Loading...' : 'Refresh' }}
                            </button>
                        </div>
                        
                        <div v-if="logSummary" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <div class="text-2xl font-bold text-blue-600">{{ logSummary.total_activities }}</div>
                                <div class="text-sm text-gray-600">Total Activities</div>
                                <div class="text-xs text-gray-500 mt-1">
                                    {{ logSummary.date_range?.start }} to {{ logSummary.date_range?.end }}
                                </div>
                            </div>
                            
                            <div class="bg-green-50 p-4 rounded-lg">
                                <div class="text-2xl font-bold text-green-600">{{ Object.keys(logSummary.stocks || {}).length }}</div>
                                <div class="text-sm text-gray-600">Active Stocks</div>
                                <div class="text-xs text-gray-500 mt-1">
                                    {{ Object.keys(logSummary.stocks || {}).slice(0, 3).join(', ') }}
                                    {{ Object.keys(logSummary.stocks || {}).length > 3 ? '...' : '' }}
                                </div>
                            </div>
                            
                            <div class="bg-purple-50 p-4 rounded-lg">
                                <div class="text-2xl font-bold text-purple-600">{{ Object.keys(logSummary.bots || {}).length }}</div>
                                <div class="text-sm text-gray-600">Bot Types</div>
                                <div class="text-xs text-gray-500 mt-1">
                                    {{ Object.keys(logSummary.bots || {}).join(', ') }}
                                </div>
                            </div>
                            
                            <div class="bg-orange-50 p-4 rounded-lg">
                                <div class="text-2xl font-bold text-orange-600">{{ Object.keys(logSummary.actions || {}).length }}</div>
                                <div class="text-sm text-gray-600">Action Types</div>
                                <div class="text-xs text-gray-500 mt-1">
                                    {{ Object.keys(logSummary.actions || {}).slice(0, 2).join(', ') }}
                                    {{ Object.keys(logSummary.actions || {}).length > 2 ? '...' : '' }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Advanced Log Controls -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium mb-4">🔍 Advanced Log Filters</h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                            <!-- Log Type Filter -->
                            <div class="space-y-2">
                                <label class="text-sm font-medium text-gray-700">Log Type</label>
                                <select v-model="logType" class="w-full form-select text-sm">
                                    <option value="daily">📅 Daily Logs</option>
                                    <option value="stock">📈 Stock-Specific</option>
                                    <option value="bot">🤖 Bot-Specific</option>
                                </select>
                            </div>
                            
                            <!-- Stock/Bot Selector -->
                            <div class="space-y-2" v-if="logType !== 'daily'">
                                <label class="text-sm font-medium text-gray-700">
                                    {{ logType === 'stock' ? 'Select Stock' : 'Select Bot Type' }}
                                </label>
                                <select v-model="selectedIdentifier" class="w-full form-select text-sm">
                                    <option value="">-- Select {{ logType === 'stock' ? 'Stock' : 'Bot' }} --</option>
                                    <option v-for="item in availableOptions" :key="item" :value="item">
                                        {{ item }}
                                    </option>
                                </select>
                            </div>
                            
                            <!-- Date Range -->
                            <div class="space-y-2">
                                <label class="text-sm font-medium text-gray-700">Start Date</label>
                                <input 
                                    type="date" 
                                    v-model="startDate" 
                                    class="w-full form-input text-sm"
                                    :max="endDate"
                                />
                            </div>
                            
                            <div class="space-y-2">
                                <label class="text-sm font-medium text-gray-700">End Date</label>
                                <input 
                                    type="date" 
                                    v-model="endDate" 
                                    class="w-full form-input text-sm"
                                    :min="startDate"
                                    :max="today"
                                />
                            </div>
                        </div>
                        
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-4">
                                <button 
                                    @click="loadLogs"
                                    class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                    :disabled="loadingLogs"
                                >
                                    {{ loadingLogs ? 'Loading...' : 'Filter Logs' }}
                                </button>
                                
                                <button 
                                    @click="resetFilters"
                                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                                >
                                    Reset Filters
                                </button>
                            </div>
                            
                            <div class="flex items-center space-x-4">
                                <button 
                                    @click="downloadLogs"
                                    class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                                    :disabled="loadingDownload || logs.length === 0"
                                >
                                    {{ loadingDownload ? 'Preparing...' : '📥 Download' }}
                                </button>
                                
                                <button 
                                    @click="archiveLogs"
                                    class="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
                                    :disabled="loadingArchive"
                                >
                                    {{ loadingArchive ? 'Archiving...' : '📦 Archive Old' }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Log Data Display -->
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-medium">📋 Trading Logs</h3>
                            <div class="text-sm text-gray-600">
                                Showing {{ logs.length }} entries
                                <span v-if="logType !== 'daily' && selectedIdentifier">
                                    for {{ logType === 'stock' ? 'stock' : 'bot' }} {{ selectedIdentifier }}
                                </span>
                            </div>
                        </div>

                        <div v-if="loadingLogs" class="text-center py-8">
                            <div class="animate-spin h-8 w-8 mx-auto border-4 border-blue-600 border-t-transparent rounded-full"></div>
                            <div class="mt-2 text-gray-600">Loading logs...</div>
                        </div>

                        <div v-else-if="logs.length === 0" class="text-center py-8 text-gray-500">
                            📭 No logs found for the selected criteria
                        </div>

                        <div v-else class="space-y-3 max-h-96 overflow-y-auto">
                            <div v-for="log in logs" :key="log.timestamp" class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1">
                                        <div class="flex items-center space-x-3 mb-2">
                                            <div class="flex items-center space-x-2">
                                                <span class="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                                                    {{ log.stock }}
                                                </span>
                                                <span class="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800">
                                                    {{ log.bot_type }}
                                                </span>
                                                <span class="text-xs px-2 py-1 rounded-full" 
                                                      :class="getActionColor(log.action)">
                                                    {{ log.action }}
                                                </span>
                                            </div>
                                            <div class="text-xs text-gray-500">
                                                {{ formatTimestamp(log.timestamp) }}
                                            </div>
                                        </div>
                                        
                                        <div v-if="log.details" class="mt-2 space-y-1">
                                            <div v-for="(value, key) in log.details" :key="key" class="text-sm">
                                                <span class="text-gray-600 capitalize">{{ key.replace('_', ' ') }}:</span>
                                                <span class="ml-2 font-medium">
                                                    {{ formatDetailValue(key, value) }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue'

// Reactive data
const logSummary = ref(null)
const logs = ref([])
const availableStocks = ref([])
const availableBots = ref([])
const logType = ref('daily')
const selectedIdentifier = ref('')
const startDate = ref('')
const endDate = ref('')
const today = ref(new Date().toISOString().split('T')[0])

// Loading states
const loadingSummary = ref(false)
const loadingLogs = ref(false)
const loadingDownload = ref(false)
const loadingArchive = ref(false)

// Initialize dates (last 7 days by default)
const initializeDates = () => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 7)
    
    endDate.value = end.toISOString().split('T')[0]
    startDate.value = start.toISOString().split('T')[0]
}

// Computed properties
const availableOptions = computed(() => {
    return logType.value === 'stock' ? availableStocks.value : availableBots.value
})

// Watch for log type changes
watch(logType, () => {
    selectedIdentifier.value = ''
    loadLogs()
})

// API methods
const refreshSummary = async () => {
    loadingSummary.value = true
    try {
        const params = new URLSearchParams({
            start_date: startDate.value,
            end_date: endDate.value
        })
        
        const response = await fetch(`/api/logs/summary?${params}`)
        const data = await response.json()
        
        if (data.success) {
            logSummary.value = data.summary
        }
    } catch (error) {
        console.error('Error fetching log summary:', error)
    } finally {
        loadingSummary.value = false
    }
}

const loadAvailableOptions = async () => {
    try {
        // Load available stocks
        const stocksResponse = await fetch('/api/logs/stocks')
        const stocksData = await stocksResponse.json()
        if (stocksData.success) {
            availableStocks.value = stocksData.stocks
        }
        
        // Load available bots
        const botsResponse = await fetch('/api/logs/bots')
        const botsData = await botsResponse.json()
        if (botsData.success) {
            availableBots.value = botsData.bots
        }
    } catch (error) {
        console.error('Error loading available options:', error)
    }
}

const loadLogs = async () => {
    loadingLogs.value = true
    try {
        const params = new URLSearchParams({
            type: logType.value,
            start_date: startDate.value,
            end_date: endDate.value
        })
        
        if (logType.value !== 'daily' && selectedIdentifier.value) {
            params.append('identifier', selectedIdentifier.value)
        }
        
        const response = await fetch(`/api/logs/advanced?${params}`)
        const data = await response.json()
        
        if (data.success) {
            logs.value = data.logs
        }
    } catch (error) {
        console.error('Error loading logs:', error)
        logs.value = []
    } finally {
        loadingLogs.value = false
    }
}

const downloadLogs = async () => {
    loadingDownload.value = true
    try {
        const params = new URLSearchParams({
            type: logType.value,
            start_date: startDate.value,
            end_date: endDate.value
        })
        
        if (logType.value !== 'daily' && selectedIdentifier.value) {
            params.append('identifier', selectedIdentifier.value)
        }
        
        const response = await fetch(`/api/logs/download?${params}`)
        const data = await response.json()
        
        if (data.success && data.download_url) {
            // Open download URL in new tab
            window.open(data.download_url, '_blank')
        }
    } catch (error) {
        console.error('Error downloading logs:', error)
        alert('Failed to download logs')
    } finally {
        loadingDownload.value = false
    }
}

const archiveLogs = async () => {
    const daysToKeep = prompt('Enter number of days to keep (default: 90):', '90')
    if (!daysToKeep) return
    
    const days = parseInt(daysToKeep)
    if (isNaN(days) || days < 1) {
        alert('Please enter a valid number of days')
        return
    }
    
    loadingArchive.value = true
    try {
        const response = await fetch('/api/logs/archive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ days_to_keep: days })
        })
        
        const data = await response.json()
        
        if (data.success) {
            alert(`Successfully archived logs older than ${days} days`)
            refreshSummary()
            loadLogs()
        } else {
            alert('Failed to archive logs: ' + (data.error || 'Unknown error'))
        }
    } catch (error) {
        console.error('Error archiving logs:', error)
        alert('Failed to archive logs')
    } finally {
        loadingArchive.value = false
    }
}

const resetFilters = () => {
    logType.value = 'daily'
    selectedIdentifier.value = ''
    initializeDates()
    loadLogs()
}

// Helper methods
const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
}

const formatDetailValue = (key, value) => {
    if (key.includes('price') || key.includes('value') || key.includes('profit')) {
        return typeof value === 'number' ? `$${value.toFixed(2)}` : value
    }
    if (key.includes('pct') || key.includes('rate') || key.includes('ratio')) {
        return typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : value
    }
    if (key.includes('duration') && key.includes('minutes')) {
        return `${value} min`
    }
    return value
}

const getActionColor = (action) => {
    const colors = {
        buy: 'bg-green-100 text-green-800',
        sell: 'bg-red-100 text-red-800',
        hold: 'bg-yellow-100 text-yellow-800',
        train_model: 'bg-blue-100 text-blue-800',
        import_data: 'bg-indigo-100 text-indigo-800',
        simulation_run: 'bg-purple-100 text-purple-800'
    }
    return colors[action] || 'bg-gray-100 text-gray-800'
}

// Lifecycle
onMounted(() => {
    initializeDates()
    loadAvailableOptions()
    refreshSummary()
    loadLogs()
})
</script>