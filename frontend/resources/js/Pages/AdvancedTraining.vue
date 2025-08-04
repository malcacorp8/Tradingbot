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
                        
                        <!-- Current Trading List -->
                        <div v-if="configuredStocks.length > 0" class="mt-4 p-4 bg-blue-50 rounded-lg">
                            <h4 class="font-medium mb-3 text-blue-800">📈 Current Trading List</h4>
                            <div class="flex flex-wrap gap-2">
                                <span 
                                    v-for="stock in configuredStocks" 
                                    :key="stock"
                                    class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                                >
                                    {{ stock }}
                                    <button 
                                        @click="removeFromTradingList(stock)"
                                        :disabled="updatingStocks"
                                        class="ml-2 text-blue-600 hover:text-red-600 transition-colors"
                                        title="Remove from trading list"
                                    >
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                        </svg>
                                    </button>
                                </span>
                            </div>
                        </div>

                        <!-- Search Results -->
                        <div v-if="searchResults.length > 0" class="mt-4">
                            <h4 class="font-medium mb-2">🔍 Search Results:</h4>
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div 
                                    v-for="stock in searchResults" 
                                    :key="stock.symbol"
                                    class="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                                    :class="stock.tradable ? 'border-gray-200' : 'border-gray-100 bg-gray-50'"
                                >
                                    <div class="font-semibold text-lg">{{ stock.symbol }}</div>
                                    <div class="text-gray-600 text-sm mb-2">{{ stock.name }}</div>
                                    <div class="text-xs text-gray-500 mb-3">{{ stock.exchange }}</div>
                                    <div class="text-sm mb-3" :class="stock.tradable ? 'text-green-600' : 'text-red-600'">
                                        {{ stock.tradable ? '✅ Tradable' : '❌ Not Tradable' }}
                                    </div>
                                    
                                    <div class="flex gap-2">
                                        <button 
                                            @click="selectStock(stock)"
                                            class="flex-1 px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
                                        >
                                            View Details
                                        </button>
                                        
                                        <button 
                                            v-if="stock.tradable && !configuredStocks.includes(stock.symbol)"
                                            @click="addToTradingList(stock.symbol)"
                                            :disabled="updatingStocks"
                                            class="flex-1 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors disabled:opacity-50"
                                        >
                                            {{ updatingStocks ? 'Adding...' : 'Add to List' }}
                                        </button>
                                        
                                        <button 
                                            v-else-if="stock.tradable && configuredStocks.includes(stock.symbol)"
                                            @click="removeFromTradingList(stock.symbol)"
                                            :disabled="updatingStocks"
                                            class="flex-1 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors disabled:opacity-50"
                                        >
                                            {{ updatingStocks ? 'Removing...' : 'Remove' }}
                                        </button>
                                        
                                        <span 
                                            v-else
                                            class="flex-1 px-3 py-1 text-sm bg-gray-300 text-gray-500 rounded text-center"
                                        >
                                            Not Tradable
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Stock Error Display -->
                <div v-if="stockError" class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-yellow-800">Notice</h3>
                            <div class="mt-2 text-sm text-yellow-700">
                                {{ stockError }}
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
                        <div v-if="importResult" class="mt-4">
                            <div v-if="importResult.error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
                                <h4 class="font-medium text-red-800 mb-2">❌ Import Error:</h4>
                                <p class="text-red-700">{{ importResult.error }}</p>
                            </div>
                            
                            <div v-else-if="importResult.success" class="p-4 bg-green-50 border border-green-200 rounded-lg">
                                <h4 class="font-medium text-green-800 mb-4">✅ Data Successfully Imported</h4>
                                
                                <!-- Summary Stats -->
                                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                                    <div class="bg-white p-3 rounded shadow-sm">
                                        <div class="text-sm text-gray-600">Data Points</div>
                                        <div class="text-lg font-semibold">{{ importResult.data_points?.toLocaleString() }}</div>
                                    </div>
                                    <div class="bg-white p-3 rounded shadow-sm">
                                        <div class="text-sm text-gray-600">Date Range</div>
                                        <div class="text-sm font-semibold">{{ formatDateRange(importResult.date_range) }}</div>
                                    </div>
                                    <div class="bg-white p-3 rounded shadow-sm">
                                        <div class="text-sm text-gray-600">Price Range</div>
                                        <div class="text-sm font-semibold">
                                            ${{ importResult.price_summary?.min_price?.toFixed(2) }} - 
                                            ${{ importResult.price_summary?.max_price?.toFixed(2) }}
                                        </div>
                                    </div>
                                    <div class="bg-white p-3 rounded shadow-sm">
                                        <div class="text-sm text-gray-600">Total Volume</div>
                                        <div class="text-sm font-semibold">{{ importResult.price_summary?.total_volume?.toLocaleString() }}</div>
                                    </div>
                                </div>

                                <!-- Sample Data Table -->
                                <div v-if="importResult.sample_data && importResult.sample_data.length > 0" class="mt-4">
                                    <h5 class="font-medium text-gray-700 mb-2">📈 Recent Data Sample (Last 10 points):</h5>
                                    <div class="overflow-x-auto">
                                        <table class="min-w-full text-xs bg-white border border-gray-200 rounded">
                                            <thead class="bg-gray-50">
                                                <tr>
                                                    <th class="px-2 py-1 text-left border-b">Time</th>
                                                    <th class="px-2 py-1 text-right border-b">Open</th>
                                                    <th class="px-2 py-1 text-right border-b">High</th>
                                                    <th class="px-2 py-1 text-right border-b">Low</th>
                                                    <th class="px-2 py-1 text-right border-b">Close</th>
                                                    <th class="px-2 py-1 text-right border-b">Volume</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(row, index) in importResult.sample_data.slice(-10)" :key="index" class="hover:bg-gray-50">
                                                    <td class="px-2 py-1 border-b text-gray-600">{{ formatTimestamp(row.timestamp) }}</td>
                                                    <td class="px-2 py-1 border-b text-right">${{ row.Open?.toFixed(2) }}</td>
                                                    <td class="px-2 py-1 border-b text-right text-green-600">${{ row.High?.toFixed(2) }}</td>
                                                    <td class="px-2 py-1 border-b text-right text-red-600">${{ row.Low?.toFixed(2) }}</td>
                                                    <td class="px-2 py-1 border-b text-right font-medium">${{ row.Close?.toFixed(2) }}</td>
                                                    <td class="px-2 py-1 border-b text-right text-gray-600">{{ row.Volume?.toLocaleString() }}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
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
                        <div v-if="simulationResult" class="mt-4">
                            <div v-if="simulationResult.error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
                                <h4 class="font-medium text-red-800 mb-2">❌ Simulation Error:</h4>
                                <p class="text-red-700">{{ simulationResult.error }}</p>
                            </div>
                            
                            <div v-else class="space-y-4">
                                <!-- Success Banner -->
                                <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
                                    <h4 class="font-medium text-green-800 mb-4">✅ Simulation Completed Successfully</h4>
                                    
                                    <!-- Performance Metrics -->
                                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                                        <div class="bg-white p-3 rounded shadow-sm">
                                            <div class="text-sm text-gray-600">Total Return</div>
                                            <div class="text-lg font-semibold" :class="simulationResult.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'">
                                                {{ simulationResult.total_return_pct?.toFixed(2) }}%
                                            </div>
                                        </div>
                                        <div class="bg-white p-3 rounded shadow-sm">
                                            <div class="text-sm text-gray-600">Win Rate</div>
                                            <div class="text-lg font-semibold text-blue-600">{{ simulationResult.win_rate?.toFixed(1) }}%</div>
                                        </div>
                                        <div class="bg-white p-3 rounded shadow-sm">
                                            <div class="text-sm text-gray-600">Total Trades</div>
                                            <div class="text-lg font-semibold">{{ simulationResult.total_trades }}</div>
                                        </div>
                                        <div class="bg-white p-3 rounded shadow-sm">
                                            <div class="text-sm text-gray-600">Sharpe Ratio</div>
                                            <div class="text-lg font-semibold text-purple-600">{{ simulationResult.sharpe_ratio?.toFixed(3) }}</div>
                                        </div>
                                    </div>
                                    
                                    <!-- Detailed Metrics -->
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                        <div class="bg-white p-4 rounded shadow-sm">
                                            <h5 class="font-medium mb-2 text-gray-700">💰 Portfolio Performance</h5>
                                            <div class="space-y-1 text-sm">
                                                <div><strong>Initial Value:</strong> ${{ simulationResult.initial_value?.toFixed(2) }}</div>
                                                <div><strong>Final Value:</strong> ${{ simulationResult.final_value?.toFixed(2) }}</div>
                                                <div><strong>Max Drawdown:</strong> <span class="text-red-600">{{ simulationResult.max_drawdown?.toFixed(2) }}%</span></div>
                                                <div><strong>Total Reward:</strong> {{ simulationResult.total_reward?.toFixed(4) }}</div>
                                            </div>
                                        </div>
                                        <div class="bg-white p-4 rounded shadow-sm">
                                            <h5 class="font-medium mb-2 text-gray-700">📊 Trading Accuracy</h5>
                                            <div class="space-y-1 text-sm">
                                                <div><strong>Winning Trades:</strong> <span class="text-green-600">{{ simulationResult.winning_trades }}</span></div>
                                                <div><strong>Losing Trades:</strong> <span class="text-red-600">{{ simulationResult.losing_trades }}</span></div>
                                                <div><strong>Avg Win:</strong> <span class="text-green-600">{{ simulationResult.avg_win?.toFixed(4) }}</span></div>
                                                <div><strong>Avg Loss:</strong> <span class="text-red-600">{{ simulationResult.avg_loss?.toFixed(4) }}</span></div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- Recent Trades -->
                                    <div v-if="simulationResult.trades && simulationResult.trades.length > 0" class="bg-white p-4 rounded shadow-sm">
                                        <h5 class="font-medium mb-2 text-gray-700">📈 Recent Trades</h5>
                                        <div class="overflow-x-auto">
                                            <table class="min-w-full text-xs">
                                                <thead class="bg-gray-50">
                                                    <tr>
                                                        <th class="px-2 py-1 text-left">Step</th>
                                                        <th class="px-2 py-1 text-left">Action</th>
                                                        <th class="px-2 py-1 text-right">Price</th>
                                                        <th class="px-2 py-1 text-right">Reward</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr v-for="(trade, index) in simulationResult.trades" :key="index" class="border-t">
                                                        <td class="px-2 py-1">{{ trade.step }}</td>
                                                        <td class="px-2 py-1">
                                                            <span :class="trade.action === 'buy' ? 'text-green-600' : 'text-red-600'">
                                                                {{ trade.action.toUpperCase() }}
                                                            </span>
                                                        </td>
                                                        <td class="px-2 py-1 text-right">${{ trade.price?.toFixed(2) }}</td>
                                                        <td class="px-2 py-1 text-right" :class="trade.reward >= 0 ? 'text-green-600' : 'text-red-600'">
                                                            {{ trade.reward?.toFixed(4) }}
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                    
                                    <!-- Model Saving Option -->
                                    <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                                        <h5 class="font-medium mb-2 text-blue-800">💾 Save This Model</h5>
                                        <div class="flex gap-2 items-end">
                                            <div class="flex-1">
                                                <label class="block text-sm font-medium text-gray-700 mb-1">Model Name</label>
                                                <input 
                                                    v-model="saveModelName" 
                                                    type="text" 
                                                    :placeholder="`${selectedStockSymbol}_best_model`"
                                                    class="w-full border-gray-300 focus:border-blue-500 focus:ring-blue-500 rounded-md shadow-sm"
                                                />
                                            </div>
                                            <div class="flex-1">
                                                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                                <input 
                                                    v-model="saveModelDescription" 
                                                    type="text" 
                                                    placeholder="High performance model with 65% win rate"
                                                    class="w-full border-gray-300 focus:border-blue-500 focus:ring-blue-500 rounded-md shadow-sm"
                                                />
                                            </div>
                                            <PrimaryButton @click="saveModel" :disabled="savingModel" class="whitespace-nowrap">
                                                {{ savingModel ? 'Saving...' : 'Save Model' }}
                                            </PrimaryButton>
                                        </div>
                                    </div>
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
const stockError = ref(null)
const configuredStocks = ref([])
const updatingStocks = ref(false)
const saveModelName = ref('')
const saveModelDescription = ref('')
const savingModel = ref(false)

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
    stockError.value = null
    
    try {
        // First get stock info
        const response = await fetch(`/api/training/stock-info/${selectedStockSymbol.value}`)
        
        if (response.status === 401) {
            stockError.value = 'Authentication required. Please log in to access the Advanced Training features.'
            return
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.stock) {
            selectedStock.value = data.stock
            if (data.message) {
                stockError.value = data.message
            }
        } else {
            // Fallback: create basic stock object
            selectedStock.value = {
                symbol: selectedStockSymbol.value,
                name: `${selectedStockSymbol.value} Stock`,
                exchange: 'NASDAQ',
                status: 'active',
                tradable: true
            }
            stockError.value = 'Limited information available for this stock'
        }
    } catch (error) {
        console.error('Error loading stock info:', error)
        stockError.value = `Error loading stock data: ${error.message}`
        
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

// Helper methods for formatting data
const formatDateRange = (dateRange) => {
    if (!dateRange || !dateRange.start || !dateRange.end) return 'N/A'
    const start = new Date(dateRange.start)
    const end = new Date(dateRange.end)
    return `${start.toLocaleDateString()} - ${end.toLocaleDateString()}`
}

const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A'
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// Stock management methods
const loadConfiguredStocks = async () => {
    try {
        const response = await fetch('/api/bot/health')
        if (response.ok) {
            const data = await response.json()
            if (data.data && data.data.configured_stocks) {
                configuredStocks.value = data.data.configured_stocks
            }
        }
    } catch (error) {
        console.error('Error loading configured stocks:', error)
    }
}

const addToTradingList = async (symbol) => {
    if (configuredStocks.value.includes(symbol)) return
    
    updatingStocks.value = true
    try {
        const newStocks = [...configuredStocks.value, symbol]
        const response = await fetch('/api/bot/configure', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                stocks: newStocks
            })
        })
        
        if (response.ok) {
            const data = await response.json()
            if (data.success && data.data && data.data.stocks) {
                configuredStocks.value = data.data.stocks
                alert(`✅ ${symbol} added to trading list successfully!`)
            }
        } else {
            throw new Error('Failed to update trading list')
        }
    } catch (error) {
        console.error('Error adding stock to trading list:', error)
        alert(`❌ Failed to add ${symbol} to trading list: ${error.message}`)
    } finally {
        updatingStocks.value = false
    }
}

