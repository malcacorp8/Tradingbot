<template>
    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                Trading Bot Dashboard
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Combined System Status & Account Balance -->
                <div class="bg-gradient-to-r from-green-50 via-blue-50 to-purple-50 overflow-hidden shadow-xl sm:rounded-xl mb-6" v-if="tradingStatus && tradingStatus.account_info">
                    <div class="p-6">
                        <!-- Main Status Bar -->
                        <div class="flex items-center justify-between mb-6">
                            <!-- System Status -->
                            <div class="flex items-center space-x-6">
                                <div class="flex items-center space-x-3">
                                    <div class="flex items-center space-x-2">
                                        <div :class="connectionStatusClass" class="w-4 h-4 rounded-full animate-pulse shadow-lg"></div>
                                        <div>
                                            <div class="text-sm font-semibold text-gray-700">System Status</div>
                                            <div class="text-xs text-gray-500">{{ connectionStatusText }}</div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Account Balance -->
                                <div class="flex items-center space-x-4 border-l-2 border-gray-200 pl-6">
                                    <div class="flex items-center space-x-2">
                                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                                        </svg>
                                        <div>
                                            <div class="text-sm font-semibold text-gray-700">Account Balance</div>
                                            <div class="text-xs text-gray-500">{{ tradingStatus.account_info.currency }} Cash</div>
                                        </div>
                                    </div>
                                    <div class="text-3xl font-bold text-green-700">
                                        ${{ formatNumber(tradingStatus.account_info.cash) }}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="flex items-center space-x-3">
                                <button 
                                    @click="refreshStatus"
                                    :disabled="loading"
                                    class="flex items-center space-x-2 px-4 py-2 bg-white text-blue-600 rounded-lg shadow hover:bg-blue-50 transition-colors disabled:opacity-50"
                                >
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                                    </svg>
                                    <span class="text-sm font-medium">{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
                                </button>
                                <button 
                                    @click="showAccountDetails = !showAccountDetails"
                                    class="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-purple-600 bg-white rounded-lg shadow hover:bg-purple-50 transition-colors"
                                >
                                    <span>{{ showAccountDetails ? 'Hide' : 'Show' }} Details</span>
                                    <svg :class="showAccountDetails ? 'rotate-180' : ''" class="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                    </svg>
                                </button>
                            </div>
                        </div>
                        
                        <!-- Quick Status Indicators -->
                        <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-green-500">
                                <div class="text-xs text-green-600 font-medium uppercase tracking-wide">Trading</div>
                                <div class="flex items-center space-x-2 mt-1">
                                    <div :class="tradingStatus.account_info.trading_blocked ? 'bg-red-500' : 'bg-green-500'" class="w-2 h-2 rounded-full"></div>
                                    <span class="text-sm font-semibold">{{ tradingStatus.account_info.trading_blocked ? 'Blocked' : 'Active' }}</span>
                                </div>
                            </div>
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-blue-500">
                                <div class="text-xs text-blue-600 font-medium uppercase tracking-wide">Backend</div>
                                <div class="flex items-center space-x-2 mt-1">
                                    <div :class="connectionStatusClass" class="w-2 h-2 rounded-full"></div>
                                    <span class="text-sm font-semibold">{{ backendConnected ? 'Connected' : 'Offline' }}</span>
                                </div>
                            </div>
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-purple-500">
                                <div class="text-xs text-purple-600 font-medium uppercase tracking-wide">Mode</div>
                                <div class="text-sm font-semibold mt-1 capitalize">{{ selectedMode }}</div>
                            </div>
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-orange-500">
                                <div class="text-xs text-orange-600 font-medium uppercase tracking-wide">Day Trades</div>
                                <div class="text-sm font-semibold mt-1">{{ tradingStatus.account_info.daytrade_count }}/3</div>
                            </div>
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-yellow-500">
                                <div class="text-xs text-yellow-600 font-medium uppercase tracking-wide">PDT Status</div>
                                <div class="text-sm font-semibold mt-1">{{ tradingStatus.account_info.pattern_day_trader ? 'Yes' : 'No' }}</div>
                            </div>
                        </div>
                        
                        <!-- Expandable Account Details -->
                        <div v-show="showAccountDetails" class="border-t pt-4 transition-all duration-300">
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div class="bg-white p-4 rounded-lg shadow-sm border-l-4 border-blue-500">
                                    <div class="text-sm text-blue-600 font-medium">Account Number</div>
                                    <div class="text-lg font-bold text-blue-800">{{ tradingStatus.account_info.account_number }}</div>
                                    <div class="text-xs text-blue-600">{{ tradingStatus.account_info.status }}</div>
                                </div>
                                <div class="bg-white p-4 rounded-lg shadow-sm border-l-4 border-purple-500">
                                    <div class="text-sm text-purple-600 font-medium">Portfolio Value</div>
                                    <div class="text-lg font-bold text-purple-800">${{ formatNumber(tradingStatus.account_info.portfolio_value) }}</div>
                                    <div class="text-xs text-purple-600">Total Equity</div>
                                </div>
                                <div class="bg-white p-4 rounded-lg shadow-sm border-l-4 border-orange-500">
                                    <div class="text-sm text-orange-600 font-medium">Buying Power</div>
                                    <div class="text-lg font-bold text-orange-800">${{ formatNumber(tradingStatus.account_info.buying_power) }}</div>
                                    <div class="text-xs text-orange-600">Available to Trade</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Enhanced Performance Summary -->
                <div class="bg-gradient-to-br from-white to-gray-50 overflow-hidden shadow-xl sm:rounded-xl mb-6" v-if="tradingStatus && tradingStatus.overall_performance">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-xl font-bold text-gray-800 flex items-center">
                                <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                </svg>
                                Trading Performance
                            </h3>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                                <span class="text-sm font-medium text-gray-600">Live Data</span>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <div class="bg-white p-6 rounded-xl shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <div class="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Trades</div>
                                        <div class="text-3xl font-bold text-gray-800 mt-1">{{ tradingStatus.overall_performance.total_trades }}</div>
                                    </div>
                                    <div class="p-3 bg-gray-100 rounded-full">
                                        <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-md border-l-4 border-green-500 hover:shadow-lg transition-shadow">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <div class="text-sm font-medium text-green-600 uppercase tracking-wide">Wins</div>
                                        <div class="text-3xl font-bold text-green-700 mt-1">{{ tradingStatus.overall_performance.total_wins }}</div>
                                        <div class="text-sm text-green-600 font-medium">{{ formatPercentage(tradingStatus.overall_performance.overall_win_rate) }}% Win Rate</div>
                                    </div>
                                    <div class="p-3 bg-green-100 rounded-full">
                                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-md border-l-4 border-red-500 hover:shadow-lg transition-shadow">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <div class="text-sm font-medium text-red-600 uppercase tracking-wide">Losses</div>
                                        <div class="text-3xl font-bold text-red-700 mt-1">{{ tradingStatus.overall_performance.total_losses }}</div>
                                    </div>
                                    <div class="p-3 bg-red-100 rounded-full">
                                        <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-md border-l-4 border-blue-500 hover:shadow-lg transition-shadow">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <div class="text-sm font-medium text-blue-600 uppercase tracking-wide">Profit/Loss</div>
                                        <div class="text-3xl font-bold mt-1" :class="getReturnClass(tradingStatus.overall_performance.total_profit)">
                                            ${{ formatNumber(tradingStatus.overall_performance.total_profit) }}
                                        </div>
                                        <div class="text-sm font-medium" :class="getReturnClass(tradingStatus.overall_performance.total_profit_percentage)">
                                            {{ formatPercentage(tradingStatus.overall_performance.total_profit_percentage) }}% Return
                                        </div>
                                    </div>
                                    <div class="p-3 bg-blue-100 rounded-full">
                                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Enhanced Best/Worst Performing -->
                        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-xl border border-green-200">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <div class="text-sm font-medium text-green-600 uppercase tracking-wide">Best Performer</div>
                                        <div class="text-xl font-bold text-green-800 mt-1">
                                            {{ tradingStatus.overall_performance.best_performing_stock }}
                                        </div>
                                        <div class="text-sm text-green-700 font-medium">
                                            +{{ formatPercentage(tradingStatus.portfolio[tradingStatus.overall_performance.best_performing_stock]?.performance?.total_return || 0) }}% Return
                                        </div>
                                    </div>
                                    <div class="p-3 bg-green-200 rounded-full">
                                        <svg class="w-6 h-6 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-gradient-to-r from-red-50 to-red-100 p-4 rounded-xl border border-red-200">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <div class="text-sm font-medium text-red-600 uppercase tracking-wide">Needs Attention</div>
                                        <div class="text-xl font-bold text-red-800 mt-1">
                                            {{ tradingStatus.overall_performance.worst_performing_stock }}
                                        </div>
                                        <div class="text-sm text-red-700 font-medium">
                                            +{{ formatPercentage(tradingStatus.portfolio[tradingStatus.overall_performance.worst_performing_stock]?.performance?.total_return || 0) }}% Return
                                        </div>
                                    </div>
                                    <div class="p-3 bg-red-200 rounded-full">
                                        <svg class="w-6 h-6 text-red-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.765 0L3.049 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>
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

                <!-- Enhanced Portfolio Overview -->
                <div class="bg-white overflow-hidden shadow-xl sm:rounded-xl mb-6" v-if="tradingStatus && tradingStatus.portfolio">
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-xl font-bold text-gray-800 flex items-center">
                                <svg class="w-6 h-6 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                </svg>
                                Stock Portfolio
                            </h3>
                            <div class="text-sm text-gray-500">Click any row to view trade details</div>
                        </div>
                        
                        <div class="overflow-x-auto">
                            <table class="min-w-full table-auto">
                                <thead>
                                    <tr class="bg-gradient-to-r from-gray-50 to-gray-100">
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Symbol</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Balance</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Position</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Price/Share</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Trades</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Wins</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Losses</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Win Rate</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Profit/Loss</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Return %</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Streak</th>
                                        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    <tr 
                                        v-for="(data, symbol) in tradingStatus.portfolio" 
                                        :key="symbol"
                                        @click="openTradeDetails(symbol)"
                                        class="hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 cursor-pointer transition-all duration-200 transform hover:scale-[1.01]"
                                    >
                                        <td class="px-6 py-4">
                                            <div class="flex items-center">
                                                <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                                    <span class="text-white font-bold text-sm">{{ symbol.charAt(0) }}</span>
                                                </div>
                                                <div class="ml-4">
                                                    <div class="text-sm font-bold text-gray-900">{{ symbol }}</div>
                                                    <div class="text-sm text-gray-500">Stock Symbol</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm font-semibold text-gray-900">
                                                ${{ formatNumber(data.performance?.balance || 0) }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {{ data.performance?.position || 0 }} shares
                                            </span>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm font-semibold text-green-700">
                                                ${{ formatNumber(data.performance?.current_price || 0) }}
                                            </div>
                                            <div class="text-xs text-gray-500">Current Price</div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm font-semibold text-gray-900">
                                                {{ data.performance?.total_trades || 0 }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm font-bold text-green-600">
                                                {{ data.performance?.wins || 0 }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm font-bold text-red-600">
                                                {{ data.performance?.losses || 0 }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold" :class="getWinRateBadgeClass(data.performance?.win_rate || 0)">
                                                {{ formatPercentage(data.performance?.win_rate || 0) }}%
                                            </span>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm font-bold" :class="getReturnClass(data.performance?.total_profit || 0)">
                                                ${{ formatNumber(data.performance?.total_profit || 0) }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm font-bold" :class="getReturnClass(data.performance?.total_return || 0)">
                                                {{ formatPercentage(data.performance?.total_return || 0) }}%
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold" :class="getStreakBadgeClass(data.performance?.current_streak || 0)">
                                                {{ data.performance?.current_streak || 0 > 0 ? '+' : '' }}{{ data.performance?.current_streak || 0 }}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="flex space-x-2">
                                                <button 
                                                    @click.stop="evaluateAgent(symbol)"
                                                    :disabled="loading"
                                                    class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
                                                >
                                                    Evaluate
                                                </button>
                                                <button 
                                                    @click.stop="retrainAgent(symbol)"
                                                    :disabled="loading || tradingActive"
                                                    class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 transition-colors"
                                                >
                                                    Retrain
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Detailed Performance Stats -->
                        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="bg-gray-50 p-4 rounded">
                                <h4 class="font-medium text-gray-800 mb-2">Average Performance</h4>
                                <div class="space-y-1 text-sm">
                                    <div>Avg Win: <span class="text-green-600 font-medium">${{ formatNumber(getAverageWin()) }}</span></div>
                                    <div>Avg Loss: <span class="text-red-600 font-medium">${{ formatNumber(getAverageLoss()) }}</span></div>
                                    <div>Largest Win: <span class="text-green-600 font-medium">${{ formatNumber(getLargestWin()) }}</span></div>
                                    <div>Largest Loss: <span class="text-red-600 font-medium">${{ formatNumber(getLargestLoss()) }}</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Trade Details Modal -->
                <div v-if="showTradeModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
                    <div class="relative bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
                        <!-- Modal Header -->
                        <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-xl">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center space-x-4">
                                    <div class="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                                        <span class="text-xl font-bold">{{ selectedStock }}</span>
                                    </div>
                                    <div>
                                        <h3 class="text-2xl font-bold">{{ selectedStock }} Trade Details</h3>
                                        <p class="text-blue-100">Trading performance and charts</p>
                                    </div>
                                </div>
                                <button 
                                    @click="closeTradeModal"
                                    class="text-white hover:text-gray-200 transition-colors"
                                >
                                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <!-- Modal Content -->
                        <div class="p-6">
                            <!-- Performance Summary -->
                            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                                <div class="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                                    <div class="text-sm font-medium text-green-600 uppercase tracking-wide">Total Profit</div>
                                    <div class="text-2xl font-bold text-green-700 mt-1">
                                        ${{ formatNumber(selectedStockData?.performance?.total_profit || 0) }}
                                    </div>
                                    <div class="text-sm text-green-600">
                                        {{ formatPercentage(selectedStockData?.performance?.total_return || 0) }}% Return
                                    </div>
                                </div>
                                <div class="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                                    <div class="text-sm font-medium text-blue-600 uppercase tracking-wide">Win Rate</div>
                                    <div class="text-2xl font-bold text-blue-700 mt-1">
                                        {{ formatPercentage(selectedStockData?.performance?.win_rate || 0) }}%
                                    </div>
                                    <div class="text-sm text-blue-600">
                                        {{ selectedStockData?.performance?.wins || 0 }} wins / {{ selectedStockData?.performance?.losses || 0 }} losses
                                    </div>
                                </div>
                                <div class="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                                    <div class="text-sm font-medium text-purple-600 uppercase tracking-wide">Average Win</div>
                                    <div class="text-2xl font-bold text-purple-700 mt-1">
                                        ${{ formatNumber(selectedStockData?.performance?.avg_win || 0) }}
                                    </div>
                                    <div class="text-sm text-purple-600">
                                        Avg Loss: ${{ formatNumber(selectedStockData?.performance?.avg_loss || 0) }}
                                    </div>
                                </div>
                                <div class="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
                                    <div class="text-sm font-medium text-orange-600 uppercase tracking-wide">Best Trade</div>
                                    <div class="text-2xl font-bold text-orange-700 mt-1">
                                        ${{ formatNumber(selectedStockData?.performance?.largest_win || 0) }}
                                    </div>
                                    <div class="text-sm text-orange-600">
                                        Worst: ${{ formatNumber(selectedStockData?.performance?.largest_loss || 0) }}
                                    </div>
                                </div>
                            </div>

                            <!-- Price Chart -->
                            <div class="bg-white rounded-lg border border-gray-200 p-6 mb-8">
                                <h4 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                    </svg>
                                    Buy/Sell Price Chart
                                </h4>
                                <div class="h-64 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg flex items-center justify-center">
                                    <canvas ref="priceChart" width="800" height="200" class="max-w-full"></canvas>
                                </div>
                            </div>

                            <!-- Recent Trades -->
                            <div class="bg-white rounded-lg border border-gray-200 p-6">
                                <h4 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                    <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                                    </svg>
                                    Recent Trades
                                </h4>
                                <div class="overflow-x-auto">
                                    <table class="min-w-full table-auto">
                                        <thead>
                                            <tr class="bg-gray-50">
                                                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Date</th>
                                                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Type</th>
                                                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Shares</th>
                                                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Buy Price</th>
                                                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Sell Price</th>
                                                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Profit/Loss</th>
                                                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Result</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-gray-200">
                                            <tr v-for="trade in mockTradeData" :key="trade.id" class="hover:bg-gray-50">
                                                <td class="px-4 py-2 text-sm text-gray-900">{{ trade.date }}</td>
                                                <td class="px-4 py-2">
                                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                        {{ trade.type }}
                                                    </span>
                                                </td>
                                                <td class="px-4 py-2 text-sm text-gray-900">{{ trade.shares }}</td>
                                                <td class="px-4 py-2 text-sm font-medium text-gray-900">${{ trade.buyPrice.toFixed(2) }}</td>
                                                <td class="px-4 py-2 text-sm font-medium text-gray-900">${{ trade.sellPrice.toFixed(2) }}</td>
                                                <td class="px-4 py-2 text-sm font-bold" :class="trade.profit >= 0 ? 'text-green-600' : 'text-red-600'">
                                                    ${{ trade.profit.toFixed(2) }}
                                                </td>
                                                <td class="px-4 py-2">
                                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                                                          :class="trade.profit >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                                                        {{ trade.profit >= 0 ? 'Win' : 'Loss' }}
                                                    </span>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
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
const showAccountDetails = ref(false)
const showTradeModal = ref(false)
const selectedStock = ref('')
const selectedStockData = ref(null)
const priceChart = ref(null)
const mockTradeData = ref([])

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

const getWinRateClass = (value) => {
    if (value >= 0.7) return 'text-green-600'  // 70%+ win rate
    if (value >= 0.5) return 'text-yellow-600' // 50-69% win rate
    return 'text-red-600'                       // <50% win rate
}

const getStreakClass = (value) => {
    if (value > 0) return 'bg-green-100 text-green-800'  // Winning streak
    if (value < 0) return 'bg-red-100 text-red-800'      // Losing streak
    return 'bg-gray-100 text-gray-800'                   // Neutral
}

const getAverageWin = () => {
    if (!tradingStatus.value?.portfolio) return 0
    const wins = Object.values(tradingStatus.value.portfolio)
        .map(p => p.performance?.avg_win || 0)
        .filter(w => w > 0)
    return wins.length > 0 ? wins.reduce((a, b) => a + b, 0) / wins.length : 0
}

const getAverageLoss = () => {
    if (!tradingStatus.value?.portfolio) return 0
    const losses = Object.values(tradingStatus.value.portfolio)
        .map(p => p.performance?.avg_loss || 0)
        .filter(l => l > 0)
    return losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / losses.length : 0
}

const getLargestWin = () => {
    if (!tradingStatus.value?.portfolio) return 0
    const largestWins = Object.values(tradingStatus.value.portfolio)
        .map(p => p.performance?.largest_win || 0)
    return Math.max(...largestWins, 0)
}

const getLargestLoss = () => {
    if (!tradingStatus.value?.portfolio) return 0
    const largestLosses = Object.values(tradingStatus.value.portfolio)
        .map(p => p.performance?.largest_loss || 0)
    return Math.max(...largestLosses, 0)
}

const getWinRateBadgeClass = (value) => {
    if (value >= 0.7) return 'bg-green-100 text-green-800'  // 70%+ win rate
    if (value >= 0.5) return 'bg-yellow-100 text-yellow-800' // 50-69% win rate
    return 'bg-red-100 text-red-800'                       // <50% win rate
}

const getStreakBadgeClass = (value) => {
    if (value > 0) return 'bg-green-100 text-green-800'  // Winning streak
    if (value < 0) return 'bg-red-100 text-red-800'      // Losing streak
    return 'bg-gray-100 text-gray-800'                   // Neutral
}

const openTradeDetails = (symbol) => {
    selectedStock.value = symbol
    selectedStockData.value = tradingStatus.value?.portfolio[symbol] || null
    generateMockTradeData(symbol)
    showTradeModal.value = true
    
    // Draw chart after modal is shown
    setTimeout(() => {
        drawPriceChart()
    }, 100)
}

const closeTradeModal = () => {
    showTradeModal.value = false
    selectedStock.value = ''
    selectedStockData.value = null
    mockTradeData.value = []
}

const generateMockTradeData = (symbol) => {
    const trades = []
    const totalTrades = tradingStatus.value?.portfolio[symbol]?.performance?.total_trades || 10
    const wins = tradingStatus.value?.portfolio[symbol]?.performance?.wins || 6
    const losses = totalTrades - wins
    
    // Generate realistic trade data
    for (let i = 0; i < Math.min(totalTrades, 10); i++) {
        const isWin = i < wins
        const buyPrice = 150 + Math.random() * 100 // $150-250
        const sellPrice = isWin 
            ? buyPrice + (Math.random() * 50 + 10) // Win: +$10-60
            : buyPrice - (Math.random() * 30 + 5)  // Loss: -$5-35
        const shares = Math.floor(Math.random() * 100) + 10 // 10-110 shares
        const profit = (sellPrice - buyPrice) * shares
        
        trades.push({
            id: i + 1,
            date: new Date(Date.now() - (i * 24 * 60 * 60 * 1000)).toLocaleDateString(),
            type: 'Day Trade',
            shares: shares,
            buyPrice: buyPrice,
            sellPrice: sellPrice,
            profit: profit
        })
    }
    
    mockTradeData.value = trades.reverse() // Show newest first
}

const drawPriceChart = () => {
    if (!priceChart.value) return
    
    const canvas = priceChart.value
    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height)
    
    // Generate sample price data for the last 30 days
    const data = []
    let price = 150 + Math.random() * 100
    for (let i = 0; i < 30; i++) {
        price += (Math.random() - 0.5) * 10 // Random walk
        data.push({
            x: i,
            price: Math.max(50, price), // Keep price above $50
            volume: Math.random() * 1000000
        })
    }
    
    // Find min/max for scaling
    const minPrice = Math.min(...data.map(d => d.price))
    const maxPrice = Math.max(...data.map(d => d.price))
    const priceRange = maxPrice - minPrice
    
    // Draw price line
    ctx.beginPath()
    ctx.strokeStyle = '#3B82F6'
    ctx.lineWidth = 3
    
    data.forEach((point, index) => {
        const x = (index / (data.length - 1)) * (width - 40) + 20
        const y = height - 40 - ((point.price - minPrice) / priceRange) * (height - 80)
        
        if (index === 0) {
            ctx.moveTo(x, y)
        } else {
            ctx.lineTo(x, y)
        }
    })
    ctx.stroke()
    
    // Add buy/sell markers
    const buyPoints = [5, 12, 18, 25] // Random buy points
    const sellPoints = [8, 15, 21, 28] // Random sell points
    
    buyPoints.forEach(index => {
        if (index < data.length) {
            const x = (index / (data.length - 1)) * (width - 40) + 20
            const y = height - 40 - ((data[index].price - minPrice) / priceRange) * (height - 80)
            
            // Buy marker (green circle)
            ctx.beginPath()
            ctx.fillStyle = '#10B981'
            ctx.arc(x, y, 6, 0, 2 * Math.PI)
            ctx.fill()
            
            // Buy label
            ctx.fillStyle = '#065F46'
            ctx.font = '10px Arial'
            ctx.fillText('BUY', x - 12, y - 10)
        }
    })
    
    sellPoints.forEach(index => {
        if (index < data.length) {
            const x = (index / (data.length - 1)) * (width - 40) + 20
            const y = height - 40 - ((data[index].price - minPrice) / priceRange) * (height - 80)
            
            // Sell marker (red circle)
            ctx.beginPath()
            ctx.fillStyle = '#EF4444'
            ctx.arc(x, y, 6, 0, 2 * Math.PI)
            ctx.fill()
            
            // Sell label
            ctx.fillStyle = '#991B1B'
            ctx.font = '10px Arial'
            ctx.fillText('SELL', x - 15, y - 10)
        }
    })
    
    // Draw axes
    ctx.beginPath()
    ctx.strokeStyle = '#6B7280'
    ctx.lineWidth = 1
    // Y-axis
    ctx.moveTo(20, 20)
    ctx.lineTo(20, height - 40)
    // X-axis
    ctx.moveTo(20, height - 40)
    ctx.lineTo(width - 20, height - 40)
    ctx.stroke()
    
    // Add labels
    ctx.fillStyle = '#6B7280'
    ctx.font = '12px Arial'
    ctx.fillText(`$${minPrice.toFixed(0)}`, 2, height - 35)
    ctx.fillText(`$${maxPrice.toFixed(0)}`, 2, 25)
    ctx.fillText('30 days ago', 25, height - 20)
    ctx.fillText('Today', width - 60, height - 20)
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