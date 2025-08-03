<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class DashboardController extends Controller
{
    private string $backendUrl;

    public function __construct()
    {
        $this->backendUrl = env('BACKEND_URL', 'http://localhost:8080');
    }

    /**
     * Display the trading dashboard
     */
    public function index(): Response
    {
        // Get initial data for dashboard
        $initialData = $this->getInitialDashboardData();

        return Inertia::render('Dashboard', [
            'initialData' => $initialData,
            'backendConnected' => $initialData['backend_connected'] ?? false
        ]);
    }

    /**
     * Get initial dashboard data
     */
    private function getInitialDashboardData(): array
    {
        try {
            // Try to get status from backend
            $response = Http::timeout(5)->get("{$this->backendUrl}/status");
            
            if ($response->successful()) {
                $statusData = $response->json();
                
                return [
                    'backend_connected' => true,
                    'trading_status' => $statusData,
                    'last_updated' => now()->toISOString()
                ];
            }
            
            return [
                'backend_connected' => false,
                'trading_status' => null,
                'error' => 'Backend not responding',
                'last_updated' => now()->toISOString()
            ];
            
        } catch (\Exception $e) {
            Log::warning('Could not connect to backend for initial data', ['error' => $e->getMessage()]);
            
            return [
                'backend_connected' => false,
                'trading_status' => null,
                'error' => 'Backend connection failed',
                'last_updated' => now()->toISOString()
            ];
        }
    }

    /**
     * Show the trading configuration page
     */
    public function configuration(): Response
    {
        $configData = $this->getConfigurationData();

        return Inertia::render('Configuration', [
            'configData' => $configData,
            'backendConnected' => $configData['backend_connected'] ?? false
        ]);
    }

    /**
     * Get configuration data
     */
    private function getConfigurationData(): array
    {
        try {
            $response = Http::timeout(5)->get("{$this->backendUrl}/status");
            
            if ($response->successful()) {
                $data = $response->json();
                
                return [
                    'backend_connected' => true,
                    'current_mode' => $data['mode'] ?? 'paper',
                    'current_stocks' => $data['stocks'] ?? [],
                    'available_stocks' => [
                        'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 
                        'AMZN', 'META', 'NFLX', 'AMD', 'INTC'
                    ]
                ];
            }
            
            return [
                'backend_connected' => false,
                'current_mode' => 'paper',
                'current_stocks' => [],
                'available_stocks' => [
                    'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 
                    'AMZN', 'META', 'NFLX', 'AMD', 'INTC'
                ]
            ];
            
        } catch (\Exception $e) {
            return [
                'backend_connected' => false,
                'current_mode' => 'paper',
                'current_stocks' => [],
                'available_stocks' => [
                    'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 
                    'AMZN', 'META', 'NFLX', 'AMD', 'INTC'
                ]
            ];
        }
    }

    /**
     * Show the analytics page
     */
    public function analytics(): Response
    {
        $analyticsData = $this->getAnalyticsData();

        return Inertia::render('Analytics', [
            'analyticsData' => $analyticsData,
            'backendConnected' => $analyticsData['backend_connected'] ?? false
        ]);
    }

    /**
     * Get analytics data
     */
    private function getAnalyticsData(): array
    {
        try {
            $response = Http::timeout(5)->get("{$this->backendUrl}/status");
            
            if ($response->successful()) {
                $data = $response->json();
                
                return [
                    'backend_connected' => true,
                    'portfolio' => $data['portfolio'] ?? [],
                    'learning_progress' => $data['learning_progress'] ?? [],
                    'performance_metrics' => $this->calculatePerformanceMetrics($data)
                ];
            }
            
            return [
                'backend_connected' => false,
                'portfolio' => [],
                'learning_progress' => [],
                'performance_metrics' => []
            ];
            
        } catch (\Exception $e) {
            return [
                'backend_connected' => false,
                'portfolio' => [],
                'learning_progress' => [],
                'performance_metrics' => []
            ];
        }
    }

    /**
     * Calculate performance metrics
     */
    private function calculatePerformanceMetrics(array $data): array
    {
        $metrics = [];
        
        if (isset($data['portfolio']) && is_array($data['portfolio'])) {
            $totalBalance = 0;
            $totalTrades = 0;
            $totalReturn = 0;
            
            foreach ($data['portfolio'] as $symbol => $portfolioData) {
                if (isset($portfolioData['performance'])) {
                    $performance = $portfolioData['performance'];
                    $totalBalance += $performance['balance'] ?? 0;
                    $totalTrades += $performance['total_trades'] ?? 0;
                    $totalReturn += $performance['total_return'] ?? 0;
                }
            }
            
            $metrics = [
                'total_balance' => $totalBalance,
                'total_trades' => $totalTrades,
                'average_return' => count($data['portfolio']) > 0 ? $totalReturn / count($data['portfolio']) : 0,
                'active_symbols' => count($data['portfolio'])
            ];
        }
        
        return $metrics;
    }

    /**
     * Show the logs page
     */
    public function logs(): Response
    {
        return Inertia::render('Logs', [
            'backendUrl' => $this->backendUrl
        ]);
    }

    /**
     * Show the advanced training page
     */
    public function advancedTraining(): Response
    {
        return Inertia::render('AdvancedTraining', [
            'backendConnected' => $this->checkBackendConnection()
        ]);
    }

    /**
     * Check if backend is connected
     */
    private function checkBackendConnection(): bool
    {
        try {
            $response = Http::timeout(5)->get("{$this->backendUrl}/health");
            return $response->successful();
        } catch (\Exception $e) {
            return false;
        }
    }
}