const removeFromTradingList = async (symbol) => {
    if (!configuredStocks.value.includes(symbol)) return
    
    updatingStocks.value = true
    try {
        const newStocks = configuredStocks.value.filter(stock => stock !== symbol)
        const response = await fetch('/api/bot/configure', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                stocks: newStocks
            })
        })
        
        if (response.ok) {
            const data = await response.json()
            if (data.success && data.data && data.data.stocks) {
                configuredStocks.value = data.data.stocks
                alert(`✅ ${symbol} removed from trading list successfully!`)
            }
        } else {
            throw new Error('Failed to update trading list')
        }
    } catch (error) {
        console.error('Error removing stock from trading list:', error)
        alert(`❌ Failed to remove ${symbol} from trading list: ${error.message}`)
    } finally {
        updatingStocks.value = false
    }
}

const saveModel = async () => {
    if (!selectedStockSymbol.value) {
        alert('❌ Please select a stock first')
        return
    }
    
    savingModel.value = true
    try {
        const response = await fetch('/api/training/save-model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                symbol: selectedStockSymbol.value,
                model_name: saveModelName.value || undefined,
                description: saveModelDescription.value || ''
            })
        })
        
        const data = await response.json()
        
        if (response.ok && data.save_result && data.save_result.success) {
            alert(`✅ Model saved successfully as "${data.save_result.model_name}"`)
            saveModelName.value = ''
            saveModelDescription.value = ''
        } else {
            const error = data.save_result?.error || data.error || 'Unknown error'
            alert(`❌ Failed to save model: ${error}`)
        }
    } catch (error) {
        console.error('Error saving model:', error)
        alert(`❌ Failed to save model: ${error.message}`)
    } finally {
        savingModel.value = false
    }
}

// Load available models on mount
onMounted(() => {
    checkAuthentication()
    loadConfiguredStocks()
})
</script> 