<template>
    <div class="bg-white p-6 rounded-lg shadow-lg">
        <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold">📈 Trading Simulation Chart</h3>
            <div class="flex items-center space-x-4">
                <div class="text-sm text-gray-600">
                    {{ simulationData.symbol }} | {{ simulationData.simulation_period?.start_date }} to {{ simulationData.simulation_period?.end_date }}
                </div>
                <button 
                    @click="toggleChartType"
                    class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                    {{ chartType === 'price' ? 'Show Portfolio' : 'Show Price' }}
                </button>
            </div>
        </div>
        
        <!-- Chart Container -->
        <div class="relative h-96 mb-6">
            <Line
                :data="chartData"
                :options="chartOptions"
                :key="chartType"
            />
        </div>
        
        <!-- Trading Statistics -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-blue-50 p-3 rounded">
                <div class="text-sm text-gray-600">Total Return</div>
                <div class="text-lg font-bold" :class="simulationData.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ simulationData.total_return_pct?.toFixed(2) }}%
                </div>
            </div>
            <div class="bg-green-50 p-3 rounded">
                <div class="text-sm text-gray-600">Win Rate</div>
                <div class="text-lg font-bold text-green-600">
                    {{ simulationData.win_rate?.toFixed(1) }}%
                </div>
            </div>
            <div class="bg-orange-50 p-3 rounded">
                <div class="text-sm text-gray-600">Total Trades</div>
                <div class="text-lg font-bold text-orange-600">
                    {{ simulationData.total_trades }}
                </div>
            </div>
            <div class="bg-purple-50 p-3 rounded">
                <div class="text-sm text-gray-600">Sharpe Ratio</div>
                <div class="text-lg font-bold text-purple-600">
                    {{ simulationData.sharpe_ratio?.toFixed(3) }}
                </div>
            </div>
        </div>
        
        <!-- Trade Details -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Recent Trades -->
            <div>
                <h4 class="text-md font-semibold mb-3">📋 Recent Trades</h4>
                <div class="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                    <div v-if="simulationData.trades?.length === 0" class="text-gray-500 text-center py-4">
                        No trades executed during simulation
                    </div>
                    <div v-else class="space-y-2">
                        <div 
                            v-for="trade in simulationData.trades?.slice(-10)" 
                            :key="trade.step"
                            class="flex items-center justify-between p-2 bg-white rounded border text-sm"
                        >
                            <div class="flex items-center space-x-2">
                                <span 
                                    class="px-2 py-1 rounded text-xs font-semibold"
                                    :class="trade.action === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                                >
                                    {{ trade.action.toUpperCase() }}
                                </span>
                                <span class="text-gray-600">
                                    ${{ trade.price?.toFixed(2) }}
                                </span>
                            </div>
                            <div class="text-right">
                                <div class="font-medium" :class="trade.reward >= 0 ? 'text-green-600' : 'text-red-600'">
                                    {{ trade.reward >= 0 ? '+' : '' }}{{ trade.reward?.toFixed(2) }}
                                </div>
                                <div class="text-xs text-gray-500">
                                    {{ formatDate(trade.timestamp) }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div>
                <h4 class="text-md font-semibold mb-3">📊 Performance Metrics</h4>
                <div class="bg-gray-50 rounded-lg p-4">
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Initial Value:</span>
                            <span class="font-medium">${{ simulationData.initial_value?.toLocaleString() }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Final Value:</span>
                            <span class="font-medium">${{ simulationData.final_value?.toLocaleString() }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Winning Trades:</span>
                            <span class="font-medium text-green-600">{{ simulationData.winning_trades }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Losing Trades:</span>
                            <span class="font-medium text-red-600">{{ simulationData.losing_trades }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg Win:</span>
                            <span class="font-medium text-green-600">{{ simulationData.avg_win_pct?.toFixed(2) }}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg Loss:</span>
                            <span class="font-medium text-red-600">{{ simulationData.avg_loss_pct?.toFixed(2) }}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Max Drawdown:</span>
                            <span class="font-medium text-red-600">{{ simulationData.max_drawdown_pct?.toFixed(2) }}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
)

// Props
const props = defineProps({
    simulationData: {
        type: Object,
        required: true
    }
})

// Reactive data
const chartType = ref('price') // 'price' or 'portfolio'

// Computed properties
const chartData = computed(() => {
    if (!props.simulationData.chart_data || props.simulationData.chart_data.length === 0) {
        return {
            labels: [],
            datasets: []
        }
    }

    const data = props.simulationData.chart_data
    const labels = data.map(item => {
        const date = new Date(item.timestamp)
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })

    if (chartType.value === 'price') {
        // Price chart with buy/sell markers
        const buyPoints = []
        const sellPoints = []
        
        props.simulationData.trades?.forEach(trade => {
            if (trade.action === 'buy') {
                buyPoints.push({
                    x: trade.step,
                    y: trade.price
                })
            } else if (trade.action === 'sell') {
                sellPoints.push({
                    x: trade.step,
                    y: trade.price
                })
            }
        })

        return {
            labels,
            datasets: [
                {
                    label: `${props.simulationData.symbol} Price`,
                    data: data.map(item => item.price),
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Buy Signals',
                    data: buyPoints.map(point => ({
                        x: labels[point.x],
                        y: point.y
                    })),
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: false,
                    pointStyle: 'triangle'
                },
                {
                    label: 'Sell Signals',
                    data: sellPoints.map(point => ({
                        x: labels[point.x],
                        y: point.y
                    })),
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: false,
                    pointStyle: 'rectRot'
                }
            ]
        }
    } else {
        // Portfolio value chart
        return {
            labels,
            datasets: [
                {
                    label: 'Portfolio Value',
                    data: data.map(item => item.portfolio_value),
                    borderColor: 'rgb(168, 85, 247)',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Cash Balance',
                    data: data.map(item => item.balance),
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    borderDash: [5, 5]
                }
            ]
        }
    }
})

const chartOptions = computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        mode: 'index',
        intersect: false,
    },
    plugins: {
        title: {
            display: true,
            text: chartType.value === 'price' 
                ? `${props.simulationData.symbol} Price with Trading Signals`
                : 'Portfolio Performance Over Time'
        },
        legend: {
            display: true,
            position: 'top'
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    const label = context.dataset.label || ''
                    const value = context.parsed.y
                    
                    if (label.includes('Price') || label.includes('Portfolio') || label.includes('Balance')) {
                        return `${label}: $${value.toFixed(2)}`
                    } else {
                        return `${label}: $${value.toFixed(2)}`
                    }
                }
            }
        }
    },
    scales: {
        x: {
            display: true,
            title: {
                display: true,
                text: 'Time'
            },
            ticks: {
                maxTicksLimit: 10
            }
        },
        y: {
            display: true,
            title: {
                display: true,
                text: chartType.value === 'price' ? 'Price ($)' : 'Value ($)'
            },
            ticks: {
                callback: function(value) {
                    return '$' + value.toFixed(0)
                }
            }
        }
    },
    elements: {
        point: {
            radius: 0,
            hoverRadius: 4
        }
    }
}))

// Methods
const toggleChartType = () => {
    chartType.value = chartType.value === 'price' ? 'portfolio' : 'price'
}

const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>